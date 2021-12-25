from typing import List

import os
import subprocess
import json
import time
import logging as log
from unittest.case import skip

import pysftp

from tempfile import NamedTemporaryFile
from unittest.case import TestCase


class DeployTestCase(TestCase):

    def setUp(self):
        cmd = 'cat ~/.bash_aliases | grep DEVELOPMENT_S99_API_TOKEN'
        self.api_token = subprocess.run(cmd, shell=True, capture_output=True).stdout.decode('utf-8').split('=')[1].strip()
        cmd = 'cat ~/.bash_aliases | grep DEVELOPMENT_S99_SSH_UUID'
        self.ssh_uuid = subprocess.run(cmd, shell=True, capture_output=True).stdout.decode('utf-8').split('=')[1].strip()
        self.private_key_path = '/home/user/.ssh/99stack_dev'
        self.deb_file = f'{os.path.dirname(os.path.realpath(__file__))}/../../dist/debian/cypherpunkpay_1.0.4_amd64.deb'
        self.test_deb_script = f'{os.path.dirname(os.path.realpath(__file__))}/resources/install_and_run_cypherpunkpay_deb.sh'

    def get_servers(self) -> List:
        log.info(f'Getting server list...')
        cmd = f'curl -X GET -H "Authorization: Bearer {self.api_token}" "https://api.99stack.com/v1/server/list"'
        response_body = subprocess.run(cmd, shell=True, capture_output=True).stdout.decode('utf-8')
        data = json.loads(response_body)
        #log.info(self.pretty(data))
        self.assert_no_error_message(data)
        return data['servers']

    def create_or_get_server(self, name):
        log.info("\n")
        had_no_network = False
        while True:
            servers = self.get_servers()
            server = next(filter(lambda server_data: server_data['name'] == name, servers), None)
            if server:
                if server['iface']:
                    ipv4 = 'NOT FOUND'
                    for address_info in server['iface']['v4']:
                        if address_info['type'] == 'public':
                            ipv4 = address_info['address']
                    log.info(f'Found {name} with IP4 {ipv4}')
                    if had_no_network:
                        log.info(f'Sleeping 10 seconds as this server was just assigned IPv4...')
                        time.sleep(10)
                    return ipv4
                else:
                    log.info(f'Found {name} but no network interface assigned yet (ongoing provisioning?)')
                    had_no_network = True
            else:
                if name == 'ubuntu2110':
                    self.create_ubuntu2110()
                if name == 'ubuntu2104':
                    self.create_ubuntu2104()
                if name == 'ubuntu2004':
                    self.create_ubuntu2004()
                if name == 'ubuntu1804':
                    self.create_ubuntu1804()
                if name == 'debian11':
                    self.create_debian11()
                if name == 'debian10':
                    self.create_debian10()
                if name == 'debian9':
                    self.create_debian9()

            log.info('Sleeping 1 second...')
            time.sleep(1)

    def create_server(self, hostname, label, region=209, plan=2101, image=2109):
        log.info(f'Creating server hostname={hostname}, image={image} ...')
        payload = '{' + f'''
          "hostname": "{hostname}",
          "label": "{label}",
          "region": {region},
          "image": {image},
          "plan": {plan},
          "ssh_key": "{self.ssh_uuid}",
          "auto_backups": false,
          "ipv6_networking": false,
          "ddos_protection": false,
          "private_networking": false,
          "script_url": ""''' + '}'
        cmd = f"curl --verbose -X POST -H 'Authorization: Bearer {self.api_token}' -H 'Content-Type: application/json' -d '{payload}' 'https://api.99stack.com/v1/server/create'"
        shell_result = subprocess.run(cmd, shell=True, capture_output=True)
        response_body = shell_result.stdout.decode('utf-8')
        data = json.loads(response_body)
        self.assert_no_error_message(data)
        return data

    def delete_server(self, server_id):
        log.info(f'Deleting server_id={server_id}...')
        payload = '{' + f'"server_id": {server_id}' + '}'
        cmd = f"curl -X DELETE -H 'Authorization: Bearer {self.api_token}' -H 'Content-Type: application/json' -d '{payload}' 'https://api.99stack.com/v1/server/remove'"
        response_body = subprocess.run(cmd, shell=True, capture_output=True).stdout.decode('utf-8')
        if response_body.strip():
            data = json.loads(response_body)
            log.error(data)
        else:
            pass  # empty body is OK

    def delete_server_if_present(self, name):
        servers_dict = self.get_servers()
        server = next(filter(lambda kv: kv[1]['name'] == name, servers_dict.items()), None)
        if server:
            server_id = server[0]
            self.delete_server(server_id)
        else:
            log.info(f"No {name} server found")

    def upload_deb_and_run_tests(self, host):
        # Run any command first so SSH adds server key temporary known_hosts before we try PySFTP,
        # which cannot be configured to fully skip host key checking
        self.run_cmd(host=host, remote_command='pwd')
        self.upload_file(local_file=self.deb_file, host=host)
        self.upload_file(local_file=self.test_deb_script, host=host)
        self.run_cmd(host=host, remote_command='chmod +x /root/install_and_run_cypherpunkpay_deb.sh')
        self.run_cmd(host=host, remote_command='/root/install_and_run_cypherpunkpay_deb.sh')

    def upload_file(self, local_file: str, host: str):
        log.info(f'Uploading {local_file} to {host}...')
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None  # Disable host key checking
        with pysftp.Connection(host=host, username='root', private_key=self.private_key_path, cnopts=cnopts) as sftp:
            sftp.cd('/root')
            sftp.put(local_file)

    def assertEmpty(self, expr, msg=None):
        self.assertFalse(expr, msg)

    def assertNotEmpty(self, expr, msg=None):
        self.assertTrue(expr, msg)

    def assertMatch(self, expected_regex, expr, msg=None):
        self.assertRegex(expr, expected_regex, msg)

    def gen_tmp_file_path(self, suffix = None):
        with NamedTemporaryFile(mode='w+b', prefix='cypherpunkpay-test-', suffix=suffix) as file:
            return file.name

    def assert_no_error_message(self, data):
        if isinstance(data, dict) and data.get('response_code') and data.get('response_code') >= 300:
            raise Exception(data)

    def pretty(self, obj):
        return json.dumps(obj, indent=4)

    def run_cmd(self, host, remote_command):
        local_command = f"ssh -o \"UserKnownHostsFile=/dev/null\" -o \"StrictHostKeyChecking=no\" root@{host} '{remote_command}'"
        log.info(f'root@{host}: {remote_command}')
        res = subprocess.run(local_command, shell=True, capture_output=True)
        out = res.stderr.decode('utf-8') + res.stdout.decode('utf-8')
        log.info(out)
        if res.returncode != 0:
            self.fail(f'Failed: {local_command}')
