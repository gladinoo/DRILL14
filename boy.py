from math import pi
from pico2d import (
    load_image, load_font, get_time, get_canvas_width,
    SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE
)
from transitions import Machine
import game_world
import game_framework
from ball import Ball


# 물리 단위 및 속도 계산 (LEC 16 슬라이드 19-28)
PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel = 30 cm (약 33.33 px/m)
RUN_SPEED_KMPH = 20.0           # 시속 20 km/h (50m 완주 약 9.00초)
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)           # 5.556 m/s
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER) # 185.185 px/s

# 보폭 기반 애니메이션 프레임 증가율 계산 (LEC 16 슬라이드 28)
STRIDE_LENGTH_M = 0.8        # 보폭 길이 0.8 m
RUN_FRAMES_PER_STRIDE = 5    # 1개 보폭에 대한 애니메이션 프레임 수
# 1초당 증가할 프레임 수 = (속도 / 보폭) * 프레임수
RUN_FRAMES_PER_SECOND = (RUN_SPEED_MPS / STRIDE_LENGTH_M) * RUN_FRAMES_PER_STRIDE


class Idle:
    def enter(self, boy):
        boy.idle_started_at = get_time()
        boy.frame = 0.0

    def do(self, boy):
        if get_time() - boy.idle_started_at >= 5.0:
            boy.fall_asleep()
        else:
            # IDLE 상태: 초당 약 8프레임 재생
            boy.frame = (boy.frame + 8.0 * game_framework.frame_time) % 8

    def draw(self, boy):
        row = 300 if boy.face_dir == 1 else 200
        boy.image.clip_draw(int(boy.frame) * 100, row, 100, 100, boy.x, boy.y)

    def space(self, boy):
        boy.fire_ball()

    def move(self, boy):
        boy.start_run()


class Sleep:
    def enter(self, boy):
        boy.frame = 0.0

    def do(self, boy):
        pass

    def draw(self, boy):
        angle = pi / 2 if boy.face_dir == 1 else -pi / 2
        flip = '' if boy.face_dir == 1 else 'h'
        boy.image.clip_composite_draw(
            int(boy.frame) * 100, 300, 100, 100,
            angle, flip, boy.x, boy.y - 30, 100, 100
        )

    def space(self, boy):
        boy.wake_up()

    def move(self, boy):
        boy.start_run()


class Run:
    def enter(self, boy):
        boy.frame = 0.0

    def do(self, boy):
        # 보폭 0.8m 기반 시간 동기화 애니메이션 및 위치 계산 (슬라이드 29)
        boy.frame = (boy.frame + RUN_FRAMES_PER_SECOND * game_framework.frame_time) % 8
        boy.x += boy.dir * RUN_SPEED_PPS * game_framework.frame_time
        boy.x = max(25, min(get_canvas_width() - 25, boy.x))

    def draw(self, boy):
        row = 100 if boy.face_dir == 1 else 0
        boy.image.clip_draw(int(boy.frame) * 100, row, 100, 100, boy.x, boy.y)

    def space(self, boy):
        boy.fire_ball()

    def move(self, boy):
        pass


class Boy:
    def __init__(self):
        self.x, self.y = 100, 90
        self.frame = 0.0
        self.image = load_image('animation_sheet.png')
        self.font = load_font('ENCR10B.TTF', 16)
        self.idle_started_at = get_time()
        self.dir = 0
        self.face_dir = 1
        self.pressed_keys = set()
        self.item = 'Ball'

        self.states = {'IDLE': Idle(), 'SLEEP': Sleep(), 'RUN': Run()}

        self.machine = Machine(
            model=self,
            states=['IDLE', 'SLEEP', 'RUN'],
            transitions=[
                {'trigger': 'fall_asleep', 'source': 'IDLE', 'dest': 'SLEEP'},
                {'trigger': 'wake_up', 'source': 'SLEEP', 'dest': 'IDLE'},
                {'trigger': 'start_run', 'source': ['IDLE', 'SLEEP'], 'dest': 'RUN'},
                {'trigger': 'stop_run', 'source': 'RUN', 'dest': 'IDLE'},
            ],
            initial='IDLE',
            auto_transitions=False,
        )

    def on_enter_IDLE(self):
        self.states['IDLE'].enter(self)

    def on_enter_SLEEP(self):
        self.states['SLEEP'].enter(self)

    def on_enter_RUN(self):
        self.states['RUN'].enter(self)

    def fire_ball(self):
        if self.item is None or self.item == 0:
            return
        ball_type = 1 if (self.item == 'Ball' or self.item == 1) else 2
        ball = Ball(self.x, self.y, self.face_dir * 10, ball_type=ball_type)
        game_world.add_object(ball, 1)

    def pause(self):
        self.pressed_keys.clear()
        if self.state == 'RUN':
            self.dir = 0
            self.stop_run()

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
            self.states[self.state].space(self)
            return

        if (event.type not in (SDL_KEYDOWN, SDL_KEYUP) or
                event.key not in (SDLK_LEFT, SDLK_RIGHT)):
            return

        if event.type == SDL_KEYDOWN:
            self.pressed_keys.add(event.key)
        else:
            self.pressed_keys.discard(event.key)

        direction = (int(SDLK_RIGHT in self.pressed_keys) -
                     int(SDLK_LEFT in self.pressed_keys))

        if direction != 0:
            self.dir = direction
            self.face_dir = direction
            if self.state in ('IDLE', 'SLEEP'):
                self.start_run()
        elif self.state == 'RUN':
            self.dir = 0
            self.stop_run()

    def update(self):
        self.states[self.state].do(self)

    def draw(self):
        self.states[self.state].draw(self)
        self.font.draw(self.x - 60, self.y + 50, f'(Time: {get_time():.2f})', (255, 255, 0))
