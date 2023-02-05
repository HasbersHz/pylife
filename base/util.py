from hutil import *


class BaseLifeErrors(LifeErrors):
    pass


def life_warning(s: str):
    print(s, file=sys.srderr)

