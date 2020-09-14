import json
import os


class Configuration:
    USER_DOCUMENTS_FOLDER = f'{os.getenv("USERPROFILE")}\Documents'
    APP_CONFIG_FOLDER = f'{os.getenv("APPDATA")}\ImageEditor'
    APP_CONFIG_FILE = f'{APP_CONFIG_FOLDER}\config.json'
    DEFAULT_CONFIG = {
        'config_version': 36,
        'input_directory': f'{USER_DOCUMENTS_FOLDER}\ImageEditor\input',
        'output_directory': f'{USER_DOCUMENTS_FOLDER}\ImageEditor\output',
        'output_image_settings': {
            'width': 1000,
            'height': 1000,
            'quality': 75,
            'color_limits': {
                'red': 252,
                'green': 252,
                'blue': 252,
                'alpha': 10
            }
        },
        'input_formats': ['.jpg', '.jpeg', '.png', '.webp', '.jfif', '.gif', '.tiff'],
        'advanced_settings': {
            'crop': True,
            'square': True,
            'fit': True,
            'square_fill_color': {
                'red': 255,
                'green': 255,
                'blue': 255
            },
            'opaque_fill_color': {
                'red': 255,
                'green': 255,
                'blue': 255
            },
        },
        'worker_limit': 4,
        'verbose_errors': False
    }

    def __init__(self):
        self.config = self._load_or_create()
        self._check_or_create_path(self.config['input_directory'])
        self._check_or_create_path(self.config['output_directory'])

    def update(self, key, value):
        """
        Updating current config
        :param key: config Key.
        :param value: config Value.
        """
        if self.config.get(key):
            print(f'{key}: {value}')
            self.config[key] = value

    def save(self):
        """
        Saving current configuration to APP_CONFIG_FILE
        """
        with open(self.APP_CONFIG_FILE, 'w') as config_file:
            json.dump(self.config, config_file)

    def _load_or_create(self):
        """
        Loads config from file or create it if it does not exists
        """
        if not os.path.exists(self.APP_CONFIG_FOLDER):
            os.makedirs(self.APP_CONFIG_FOLDER)
        if not os.path.isfile(self.APP_CONFIG_FILE):
            with open(self.APP_CONFIG_FILE, 'w+') as config_file:
                json.dump(self.DEFAULT_CONFIG, config_file)
        with open(self.APP_CONFIG_FILE, 'r') as config_file:
            config = json.loads(config_file.read())
        if config['config_version'] < self.DEFAULT_CONFIG['config_version']:
            with open(self.APP_CONFIG_FILE, 'w+') as config_file:
                json.dump(self.DEFAULT_CONFIG, config_file)
            config = self.DEFAULT_CONFIG
        return config

    @staticmethod
    def _check_or_create_path(path):
        """
        Check if path does not exists and create create it
        :return: None
        """
        if not os.path.exists(path):
            os.makedirs(path)
