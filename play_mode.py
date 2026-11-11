from pico2d import (
    clear_canvas, update_canvas, get_events, load_font, get_time,
    SDL_QUIT, SDL_KEYDOWN, SDLK_ESCAPE, SDLK_p, SDLK_i, SDLK_r
)
import game_world
import game_framework
from boy import Boy
from grass import Grass
from bird import Bird

boy = None
grass = None
birds = []
font = None


def init():
    global boy, grass, birds, font

    font = load_font('ENCR10B.TTF', 16)

    # 1. 잔디 (배경 레이어 0)
    grass = Grass()
    game_world.add_object(grass, 0)

    # 2. 소년 (캐릭터 레이어 1)
    boy = Boy()
    boy.x = 100
    game_world.add_object(boy, 1)

    # 3. 10마리 새떼 생성 및 게임 월드 등록 (레이어 1)
    birds = [Bird() for _ in range(10)]
    for bird in birds:
        game_world.add_object(bird, 1)


def finish():
    global boy, grass, birds, font
    game_world.clear()
    boy = None
    grass = None
    birds = []
    font = None


def pause():
    if boy and hasattr(boy, 'pause'):
        boy.pause()


def resume():
    pass


def update():
    game_world.update()


def render():
    clear_canvas()
    game_world.render()
    update_canvas()


def draw():
    render()


def handle_events():
    global boy
    import item_mode
    import pause_mode

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
            elif event.key == SDLK_i:
                game_framework.push_mode(item_mode)
            elif event.key == SDLK_p:
                game_framework.push_mode(pause_mode)
            else:
                if boy:
                    boy.handle_event(event)
        else:
            if boy:
                boy.handle_event(event)
