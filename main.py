from os import abort

from flask import Flask, render_template, request
from data import db_session
from werkzeug.utils import redirect
from data.models.player import Player
from data.models.player_class import PlayerClass
from data.models.location import Location
from data.models.enemy import Enemy
from data.models.items import Items
from data.models.item_type import ItemType
from data.forms import *
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

db_session.global_init('db/game_database.db')
app = Flask(__name__)
app.config['SECRET_KEY'] = '3yzwyB8X88GaxcWDLkmFXG05GC0brVLKCTJFtr1'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(player_id):
    db_sess = db_session.create_session()
    return db_sess.query(Player).get(player_id)


@app.route('/')
def main_page():
    return render_template('basic_template.html', heading='Тени Аркполиса')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = NewPlayerForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('registration_page.html', heading='Регистрация',
                                   form=form,
                                   message='Пароли не совпадают')
        db_sess = db_session.create_session()
        if db_sess.query(Player).filter(Player.email == form.email.data).first():
            return render_template('registration_page.html', heading='Регистрация',
                                   form=form,
                                   message='Пользователь с такой почтой уже есть')
        if form.player_class.data == 1:
            health = 40
        else:
            health = 30
        player = Player(
            email=form.email.data,
            name=form.name.data,
            surname=form.surname.data,
            nickname=form.nickname.data,
            inventory=None,
            equipped=None,
            money=0,
            location='1/free',
            player_class=form.player_class.data,
            hp=health,
            level='0/100-1')
        player.set_password(form.password.data)
        db_sess.add(player)
        db_sess.commit()
        return redirect('/')
    return render_template('registration_page.html', heading='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(Player).filter(Player.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('autorisation_page.html',
                               message='Неправильная почта или пароль',
                               form=form)
    return render_template('autorisation_page.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/message/<text>')
def message(text):
    if text == 'low_access':
        t = 'У вас недостаточно прав для выполнения данного действия!'
        return render_template('message_page.html', title='Внимание!', message=t)
    else:
        t = 'Произошла ошибка!'
        return render_template('message_page.html', title='Внимание!', message=t)


@app.route('/items_table', methods=['GET', 'POST'])
def items_table():
    db_sess = db_session.create_session()
    flag = current_user in db_sess.query(Player).filter(Player.id.in_([1, 2, 3]))
    i = db_sess.query(Items)
    items = []
    for thing in i:
        req_class = db_sess.query(PlayerClass).filter(PlayerClass.id == thing.class_required).first().name
        item_type = db_sess.query(ItemType).filter(ItemType.id == thing.item_type).first().name
        mini = [thing.id, thing.name, thing.rarity, item_type, thing.protection, thing.attack, req_class, thing.cost]
        items.append(mini)
    return render_template('items_page.html', heading='Просмотр вещей', items=items, access=flag)


@app.route('/enemy_table', methods=['GET', 'POST'])
def enemy_table():
    db_sess = db_session.create_session()
    flag = current_user in db_sess.query(Player).filter(Player.id.in_([1, 2, 3]))
    i = db_sess.query(Enemy)
    enemies = []
    for antagonist in i:
        location = db_sess.query(Location).filter(Location.id == antagonist.location).first().name
        mini = [antagonist.id, antagonist.name, location, antagonist.min_level]
        enemies.append(mini)
    return render_template('enemy_page.html', heading='Просмотр врагов', enemies=enemies, access=flag)


