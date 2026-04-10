"""Secure credential storage utilities."""

import getpass
import json
import logging
import os
import platform
from pathlib import Path
from typing import Optional

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
    USERNAME_KEY = "username"
    PASSWORD_KEY = "password"
    AUTH_METHOD_KEY = "auth-method"

    def __init__(self):
        self._log = logging.getLogger(__name__)
        self.use_keyring = HAS_KEYRING and self._keyring_available()
        self.use_encryption = HAS_CRYPTOGRAPHY

        if not self.use_keyring and not self.use_encryption:
            raise AuthenticationError(
                "Neither keyring nor cryptography is available. "
                "Install with: pip install acled[cli]"
            )

        if not self.use_keyring and self.use_encryption:
            self._log.warning(
                "System keyring unavailable; falling back to file-based "
                "credential storage. Credentials are encrypted but the "
                "encryption key is derived from machine identity, which "
                "provides limited protection."
            )

    def _keyring_available(self) -> bool:
        """Check if keyring is available and functional."""
        try:
            keyring.get_keyring()
            return True
        except (RuntimeError, AttributeError, ImportError):
            return False

    def store_credentials(
            self,
            api_key: Optional[str] = None,
            email: Optional[str] = None,
            username: Optional[str] = None,
            password: Optional[str] = None,
            auth_method: str = "legacy"
    ) -> None:
        """Store credentials securely."""
        if self.use_keyring:
            self._store_with_keyring(
                api_key=api_key, email=email, username=username,
                password=password, auth_method=auth_method
            )
        else:
            self._store_with_encryption(
                api_key=api_key, email=email, username=username,
                password=password, auth_method=auth_method
            )

    def get_credentials(self) -> dict:
        """Retrieve stored credentials."""
        if self.use_keyring:
            return self._get_from_keyring()
        return self._get_from_encrypted_file()

    def has_stored_credentials(self) -> bool:
        """Check if credentials are stored."""
        try:
            creds = self.get_credentials()
            auth_method = creds.get('auth_method', 'legacy')
            if auth_method == 'legacy':
                return bool(creds.get('api_key') and creds.get('email'))
            return bool(creds.get('username') and creds.get('password'))
        except (AuthenticationError, OSError, RuntimeError):
            return False

    def get_stored_email(self) -> Optional[str]:
        """Get just the stored email (for status display)."""
        try:
            creds = self.get_credentials()
            return creds.get('email') or creds.get('username')
        except (AuthenticationError, OSError, RuntimeError):
            return None

    def get_token_file(self) -> str:
        """Get path to the OAuth token cache file.

        Returns:
            str: Absolute path to the token cache file.
        """
        return str(self._get_config_dir() / "tokens.json")

    def clear_credentials(self) -> None:
        """Clear stored credentials."""
        if self.use_keyring:
            self._clear_keyring()
        else:
            self._clear_encrypted_file()

    def _store_with_keyring(
            self,
            api_key: Optional[str] = None,
            email: Optional[str] = None,
            username: Optional[str] = None,
            password: Optional[str] = None,
            auth_method: str = "legacy"
    ) -> None:
        """Store credentials using system keyring."""
        try:
            # Store auth method
            keyring.set_password(self.SERVICE_NAME, self.AUTH_METHOD_KEY, auth_method)

            # Store appropriate credentials based on auth method
            if auth_method == "legacy":
                if api_key:
                    keyring.set_password(self.SERVICE_NAME, self.API_KEY_USERNAME, api_key)
                if email:
                    keyring.set_password(self.SERVICE_NAME, self.EMAIL_USERNAME, email)
            else:  # oauth
                if username:
                    keyring.set_password(self.SERVICE_NAME, self.USERNAME_KEY, username)
                if password:
                    keyring.set_password(self.SERVICE_NAME, self.PASSWORD_KEY, password)
        except Exception as e:
            raise AuthenticationError(f"Failed to store credentials in keyring: {e}") from e

    def _get_from_keyring(self) -> dict:
        """Retrieve credentials from system keyring."""
        try:
            auth_method = keyring.get_password(self.SERVICE_NAME, self.AUTH_METHOD_KEY) or "legacy"

            result = {'auth_method': auth_method}

            if auth_method == "legacy":
                api_key = keyring.get_password(self.SERVICE_NAME, self.API_KEY_USERNAME)
                email = keyring.get_password(self.SERVICE_NAME, self.EMAIL_USERNAME)
                if not api_key or not email:
                    raise AuthenticationError("No stored credentials found")
                result.update({'api_key': api_key, 'email': email})
            else:  # oauth
                username = keyring.get_password(self.SERVICE_NAME, self.USERNAME_KEY)
                password = keyring.get_password(self.SERVICE_NAME, self.PASSWORD_KEY)

                if not (username and password):
                    raise AuthenticationError("No stored OAuth credentials found")

                result.update({
                    'username': username,
                    'password': password
                })

            return result
        except AuthenticationError:
            raise
        except Exception as e:
            raise AuthenticationError(f"Failed to retrieve credentials from keyring: {e}") from e

    def _clear_keyring(self) -> None:
        """Clear credentials from system keyring."""
        # Try to delete all possible credential keys
        keys_to_delete = [
            self.API_KEY_USERNAME,
            self.EMAIL_USERNAME,
            self.USERNAME_KEY,
            self.PASSWORD_KEY,
            self.AUTH_METHOD_KEY
        ]

        for key in keys_to_delete:
            try:
                keyring.delete_password(self.SERVICE_NAME, key)
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
        machine_id = f"{platform.node()}-{platform.system()}-{getpass.getuser()}"
        return machine_id[:32].ljust(32, '0')  # Ensure consistent length

    def _store_with_encryption(
            self,
            api_key: Optional[str] = None,
            email: Optional[str] = None,
            username: Optional[str] = None,
            password: Optional[str] = None,
            auth_method: str = "legacy"
    ) -> None:
        """Store credentials using file encryption."""
        try:
            # Use machine-specific password for encryption
            machine_password = self._get_machine_identifier()
            salt = os.urandom(16)
            key = self._derive_key(machine_password, salt)
            fernet = Fernet(key)

            # Prepare data to encrypt
            data = {
                "auth_method": auth_method,
                "api_key": api_key,
                "email": email,
                "username": username,
                "password": password
            }
            # Remove None values
            data = {k: v for k, v in data.items() if v is not None}

            # Encrypt data
            encrypted_data = fernet.encrypt(json.dumps(data).encode())

            # Store salt and encrypted data
            credentials_file = self._get_credentials_file()
            with open(credentials_file, 'wb') as f:
                f.write(salt + encrypted_data)

            # Set restrictive permissions (Unix-like systems)
            if platform.system() != "Windows":
                credentials_file.chmod(0o600)

        except Exception as e:
            raise AuthenticationError(f"Failed to store encrypted credentials: {e}") from e

    def _get_from_encrypted_file(self) -> dict:
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
            machine_password = self._get_machine_identifier()
            key = self._derive_key(machine_password, salt)
            fernet = Fernet(key)

            decrypted_data = fernet.decrypt(encrypted_data)
            data = json.loads(decrypted_data.decode())

            # Ensure auth_method is present
            if 'auth_method' not in data:
                # Legacy data format - assume legacy auth
                if 'api_key' in data and 'email' in data:
                    data['auth_method'] = 'legacy'

            return data

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
