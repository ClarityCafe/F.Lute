import math


def multiplier_from_db(db: float) -> float:
    return 2 ** (db / 10)


def db_from_multiplier(mult: float) -> float:
    return 10 * math.log2(mult)
