import random
import sqlite3


def sql_list(listt):
    new_list = []
    for i in listt:
        new_list.append(i[0])
    return new_list


def sunduk(id_pleer, sunduk_list):
    print(f'вы нашли сундук в нем {len(sunduk_list)} предмета')
    money = list(cur.execute(f"""SELECT money FROM players
                                WHERE id={id_pleer}""").fetchall())[0][0]
    cost = {}
    name = {}
    for i in sunduk_list:
        cost[i] = list(cur.execute(f"""SELECT cost FROM items
                                WHERE id={i}""").fetchall())[0][0]
    for i in sunduk_list:
        name[i] = list(cur.execute(f"""SELECT name FROM items
                                WHERE id={i}""").fetchall())[0][0]
    print(f'''вы нашли сундук в нем {len(sunduk_list)} 
            {name[sunduk_list[0]], name[sunduk_list[1]], name[sunduk_list[2]]}''')
    print('вы можете купить любой из них')
    print(f'''первый стоит {cost[sunduk_list[0]]} монет
торой стоит {cost[sunduk_list[1]]} монет
третий стоит {cost[sunduk_list[2]]} монет''')
    btn = int(input()) # перед игроком 4 кнопки 4 чтобы отказаться 1 2 3 чтобы купить
    while True:
        if btn == 4:
            break
        else:
            if money >= cost[sunduk_list[btn - 1]]:
                print('вы успешно купили вещ')
                inwentar = str(cur.execute(f"""SELECT inventory FROM players
                                WHERE id={id_pleer}""").fetchall())[0]
                if inwentar == None:
                    new_in = str(sunduk_list[btn - 1])
                else:
                    new_in = inwentar.split('/')
                    new_in.append(str(sunduk_list[btn - 1]))
                print(f"""UPDATE players
SET inventory = {'/'.join(new_in)}
WHERE id={id_pleer}""")
                cur.execute(f"""UPDATE players
SET inventory = {'/'.join(new_in)}
WHERE id={id_pleer}""")
                print(id_pleer)
                cur.execute(f"""UPDATE players
                                    SET money = {money-cost[sunduk_list[btn - 1]]}
                                    WHERE id={id_pleer}""")
                break
            else:
                print("у вас не хватает манет")
                btn = int(input())


def boy(id_pleer, id_monster):
    pass


def golovolomka(id_pleer):
    pass


triger = True
con = sqlite3.connect("game_database.db")
id_pl = 1
cur = con.cursor()
name = cur.execute(f"""SELECT nickname FROM players
            WHERE id={id_pl}""").fetchall()

while triger:
    level = list(cur.execute(f"""SELECT level FROM players
                                WHERE id={id_pl}""").fetchall())[0][0]
    location = list(cur.execute(f"""SELECT location FROM players
                                WHERE id={id_pl}""").fetchall())[0][0]

    # выбор предмета для сундука
    list_items = sql_list(list(cur.execute(f"""SELECT id FROM items""").fetchall()))
    items_id = random.choices(list_items, k=3)

    # выбор врага для боя
    list_enemis = sql_list(list(cur.execute(f"""SELECT id FROM enemies
                                        WHERE location={location}""").fetchall()))
    enemi_id = random.choice(list_enemis)

    koef = random.random()
    if koef < 0.9:
        boy(id_pl, enemi_id)
    elif koef < 0.95:
        sunduk(id_pl, items_id)
    else:
        golovolomka(id_pl)
    hp = list(cur.execute(f"""SELECT hp FROM players
                                WHERE id={id_pl}""").fetchall())[0][0]
    if int(hp) <= 0:
        triger = False
        con.close()
