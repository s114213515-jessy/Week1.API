CREATE DATABASE fastapi_dev;
CREATE USER dev_user WITH PASSWORD 'dev_password';
GRANT ALL PRIVILEGES ON DATABASE fastapi_dev TO dev_user;

\connect fastapi_dev
GRANT USAGE, CREATE ON SCHEMA public TO dev_user;

CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

GRANT SELECT ON TABLE notes TO dev_user;
GRANT INSERT ON TABLE notes TO dev_user;
GRANT USAGE, SELECT ON SEQUENCE notes_id_seq TO dev_user;
