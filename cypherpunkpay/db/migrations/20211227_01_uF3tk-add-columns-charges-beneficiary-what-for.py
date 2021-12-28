from yoyo import step

__depends__ = {}

steps = [
    step("""
      ALTER TABLE charges
      ADD COLUMN beneficiary text
    """),
    step("""
      ALTER TABLE charges
      ADD COLUMN what_for text
    """)
]
