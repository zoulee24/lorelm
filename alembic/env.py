import os
from logging.config import fileConfig

from dotenv import load_dotenv
from pgvector.sqlalchemy import Vector
from sqlalchemy import engine_from_config, pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from backend.models import DbBase
from backend.models.admin import User

target_metadata = DbBase.metadata
# target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def render_item(type_, obj, autogen_context):
    """让 Alembic 能渲染 pgvector 和 GIN 索引"""
    if type_ == "type" and isinstance(obj, Vector):  # pgvector
        autogen_context.imports.add("from pgvector.sqlalchemy import Vector")
        return f"Vector({obj.dim})"
    return False


def process_revision_directives(context, revision, directives):
    script = directives[0]
    if script.upgrade_ops.is_empty():
        return
    # 在upgrade操作后添加自定义SQL
    upgrade_ops = script.upgrade_ops.ops
    # 添加自定义SQL操作
    from alembic.operations import ops

    upgrade_ops.insert(0, ops.ExecuteSQLOp("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
    upgrade_ops.insert(0, ops.ExecuteSQLOp("CREATE EXTENSION IF NOT EXISTS vector;"))

    custom_sql = """
    CREATE OR REPLACE FUNCTION update_document_tsvector() 
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.content_ltks_tsvector := to_tsvector('simple', COALESCE(NEW.content_ltks, ''));
        NEW.content_sm_ltks_tsvector := to_tsvector('simple', COALESCE(NEW.content_sm_ltks, ''));
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    DROP TRIGGER IF EXISTS trigger_update_document_tsvector ON document;
    CREATE TRIGGER trigger_update_document_tsvector
        BEFORE INSERT OR UPDATE ON document
        FOR EACH ROW
        EXECUTE FUNCTION update_document_tsvector();
    """.strip()
    # # 将自定义SQL作为操作添加到upgrade操作列表中
    # upgrade_ops.append(ops.ExecuteSQLOp(custom_sql))

    # 添加创建默认用户的SQL
    create_user_sql = """
    INSERT INTO "user" (email, nickname, password, gender, avatar, disabled, language, is_admin, is_delete, created_at, updated_at)
    VALUES ('zoulee24@qq.com', 'loreuser', '123456', '男', '/lorelm/resource/default_avatar.webp', false, '简体中文', true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    ON CONFLICT DO NOTHING;
    """.strip()
    upgrade_ops.append(ops.ExecuteSQLOp(create_user_sql))


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    load_dotenv()

    db_name = os.getenv("POSTGRES_DB", "lorelm")
    user = os.getenv("POSTGRES_USER", "lorelm")
    password = os.getenv("POSTGRES_PASSWORD", "lorelm123")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", 5432)

    url = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db_name}"
    # url = config.get_main_option("sqlalchemy.url")
    print(url)

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

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    load_dotenv()

    db_name = os.getenv("POSTGRES_DB", "lorelm")
    user = os.getenv("POSTGRES_USER", "lorelm")
    password = os.getenv("POSTGRES_PASSWORD", "lorelm123")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", 5432)

    url = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db_name}"

    connectable = engine_from_config(
        {
            "sqlalchemy.url": url,
        },
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_item=render_item,
            process_revision_directives=process_revision_directives,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
