import sqlalchemy
from .db_session import SqlAlchemyBase


class Items(SqlAlchemyBase):
    __tablename__ = 'items'

    id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    item_type = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('item_types.id'), nullable=False)
    protection = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    attack = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    class_required = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('classes.id'), nullable=False)
    cost = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
