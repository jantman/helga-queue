import re
from helga_queue.version import VERSION


class TestPlugin:

    def test_version(self):
        m = re.match('^\d+\.\d+\.\d+$', VERSION)
        assert m is not None
