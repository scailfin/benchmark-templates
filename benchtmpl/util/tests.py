"""Base classes and methods that are used for unit tests."""


class FakeStream(object):
    """Fake stream object to test upload from stream. Needs to implement the
    save(filename) method.
    """
    def save(self, filename):
        """Write simple text to given file."""
        with open(filename, 'w') as f:
            f.write('This is a fake\n')
