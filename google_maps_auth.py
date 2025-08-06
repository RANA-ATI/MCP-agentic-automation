# google_maps_auth.py

import os

class GoogleMapsAuthenticator:
    """
    Handles API key retrieval for Google Maps-based services.
    """
    def __init__(self, api_key_env_var: str = "GOOGLE_MAPS_API_KEY"):
        """
        Initializes the authenticator using environment variable.

        Args:
            api_key_env_var (str): Environment variable name where the API key is stored
        """
        self.api_key_env_var = api_key_env_var
        self.api_key = self._load_api_key()

    def _load_api_key(self) -> str:
        """
        Load the API key from environment variable.

        Returns:
            str: Google Maps API Key

        Raises:
            EnvironmentError: If API key is not found
        """
        api_key = os.getenv(self.api_key_env_var)
        if not api_key:
            raise EnvironmentError(f"API key not found in environment variable: {self.api_key_env_var}")
        return api_key

    def get_api_key(self) -> str:
        """
        Return the API key.

        Returns:
            str: Google Maps API Key
        """
        return self.api_key
