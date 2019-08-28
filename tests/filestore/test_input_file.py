"""Test input file handle."""


from benchtmpl.io.files.base import FileHandle, InputFile


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
