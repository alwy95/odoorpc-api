from pathlib import Path

from dotenv import dotenv_values

CORE_DIR = Path(__file__).parent
BASE_DIR = CORE_DIR.parent

DEFAULT_ENV_PATH = CORE_DIR / ".env.default"
USER_ENV_PATH = BASE_DIR / ".env"

default_config = dotenv_values(DEFAULT_ENV_PATH)
user_config = dotenv_values(USER_ENV_PATH)

merged_config = {**default_config, **user_config}


class Env:
    """
    Auto-casts .env variables to Python types (Bool/Int) with root-level overrides.
    """
    def __init__(self, adict):
        """Initializes by processing merged default and user configurations."""
        processed_dict = {k: self._convert(v) for k, v in adict.items()}
        self.__dict__.update(processed_dict)
    

    def _convert(self, value):
        """Performs type casting for Boolean and Integer strings."""
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
        
        if value.isdigit():
            return int(value)
        
        return value


    def __getattr__(self, name):
        """Safety fallback returning None for undefined variables."""
        return None


# Global instance for project-wide use
env = Env(merged_config)