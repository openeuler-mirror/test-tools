import os
from dotenv import dotenv_values
from pydantic import BaseModel, Field
from typing import Optional

CONFIG_FILE_PATH = ".env"
current_file_path = os.path.abspath(__file__)
current_dir_path = os.path.dirname(current_file_path)


class ConfigModel(BaseModel):
    # OpenAI API
    LLM_KEY: Optional[str] = Field(description="OpenAI API 密钥", default=None)
    LLM_URL: Optional[str] = Field(description="OpenAI API URL地址", default=None)
    LLM_MODEL: Optional[str] = Field(description="OpenAI API 模型名", default=None)


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