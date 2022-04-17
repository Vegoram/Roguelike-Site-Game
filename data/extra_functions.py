from random import randint


def count_monster_hp(level):
    return 30 + (level - 1) * 10 + randint(0 - level * 2, level * 2)
