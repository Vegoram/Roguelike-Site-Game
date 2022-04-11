from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, SubmitField, RadioField
from wtforms.validators import DataRequired


class NewPlayerForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    nickname = StringField('Игровой никнейм', validators=[DataRequired()])
    player_class = RadioField('Класс', choices=[(1, 'Страж'), (2, 'Стрелок'), (3, 'Тень')])
    submit = SubmitField('Создать игрока!')
