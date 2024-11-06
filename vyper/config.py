from pathlib import Path
from pydantic_settings import BaseSettings


VYPER_SRC_ROOT = Path(__file__).parent


class Config(BaseSettings):
    _vyper_src_root: Path = VYPER_SRC_ROOT

    grammar_filename: str = "vyper.lark"
    grammar_path: Path = _vyper_src_root / grammar_filename
