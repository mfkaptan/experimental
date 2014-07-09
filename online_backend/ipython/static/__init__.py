import sys
from ._notebook import NotebookFinder

sys.meta_path.append(NotebookFinder())
