#!/usr/bin/env python
import os

from ldraw import download, generate
from ldraw.dirs import get_data_dir

# useful for autocompletion in some IDEs

output_dir = os.path.join(get_data_dir(), "ldraw")
parts_lst = os.path.join(output_dir, "parts.lst")
if not os.path.exists(output_dir):
    download(output_dir)
generate(parts_lst, "ldraw", force=True)
