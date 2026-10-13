from app.config import Settings


def test_neon_database_url_uses_psycopg_driver() -> None:
    settings = Settings(
        _env_file=None,
        database_url=(
            "postgresql://user:password@example-pooler.neon.tech/neondb"
            "?sslmode=require&channel_binding=require"
        ),
    )

    assert settings.sqlalchemy_database_url == (
        "postgresql+psycopg://user:password@example-pooler.neon.tech/neondb"
        "?sslmode=require&channel_binding=require"
    )


def test_explicit_psycopg_database_url_is_unchanged() -> None:
    url = "postgresql+psycopg://user:password@localhost:5432/dyslexialearn"
    settings = Settings(_env_file=None, database_url=url)

    assert settings.sqlalchemy_database_url == url
