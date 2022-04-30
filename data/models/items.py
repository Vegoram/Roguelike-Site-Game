import sqlalchemy
from sqlalchemy import orm
from ..db_session import SqlAlchemyBase


class Items(SqlAlchemyBase):
    __tablename__ = 'items'

    id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    rarity = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    item_type_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('item_types.id'), nullable=False)
    protection = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    attack = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    class_required = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('player_classes.id'), nullable=False)
    cost = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

    item_type = orm.relation('ItemType')
