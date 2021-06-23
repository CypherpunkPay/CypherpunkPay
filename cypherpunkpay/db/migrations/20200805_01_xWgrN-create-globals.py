"""
Create globals
"""

from yoyo import step

__depends__ = {}

steps = [
    step("""
      CREATE TABLE globals (
        id integer primary key,

        key text not null unique,
        value text,

        created_at timestamp not null,
        updated_at timestamp not null
      )
    """)
]
