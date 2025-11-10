# Google Drive Integration Guide

## Overview
Allow users to connect their Google Drive and import files from specific folders instead of uploading files one by one.

## Prerequisites

### 1. Set up Google Cloud Project
1. Go to https://console.cloud.google.com
2. Create a new project or select existing one
3. Enable Google Drive API:
   - Go to "APIs & Services" → "Library"
   - Search for "Google Drive API"
   - Click "Enable"

### 2. Create OAuth2 Credentials
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Application type: **Web application**
4. Name: `Renewable DD Tool`
5. Authorized redirect URIs:
   ```
   https://renewable-dd-tool.netlify.app/auth/google/callback
   http://localhost:3000/auth/google/callback
   ```
6. Click "Create"
7. **Save the Client ID and Client Secret**

### 3. Add Environment Variables

#### Backend (Hugging Face Space)
Add these secrets in Hugging Face Space settings:
- `GOOGLE_CLIENT_ID` - Your OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Your OAuth client secret
- `GOOGLE_REDIRECT_URI` - `https://renewable-dd-tool.netlify.app/auth/google/callback`

#### Frontend (Netlify)
Add these environment variables:
- `NEXT_PUBLIC_GOOGLE_CLIENT_ID` - Your OAuth client ID
- `NEXT_PUBLIC_REDIRECT_URI` - `https://renewable-dd-tool.netlify.app/auth/google/callback`

## Implementation Plan

### Phase 1: OAuth Authentication (2-3 hours)
**Backend:**
- [ ] Create `/api/v1/auth/google/authorize` endpoint
- [ ] Create `/api/v1/auth/google/callback` endpoint
- [ ] Store OAuth tokens securely (encrypted)
- [ ] Token refresh logic

**Frontend:**
- [ ] "Connect Google Drive" button
- [ ] OAuth popup window
- [ ] Handle callback and store session
- [ ] Display connection status

### Phase 2: Drive Folder Browser (3-4 hours)
**Backend:**
- [ ] Create `/api/v1/drive/folders` endpoint (list folders)
- [ ] Create `/api/v1/drive/files/{folder_id}` endpoint
- [ ] Permission checking (user has access)

**Frontend:**
- [ ] Folder browser UI component
- [ ] File tree view
- [ ] Search functionality
- [ ] File preview

### Phase 3: File Import (2-3 hours)
**Backend:**
- [ ] Create `/api/v1/drive/import` endpoint
- [ ] Download files from Drive to backend
- [ ] Process files (same as upload)
- [ ] Batch import support

**Frontend:**
- [ ] File selection checkboxes
- [ ] "Import Selected" button
- [ ] Progress indicator
- [ ] Success/error notifications

### Phase 4: Sync & Updates (3-4 hours)
**Backend:**
- [ ] Watch for Drive changes (webhooks)
- [ ] Auto-sync when files change
- [ ] Conflict resolution

**Frontend:**
- [ ] Sync status indicator
- [ ] Manual sync button
- [ ] Last sync timestamp

## Estimated Total Time: 10-14 hours

## Security Considerations
1. **Never store credentials in frontend** - Only client ID is public
2. **Encrypt tokens** - Use backend encryption for OAuth tokens
3. **Limit scopes** - Only request `drive.readonly` or specific folder access
4. **HTTPS only** - All OAuth flows must use HTTPS
5. **Token expiry** - Implement proper refresh token flow

## User Flow

### First Time Connection:
1. User clicks "Connect Google Drive"
2. OAuth popup opens
3. User logs in to Google and grants permissions
4. Backend receives OAuth code
5. Backend exchanges code for access token
6. Frontend shows "Connected" status

### Using Google Drive:
1. User clicks "Browse Drive" or "Import from Drive"
2. Folder browser opens showing their Drive folders
3. User navigates to DD folder
4. User selects files to import
5. Backend downloads files from Drive
6. Files processed and added to project
7. Progress shown in UI

## Benefits Over Manual Upload
- ✅ Faster - Import entire folders at once
- ✅ No file size limits (handles large files better)
- ✅ Organized - Maintains folder structure
- ✅ Synced - Can auto-update when Drive files change
- ✅ Collaborative - Multiple users can access same Drive folder
- ✅ Audit trail - Know which Drive files were analyzed

## Next Steps
1. Set up Google Cloud project and get credentials
2. Add environment variables to Hugging Face and Netlify
3. I'll implement the OAuth flow and Drive API integration
4. Test with a sample Drive folder
5. Deploy and share with colleagues

## Cost
- Google Drive API: **Free** (1 billion requests/day limit)
- OAuth: **Free**
- Storage: Only costs if storing copies (we can stream files)
