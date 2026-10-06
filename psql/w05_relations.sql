-- Run this against the existing fastapi_dev database as postgres.
-- This migration is safe to run more than once.

CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

ALTER TABLE notes
    ADD COLUMN IF NOT EXISTS category_id INTEGER;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'notes_category_id_fkey'
          AND conrelid = 'notes'::regclass
    ) THEN
        ALTER TABLE notes
            ADD CONSTRAINT notes_category_id_fkey
            FOREIGN KEY (category_id)
            REFERENCES categories (id)
            ON DELETE SET NULL;
    END IF;
END;
$$;

CREATE TABLE IF NOT EXISTS note_tags (
    note_id INTEGER NOT NULL REFERENCES notes (id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags (id) ON DELETE CASCADE,
    PRIMARY KEY (note_id, tag_id)
);

CREATE INDEX IF NOT EXISTS notes_category_id_idx ON notes (category_id);
CREATE INDEX IF NOT EXISTS note_tags_tag_id_idx ON note_tags (tag_id);

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE categories TO dev_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE tags TO dev_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE note_tags TO dev_user;
GRANT USAGE, SELECT ON SEQUENCE categories_id_seq TO dev_user;
GRANT USAGE, SELECT ON SEQUENCE tags_id_seq TO dev_user;
