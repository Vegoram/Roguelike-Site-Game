from random import randint


def count_player_hp(level, is_guard):
    if is_guard:
        return 40 + (level - 1) * 12
    return 30 + (level - 1) * 10


def count_monster_hp(level):
    return 30 + (level - 1) * 10 + randint(0 - level * 2, level * 2)


def count_attack(level):
    return int(count_monster_hp(level) / (5 + (level // 5))) + 1


def count_exp(level):
    rand_diapason = 5 + level * 2
    return int(count_exp_to_new_level(level) / (3 + (level // 3))) + randint(0 - rand_diapason, rand_diapason)


def count_exp_to_new_level(level):
    exp = 0
    for stage in range(1, level // 10 + 2):
        exp += 100 * stage * (level - (10 * (stage - 1)))
    return exp
