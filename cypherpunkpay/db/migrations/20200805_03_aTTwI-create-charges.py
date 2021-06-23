"""
Create charges
"""

from yoyo import step

__depends__ = {}

steps = [
    step("""
      CREATE TABLE charges (
        uid text primary key not null,

        time_to_pay_ms integer not null,
        time_to_complete_ms integer not null,
        merchant_order_id text,

        total integer not null,
        currency text not null,

        cc_total integer,
        cc_currency text,
        cc_address text,
        cc_price integer,

        usd_total integer,

        pay_status text not null,
        status text not null,
        cc_received_total integer not null,
        confirmations integer not null default 0,

        activated_at timestamp,
        paid_at timestamp,
        completed_at timestamp,
        expired_at timestamp,
        cancelled_at timestamp,
        payment_completed_url_called_at timestamp,

        wallet_fingerprint text,
        address_derivation_index integer,

        status_fixed_manually boolean not null default false,

        block_explorer_1 text,
        block_explorer_2 text,
        subsequent_discrepancies integer not null default 0,

        created_at timestamp not null,
        updated_at timestamp not null
      )
    """)
]
