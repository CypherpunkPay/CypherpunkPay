from unittest.case import skip

from tests.deploy.deploy_test_case import DeployTestCase


class DeployToUbuntu2004Test(DeployTestCase):

    @skip
    def test_ubuntu2004(self):
        host_ipv4 = self.create_or_get_server('ubuntu2004')
        self.upload_deb_and_run_tests(host_ipv4)

    @skip
    def test_delete_ubuntu2004(self):
        self.delete_server_if_present('ubuntu2004')

    def create_ubuntu2004(self):
        server_info = self.create_server(
            hostname='ubuntu2004',
            label='ubuntu2004',
            region=209,
            plan=2101,
            image=1112
        )
        #log.info(server_info)
