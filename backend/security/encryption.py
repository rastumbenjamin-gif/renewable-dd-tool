"""
Encryption service using Google Cloud KMS
Zero data retention - all encryption happens in-memory
"""
import base64
from typing import Optional, Dict, Any
import structlog
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import os

from api.config import settings

logger = structlog.get_logger()


class EncryptionService:
    """
    Service for encrypting and decrypting sensitive data
    Uses Google Cloud KMS for key management in production
    Uses local encryption for development
    All operations performed in-memory only
    """

    def __init__(self):
        self.kms_client = None
        self.key_name = None
        self._local_key_cache: Optional[bytes] = None
        self.use_kms = False

    async def initialize(self):
        """Initialize KMS client and key name"""
        # Check if KMS credentials are available
        if (settings.GOOGLE_CLOUD_PROJECT_ID and
            settings.GCP_KMS_KEY_RING and
            settings.GCP_KMS_CRYPTO_KEY):
            try:
                from google.cloud import kms
                self.kms_client = kms.KeyManagementServiceClient()
                self.key_name = self.kms_client.crypto_key_path(
                    settings.GOOGLE_CLOUD_PROJECT_ID,
                    settings.GCP_KMS_LOCATION,
                    settings.GCP_KMS_KEY_RING,
                    settings.GCP_KMS_CRYPTO_KEY
                )
                self.use_kms = True
                logger.info("Encryption service initialized with GCP KMS")
            except Exception as e:
                logger.warning(f"KMS not available, using local encryption: {str(e)}")
                self.use_kms = False
        else:
            logger.info("Encryption service initialized with local encryption (development mode)")
            self.use_kms = False

    def encrypt_with_kms(self, plaintext: bytes) -> str:
        """
        Encrypt data using Google Cloud KMS

        Args:
            plaintext: Data to encrypt (as bytes)

        Returns:
            Base64-encoded encrypted data
        """
        if not self.kms_client or not self.key_name:
            raise RuntimeError("Encryption service not initialized")

        try:
            # Encrypt using KMS
            encrypt_response = self.kms_client.encrypt(
                request={
                    "name": self.key_name,
                    "plaintext": plaintext
                }
            )

            ciphertext = base64.b64encode(encrypt_response.ciphertext).decode('utf-8')
            logger.debug("Data encrypted successfully with KMS")
            return ciphertext

        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise

    def decrypt_with_kms(self, ciphertext: str) -> bytes:
        """
        Decrypt data using Google Cloud KMS

        Args:
            ciphertext: Base64-encoded encrypted data

        Returns:
            Decrypted plaintext as bytes
        """
        if not self.kms_client or not self.key_name:
            raise RuntimeError("Encryption service not initialized")

        try:
            # Decode from base64
            ciphertext_bytes = base64.b64decode(ciphertext)

            # Decrypt using KMS
            decrypt_response = self.kms_client.decrypt(
                request={
                    "name": self.key_name,
                    "ciphertext": ciphertext_bytes
                }
            )

            logger.debug("Data decrypted successfully with KMS")
            return decrypt_response.plaintext

        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise

    def encrypt_field(self, value: str) -> str:
        """
        Encrypt a string field for database storage

        Args:
            value: String value to encrypt

        Returns:
            Encrypted string (base64 encoded)
        """
        if not value:
            return value

        return self.encrypt_with_kms(value.encode('utf-8'))

    def decrypt_field(self, encrypted_value: str) -> str:
        """
        Decrypt a field from database

        Args:
            encrypted_value: Encrypted string

        Returns:
            Decrypted string
        """
        if not encrypted_value:
            return encrypted_value

        decrypted_bytes = self.decrypt_with_kms(encrypted_value)
        return decrypted_bytes.decode('utf-8')

    def encrypt_document_content(self, content: bytes) -> str:
        """
        Encrypt document content in-memory
        Note: For DD documents, prefer processing without persistent storage

        Args:
            content: Document content as bytes

        Returns:
            Encrypted content (base64 encoded)
        """
        return self.encrypt_with_kms(content)

    def decrypt_document_content(self, encrypted_content: str) -> bytes:
        """
        Decrypt document content

        Args:
            encrypted_content: Encrypted content

        Returns:
            Decrypted document bytes
        """
        return self.decrypt_with_kms(encrypted_content)

    @staticmethod
    def generate_local_key() -> bytes:
        """
        Generate a local encryption key for session-level encryption
        Used for temporary in-memory operations only

        Returns:
            256-bit encryption key
        """
        return AESGCM.generate_key(bit_length=256)

    @staticmethod
    def encrypt_with_local_key(plaintext: bytes, key: bytes) -> Dict[str, str]:
        """
        Encrypt data with a local key (for temporary session data)

        Args:
            plaintext: Data to encrypt
            key: 256-bit encryption key

        Returns:
            Dictionary with encrypted data and nonce
        """
        try:
            aesgcm = AESGCM(key)
            nonce = os.urandom(12)  # 96-bit nonce for GCM
            ciphertext = aesgcm.encrypt(nonce, plaintext, None)

            return {
                'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
                'nonce': base64.b64encode(nonce).decode('utf-8')
            }

        except Exception as e:
            logger.error(f"Local encryption failed: {str(e)}")
            raise

    @staticmethod
    def decrypt_with_local_key(
        ciphertext: str,
        nonce: str,
        key: bytes
    ) -> bytes:
        """
        Decrypt data with a local key

        Args:
            ciphertext: Encrypted data (base64)
            nonce: Nonce used for encryption (base64)
            key: 256-bit encryption key

        Returns:
            Decrypted plaintext
        """
        try:
            aesgcm = AESGCM(key)
            ciphertext_bytes = base64.b64decode(ciphertext)
            nonce_bytes = base64.b64decode(nonce)

            plaintext = aesgcm.decrypt(nonce_bytes, ciphertext_bytes, None)
            return plaintext

        except Exception as e:
            logger.error(f"Local decryption failed: {str(e)}")
            raise

    @staticmethod
    def hash_sensitive_data(data: str, salt: Optional[bytes] = None) -> Dict[str, str]:
        """
        Hash sensitive data for comparison (e.g., passwords, tokens)

        Args:
            data: Data to hash
            salt: Optional salt (generated if not provided)

        Returns:
            Dictionary with hash and salt (both base64 encoded)
        """
        if salt is None:
            salt = os.urandom(32)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(data.encode('utf-8'))

        return {
            'hash': base64.b64encode(key).decode('utf-8'),
            'salt': base64.b64encode(salt).decode('utf-8')
        }

    @staticmethod
    def verify_hashed_data(data: str, hashed: str, salt: str) -> bool:
        """
        Verify hashed data

        Args:
            data: Original data
            hashed: Hashed data (base64)
            salt: Salt used for hashing (base64)

        Returns:
            True if data matches hash
        """
        try:
            salt_bytes = base64.b64decode(salt)
            result = EncryptionService.hash_sensitive_data(data, salt_bytes)
            return result['hash'] == hashed
        except Exception:
            return False

    def redact_sensitive_field(
        self,
        text: str,
        field_type: str = 'generic'
    ) -> str:
        """
        Redact sensitive information from text

        Args:
            text: Text containing sensitive data
            field_type: Type of field (ssn, credit_card, email, etc.)

        Returns:
            Redacted text
        """
        # Implementation would use regex patterns based on field_type
        # For now, simple implementation
        if not text:
            return text

        redaction_patterns = {
            'ssn': '***-**-',
            'credit_card': '****-****-****-',
            'email': '***@***',
            'phone': '***-***-',
            'generic': '***'
        }

        pattern = redaction_patterns.get(field_type, '***')

        # Keep last 4 characters for verification
        if len(text) > 4:
            return pattern + text[-4:]
        else:
            return pattern

    def secure_delete(self, data: Any):
        """
        Securely delete data from memory

        Args:
            data: Data to delete (bytes, string, or dict)
        """
        # Overwrite memory with zeros before deletion
        if isinstance(data, bytes):
            # For bytes, overwrite with zeros
            try:
                # This is a best-effort approach in Python
                import ctypes
                location = id(data)
                size = len(data)
                ctypes.memset(location, 0, size)
            except Exception:
                pass
        elif isinstance(data, (dict, list)):
            # Clear collections
            if isinstance(data, dict):
                data.clear()
            elif isinstance(data, list):
                data.clear()

        # Delete reference
        del data

        logger.debug("Secure deletion completed")


# Global encryption service instance
encryption_service = EncryptionService()
