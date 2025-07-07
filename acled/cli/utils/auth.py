"""Secure credential storage utilities."""

import json
import os
import platform
from pathlib import Path
from typing import Optional, Tuple

try:
    import keyring
    HAS_KEYRING = True
except ImportError:
    keyring = None
    HAS_KEYRING = False

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import base64
    HAS_CRYPTOGRAPHY = True
except ImportError:
    Fernet = None
    hashes = None
    PBKDF2HMAC = None
    base64 = None
    HAS_CRYPTOGRAPHY = False


class AuthenticationError(Exception):
    """Authentication-related errors."""


class CredentialManager:
    """Manages secure storage and retrieval of API credentials."""
    
    SERVICE_NAME = "acled-cli"
    API_KEY_USERNAME = "api-key"
    EMAIL_USERNAME = "email"
    
    def __init__(self):
        self.use_keyring = HAS_KEYRING and self._keyring_available()
        self.use_encryption = HAS_CRYPTOGRAPHY
        
        if not self.use_keyring and not self.use_encryption:
            raise AuthenticationError(
                "Neither keyring nor cryptography is available. "
                "Install with: pip install acled[cli]"
            )
    
    def _keyring_available(self) -> bool:
        """Check if keyring is available and functional."""
        try:
            # Test keyring functionality
            keyring.get_keyring()
            return True
        except Exception:
            return False
    
    def store_credentials(self, api_key: str, email: str) -> None:
        """Store credentials securely."""
        if self.use_keyring:
            self._store_with_keyring(api_key, email)
        else:
            self._store_with_encryption(api_key, email)
    
    def get_credentials(self) -> Tuple[str, str]:
        """Retrieve stored credentials."""
        if self.use_keyring:
            return self._get_from_keyring()
        else:
            return self._get_from_encrypted_file()
    
    def has_stored_credentials(self) -> bool:
        """Check if credentials are stored."""
        try:
            api_key, email = self.get_credentials()
            return bool(api_key and email)
        except Exception:
            return False
    
    def get_stored_email(self) -> Optional[str]:
        """Get just the stored email (for status display)."""
        try:
            _, email = self.get_credentials()
            return email
        except Exception:
            return None
    
    def clear_credentials(self) -> None:
        """Clear stored credentials."""
        if self.use_keyring:
            self._clear_keyring()
        else:
            self._clear_encrypted_file()
    
    def _store_with_keyring(self, api_key: str, email: str) -> None:
        """Store credentials using system keyring."""
        try:
            keyring.set_password(self.SERVICE_NAME, self.API_KEY_USERNAME, api_key)
            keyring.set_password(self.SERVICE_NAME, self.EMAIL_USERNAME, email)
        except Exception as e:
            raise AuthenticationError(f"Failed to store credentials in keyring: {e}") from e
    
    def _get_from_keyring(self) -> Tuple[str, str]:
        """Retrieve credentials from system keyring."""
        try:
            api_key = keyring.get_password(self.SERVICE_NAME, self.API_KEY_USERNAME)
            email = keyring.get_password(self.SERVICE_NAME, self.EMAIL_USERNAME)
            
            if not api_key or not email:
                raise AuthenticationError("No stored credentials found")
            
            return api_key, email
        except AuthenticationError:
            raise
        except Exception as e:
            raise AuthenticationError(f"Failed to retrieve credentials from keyring: {e}") from e
    
    def _clear_keyring(self) -> None:
        """Clear credentials from system keyring."""
        try:
            keyring.delete_password(self.SERVICE_NAME, self.API_KEY_USERNAME)
            keyring.delete_password(self.SERVICE_NAME, self.EMAIL_USERNAME)
        except Exception:
            # Ignore errors when clearing (credentials might not exist)
            pass
    
    def _get_config_dir(self) -> Path:
        """Get platform-appropriate config directory."""
        if platform.system() == "Windows":
            config_dir = Path(os.environ.get("APPDATA", "~")) / "acled-cli"
        elif platform.system() == "Darwin":  # macOS
            config_dir = Path("~/.config/acled-cli").expanduser()
        else:  # Linux and others
            config_dir = Path(os.environ.get("XDG_CONFIG_HOME", "~/.config")).expanduser() / "acled-cli"
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    def _get_credentials_file(self) -> Path:
        """Get path to encrypted credentials file."""
        return self._get_config_dir() / "credentials.enc"
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password and salt."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def _get_machine_identifier(self) -> str:
        """Get a machine-specific identifier for encryption."""
        # Use platform and user info as basis for machine-specific key
        import getpass
        machine_id = f"{platform.node()}-{platform.system()}-{getpass.getuser()}"
        return machine_id[:32].ljust(32, '0')  # Ensure consistent length
    
    def _store_with_encryption(self, api_key: str, email: str) -> None:
        """Store credentials using file encryption."""
        try:
            # Use machine-specific password for encryption
            password = self._get_machine_identifier()
            salt = os.urandom(16)
            key = self._derive_key(password, salt)
            fernet = Fernet(key)
            
            # Prepare data to encrypt
            data = json.dumps({
                "api_key": api_key,
                "email": email
            })
            
            # Encrypt data
            encrypted_data = fernet.encrypt(data.encode())
            
            # Store salt and encrypted data
            credentials_file = self._get_credentials_file()
            with open(credentials_file, 'wb') as f:
                f.write(salt + encrypted_data)
            
            # Set restrictive permissions (Unix-like systems)
            if platform.system() != "Windows":
                credentials_file.chmod(0o600)
                
        except Exception as e:
            raise AuthenticationError(f"Failed to store encrypted credentials: {e}") from e
    
    def _get_from_encrypted_file(self) -> Tuple[str, str]:
        """Retrieve credentials from encrypted file."""
        try:
            credentials_file = self._get_credentials_file()
            if not credentials_file.exists():
                raise AuthenticationError("No stored credentials found")
            
            # Read salt and encrypted data
            with open(credentials_file, 'rb') as f:
                file_data = f.read()
            
            salt = file_data[:16]
            encrypted_data = file_data[16:]
            
            # Decrypt data
            password = self._get_machine_identifier()
            key = self._derive_key(password, salt)
            fernet = Fernet(key)
            
            decrypted_data = fernet.decrypt(encrypted_data)
            data = json.loads(decrypted_data.decode())
            
            return data["api_key"], data["email"]
            
        except AuthenticationError:
            raise
        except Exception as e:
            raise AuthenticationError(f"Failed to retrieve encrypted credentials: {e}") from e
    
    def _clear_encrypted_file(self) -> None:
        """Clear encrypted credentials file."""
        try:
            credentials_file = self._get_credentials_file()
            if credentials_file.exists():
                credentials_file.unlink()
        except Exception:
            # Ignore errors when clearing
            pass