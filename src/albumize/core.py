import base64
import mimetypes
import os
from itertools import chain
from pathlib import Path
from typing import List, NamedTuple, Sequence

from jinja2 import Environment, FileSystemLoader, select_autoescape

HERE: Path = Path(__file__).resolve().parent
TEMPLATES_DIR = HERE / "templates"


class Image(NamedTuple):
    path: Path
    src: Path = None

    @property
    def file_uri(self):
        return self.path.as_uri()

    @property
    def data_uri(self):
        data = encode_image(self.path)
        mime, _ = mimetypes.guess_type(self.path)
        return f"data:{mime};base64,{data}"

    @property
    def rel(self):
        if self.src is None:
            return str(self.path)
        return os.path.relpath(self.path, self.src)


loader = FileSystemLoader([str(TEMPLATES_DIR)])
env = Environment(loader=loader, autoescape=select_autoescape())


def find_images(src: Path, exts: Sequence[str], recursive: bool) -> List[Path]:
    globs = (f"*{ext}" for ext in exts)
    glob_func = src.rglob if recursive else src.glob
    return [Image(path, src) for path in chain.from_iterable(map(glob_func, globs))]


def encode_image(file: Path) -> str:
    data = base64.urlsafe_b64encode(file.read_bytes())
    return data.decode()
