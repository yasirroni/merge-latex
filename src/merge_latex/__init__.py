"""Package for merging LaTeX files.

This package provides functionality to merge multiple LaTeX files into one
consolidated document, handling includes and macros properly.
"""
from .core import merge_tex_files, read_tex_files
from .version import __version__


__all__ = ['merge_tex_files', 'read_tex_files', '__version__']
