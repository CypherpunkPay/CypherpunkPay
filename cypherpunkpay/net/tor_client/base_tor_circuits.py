from abc import abstractmethod


class BaseTorCircuits(object):

    SHARED_CIRCUIT_ID = 'shared_circuit'  # for requests were linkability of actions does not matter (price tickers, blockchain height checking etc)
    LOCAL_NETWORK = 'local_network'  # for requests where the target is in the local network or tor should not be used (merchant callback url)

    @abstractmethod
    def mark_as_broken(self, label):
        pass

    @abstractmethod
    def get_for(self, privacy_context):
        pass

    @abstractmethod
    def close(self):
        pass
