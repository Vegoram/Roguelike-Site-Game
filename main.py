from os import listdir
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
from data.formulas import *
from data.forms import *
from flask_restful import abort, Api
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from random import choice


# Создаю словарь с расшифровкой кодов сообщений
MESSAGES = {'register_success': 'Вы успешно зарегистрировались! Теперь выполните вход.',
            'low_access': 'У вас недостаточно прав для выполнения данного действия!',
            'enemy_success': 'Вы успешно добавили врага!',
            'item_success': 'Вы успешно добавили предмет!',
            'sell_success': 'Вы успешно продали вещь!',
            'no_item': 'У вас в инвентаре нет этой вещи!',
            'no_class': 'У вас неподходящий класс для экипирования этой вещи!',
            'no_slot': 'Вы уже одели другую вещь этого типа!',
            'equip_success': 'Вы успешно экипировали вещь!',
            'un_equip_success': 'Вы успешно сняли вещь!',
            'del_enemy_success': 'Вы успешно удалили врага!',
            'del_enemy_fail': 'Нельзя удалить несуществующего врага!',
            'del_item_success': 'Вы успешно удалили вещь!',
            'del_item_fail': 'Нельзя удалить несуществующую вещь!',
            'level_too_small': 'У вас слишком маленький уровень!',
            'busy': 'Вы должны быть свободны для выполнения этого действия',
            'wrong_location': 'Вы не можете выполнять это действие в текущей локации'}
# Словарь с расшифровкой кодов сообщений завершения событий
ADDITIONAL_TEXTS = {'solve_success': 'Вы успешно решили головоломку! Предмет добавлен в инвентарь.',
                    'solve_fail': 'К сожалению, это неверное решение...',
                    'fight_success': 'Вы одержали победу в схватке!',
                    'fight_fail': 'К сожалению, вы потерпели поражение...',
                    'buy_success': 'Вы успешно приобрели предмет!',
                    'buy_fail': 'Вы ушли, ничего не купив'}
# Шансы выпадения вещи в зависимости от ключа - уровня локации
ITEM_DROP_CHANCES = {1: (0, 0, 0, 5, 30, 100),
                     10: (0, 0, 5, 30, 70, 100),
                     20: (0, 1, 15, 50, 90, 100),
                     40: (2, 5, 30, 70, 100, 100)}

db_session.global_init('db/game_database.db')
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = '3yzwyB8X88GaxcWDLkmFXG05GC0brVLKCTJFtr1'
login_manager = LoginManager()
login_manager.init_app(app)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@login_manager.user_loader
def load_user(player_id):
    db_sess = db_session.create_session()
    return db_sess.query(Player).get(player_id)


@app.route('/')  # Пустая главная страница
def main_page():
    db_sess = db_session.create_session()
    access = current_user.is_authenticated and current_user in db_sess.query(Player).filter(Player.id.in_([1, 2, 3]))
    # access - является ли пользователь админом
    return render_template('home_page.html', heading='Тени Аркполиса', access=access)


