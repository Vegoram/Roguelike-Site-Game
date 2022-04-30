import sqlalchemy
from ..db_session import SqlAlchemyBase


class PlayerClass(SqlAlchemyBase):
    __tablename__ = 'player_classes'

    id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
