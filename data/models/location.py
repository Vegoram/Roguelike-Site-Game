import sqlalchemy
from ..db_session import SqlAlchemyBase


class Location(SqlAlchemyBase):
    __tablename__ = 'locations'

    id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    level = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
