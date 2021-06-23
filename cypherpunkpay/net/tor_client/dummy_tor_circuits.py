from cypherpunkpay.net.tor_client.base_tor_circuits import BaseTorCircuits


class DummyTorCircuits(BaseTorCircuits):

    def get_for(self, privacy_context):
        pass

    def mark_as_broken(self, label):
        pass

    def close(self):
        pass
