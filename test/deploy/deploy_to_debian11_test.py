from unittest.case import skip

from test.deploy.deploy_test_case import DeployTestCase


class DeployToDebian11Test(DeployTestCase):

    @skip
    def test_debian11(self):
        host_ipv4 = self.create_or_get_server('debian11')
        self.upload_deb_and_run_tests(host_ipv4)

    @skip
    def test_delete_debian11(self):
        self.delete_server_if_present('debian11')

    def create_debian11(self):
        server_info = self.create_server(
            hostname='debian11',
            label='debian11',
            region=101,  # Amsterdam
            plan=1101,
            image=1122
        )
        #log.info(server_info)
