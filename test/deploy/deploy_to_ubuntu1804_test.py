from unittest.case import skip

from test.deploy.deploy_test_case import DeployTestCase


class DeployToUbuntu1804Test(DeployTestCase):

    #@skip
    def test_ubuntu1804(self):
        host_ipv4 = self.create_or_get_server('ubuntu1804')
        self.upload_deb_and_run_tests(host_ipv4)

    @skip
    def test_delete_ubuntu1804(self):
        self.delete_server_if_present('ubuntu1804')

    def create_ubuntu1804(self):
        server_info = self.create_server(
            hostname='ubuntu1804',
            label='ubuntu1804',
            region=101,  # Amsterdam
            plan=1101,
            image=1109
        )
        #print(server_info)
