from unittest.case import skip

from tests.deploy.deploy_test_case import DeployTestCase


class DeployToDebian10Test(DeployTestCase):

    @skip
    def test_debian10(self):
        host_ipv4 = self.create_or_get_server('debian10')
        self.upload_deb_and_run_tests(host_ipv4)

    @skip
    def test_delete_debian10(self):
        self.delete_server_if_present('debian10')

    def create_debian10(self):
        server_info = self.create_server(
            hostname='debian10',
            label='debian10',
            region=101,
            plan=1101,
            image=1108
        )
        #log.info(server_info)
