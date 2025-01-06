import os
from dotenv import dotenv_values

CONFIG_FILE_PATH = ".env"
current_file_path = os.path.abspath(__file__)
current_dir_path = os.path.dirname(current_file_path)


class Config:
    config: dict

    def __init__(self):
        config_file = os.path.join(current_dir_path, CONFIG_FILE_PATH)
        self.config = dotenv_values(config_file)

    def __getitem__(self, key):
        if key in self.config:
            return self.config[key]
        else:
            return None


config = Config()