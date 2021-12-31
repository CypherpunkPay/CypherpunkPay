from yoyo import step

__depends__ = {}

steps = [
    step("""
      ALTER TABLE charges
      RENAME COLUMN payment_completed_url_called_at TO merchant_callback_url_called_at;
    """)
]
