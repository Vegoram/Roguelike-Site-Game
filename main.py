from flask import Flask, render_template, request, jsonify, make_response
from data import db_session, enemy_api
from werkzeug.utils import redirect
from werkzeug.exceptions import abort
from data.models.player import Player
from data.models.player_class import PlayerClass
from data.models.location import Location
from data.models.enemy import Enemy
from data.models.items import Items
from data.models.item_type import ItemType
from data.extra_functions import *
from data.forms import *
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import abort, Api
from random import choice

MESSAGES = {'low_access': 'У вас недостаточно прав для выполнения данного действия!',
            'sell_success': 'Вы успешно продали вещь!',
            'no_item': 'У вас в инвентаре нет этой вещи!',
            'no_class': 'У вас неподходящий класс для экипирования этой вещи!',
            'no_slot': 'Вы уже одели другую вещь этого типа!',
            'equip_success': 'Вы успешно экипировали вещь!',
            'un_equip_success': 'Вы успешно сняли вещь!'}

db_session.global_init('db/game_database.db')
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = '3yzwyB8X88GaxcWDLkmFXG05GC0brVLKCTJFtr1'
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/game_database.db")
    app.register_blueprint(enemy_api.blueprint)
    app.run()


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


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


@app.route('/message/<text>/<second_button>')
def message(text, second_button):
    try:
        t = MESSAGES[text]
    except Exception as e:
        t = 'Произошла ошибка!'
    return render_template('message_page.html', heading='Внимание!', button=second_button, message=t)


@app.route('/new_enemy', methods=['GET', 'POST'])
@login_required
def new_enemy():
    db_sess = db_session.create_session()
    if current_user not in db_sess.query(Player).filter(Player.id.in_([1, 2, 3])).fetchall():
        return redirect('/message/low_access/no')
    form = NewEnemyForm()
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
        return redirect('/new_enemy')
    return render_template('new_enemy_page.html', heading='Новый враг', form=form)


@app.route('/new_item', methods=['GET', 'POST'])
@login_required
def new_item():
    db_sess = db_session.create_session()
    if current_user not in db_sess.query(Player).filter(Player.id.in_([1, 2, 3])).fetchall():
        return redirect('/message/low_access')
    form = NewItemForm()
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
        return redirect('/new_item')
    return render_template('new_item_page.html', heading='Новый предмет', form=form)


@app.route('/items_table', methods=['GET', 'POST'])
def items_table():
    db_sess = db_session.create_session()
    flag = current_user in db_sess.query(Player).filter(Player.id.in_([1, 2, 3]))
    i = db_sess.query(Items).filter(Items.id > 0)
    items = []
    for thing in i:
        req_class = db_sess.query(PlayerClass).filter(PlayerClass.id == thing.class_required).first().name
        item_type = db_sess.query(ItemType).filter(ItemType.id == thing.item_type).first().name
        mini = [thing.name, thing.rarity, item_type, thing.protection, thing.attack, req_class, thing.cost]
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


@app.route('/edit_enemy/<int:enemy_id>', methods=['GET', 'POST'])
@login_required
def edit_enemy(enemy_id):
    db_sess = db_session.create_session()
    if current_user not in db_sess.query(Player).filter(Player.id.in_([0, 2, 3])):
        return redirect('/message/low_access')
    form = NewEnemyForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        enemy = db_sess.query(Enemy).filter(Enemy.id == enemy_id).first()
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
        monster = db_sess.query(Enemy).filter(Enemy.id == enemy_id).first()
        monster.name = form.name.data
        monster.location = form.location.data
        monster.min_level = int(form.min_level.data)
        db_sess.commit()
        return redirect('/enemy_table')
    return render_template('new_enemy_page.html', heading='Редактирование врага', form=form)


