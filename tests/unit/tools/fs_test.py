from cypherpunkpay.tools.fs import dir_of


class FsTest:

    def test_dir_of(self):
        this_dir = dir_of(__file__)
        assert this_dir.is_dir()
        assert this_dir.name == 'tools'
