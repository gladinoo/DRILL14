world = [[], [], []]  # 0: 배경, 1: 오브젝트, 2: UI


def add_object(o, depth=1):
    world[depth].append(o)


def add_oject(o, depth=1):
    """교수님 코드 오타 호환용 별칭"""
    add_object(o, depth)


def add_objects(ol, depth=1):
    world[depth].extend(ol)


def remove_object(o):
    for layer in world:
        if o in layer:
            layer.remove(o)
            return


def update():
    for layer in world:
        for o in layer[:]:
            o.update()


def render():
    for layer in world:
        for o in layer[:]:
            o.draw()


def clear():
    for layer in world:
        layer.clear()
