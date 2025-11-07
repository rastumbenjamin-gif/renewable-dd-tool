"""
Google Drive API client for document management
"""
from typing import List, Optional, Dict, Any, BinaryIO
import io
import os
from datetime import datetime
import structlog
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError

from api.config import settings
from security.encryption import EncryptionService

logger = structlog.get_logger()


class GoogleDriveClient:
    """Client for interacting with Google Drive API"""

    SCOPES = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive.metadata.readonly'
    ]

    # DD folder structure
    FOLDER_STRUCTURE = {
        'Legal': ['Contracts', 'Permits', 'Compliance'],
        'Technical': ['Equipment', 'Production Data', 'Interconnection'],
        'Financial': ['Models', 'Audits', 'Tax'],
        'Environmental': ['Assessments', 'Permits', 'Reports'],
        'Commercial': ['PPAs', 'Offtake', 'Market Analysis']
    }

    def __init__(self, credentials: Optional[Credentials] = None):
        self.credentials = credentials
        self.service = None
        self.encryption_service = EncryptionService()

    def authenticate_with_oauth(self, authorization_code: str) -> Credentials:
        """
        Authenticate using OAuth 2.0 authorization code

        Args:
            authorization_code: Authorization code from OAuth flow

        Returns:
            Google OAuth credentials
        """
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                    }
                },
                scopes=self.SCOPES,
                redirect_uri=settings.GOOGLE_REDIRECT_URI,
            )

            flow.fetch_token(code=authorization_code)
            self.credentials = flow.credentials
            self.service = build('drive', settings.GOOGLE_DRIVE_API_VERSION, credentials=self.credentials)

            logger.info("Successfully authenticated with Google Drive")
            return self.credentials

        except Exception as e:
            logger.error(f"OAuth authentication failed: {str(e)}")
            raise

    def refresh_credentials(self) -> Credentials:
        """Refresh expired credentials"""
        if self.credentials and self.credentials.expired and self.credentials.refresh_token:
            try:
                self.credentials.refresh(Request())
                logger.info("Credentials refreshed successfully")
                return self.credentials
            except Exception as e:
                logger.error(f"Failed to refresh credentials: {str(e)}")
                raise
        return self.credentials

    def initialize_service(self):
        """Initialize the Drive service"""
        if not self.service:
            if not self.credentials:
                raise ValueError("Credentials not set. Authenticate first.")
            self.service = build('drive', settings.GOOGLE_DRIVE_API_VERSION, credentials=self.credentials)

    def create_project_folder_structure(self, project_name: str) -> Dict[str, str]:
        """
        Create standardized DD folder structure for a project

        Args:
            project_name: Name of the DD project

        Returns:
            Dictionary mapping folder names to folder IDs
        """
        self.initialize_service()
        folder_ids = {}

        try:
            # Create root project folder
            root_folder_name = f"DD-{project_name}"
            root_folder_metadata = {
                'name': root_folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            root_folder = self.service.files().create(
                body=root_folder_metadata,
                fields='id, name'
            ).execute()

            root_folder_id = root_folder['id']
            folder_ids['root'] = root_folder_id
            logger.info(f"Created root folder: {root_folder_name} (ID: {root_folder_id})")

            # Create category folders
            for category, subfolders in self.FOLDER_STRUCTURE.items():
                category_metadata = {
                    'name': category,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [root_folder_id]
                }
                category_folder = self.service.files().create(
                    body=category_metadata,
                    fields='id, name'
                ).execute()

                category_id = category_folder['id']
                folder_ids[category] = category_id
                logger.info(f"Created category folder: {category}")

                # Create subfolders
                for subfolder in subfolders:
                    subfolder_metadata = {
                        'name': subfolder,
                        'mimeType': 'application/vnd.google-apps.folder',
                        'parents': [category_id]
                    }
                    subfolder_obj = self.service.files().create(
                        body=subfolder_metadata,
                        fields='id, name'
                    ).execute()
                    folder_ids[f"{category}/{subfolder}"] = subfolder_obj['id']

            logger.info(f"Project folder structure created successfully for {project_name}")
            return folder_ids

        except HttpError as error:
            logger.error(f"Failed to create folder structure: {error}")
            raise

    def list_files_in_folder(self, folder_id: str, recursive: bool = False) -> List[Dict[str, Any]]:
        """
        List all files in a folder

        Args:
            folder_id: Google Drive folder ID
            recursive: Whether to list files recursively in subfolders

        Returns:
            List of file metadata dictionaries
        """
        self.initialize_service()
        files = []

        try:
            query = f"'{folder_id}' in parents and trashed=false"
            page_token = None

            while True:
                response = self.service.files().list(
                    q=query,
                    spaces='drive',
                    fields='nextPageToken, files(id, name, mimeType, size, createdTime, modifiedTime, parents, webViewLink)',
                    pageToken=page_token
                ).execute()

                batch_files = response.get('files', [])
                files.extend(batch_files)

                page_token = response.get('nextPageToken')
                if not page_token:
                    break

            # If recursive, get files from subfolders
            if recursive:
                for file in batch_files:
                    if file['mimeType'] == 'application/vnd.google-apps.folder':
                        subfolder_files = self.list_files_in_folder(file['id'], recursive=True)
                        files.extend(subfolder_files)

            logger.info(f"Listed {len(files)} files in folder {folder_id}")
            return files

        except HttpError as error:
            logger.error(f"Failed to list files: {error}")
            raise

    def download_file(self, file_id: str) -> bytes:
        """
        Download file from Google Drive

        Args:
            file_id: Google Drive file ID

        Returns:
            File content as bytes
        """
        self.initialize_service()

        try:
            request = self.service.files().get_media(fileId=file_id)
            file_buffer = io.BytesIO()
            downloader = MediaIoBaseDownload(file_buffer, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()
                logger.info(f"Download progress: {int(status.progress() * 100)}%")

            file_content = file_buffer.getvalue()
            logger.info(f"Downloaded file {file_id} ({len(file_content)} bytes)")

            return file_content

        except HttpError as error:
            logger.error(f"Failed to download file: {error}")
            raise

    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """
        Get file metadata

        Args:
            file_id: Google Drive file ID

        Returns:
            File metadata dictionary
        """
        self.initialize_service()

        try:
            file_metadata = self.service.files().get(
                fileId=file_id,
                fields='id, name, mimeType, size, createdTime, modifiedTime, parents, webViewLink, owners, permissions'
            ).execute()

            return file_metadata

        except HttpError as error:
            logger.error(f"Failed to get file metadata: {error}")
            raise

    def upload_file(
        self,
        file_path: str,
        folder_id: str,
        file_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload file to Google Drive

        Args:
            file_path: Local file path
            folder_id: Target folder ID in Google Drive
            file_name: Optional custom file name

        Returns:
            Uploaded file metadata
        """
        self.initialize_service()

        if not file_name:
            file_name = os.path.basename(file_path)

        try:
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }

            media = MediaFileUpload(file_path, resumable=True)
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, mimeType, size, webViewLink'
            ).execute()

            logger.info(f"Uploaded file: {file_name} (ID: {file['id']})")
            return file

        except HttpError as error:
            logger.error(f"Failed to upload file: {error}")
            raise

    def delete_file(self, file_id: str):
        """
        Delete file from Google Drive (move to trash)

        Args:
            file_id: Google Drive file ID
        """
        self.initialize_service()

        try:
            self.service.files().delete(fileId=file_id).execute()
            logger.info(f"Deleted file: {file_id}")

        except HttpError as error:
            logger.error(f"Failed to delete file: {error}")
            raise

    def share_folder(self, folder_id: str, email: str, role: str = 'reader'):
        """
        Share folder with a user

        Args:
            folder_id: Google Drive folder ID
            email: Email of the user to share with
            role: Permission role (reader, writer, commenter)
        """
        self.initialize_service()

        try:
            permission = {
                'type': 'user',
                'role': role,
                'emailAddress': email
            }

            self.service.permissions().create(
                fileId=folder_id,
                body=permission,
                fields='id',
                sendNotificationEmail=True
            ).execute()

            logger.info(f"Shared folder {folder_id} with {email} ({role})")

        except HttpError as error:
            logger.error(f"Failed to share folder: {error}")
            raise

    def get_folder_size(self, folder_id: str) -> int:
        """
        Calculate total size of all files in folder

        Args:
            folder_id: Google Drive folder ID

        Returns:
            Total size in bytes
        """
        files = self.list_files_in_folder(folder_id, recursive=True)
        total_size = sum(int(f.get('size', 0)) for f in files if f['mimeType'] != 'application/vnd.google-apps.folder')
        return total_size
