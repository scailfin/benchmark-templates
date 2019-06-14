"""Utility classes for I/O oprtations of the multi-process backend."""

import errno
import os
import shutil


class FileCopy(object):
    """File upload function that copies files to a local directory instead of
    uploading them to a remote server. This class is used as argument for the
    REANA upload function that prepares a workflow run.
    """
    def __init__(self, destination_dir):
        """Initialize the destination directory into which all files are copied.

        Parameters
        ----------
        destination_dir: string
            Path to local directory
        """
        self.destination_dir = destination_dir

    def __call__(self, source, target):
        """Copy the local source file to the relative target location in the
        destination directory.

        Parameters
        ----------
        source: string
            Path to file on disk
        target: string
            Relative target path for file in destination directory
        """
        dst = os.path.join(self.destination_dir, target)
        # If the source references a directory the whole directory tree is
        # copied
        if os.path.isdir(source):
            shutil.copytree(src=source, dst=dst)
        else:
            # Based on https://stackoverflow.com/questions/2793789/create-destination-path-for-shutil-copy-files/3284204
            try:
                shutil.copy(src=source, dst=dst)
            except IOError as e:
                # ENOENT(2): file does not exist, raised also on missing dest
                # parent dir
                if e.errno != errno.ENOENT or not os.path.isfile(source):
                    raise
                # try creating parent directories
                os.makedirs(os.path.dirname(dst))
                shutil.copy(src=source, dst=dst)
