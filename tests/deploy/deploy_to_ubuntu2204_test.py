from unittest.case import skip

from tests.deploy.deploy_test_case import DeployTestCase


class DeployToUbuntu2204Test(DeployTestCase):

    @skip
    def test_ubuntu2204(self):
        host_ipv4 = self.create_or_get_server('ubuntu2204')
        self.upload_deb_and_run_tests(host_ipv4)

    @skip
    def test_delete_ubuntu2204(self):
        self.delete_server_if_present('ubuntu2204')

    def create_ubuntu2204(self):
        server_info = self.create_server(
            hostname='ubuntu2204',
            label='ubuntu2204',
            region=209,
            plan=2101,
            image=2117
        )
        #log.info(server_info)
