"""
__init__.py - Package file for the ldraw Python package.

Copyright (C) 2008 David Boddie <david@boddie.org.uk>

This file is part of the ldraw Python package.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import sys
import imp

import os

from ldraw.config import get_config, write_config
from ldraw.library_gen import library_gen_main
from ldraw.dirs import get_data_dir, get_config_dir
from ldraw.download import download_main

data_dir = get_data_dir()


class CustomImporter(object):
    virtual_module = 'ldraw.library'
    def find_module(self, fullname, path=None):
        """This method is called by Python if this class
           is on sys.path. fullname is the fully-qualified
           name of the module to look for, and path is either
           __path__ (for submodules and subpackages) or None (for
           a top-level module/package).

           Note that this method will be called every time an import
           statement is detected (or __import__ is called), before
           Python's built-in package/module-finding code kicks in.
           Also note that if this method is called via pkgutil, it is possible
           that path will not be passed as an argument, hence the default value.
           Thanks to Damien Ayers for pointing this out!"""

        if fullname.startswith(self.virtual_module):
            # As per PEP #302 (which implemented the sys.meta_path protocol),
            # if fullname is the name of a module/package that we want to
            # report as found, then we need to return a loader object.
            # In this simple example, that will just be self.

            return self

        # If we don't provide the requested module, return None, as per
        # PEP #302.

        return None

    def load_module(self, fullname):
        """This method is called by Python if CustomImporter.find_module
           does not return None. fullname is the fully-qualified name
           of the module/package that was requested."""

        if not fullname.startswith(self.virtual_module):
            # Raise ImportError as per PEP #302 if the requested module/package
            # couldn't be loaded. This should never be reached in this
            # simple example, but it's included here for completeness. :)
            raise ImportError(fullname)

        # PEP#302 says to return the module if the loader object (i.e,
        # this class) successfully loaded the module.
        # Note that a regular class works just fine as a module.

        ldraw_path = os.path.abspath(os.path.dirname(__file__))
        config = get_config()
        parts_lst_path = config['parts.lst']

        def load_lib_from(library_dir):
            dot_split = fullname.split('.')
            dot_split.pop(0)
            lib_name = dot_split[-1]
            lib_dir = os.path.join(library_dir, *tuple(dot_split[:-1]))
            info = imp.find_module(lib_name, [lib_dir])
            library_module = imp.load_module(lib_name, *info)
            return library_module

        def load_lib():
            try:
                return load_lib_from(ldraw_path)
            except ImportError, e:
                return load_lib_from(data_dir)

        def write_lib():
            try:
                # try to write the library to ldraw package folder (can work if user-writeable)
                library_gen_main(parts_lst_path, ldraw_path)
            except Exception, e:
                # write it to data_dir
                library_gen_main(parts_lst_path, data_dir)

        # if the library already exists and correctly generated,
        # the __hash__ will prevent re-generation
        write_lib()
        return load_lib()


if not any(isinstance(o, CustomImporter) for o in sys.meta_path):
    # Add our import hook to sys.meta_path
    sys.meta_path.append(CustomImporter())
