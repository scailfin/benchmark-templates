# This file is part of the Reproducible Open Benchmarks for Data Analysis
# Platform (ROB).
#
# Copyright (C) 2019 NYU.
#
# ROB is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.

"""Test input file handle."""


from robtmpl.core.io.files.base import FileHandle
from robtmpl.template.parameter.value import InputFile


class TestInputFile(object):
    def test_source_and_target_path(self):
        """Test source and target path methods for input file handle."""
        fh = FileHandle(filepath='/home/user/files/myfile.txt')
        # Input file handle without target path
        f = InputFile(f_handle=fh)
        assert f.source() == '/home/user/files/myfile.txt'
        assert f.target() == 'myfile.txt'
        # Input file handle with target path
        f = InputFile(f_handle=fh, target_path='data/names.txt')
        assert f.source() == '/home/user/files/myfile.txt'
        assert f.target() == 'data/names.txt'
