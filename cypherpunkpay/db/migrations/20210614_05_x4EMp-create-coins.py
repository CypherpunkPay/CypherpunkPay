"""
Create coins
"""

from yoyo import step

__depends__ = {}

steps = [
    step("""
      CREATE TABLE coins (
        cc_currency text not null,
        cc_network text not null,
        blockchain_height int not null default 0
      );
    """),
    step("""
      INSERT INTO coins(cc_currency, cc_network) VALUES ('btc', 'mainnet');
    """),
    step("""
      INSERT INTO coins(cc_currency, cc_network) VALUES ('btc', 'testnet');
    """),
    step("""
      INSERT INTO coins(cc_currency, cc_network) VALUES ('xmr', 'mainnet');
    """),
    step("""
      INSERT INTO coins(cc_currency, cc_network) VALUES ('xmr', 'stagenet');
    """),
]
