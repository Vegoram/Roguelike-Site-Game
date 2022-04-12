import sqlalchemy
from ..db_session import SqlAlchemyBase


class ItemType(SqlAlchemyBase):
    __tablename__ = 'item_types'

    id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