@app.route('/register', methods=['GET', 'POST'])  # Регистрация нового пользователя
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
        if form.player_class.data == 1:  # Классу "Страж" изначально выдаются доп. жизни
            health = '40'
        else:
            health = '30'
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
        return redirect('/message/register_success/no')
    return render_template('registration_page.html', heading='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])  # Авторизация
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


@app.route('/logout')  # Выход из учетной записи
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/profile')  # Страница с профилем игрока
@login_required
def profile():
    db_sess = db_session.create_session()
    name = current_user.surname + ' ' + current_user.name
    nickname = current_user.nickname
    exp, level = tuple(current_user.level.split('-'))
    health = current_user.hp
    player_class = db_sess.query(PlayerClass).filter(PlayerClass.id == current_user.player_class).first().name
    return render_template('profile_page.html', heading='Профиль', name=name, nickname=nickname,
                           level=level, exp=exp, health=health, player_class=player_class)


@app.route('/guide')  # Справочник, который автоматически составляется из текстовых файлов в нужном каталоге
@login_required
def guide():
    page_names = filter(lambda x: x.endswith('.txt'), listdir('./data/guide_pages'))
    pages = []
    for page_name in page_names:
        with open(f'./data/guide_pages/{page_name}') as file:
            data = list(map(lambda x: x.strip(), file.readlines()))
        heading = data[0]
        text = ' '.join(data[1:])
        pages.append([heading, text])
    return render_template('guide_page.html', heading='Справочник', pages=pages)


@app.route('/message/<text>/<second_button>')  # Страница с сообщением о чем-то
# Параметр second_button определяет, есть ли вторая кнопка, и если да, то указывает куда эта кнопка ведет
def message(text, second_button):
    try:
        t = MESSAGES[text]
    except KeyError:
        t = 'Произошла ошибка!'
    return render_template('message_page.html', heading='Внимание!', button=second_button, message=t)


@app.route('/new_enemy', methods=['GET', 'POST'])  # Форма для добавления врага
@login_required
def new_enemy():
    db_sess = db_session.create_session()
    # Проверка, является ли пользователь админом
    if current_user not in db_sess.query(Player).filter(Player.id.in_([1, 2, 3])):
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
        location = db_sess.query(Location).filter(Location.id == form.location.data).first()
        monster = Enemy(name=form.name.data,
                        min_level=int(form.min_level.data))
        location.enemies.append(monster)
        db_sess.commit()
        return redirect('/message/enemy_success/new_enemy')
    return render_template('new_enemy_page.html', heading='Новый враг', form=form)


@app.route('/new_item', methods=['GET', 'POST'])  # Форма для добавления нового предмета
@login_required
def new_item():
    db_sess = db_session.create_session()
    # Проверка, является ли пользователь админом
    if current_user not in db_sess.query(Player).filter(Player.id.in_([1, 2, 3])):
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
        i_type = db_sess.query(ItemType).filter(ItemType.id == form.item_type.data).first()
        item = Items(name=form.name.data,
                     rarity=form.rarity.data,
                     protection=int(form.protection.data),
                     attack=int(form.attack.data),
                     class_required=form.class_required.data,
                     cost=int(form.cost.data))
        i_type.items.append(item)
        db_sess.commit()
        return redirect('/message/item_success/new_item')
    return render_template('new_item_page.html', heading='Новый предмет', form=form)


@app.route('/items_table', methods=['GET', 'POST'])  # Таблица, показывающая все предметы в игре
@login_required
def items_table():
    db_sess = db_session.create_session()
    # Проверка, является ли пользователь админом
    if current_user not in db_sess.query(Player).filter(Player.id.in_([1, 2, 3])):
        return redirect('/message/low_access')
    i = db_sess.query(Items).filter(Items.id > 0)
    items = []
    for thing in i:  # Составляем список списков со всей нужной информацией по каждому предмету
        req_class = db_sess.query(PlayerClass).filter(PlayerClass.id == thing.class_required).first().name
        mini = [thing.id, thing.name, thing.rarity, thing.item_type.name,
                thing.protection, thing.attack, req_class, thing.cost]
        items.append(mini)
    return render_template('items_page.html', heading='Просмотр вещей', items=items)


@app.route('/enemy_table', methods=['GET', 'POST'])  # Таблица, показывающая всех врагов в игре
@login_required
def enemy_table():
    db_sess = db_session.create_session()
    # Проверка, является ли пользователь админом
    if current_user not in db_sess.query(Player).filter(Player.id.in_([1, 2, 3])):
        return redirect('/message/low_access')
    i = db_sess.query(Enemy)
    enemies = []
    for antagonist in i:  # Составляем список списков со всей нужной информацией по каждому врагу
        mini = [antagonist.id, antagonist.name, antagonist.located.name, antagonist.min_level]
        enemies.append(mini)
    return render_template('enemy_page.html', heading='Просмотр врагов', enemies=enemies)


@app.route('/edit_enemy/<int:enemy_id>', methods=['GET', 'POST'])  # Форма редактирования врага по id
@login_required
def edit_enemy(enemy_id):
    db_sess = db_session.create_session()
    # Проверка, является ли пользователь админом
    if current_user not in db_sess.query(Player).filter(Player.id.in_([0, 2, 3])):
        return redirect('/message/low_access')
    form = NewEnemyForm()
    # Заполнение полей формы
    if request.method == 'GET':
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
        monster = db_sess.query(Enemy).filter(Enemy.id == enemy_id).first()
        monster.name = form.name.data
        monster.location = form.location.data
        monster.min_level = int(form.min_level.data)
        db_sess.commit()
        return redirect('/enemy_table')
    return render_template('new_enemy_page.html', heading='Редактирование врага', form=form)


@app.route('/edit_item/<int:item_id>', methods=['GET', 'POST'])  # Форма редактирования предмета по id
@login_required
def edit_item(item_id):
    db_sess = db_session.create_session()
    # Проверка, является ли пользователь админом
    if current_user not in db_sess.query(Player).filter(Player.id.in_([1, 2, 3])):
        return redirect('/message/low_access')
    form = NewItemForm()
    # Заполнение полей формы
    if request.method == 'GET':
        db_sess = db_session.create_session()
        items = db_sess.query(Items).filter(Items.id == item_id).first()
        if items:
            form.name.data = items.name
            form.rarity.data = items.rarity
            form.item_type.data = items.item_type_id
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
        item = db_sess.query(Items).filter(Items.id == item_id).first()
        item.name = form.name.data
        item.rarity = form.rarity.data
        item.item_type_id = form.item_type.data
        item.protection = int(form.protection.data)
        item.attack = int(form.attack.data)
        item.class_required = form.class_required.data
        item.cost = int(form.cost.data)
        db_sess.commit()
        return redirect('/items_table')
    return render_template('new_item_page.html', heading='Редактирование предмета', form=form)


@app.route('/delete_enemy/<int:enemy_id>', methods=['GET', 'POST'])  # Удаление врага по id
@login_required
def delete_enemy(enemy_id):
    db_sess = db_session.create_session()
    # Проверка, является ли пользователь админом
    if current_user not in db_sess.query(Player).filter(Player.id.in_([1, 2, 3])):
        return redirect('/message/low_access')
    enemy = db_sess.query(Enemy).filter(Enemy.id == enemy_id).first()
    if enemy:
        db_sess.delete(enemy)
        db_sess.commit()
        return redirect('/message/del_enemy_success/enemy_table')
    else:
        return redirect('/message/del_enemy_fail/enemy_table')


@app.route('/delete_item/<int:item_id>', methods=['GET', 'POST'])  # Удаление предмета по id
@login_required
def delete_item(item_id):
    db_sess = db_session.create_session()
    # Проверка, является ли пользователь админом
    if current_user not in db_sess.query(Player).filter(Player.id.in_([1, 2, 3])):
        return redirect('/message/low_access')
    item = db_sess.query(Items).filter(Items.id == item_id).first()
    if item:
        db_sess.delete(item)
        db_sess.commit()
        return redirect('/message/del_item_success/items_table')
    else:
        return redirect('/message/del_item_fail/items_table')


# Функция для снятия предмета с игрока и перемещения его в инвентарь
@app.route('/un_equip_item/<item_id>', methods=['GET', 'POST'])
@login_required
def un_equip_item(item_id):
    status = current_user.location.split('/')
    if status[1] != 'free':  # Проверка на то, свободен ли пользователь
        return redirect('/message/busy/adventure')
    db_sess = db_session.create_session()
    try:  # Проверка на то, надета ли эта вещь на него
        check = item_id in current_user.equipped
    except TypeError:  # Исключение ошибки если у пользователя ничего не надето
        check = False
    if check:
        old_equipped = current_user.equipped.split(',')
        i = old_equipped.index(item_id)
        new_equipped = ','.join(old_equipped[:i] + old_equipped[i + 1:])
        if current_user.inventory:  # Если инвентарь пустой, то добавляем с запятой, если нет то просто
            new_inventory = current_user.inventory + ',' + item_id
        else:
            new_inventory = item_id
        player = db_sess.query(Player).filter(Player.id == current_user.id).first()
        player.inventory = new_inventory
        player.equipped = new_equipped
        db_sess.commit()
        text = 'un_equip_success'
    else:
        text = 'no_item'
    return redirect(f'/message/{text}/inventory')


# Функция для экипирования какого-либо предмета из инвентаря
@app.route('/equip_item/<item_id>', methods=['GET', 'POST'])
@login_required
def equip_item(item_id):
    status = current_user.location.split('/')
    if status[1] != 'free':  # Проверка на то, свободен ли пользователь
        return redirect('/message/busy/adventure')
    db_sess = db_session.create_session()
    item_to_equip = db_sess.query(Items).filter(Items.id == int(item_id)).first()
    try:  # Проверка на то, есть ли эта вещь у него
        check = item_id in current_user.inventory
    except TypeError:  # Исключение ошибки если у пользователя ничего нет
        check = False
    if check:
        if item_to_equip.class_required == current_user.player_class:
            # Дальше идут переборы инвентаря чтобы проверить, не надета ли ещё одна вещь такого типа
            # Например, нельзя надеть два шлема или две пары сапог
            if not current_user.equipped:
                flag = True
            elif item_to_equip.item_type_id in range(1, 5):
                flag = True
                for i_id in current_user.equipped.split(','):
                    checking_item = db_sess.query(Items).filter(Items.id == i_id).first()
                    if checking_item.item_type_id == item_to_equip.item_type_id:
                        flag = False
                        break
            else:
                flag = True
                for i_id in current_user.equipped.split(','):
                    checking_item = db_sess.query(Items).filter(Items.id == i_id).first()
                    if checking_item.item_type_id in range(5, 12):
                        flag = False
                        break
            if flag:  # Если все корректно, то надеваем вещь
                old_inventory = current_user.inventory.split(',')
                i = old_inventory.index(item_id)
                new_inventory = ','.join(old_inventory[:i] + old_inventory[i + 1:])
                if current_user.equipped:
                    new_equipped = current_user.equipped + ',' + item_id
                else:
                    new_equipped = item_id
                player = db_sess.query(Player).filter(Player.id == current_user.id).first()
                player.inventory = new_inventory
                player.equipped = new_equipped
                db_sess.commit()
                text = 'equip_success'
            else:
                text = 'no_slot'
        else:
            text = 'no_class'
    else:
        text = 'no_item'
    return redirect(f'/message/{text}/inventory')


# Функция для продажи предмета из инвентаря
@app.route('/sell_item/<item_id>', methods=['GET', 'POST'])
@login_required
def sell_item(item_id):
    status = current_user.location.split('/')
    if status[1] != 'free':  # Проверка на то, свободен ли пользователь
        return redirect('/message/busy/adventure')
    db_sess = db_session.create_session()
    try:  # Проверка на то, есть ли эта вещь у него
        check = item_id in current_user.inventory
    except TypeError:  # Исключение ошибки если у пользователя ничего нет
        check = False
    if check:
        old_inventory = current_user.inventory.split(',')
        i = old_inventory.index(item_id)
        new_inventory = ','.join(old_inventory[:i] + old_inventory[i + 1:])
        new_money = db_sess.query(Items).filter(Items.id == item_id).first().cost + current_user.money
        player = db_sess.query(Player).filter(Player.id == current_user.id).first()
        player.inventory = new_inventory
        player.money = new_money
        db_sess.commit()
        text = 'sell_success'
    else:
        text = 'no_item'
    return redirect(f'/message/{text}/inventory')


# Страница с инвентарем пользователя
@app.route('/inventory', methods=['GET', 'POST'])
@login_required
def inventory_page():
    db_sess = db_session.create_session()
    items = []
    items_2 = []
    money = current_user.money
    if current_user.inventory:  # Перебор имеющихся предметов
        for t in current_user.inventory.split(','):
            thing = db_sess.query(Items).filter(Items.id == t).first()
            req_class = db_sess.query(PlayerClass).filter(PlayerClass.id == thing.class_required).first().name
            item_type = db_sess.query(ItemType).filter(ItemType.id == thing.item_type_id).first().name
            mini = [thing.name, thing.rarity, item_type, thing.protection, thing.attack, req_class, thing.cost, t,
                    thing.class_required in range(1, 12)]
            items.append(mini)
    else:
        items = []
    if current_user.equipped:  # Перебор надетых предметов
        for t in current_user.equipped.split(','):
            thing = db_sess.query(Items).filter(Items.id == t).first()
            req_class = db_sess.query(PlayerClass).filter(PlayerClass.id == thing.class_required).first().name
            item_type = db_sess.query(ItemType).filter(ItemType.id == thing.item_type_id).first().name
            mini = [thing.name, thing.rarity, item_type, thing.protection, thing.attack, req_class, thing.cost, t]
            items_2.append(mini)
    else:
        items_2 = []
    return render_template('inventory_page.html', money=money, heading='Ваш инвентарь', bag=items, items_on=items_2)


# Функция, обрабатывающая ход пользователя во время битвы
@app.route('/turn', methods=['GET', 'POST'])
@login_required
def turn():
    db_sess = db_session.create_session()
    info = current_user.location.split('/')
    if info[1] == 'fighting':  # Проверка на то, идет ли бой
        user_weapon_attack = 0
        try:  # Проверка на то, есть ли у пользователя надетые вещи
            equipment = current_user.equipped.split(',')
        except Exception:  # Исключение если их у него нет
            equipment = []
        for item_id in equipment:  # Перебор всех вещей, надетых на пользователя, и суммирование их атаки
            item = db_sess.query(Items).filter(Items.id == item_id).first()
            user_weapon_attack += item.attack
        # Проверка на промах. Если пользователь - Тень, то он не промахивается
        if randint(1, 100) < 90 or current_user.player_class == 3:
            damage = count_attack(int(info[3])) + user_weapon_attack
        else:
            damage = 0
        # Проверка на критический урон, если пользователь - Стрелок
        if current_user.player_class == 2 and randint(1, 100) < 15:
            damage = int(damage * 1.7)
        info[4] = str(int(info[4]) - damage)
        player = db_sess.query(Player).filter(Player.id == current_user.id).first()
        player.location = '/'.join(info)
        db_sess.commit()
        if int(info[4]) > 0:  # Если враг ещё жив, то дальше атакует он
            get_damage()
        return redirect('/adventure')
    return redirect('/message/busy/adventure')


@app.route('/get_free', methods=['GET', 'POST'])  # Метод, делающий пользователя не занятым ничем
@login_required
def get_free():
    db_sess = db_session.create_session()
    info = current_user.location.split('/')
    player = db_sess.query(Player).filter(Player.id == current_user.id).first()
    player.location = f'{info[0]}/free'
    db_sess.commit()
    return redirect('/adventure')


# Пользователь получает урон
def get_damage():
    db_sess = db_session.create_session()
    info = current_user.location.split('/')
    if info[1] == 'fighting':  # Проверка на то, идет ли бой
        user_armor_protection = 0
        try:  # Проверка на то, есть ли у пользователя надетые вещи
            equipment = current_user.equipped.split(',')
        except Exception:  # Исключение если их у него нет
            equipment = []
        for item_id in equipment:  # Перебор всех вещей, надетых на пользователя, и суммирование их защиты
            item = db_sess.query(Items).filter(Items.id == item_id).first()
            user_armor_protection += item.protection
        damage = count_attack(int(info[3])) - user_armor_protection
        print(damage)
        if damage <= 0:
            damage = 1
        # Если пользователь - Тень, то у него есть 15% шанс увернуться от атаки
        if current_user.player_class == 3 and randint(1, 100) < 15:
            damage = 0
        player = db_sess.query(Player).filter(Player.id == current_user.id).first()
        player.hp = str(int(player.hp) - damage)
        db_sess.commit()
        return redirect('/adventure')
    return redirect('/message/busy/adventure')


@app.route('/explore', methods=['GET', 'POST'])  # Функция генерирует пользователю занятие
@login_required
def exploring_page():
    status = current_user.location.split('/')
    if status[1] != 'free':  # Проверка на то, свободен ли пользователь
        return redirect('/message/busy/adventure')
    if status[0] == '1':
        return redirect('/message/wrong_location/adventure')
    db_sess = db_session.create_session()
    number = randint(1, 100)
    if number in range(1, 6):  # Выпала головоломка
        doing = f'{status[0]}/solving/{randint(0, 5)}'
    elif number in range(6, 11):  # Выпала возможность купить
        doing = f'{status[0]}/buying'
    else:  # Выпало сражение с монстром
        monster = choice(list(db_sess.query(Enemy).filter(Enemy.location == status[0],
                                                          Enemy.min_level >= int(current_user.level.split('-')[1]))))
        if randint(1, 10) < 9:
            enemy_level = int(current_user.level.split('-')[1])
        else:
            enemy_level = int(current_user.level.split('-')[1]) + randint(-1, 1)
        if enemy_level <= 0:
            enemy_level = 1
        doing = f'{status[0]}/fighting/{monster.name}/{enemy_level}/{count_monster_hp(int(enemy_level))}'
    player = db_sess.query(Player).filter(Player.id == current_user.id).first()
    player.location = doing
    db_sess.commit()
    return redirect('/adventure')


@app.route('/change_location/<int:location_id>', methods=['GET', 'POST'])  # Меняет локацию пользователя
@login_required
def change_location_page(location_id):
    db_sess = db_session.create_session()
    status = current_user.location.split('/')
    if status[1] != 'free':  # Проверка на то, свободен ли пользователь
        return redirect('/message/busy/adventure')
    location = db_sess.query(Location).filter(Location.id == location_id).first()
    if int(current_user.level.split('-')[1]) < int(location.level):  # Проверка на то, подходит ли он по уровню
        return redirect('/message/level_too_small/adventure')
    player = db_sess.query(Player).filter(Player.id == current_user.id).first()
    player.location = f'{location_id}/free'
    db_sess.commit()
    return redirect('/adventure')


def give_reward(rarity='random'):  # Выдает пользователю предмет со случайной редкостью, если таковая не указана
    db_sess = db_session.create_session()
    location = db_sess.query(Location).filter(Location.id == current_user.location.split('/')[0]).first()
    if rarity == 'random':
        number = randint(1, 100)
        drop_chances = ITEM_DROP_CHANCES[location.level]  # Получение шансов выпадения из словаря
        if number <= drop_chances[0]:
            rarity = 'Легендарное'
        elif number <= drop_chances[1]:
            rarity = 'Шедевральное'
        elif number <= drop_chances[2]:
            rarity = 'Высокотехнологичное'
        elif number <= drop_chances[3]:
            rarity = 'Качественное'
        elif number <= drop_chances[4]:
            rarity = 'Обычное'
        elif number <= drop_chances[5]:
            rarity = 'Мусорное'
    number = randint(1, 100)
    classes = list(range(1, 4))
    if number <= 60:
        item_class = location.fav_class
    else:
        classes.remove(location.fav_class)
        item_class = choice(classes)
    item_id = choice(list(db_sess.query(Items).filter(Items.class_required == item_class,
                                                      Items.rarity == rarity))).id
    new_inventory = str(item_id)
    if current_user.inventory:
        new_inventory = current_user.inventory + ',' + str(item_id)
    player = db_sess.query(Player).filter(Player.id == current_user.id).first()
    player.inventory = new_inventory
    db_sess.commit()


def give_exp(number_of_exp=-1):  # Генерирует количество опыта, если оно не указано и выдает пользователю
    db_sess = db_session.create_session()
    if number_of_exp == -1:
        number_of_exp = count_exp(int(current_user.level.split('-')[1]))
    new_level = int(current_user.level.split('-')[1])
    new_exp = list(map(int, current_user.level.split('-')[0].split('/')))
    new_exp[0] += number_of_exp
    while new_exp[0] >= new_exp[1]:
        new_exp[0] -= new_exp[1]
        new_level += 1
        new_exp[1] = count_exp_to_new_level(int(new_level))
    new_value = f'{new_exp[0]}/{new_exp[1]}-{new_level}'
    player = db_sess.query(Player).filter(Player.id == current_user.id).first()
    player.level = new_value
    db_sess.commit()


def normalize_hp():  # Возвращает здоровье пользователя в норму
    db_sess = db_session.create_session()
    player = db_sess.query(Player).filter(Player.id == current_user.id).first()
    player.hp = str(count_player_hp(int(current_user.level.split('-')[1]), player.player_class == 1))
    db_sess.commit()


# Функция, генерирующая страницу с игрой
@app.route('/adventure', methods=['GET', 'POST'])
@login_required
def adventure_page():
    db_sess = db_session.create_session()
    status = current_user.location.split('/')
    location = db_sess.query(Location).filter(Location.id == int(status[0])).first()
    occupation = status[1]
    loc_name = location.name
    loc_text = location.description
    if status[0] != '1':  # Проверка на то, что пользователь не находится в стартовой локации
        if occupation == 'free':  # Пользователь свободен
            return render_template('adventure_free_page.html', heading='Приключение', location=loc_text, place=loc_name)
        elif occupation == 'fighting':  # Пользователь сражается
            if int(current_user.hp) <= 0:  # Поражение
                get_free()
                normalize_hp()
                return render_template('adventure_free_page.html', heading='Приключение', location=loc_text,
                                       place=loc_name, additional_text=ADDITIONAL_TEXTS['fight_fail'])
            elif int(status[4]) <= 0:  # Победа
                give_reward()
                normalize_hp()
                give_exp()
                get_free()
                return render_template('adventure_free_page.html', heading='Приключение', location=loc_text,
                                       place=loc_name, additional_text=ADDITIONAL_TEXTS['fight_success'])
            return render_template('adventure_fighting_page.html', heading='Приключение', place=loc_name,
                                   enemy_name=status[2], enemy_level=status[3], player_hp=current_user.hp,
                                   enemy_hp=status[4])
        elif occupation == 'solving':  # Пользователь решает головоломку
            form = SolvingForm()
            if form.validate_on_submit():
                answer = form.item_type.data
                if answer == status[2]:  # Правильное решение
                    give_reward()
                    player = db_sess.query(Player).filter(Player.id == current_user.id).first()
                    player.location = f'{status[0]}/free'
                    db_sess.commit()
                    return render_template('adventure_free_page.html', heading='Приключение', location=loc_text,
                                           place=loc_name, additional_text=ADDITIONAL_TEXTS['solve_success'])
                else:  # Неправильное решение
                    player = db_sess.query(Player).filter(Player.id == current_user.id).first()
                    player.location = f'{status[0]}/free'
                    db_sess.commit()
                    return render_template('adventure_free_page.html', heading='Приключение', location=loc_text,
                                           place=loc_name, additional_text=ADDITIONAL_TEXTS['solve_fail'])
            return render_template('adventure_solving_page.html', heading='Приключение', form=form,
                                   location=loc_text, place=loc_name, image=status[2])
        elif occupation == 'buying':  # Пользователь торгует
            form = BuyingForm()
            if form.validate_on_submit():
                answer = form.box_type.data
                if answer == 'no':  # Если пользователь ушел
                    get_free()
                    return render_template('adventure_free_page.html', heading='Приключение', location=loc_text,
                                           place=loc_name, additional_text=ADDITIONAL_TEXTS['buy_fail'])
                else:  # Если что-то купил
                    give_reward(answer)
                    get_free()
                    return render_template('adventure_free_page.html', heading='Приключение', location=loc_text,
                                           place=loc_name, additional_text=ADDITIONAL_TEXTS['buy_success'])
            return render_template('adventure_buying_page.html', heading='Приключение', form=form,
                                   location=loc_text, place=loc_name)
    else:  # Генерирование специальной страницы, если пользователь в стартовой локации
        variants = []
        for loc in db_sess.query(Location).filter(Location.id > 1):
            variants.append([loc.name, loc.level])
        return render_template('adventure_start_location_page.html', heading='Приключение', variants=variants)


if __name__ == '__main__':
    app.register_blueprint(enemy_api.blueprint)
    app.run(port=8080, host='127.0.0.1')  # Запуск приложения
