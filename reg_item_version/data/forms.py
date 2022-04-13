from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, SubmitField, RadioField
from wtforms.validators import DataRequired


class NewPlayerForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Пароль ещё раз', validators=[DataRequired()])
    nickname = StringField('Игровой никнейм', validators=[DataRequired()])
    player_class = RadioField('Игровой класс', choices=[(1, 'Страж'), (2, 'Стрелок'), (3, 'Тень')])
    submit = SubmitField('Создать игрока!')

class NewItem(FlaskForm):
    classs = StringField('Класс', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Тип', validators=[DataRequired()])
    difens = StringField('Защита', validators=[DataRequired()])
    attac = StringField('Атака', validators=[DataRequired()])
    costs = StringField('Цена', validators=[DataRequired()])
    submit = SubmitField('Создать предмет!')




