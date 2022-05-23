from multiprocessing import RLock
from typing import List
from monero.transaction import Transaction
import shelve


class MoneroAddressTransactionsDB:
    """File-persisted dictionary of address -> transactions"""

    def __init__(self, filepath: str):
        self.lock = RLock()
        self.filepath = filepath
        self.shelve = shelve.open(filepath, protocol=4)

    def get_transactions(self, address: str):
        with self.lock:
            return self.shelve.get(address, [])

    def add_transaction(self, address: str, tx: Transaction):
        if not isinstance(tx, Transaction):
            raise ValueError()
        with self.lock:
            txs: List[Transaction] = self.shelve.get(address, [])
            txs.append(tx)
            self.shelve[address] = txs

    def delete(self, address: str):
        with self.lock:
            if address in self.shelve:
                self.shelve.pop(address)

    def close(self):
        with self.lock:
            self.shelve.close()
