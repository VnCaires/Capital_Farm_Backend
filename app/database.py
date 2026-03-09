from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///./freefarm.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def run_startup_migrations() -> None:
    """Lightweight SQLite-safe migrations for local development."""
    with engine.begin() as connection:
        inspector = inspect(connection)
        table_names = set(inspector.get_table_names())

        if "players" in table_names:
            player_columns = {col["name"] for col in inspector.get_columns("players")}
            if "email" not in player_columns:
                connection.execute(text("ALTER TABLE players ADD COLUMN email VARCHAR"))
            if "email_verified" not in player_columns:
                connection.execute(
                    text("ALTER TABLE players ADD COLUMN email_verified BOOLEAN NOT NULL DEFAULT 1")
                )
            connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_players_email ON players (email)"))
