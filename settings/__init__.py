import importlib
import os

from scrapper.utils.exceptions import NotConfigurated

ENVIRONMENT_VARIABLE = "OVER_BOT_SETTINGS_MODULE"


class Settings:  # pylint: disable=too-few-public-methods

    _attrs_dict = {}

    def __init__(self):
        self._setup()

    def __getattr__(self, name):
        # this used to avoid pylint E1101 error when module is not loaded
        # so no instance attributes (from settings file) are available at
        # the moment of pylint check
        raise AttributeError(f'Option "{name}" is not set in settings file.')

    def _setup(self):
        settings_module = os.environ.get(ENVIRONMENT_VARIABLE)
        if not settings_module:
            raise NotConfigurated('Settings module name was not added (correctly) as environment variable')

        self._initialized = True

        settings_mod = importlib.import_module(f'.{settings_module}', '.settings')

        for setting in dir(settings_mod):
            if setting.isupper():
                setting_value = getattr(settings_mod, setting)
                setattr(self, setting, setting_value)


settings = Settings()
