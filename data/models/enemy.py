import sqlalchemy
from sqlalchemy import orm
from ..db_session import SqlAlchemyBase


class Enemy(SqlAlchemyBase):
    __tablename__ = 'enemies'

    id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    location = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('locations.id'), nullable=False)
    min_level = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

    located = orm.relation('Location')
