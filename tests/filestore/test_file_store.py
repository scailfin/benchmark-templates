"""Test simple file store functionality."""

import datetime
import os
import pytest

from benchtmpl.io.files.store import Filestore
from benchtmpl.util.tests import FakeStream


DIR = os.path.dirname(os.path.realpath(__file__))
LOCAL_FILE = os.path.join(DIR, '../.files/schema.json')


class TestFilestore(object):
    def test_create_and_delete_file(self, tmpdir):
        """Test creating a new run resource for a template handle."""
        fs = Filestore(directory=str(tmpdir))
        # Create new entry from local file
        fh = fs.upload_file(LOCAL_FILE)
        assert os.path.isdir(os.path.join(str(tmpdir), fh.identifier))
        assert os.path.isfile(fh.filepath)
        assert fh.name == 'schema.json'
        assert fh.size == 1765
        assert isinstance(fh.created_at, datetime.date)
        # Get the file handle
        fh1 = fs.get_file(fh.identifier)
        assert fh.identifier == fh1.identifier
        assert fh.name == fh1.name
        # Delete the uploaded file
        result = fs.delete_file(fh.identifier)
        assert result
        assert not os.path.isdir(os.path.join(str(tmpdir), fh.identifier))
        assert not os.path.isfile(fh.filepath)
        assert fs.get_file(fh.identifier) is None
        # Deleting a non existing file returns False
        result = fs.delete_file(fh.identifier)
        assert not result

    def test_upload_get_and_list_files(self, tmpdir):
        """Test uploading and accessing files for a run."""
        fs = Filestore(directory=str(tmpdir))
        fh1 = fs.upload_file(LOCAL_FILE)
        fh2 = fs.upload_file(LOCAL_FILE)
        # Both files have the same name but different identifier (and point to
        # different paths)
        assert fh1.identifier != fh2.identifier
        assert fh1.filepath != fh2.filepath
        assert fh1.name == fh2.name
        # File listing contains two elements
        files = fs.list_files()
        assert len(files) == 2
        assert files[0].name == files[1].name
        assert files[0].identifier != files[1].identifier
        assert files[0].filepath != files[1].filepath
        # Recreate the file store and check that the two files still exist
        fs = Filestore(directory=str(tmpdir))
        files = fs.list_files()
        assert len(files) == 2
        assert files[0].name == files[1].name
        assert files[0].identifier != files[1].identifier
        assert files[0].filepath != files[1].filepath
        # Unpload unknown file will raise value error
        with pytest.raises(ValueError):
            fs.upload_file('tests/files/thisisnotafile.noway')
        # Upload third file from stream
        fh = fs.upload_stream(FakeStream(), 'file.txt')
        assert len(fs.list_files()) == 3
        assert fh.name == 'file.txt'
        # Delete file
        files = fs.list_files()
        assert fh.identifier in [f.identifier for f in files]
        fs.delete_file(fh.identifier)
        files = fs.list_files()
        assert len(files) == 2
        assert fh.identifier not in [f.identifier for f in files]
        # Recreate the file store and check that only the two files still exist
        fs = Filestore(directory=str(tmpdir))
        files = fs.list_files()
        assert len(files) == 2
        assert fh.identifier not in [f.identifier for f in files]
