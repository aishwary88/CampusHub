import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load environment variables from backend/.env so DATABASE_URL is available
# whether alembic is run from the project root or CI.
# ---------------------------------------------------------------------------
_env_path = os.path.join(os.path.dirname(__file__), "..", "backend", ".env")
load_dotenv(dotenv_path=_env_path)

# ---------------------------------------------------------------------------
# Make sure the backend package is importable (alembic is run from project root)
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

# ---------------------------------------------------------------------------
# Alembic Config object — gives access to values in alembic.ini
# ---------------------------------------------------------------------------
config = context.config

# Inject DATABASE_URL into alembic config so %(DATABASE_URL)s in alembic.ini resolves
database_url = os.getenv("DATABASE_URL", "")
if not database_url:
    raise RuntimeError(
        "DATABASE_URL environment variable is not set. "
        "Check that backend/.env exists and contains DATABASE_URL."
    )
config.set_main_option("sqlalchemy.url", database_url)

# Interpret the config file for Python logging (if present)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Import Base and all models so Alembic can detect them for autogenerate
# ---------------------------------------------------------------------------
from app.database.database import Base  # noqa: E402

# Import all model modules to register their tables on Base.metadata
import app.models.user          # noqa: F401, E402
import app.models.club          # noqa: F401, E402
import app.models.event         # noqa: F401, E402
import app.models.post          # noqa: F401, E402
import app.models.notification  # noqa: F401, E402

target_metadata = Base.metadata

# ---------------------------------------------------------------------------
# Run migrations
# ---------------------------------------------------------------------------


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine.
    By skipping the Engine creation, we don't even need a DBAPI to be available.
    Calls to context.execute() here emit the given string to the script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate a connection
    with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