@app.route('/enemy_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def enemy_delete(id):
    db_sess = db_session.create_session()
    enemy = db_sess.query(Enemy).filter(Enemy.id == id).first()
    if enemy:
        db_sess.delete(enemy)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/enemy_table')


@app.route('/items_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def items_delete(id):
    db_sess = db_session.create_session()
    items = db_sess.query(Items).filter(Items.id == id).first()
    if items:
        db_sess.delete(items)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/items_table')


@app.route('/new_enemy', methods=['GET', 'POST'])
@login_required
def add_enemy():
    form = NewEnemyForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        monster = Enemy(name=form.name.data,
                        location=form.location.data,
                        min_level=int(form.min_level.data))
        db_sess.add(monster)
        db_sess.commit()
        return redirect('/enemy_table')
    return render_template('new_enemy_page.html', title='Добавление врага',
                           form=form)


@app.route('/new_item', methods=['GET', 'POST'])
@login_required
def add_item():
    db_sess = db_session.create_session()
    form = NewItemForm()
    if form.validate_on_submit():
        item = Items(name=form.name.data,
                     rarity=form.rarity.data,
                     item_type=form.item_type.data,
                     protection=int(form.protection.data),
                     attack=int(form.attack.data),
                     class_required=form.class_required.data,
                     cost=int(form.cost.data))
        db_sess.add(item)
        db_sess.commit()
        return redirect('/items_table')
    return render_template('new_item_page.html', heading='Новый предмет', form=form)


@app.route('/new_enemy/<int:id>', methods=['GET', 'POST'])
@login_required
def new_enemy(id):
    db_sess = db_session.create_session()
    if current_user not in db_sess.query(Player).filter(Player.id.in_([0, 2, 3])).fetchall():
        return redirect('/message/low_access')
    form = NewEnemyForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        enemy = db_sess.query(Enemy).filter(Enemy.id == id).first()
        if enemy:
            form.name.data = enemy.name
            form.location.data = enemy.location
            form.min_level.data = int(enemy.min_level)
        else:
            abort(404)
    if form.validate_on_submit():
        if db_sess.query(Location).filter(Location.id == form.location.data).first().level > int(form.min_level.data):
            return render_template('new_enemy_page.html', heading='Новый враг',
                                   form=form,
                                   message='Уровень монстра слишком мал для этой локации')
        if db_sess.query(Enemy).filter(Enemy.name == form.name.data).first():
            return render_template('new_enemy_page.html', heading='Новый враг',
                                   form=form,
                                   message='Монстр с таким именем уже существует')
        monster = Enemy(name=form.name.data,
                        location=form.location.data,
                        min_level=int(form.min_level.data))
        db_sess.add(monster)
        db_sess.commit()
        return redirect('/enemy_table')
    return render_template('new_enemy_page.html', heading='Редактирование врага', form=form)


@app.route('/new_item/<int:id>', methods=['GET', 'POST'])
@login_required
def new_item(id):
    db_sess = db_session.create_session()
    if current_user not in db_sess.query(Player).filter(Player.id.in_([1, 2, 3])).fetchall():
        return redirect('/message/low_access')
    form = NewItemForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        items = db_sess.query(Items).filter(Items.id == id).first()
        if items:
            form.name.data = items.name
            form.rarity.data = items.rarity
            form.item_type.data = items.item_type
            form.protection.data = int(items.protection)
            form.attack.data = int(items.attack)
            form.class_required.data = items.class_required
            form.cost.data = int(items.cost)
        else:
            abort(404)
    if form.validate_on_submit():
        if form.item_type in range(1, 5) and not form.protection.data:
            return render_template('new_item_page.html', heading='Новый предмет',
                                   form=form,
                                   message='Предмет с типом "Доспех" должен иметь показатель защиты')
        if form.item_type in range(5, 12) and not form.attack.data:
            return render_template('new_item_page.html', heading='Новый предмет',
                                   form=form,
                                   message='Предмет с типом "Оружие" должен иметь показатель атаки')
        if db_sess.query(Items).filter(Items.name == form.name.data).first():
            return render_template('new_item_page.html', heading='Новый предмет',
                                   form=form,
                                   message='Предмет с таким названием уже существует')
        item = Items(name=form.name.data,
                     rarity=form.rarity.data,
                     item_type=form.item_type.data,
                     protection=int(form.protection.data),
                     attack=int(form.attack.data),
                     class_required=form.class_required.data,
                     cost=int(form.cost.data))
        db_sess.add(item)
        db_sess.commit()
        return redirect('/items_table')
    return render_template('new_item_page.html', heading='Новый предмет', form=form)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
