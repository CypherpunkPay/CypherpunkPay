from cypherpunkpay.common import *
from cypherpunkpay.models.charge import Charge
from cypherpunkpay.models.user import User
from cypherpunkpay.models.dummy_store_order import DummyStoreOrder


class UidNotUnique(Exception):
    pass


class UsernameNotUnique(Exception):
    pass


class DB(ABC):

    def connect(self):
        self.__enter__()

    @abstractmethod
    def __enter__(self):
        ...

    def disconnect(self):
        self.__exit__()

    @abstractmethod
    def __exit__(self):
        ...

    @abstractmethod
    def migrate(self):
        ...

    @abstractmethod
    def insert(self, obj: [User, Charge, DummyStoreOrder]):
        ...

    @abstractmethod
    def save(self, obj: [User, Charge]):
        ...

    @abstractmethod
    def reload(self, obj: [User, Charge]) -> [User, Charge]:
        ...

    # -- Charges ------------------------------------------------------------------------------------------------------

    @abstractmethod
    def get_charges_count(self) -> int:
        ...

    @abstractmethod
    def get_charges(self) -> List[Charge]:
        ...

    @abstractmethod
    def get_charge_by_uid(self, uid) -> Charge:
        ...

    @abstractmethod
    def get_charges_by_status(self, expected_status) -> List[Charge]:
        ...

    @abstractmethod
    def get_recently_created_charges(self, delta: [datetime.timedelta, None] = None) -> List[Charge]:
        ...

    @abstractmethod
    def get_recently_activated_charges(self, delta: [datetime.timedelta, None] = None) -> List[Charge]:
        ...

    @abstractmethod
    def count_charges_where_wallet_fingerprint_is(self, wallet_fingerprint) -> int:
        ...

    @abstractmethod
    def get_last_charge(self) -> Charge:
        ...

    @abstractmethod
    def get_charges_for_merchant_notification(self, statuses: List):
        ...

    @abstractmethod
    def count_and_sum_charges_grouped_by_status(self, activated_after: datetime) -> Dict:
        ...

    # -- Users --------------------------------------------------------------------------------------------------------

    @abstractmethod
    def get_users_count(self) -> int:
        ...

    @abstractmethod
    def get_users(self) -> List[User]:
        ...

    @abstractmethod
    def get_user_by_username(self, username: str) -> User:
        ...

    @abstractmethod
    def delete_all_users(self) -> None:
        ...

    # -- Orders (Dummy Store) -----------------------------------------------------------------------------------------

    @abstractmethod
    def get_order_by_uid(self, merchant_order_id: str) -> DummyStoreOrder:
        ...

    @abstractmethod
    def get_orders(self) -> List[DummyStoreOrder]:
        ...

    # -- Utils --------------------------------------------------------------------------------------------------------

    @abstractmethod
    def get_blockchain_height(self, coin: str, cc_network: str) -> int:
        ...

    @abstractmethod
    def update_blockchain_height(self, coin: str, cc_network: str, height: int):
        ...

    @abstractmethod
    def get_admin_unique_path_segment(self) -> str:
        ...

    @abstractmethod
    def insert_admin_unique_path_segment(self, v) -> None:
        ...

    def raise_unknown_type(self, obj):
        raise Exception(f"Unknown type {type(obj)}")
