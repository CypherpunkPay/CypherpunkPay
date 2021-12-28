from yoyo import step

__depends__ = {}

steps = [
    step("""
      ALTER TABLE charges
      ADD COLUMN cc_lightning_payment_request text
    """)
]
