from pico2d import load_image, get_canvas_width
import random
import game_framework


# 물리 단위 및 기본 상수 (LEC 16 슬라이드 19-23)
PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel = 30 cm (약 33.33 px/m)

# 스프라이트 시트 사양 (bird_animation.png: 918 x 506, 5열 x 3행, 총 14프레임)
SHEET_W, SHEET_H = 918, 506
COLS, ROWS = 5, 3
TOTAL_FRAMES = 14

# 단일 프레임 정밀 클리핑 좌표 룩업 테이블 (left, bottom, width, height)
FRAME_COORDS = [
    (0,   338, 183, 168),  # Frame 0
    (183, 338, 184, 168),  # Frame 1
    (367, 338, 183, 168),  # Frame 2
    (550, 338, 184, 168),  # Frame 3
    (734, 338, 184, 168),  # Frame 4
    (0,   169, 183, 169),  # Frame 5
    (183, 169, 184, 169),  # Frame 6
    (367, 169, 183, 169),  # Frame 7
    (550, 169, 184, 169),  # Frame 8
    (734, 169, 184, 169),  # Frame 9
    (0,     0, 183, 169),  # Frame 10
    (183,   0, 184, 169),  # Frame 11
    (367,   0, 183, 169),  # Frame 12
    (550,   0, 184, 169),  # Frame 13
]

DRAW_W = 100
DRAW_H = 92


class Bird:
    image = None

    def __init__(self):
        if Bird.image is None:
            Bird.image = load_image('bird_animation.png')
        self.x = 400.0
        self.y = 400.0
        self.frame = 0.0
        self.dir = 1

        # 실제 조류 비행 속도 모델링 (30.0 ~ 48.0 km/h)
        self.speed_kmph = 36.0  # 기본 36 km/h = 10 m/s
        self.speed_mps = (self.speed_kmph * 1000.0 / 3600.0)
        self.speed_pps = self.speed_mps * PIXEL_PER_METER

    def update(self):
        dt = game_framework.frame_time
        self.frame = (self.frame + 14.0 * dt) % TOTAL_FRAMES
        self.x += self.dir * self.speed_pps * dt

    def draw(self):
        idx = int(self.frame) % TOTAL_FRAMES
        left, bottom, width, height = FRAME_COORDS[idx]
        self.image.clip_draw(left, bottom, width, height, self.x, self.y, DRAW_W, DRAW_H)
