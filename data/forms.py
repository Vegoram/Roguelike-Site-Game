from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, SubmitField, RadioField, IntegerField, BooleanField
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


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class NewItemForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    rarity = RadioField('Качество', choices=[('Мусорное', 'Мусорное'), ('Обычное', 'Обычное'),
                                             ('Качественное', 'Качественное'),
                                             ('Высокотехнологичное', 'Высокотехнологичное'),
                                             ('Шедевральное', 'Шедевральное'), ('Легендарное', 'Легендарное')])
    item_type = RadioField('Тип', choices=[(1, 'Доспех-Шлем'), (2, 'Доспех-Нагрудник'),
                                           (3, 'Доспех-Поножи'), (4, 'Доспех-Сапоги'),
                                           (5, 'Оружие-Колющее'), (6, 'Оружие-Режущее'),
                                           (7, 'Оружие-Дробящее'), (8, 'Оружие-Огнестрельное'),
                                           (9, 'Оружие-Лазерное'), (10, 'Оружие-Плазменное'),
                                           (11, 'Оружие-Уникальное'), (12, 'Другое-Предмет для события'),
                                           (13, 'Другое-На продажу')],
                           validators=[DataRequired()])
    protection = IntegerField('Защита (поставьте 0 если нет)')
    attack = IntegerField('Атака (поставьте 0 если нет)')
    class_required = RadioField('Необходимый класс', choices=[(1, 'Страж'), (2, 'Стрелок'), (3, 'Тень')])
    cost = IntegerField('Цена', validators=[DataRequired()])
    submit = SubmitField('Создать предмет!')


class NewEnemyForm(FlaskForm):
    name = StringField('Название врага', validators=[DataRequired()])
    location = RadioField('Локация, где враг может встретиться',
                          choices=[(2, 'Катакомбы Аркполиса'), (3, 'Канализационные стоки Аркполиса'),
                                   (4, 'Подземные убежища Аркполиса'), (5, 'Погребенный храм Девяти Теней'),
                                   (6, 'Развалины НИО'), (7, 'Складские помещения НИО'),
                                   (8, 'Отдел тестирования боевого снаряжения'), (9, 'Орудийные цехи НИО'),
                                   (10, 'Свалка Аркполиса'), (11, 'Куча металлолома'),
                                   (12, 'Мусорная пещера'), (13, 'Радиоактивное болото')], validators=[DataRequired()])
    min_level = IntegerField('Минимальный уровень монстра', validators=[DataRequired()])
    submit = SubmitField('Добавить врага')


class AttackForm(FlaskForm):
    attack_type = RadioField('Каким ударом вы хотите атаковать?',
                             choices=[(1, 'Базовая атака'), (2, 'Специальная атака')], validators=[DataRequired()])
    submit = SubmitField('Атакаовать!')
