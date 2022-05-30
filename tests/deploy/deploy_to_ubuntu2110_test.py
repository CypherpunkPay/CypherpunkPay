from unittest.case import skip

from tests.deploy.deploy_test_case import DeployTestCase


class DeployToUbuntu2110Test(DeployTestCase):

    @skip
    def test_ubuntu2110(self):
        host_ipv4 = self.create_or_get_server('ubuntu2110')
        self.upload_deb_and_run_tests(host_ipv4)

    @skip
    def test_delete_ubuntu2110(self):
        self.delete_server_if_present('ubuntu2110')

    def create_ubuntu2110(self):
        server_info = self.create_server(
            hostname='ubuntu2110',
            label='ubuntu2110',
            region=209,
            plan=2101,
            image=1125
        )
        #log.info(server_info)
