import json
import os
from pathlib import Path


class Config:
    __env_prefix = "OHM"

    def __init__(self, content_path: str = None, build_path: str = None, random_seed: int | None = None):
        if os.path.isfile("config/config.json"):
            with open("config/config.json") as file:
                self.config = json.load(file)
        else:
            self.config = {}

        self.p_data = Path(self.get_config_value("input", "content") if content_path is None else content_path)
        self.language = self._detect_language(self.p_data)

        self.p_data_toc = self.p_data / "toc"

        self.p_data_contents = self.p_data / "contents"
        self.p_data_questions = self.p_data_contents / "questions"
        self.p_data_html = self.p_data_contents / "html"
        self.p_data_photos = self.p_data_contents / "photos"
        self.p_data_pictures = self.p_data_contents / "drawings"
        self.p_data_sections = self.p_data_contents / "sections"
        self.p_data_slides = self.p_data_contents / "slides"
        self.p_data_snippets = self.p_data_contents / "snippets"
        self.p_data_static = self.p_data_contents / "static"
        self.p_data_solutions = self.p_data_contents / "solutions"

        self.p_data_fragenkatalog = self.p_data_questions / self.get_config_value("questions", "fragenkatalog3b.json")
        self.p_data_fragenkatalog_upstream = self.p_data_questions / self.get_config_value("questions_upstream")

        self.p_data_metadata = self.p_data_questions / "metadata3b.json"

        self.p_build = Path(self.get_config_value("output", "./build") if build_path is None else build_path)
        self.p_build_photos = self.p_build / "photos"
        self.p_build_pictures = self.p_build / "pictures"
        self.p_build_assets = self.p_build / "assets"

        self.p_assets = Path("./assets")
        self.p_templates = Path("./templates")
        self.p_generator_extra_content = self.p_data / "generator_extra_content"
        self.p_generator_extra_content_default = self.p_generator_extra_content / "de"
        self.p_generator_extra_content_language = self.p_generator_extra_content / self.language
        self.random_seed = self._parse_random_seed(random_seed if random_seed is not None else self.config.get("random_seed"))

    def get_config_value(self, key: str, default=None):
        if key in self.config:
            return self.config[key]
        elif f"{self.__env_prefix}_{key.upper()}" in os.environ.keys():
            return os.environ[f"{self.__env_prefix}_{key.upper()}"]
        elif default is not None:
            return default
        else:
            raise Exception(
                f"ERROR: Required value for '{key}' not found."
                f"Add to config.json or env as '${self.__env_prefix}_{key.upper()}'"
            )

    @staticmethod
    def _detect_language(content_path: Path) -> str:
        candidate = content_path.name.lower()
        if candidate in {"de", "fr", "it"}:
            return candidate
        return "de"

    @staticmethod
    def _parse_random_seed(value) -> int | None:
        if value in (None, ""):
            return None
        return int(value)
