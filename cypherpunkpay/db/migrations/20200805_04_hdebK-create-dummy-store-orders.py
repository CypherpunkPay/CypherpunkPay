"""
Create dummy_store_orders
"""

from yoyo import step

__depends__ = {}

steps = [
    step("""
      CREATE TABLE dummy_store_orders (
        uid text primary key not null,

        item_id integer not null,

        total integer not null,
        currency text not null,

        cc_total integer,
        cc_currency text
      )
    """)
]
