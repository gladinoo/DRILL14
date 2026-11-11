from pico2d import (
    clear_canvas, update_canvas, get_events, load_font, get_time,
    SDL_QUIT, SDL_KEYDOWN, SDLK_ESCAPE, SDLK_p, SDLK_i, SDLK_r, SDLK_d
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
font_big = None
show_debug = False


def init():
    global boy, grass, birds, font, font_big, show_debug

    font = load_font('ENCR10B.TTF', 16)
    font_big = load_font('ENCR10B.TTF', 24)
    show_debug = False

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

    print(f'>>> [Drill #14] 10마리 새떼 비행 시뮬레이션 시작! (총 {len(birds)}마리)', flush=True)


def finish():
    global boy, grass, birds, font, font_big
    game_world.clear()
    boy = None
    grass = None
    birds = []
    font = None
    font_big = None


def pause():
    if boy and hasattr(boy, 'pause'):
        boy.pause()


def resume():
    pass


def reset_birds():
    """새떼 10마리를 새로운 랜덤 위치와 속도로 재배치"""
    global birds
    for bird in birds:
        game_world.remove_object(bird)
    birds = [Bird() for _ in range(10)]
    for bird in birds:
        game_world.add_object(bird, 1)
    print('>>> [Drill #14] 10마리 새떼를 새로운 위치와 속도로 재배치했습니다.', flush=True)


def update():
    game_world.update()


def render():
    clear_canvas()
    game_world.render()

    # 상단 HUD 정보 출력
    if font:
        fps = 1.0 / game_framework.frame_time if game_framework.frame_time > 0 else 0.0
        hud_text = f'Frame Time: {game_framework.frame_time:.5f}s  |  FPS: {fps:.1f}  |  Birds: {len(birds)}마리'
        font.draw(20, 575, hud_text, (240, 240, 240))

        help_text = '[ESC: 종료]  [R: 새떼 재배치]  [D: 디버그 상세 정보 온/오프]  [화살표/스페이스: 소년 조작]'
        font.draw(20, 550, help_text, (180, 220, 255))

        # 디버그 모드일 때 각 새의 비행 물리 정보 출력
        if show_debug:
            for i, bird in enumerate(birds):
                debug_info = f'#{i+1}: {bird.speed_kmph:.1f}km/h ({bird.frames_per_second:.1f}fps, dir: {bird.dir:+d})'
                font.draw(int(bird.x) - 45, int(bird.y) + 50, debug_info, (255, 255, 100))

    update_canvas()


def draw():
    render()


def handle_events():
    global boy, show_debug
    import item_mode
    import pause_mode

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
            elif event.key == SDLK_r:
                reset_birds()
            elif event.key == SDLK_d:
                show_debug = not show_debug
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


if __name__ == '__main__':
    import os
    import sys
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    sys.path.insert(0, script_dir)
    from pico2d import open_canvas, close_canvas
    open_canvas(1600, 600)
    game_framework.run(sys.modules[__name__])
    close_canvas()