@app.route('/edit_item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    db_sess = db_session.create_session()
    if current_user not in db_sess.query(Player).filter(Player.id.in_([1, 2, 3])):
        return redirect('/message/low_access')
    form = NewItemForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        items = db_sess.query(Items).filter(Items.id == item_id).first()
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
        item = db_sess.query(Items).filter(Items.id == item_id).first()
        item.name = form.name.data
        item.rarity = form.rarity.data
        item.item_type = form.item_type.data
        item.protection = int(form.protection.data)
        item.attack = int(form.attack.data)
        item.class_required = form.class_required.data
        item.cost = int(form.cost.data)
        db_sess.commit()
        return redirect('/items_table')
    return render_template('new_item_page.html', heading='Редактирование предмета', form=form)


@app.route('/un_equip_item/<item_id>', methods=['GET', 'POST'])
@login_required
def un_equip_item(item_id):
    db_sess = db_session.create_session()
    try:
        check = item_id in current_user.equipped
    except TypeError:
        check = False
    if check:
        old_equipped = current_user.equipped.split(',')
        i = old_equipped.index(item_id)
        new_equipped = ','.join(old_equipped[:i] + old_equipped[i + 1:])
        if current_user.inventory:
            new_inventory = current_user.inventory + ',' + item_id
        else:
            new_inventory = item_id
        player = db_sess.query(Player).filter(Player.id == current_user.id).first()
        player.email = current_user.email
        player.name = current_user.name
        player.surname = current_user.surname
        player.nickname = current_user.nickname
        player.inventory = new_inventory
        player.equipped = new_equipped
        player.money = current_user.money
        player.location = current_user.location
        player.player_class = current_user.player_class
        player.hp = current_user.hp
        player.level = current_user.level
        db_sess.commit()
        text = 'un_equip_success'
    else:
        text = 'no_item'
    return redirect(f'/message/{text}/inventory')


@app.route('/equip_item/<item_id>', methods=['GET', 'POST'])
@login_required
def equip_item(item_id):
    db_sess = db_session.create_session()
    our_item = db_sess.query(Items).filter(Items.id == int(item_id)).first()
    try:
        check = item_id in current_user.inventory
    except TypeError:
        check = False
    if check:
        if our_item.class_required == current_user.player_class:
            if not current_user.equipped:
                flag = True
            elif our_item.item_type in range(1, 5):
                flag = True
                for i_id in current_user.equipped.split(','):
                    this_item = db_sess.query(Items).filter(Items.id == i_id).first()
                    if this_item.item_type == our_item.item_type:
                        flag = False
                        break
            else:
                flag = True
                for i_id in current_user.equipped.split(','):
                    this_item = db_sess.query(Items).filter(Items.id == i_id).first()
                    if this_item.item_type in range(5, 12):
                        flag = False
                        break
            if flag:
                old_inventory = current_user.inventory.split(',')
                i = old_inventory.index(item_id)
                new_inventory = ','.join(old_inventory[:i] + old_inventory[i + 1:])
                if current_user.equipped:
                    new_equipped = current_user.equipped + ',' + item_id
                else:
                    new_equipped = item_id
                player = db_sess.query(Player).filter(Player.id == current_user.id).first()
                player.email = current_user.email
                player.name = current_user.name
                player.surname = current_user.surname
                player.nickname = current_user.nickname
                player.inventory = new_inventory
                player.equipped = new_equipped
                player.money = current_user.money
                player.location = current_user.location
                player.player_class = current_user.player_class
                player.hp = current_user.hp
                player.level = current_user.level
                db_sess.commit()
                text = 'equip_success'
            else:
                text = 'no_slot'
        else:
            text = 'no_class'
    else:
        text = 'no_item'
    return redirect(f'/message/{text}/inventory')


@app.route('/sell_item/<item_id>', methods=['GET', 'POST'])
@login_required
def sell_item(item_id):
    db_sess = db_session.create_session()
    try:
        check = item_id in current_user.inventory
    except TypeError:
        check = False
    if check:
        old_inventory = current_user.inventory.split(',')
        i = old_inventory.index(item_id)
        new_inventory = ','.join(old_inventory[:i] + old_inventory[i + 1:])
        new_money = db_sess.query(Items).filter(Items.id == item_id).first().cost + current_user.money
        player = db_sess.query(Player).filter(Player.id == current_user.id).first()
        player.email = current_user.email
        player.name = current_user.name
        player.surname = current_user.surname
        player.nickname = current_user.nickname
        player.inventory = new_inventory
        player.equipped = current_user.equipped
        player.money = new_money
        player.location = current_user.location
        player.player_class = current_user.player_class
        player.hp = current_user.hp
        player.level = current_user.level
        db_sess.commit()
        text = 'sell_success'
    else:
        text = 'no_item'
    return redirect(f'/message/{text}/inventory')


@app.route('/inventory', methods=['GET', 'POST'])
@login_required
def inventory_page():
    db_sess = db_session.create_session()
    items = []
    items_2 = []
    money = current_user.money
    if current_user.inventory:
        for t in current_user.inventory.split(','):
            thing = db_sess.query(Items).filter(Items.id == t).first()
            req_class = db_sess.query(PlayerClass).filter(PlayerClass.id == thing.class_required).first().name
            item_type = db_sess.query(ItemType).filter(ItemType.id == thing.item_type).first().name
            mini = [thing.name, thing.rarity, item_type, thing.protection, thing.attack, req_class, thing.cost, t,
                    thing.class_required in range(1, 12)]
            items.append(mini)
    else:
        items = []
    if current_user.equipped:
        for t in current_user.equipped.split(','):
            thing = db_sess.query(Items).filter(Items.id == t).first()
            req_class = db_sess.query(PlayerClass).filter(PlayerClass.id == thing.class_required).first().name
            item_type = db_sess.query(ItemType).filter(ItemType.id == thing.item_type).first().name
            mini = [thing.name, thing.rarity, item_type, thing.protection, thing.attack, req_class, thing.cost, t]
            items_2.append(mini)
    else:
        items_2 = []
    return render_template('inventory_page.html', money=money, heading='Ваш инвентарь', bag=items, items_on=items_2)


@app.route('/adventure', methods=['GET', 'POST'])
@login_required
def adventure_page():
    db_sess = db_session.create_session()
    status = current_user.location.split('/')
    location = db_sess.query(Location).filter(Location.id == int(status[0]))
    occupation = status[1]
    loc_name = location.name
    loc_text = location.description
    if occupation == 'free':
        occ_text = 'Вы ничем не заняты. Вы можете заняться своей экипировкой или исследовать эту локацию.'
        form = ExploreButtonForm()
        if form.validate_on_submit():
            number = randint(1, 100)
            if number in range(1, 6):
                doing = f'{status[0]}/solving/{randint(1, 6)}'
            elif number in range(6, 11):
                doing = f'{status[0]}/buying'
            else:
                monster = choice(db_sess.query(Enemy).filter(Enemy.location == status[0],
                                                             Enemy.min_level >= current_user.level))
                enemy_level = current_user.level + randint(-1, 1)
                if enemy_level <= 0:
                    enemy_level = 1
                doing = f'{status[0]}/fighting/{monster.id}/{enemy_level}/{count_monster_hp(enemy_level)}'
            player = db_sess.query(Player).filter(Player.id == current_user.id).first()
            player.location = doing
            db_sess.commit()
        return render_template('adventure_page.html', heading='Приключение', form=form, occupation=occ_text,
                               location=loc_text, place=loc_name)
    elif occupation == 'fighting':
        occ_text = ''
    elif occupation == 'solving':
        occ_text = ''
    elif occupation == 'buying':
        occ_text = ''


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
