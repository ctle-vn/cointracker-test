from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base
from sqlalchemy_repr import RepresentableBase

# This is the naming convention used by Alembic to generate migration files.
# It's needed for reverts to work properly.
# See: https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/#using-custom-metadata-and-naming-conventions
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

Base = declarative_base(
    cls=RepresentableBase, metadata=MetaData(naming_convention=convention)
)
