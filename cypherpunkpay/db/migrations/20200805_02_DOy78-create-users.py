"""
Create users
"""

from yoyo import step

__depends__ = {}

steps = [
    step("""
      CREATE TABLE users (
        id integer primary key,
        username text unique,
        password_hash text,
        created_at timestamp,
        updated_at timestamp
      )
    """)
]
