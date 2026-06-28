import yaml
from utils.path_tools import get_abs_path

class ConfigHandler(object):
    @staticmethod
    def load_chroma_config(config_path: str=get_abs_path("config/chroma.yml"), encoding="utf-8"):
        with open(config_path, "r", encoding=encoding) as f:
            return yaml.load(f.read(), Loader=yaml.FullLoader)

    @staticmethod
    def load_prompts_config(config_path: str=get_abs_path("config/prompts.yml"), encoding="utf-8"):
        with open(config_path, "r", encoding=encoding) as f:
            return yaml.load(f.read(), Loader=yaml.FullLoader)


chroma_conf = ConfigHandler.load_chroma_config()
prompts_conf = ConfigHandler.load_prompts_config()