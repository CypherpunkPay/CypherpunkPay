from unittest.case import skip

from test.deploy.deploy_test_case import DeployTestCase


class DeployToUbuntu2104Test(DeployTestCase):

    #@skip
    def test_ubuntu2104(self):
        host_ipv4 = self.create_or_get_server('ubuntu2104')
        self.upload_deb_and_run_tests(host_ipv4)

    @skip
    def test_delete_ubuntu2104(self):
        self.delete_server_if_present('ubuntu2104')

    def create_ubuntu2104(self):
        server_info = self.create_server(
            hostname='ubuntu2104',
            label='ubuntu2104',
            region=209,
            plan=2101,
            image=2114
        )
        #log.info(server_info)
