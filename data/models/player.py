import sqlalchemy
from flask_login import UserMixin
from ..db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash


class Player(SqlAlchemyBase, UserMixin):
    __tablename__ = 'players'

    id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, primary_key=True, autoincrement=True)
    email = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    password = sqlalchemy.Column(sqlalchemy.String)
    nickname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    inventory = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    equipped = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    money = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    location = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    player_class = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('player_classes.id'), nullable=False)
    hp = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    level = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
