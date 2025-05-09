import os
import re

import setuptools


# dynamic versions
current_path = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(current_path, "src", "merge_latex", "version.py"), "rt") as f:
    version_line = f.read()

m = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_line, re.M)
__version__ = m.group(1)

# setuptools
setuptools.setup(
    version=__version__,
)
