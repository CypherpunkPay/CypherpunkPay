from abc import abstractmethod


class BaseTorCircuits(object):

    SHARED_CIRCUIT_ID = 'shared_circuit'  # for requests were linkability of actions does not matter (merchant callbacks, price tickers, blockchain height, etc)
    SKIP_TOR = 'skip_tor'  # for requests where the target is in the local network or Tor cannot be used for other reasons

    @abstractmethod
    def mark_as_broken(self, label):
        pass

    @abstractmethod
    def get_for(self, privacy_context):
        pass

    @abstractmethod
    def close(self):
        pass
