"""The five built-in tools.

Each tool is a plain Python function with the @tool decorator. Strands
reads the signature + docstring and turns them into the JSON schema the
model sees. That schema IS the tool's UI for the model — write docstrings
for the model, not for humans.

Reading order: read_file -> write_file -> run_command -> search -> web_search
"""

from .file_read import read_file
from .file_write import write_file
from .shell import run_command
from .search import search
from .web import web_search

ALL_TOOLS = [read_file, write_file, run_command, search, web_search]
