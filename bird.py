"""
Drill #14: 새의 비행 애니메이션 구현 (AI 활용)
[새의 비행 애니메이션 개발 논리 및 물리 모델링]
1. 2D 게임 공간 물리 축척: PIXEL_PER_METER = 10.0 / 0.3 (약 33.33 px/m)
2. 비행 속도: 실제 조류의 순항 비행 속력 30.0 ~ 48.0 km/h (약 8.33 ~ 13.33 m/s) 개체별 난수 부여
3. 날갯짓 주기 및 FPS 연동: 소년의 보폭 공식과 대응하여 1회 날갯짓(14프레임)당 3.0m 전진 가정
   frames_per_second = (speed_mps / 3.0) * 14 -> 비행 속도가 빠를수록 날갯짓도 역동적으로 가속
4. 14프레임 스프라이트 시트 분석: 918x506 (5열 3행), 마지막 빈칸 제외 14프레임 정밀 인덱싱
5. 좌우 반전 및 화면 경계 반사: dir=1 정방향, dir=-1 수평반전('h'), 좌우 화면 경계 반사
6. 10마리 군집(Flock) 다양성: 위치, 고도, 속도, 방향, 날갯짓 위상(Frame offset) 난수화
"""
from pico2d import load_image, get_canvas_width
import random
import game_framework


# ==============================================================================
# [물리 단위 및 기본 상수 - LEC 16 시간 기반 물리 모델]
# ==============================================================================
PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel = 30 cm (약 33.33 px/m)

# bird_animation.png 스프라이트 시트 분석 (918 x 506 픽셀, 5열 x 3행)
# 총 15개 격자 중 마지막 칸(행 2, 열 4)은 빈칸(Alpha=0)이며 유효 프레임은 총 14개
SHEET_W, SHEET_H = 918, 506
COLS, ROWS = 5, 3
TOTAL_FRAMES = 14

# 단일 프레임 정밀 클리핑 좌표 룩업 테이블 (left, bottom, width, height)
# Pico2D는 좌하단(bottom=0) 기준이므로 상단 행부터 역순 계산
FRAME_COORDS = [
    (0,   338, 183, 168),  # Frame 0 (Row 0, Col 0)
    (183, 338, 184, 168),  # Frame 1 (Row 0, Col 1)
    (367, 338, 183, 168),  # Frame 2 (Row 0, Col 2)
    (550, 338, 184, 168),  # Frame 3 (Row 0, Col 3)
    (734, 338, 184, 168),  # Frame 4 (Row 0, Col 4)
    (0,   169, 183, 169),  # Frame 5 (Row 1, Col 0)
    (183, 169, 184, 169),  # Frame 6 (Row 1, Col 1)
    (367, 169, 183, 169),  # Frame 7 (Row 1, Col 2)
    (550, 169, 184, 169),  # Frame 8 (Row 1, Col 3)
    (734, 169, 184, 169),  # Frame 9 (Row 1, Col 4)
    (0,     0, 183, 169),  # Frame 10 (Row 2, Col 0)
    (183,   0, 184, 169),  # Frame 11 (Row 2, Col 1)
    (367,   0, 183, 169),  # Frame 12 (Row 2, Col 2)
    (550,   0, 184, 169),  # Frame 13 (Row 2, Col 3)
]

# 화면 렌더링 크기:
# 게임 화면(1600x600)에서 시각적 가시성과 날갯짓 모션 표현을 위해
# 원본 비율(183.6 : 168.67)을 유지하며 가로 100px, 세로 92px로 렌더링
DRAW_W = 100
DRAW_H = 92


class Bird:
    image = None

    def __init__(self, x=None, y=None, dir=None, speed_kmph=None):
        if Bird.image is None:
            Bird.image = load_image('bird_animation.png')

        half_w = DRAW_W / 2
        canvas_w = get_canvas_width() if get_canvas_width() > 0 else 1600

        # 1. 위치 설정: 소년(y=90)의 위쪽 하늘 고도(y: 300 ~ 540)에 랜덤 배치
        self.x = x if x is not None else random.uniform(half_w + 50, canvas_w - half_w - 50)
        self.y = y if y is not None else random.uniform(300.0, 540.0)

        # 2. 비행 방향 설정 (1: 오른쪽 비행, -1: 왼쪽 비행)
        self.dir = dir if dir is not None else random.choice([-1, 1])

        # 3. 비행 속도 계산 (실제 조류 비행 속도: 30.0 ~ 48.0 km/h)
        # km/h -> m/s -> px/s 변환
        self.speed_kmph = speed_kmph if speed_kmph is not None else random.uniform(30.0, 48.0)
        self.speed_mps = (self.speed_kmph * 1000.0 / 3600.0)
        self.speed_pps = self.speed_mps * PIXEL_PER_METER

        # 4. 날갯짓 빈도 (Wingbeat Frequency) 및 프레임 증가율 계산 (LEC 16 슬라이드 28 공식 응용)
        # 소년의 1보폭(Stride)에 대응하여, 새의 1회 날갯짓 동안 전진하는 거리(Advance per stroke)를 약 3.0m로 모델링
        # 1회 날갯짓 사이클 = 14프레임
        distance_per_flap_m = 3.0
        flaps_per_second = self.speed_mps / distance_per_flap_m
        self.frames_per_second = flaps_per_second * TOTAL_FRAMES  # 초당 프레임 재생 속도

        # 5. 애니메이션 시작 프레임 위상 분산 (0.0 ~ 13.9)
        # 모든 새가 동시에 날개를 퍼덕이지 않고 자연스럽게 엇갈리도록 랜덤 위상 부여
        self.frame = random.uniform(0.0, float(TOTAL_FRAMES))

    def update(self):
        dt = game_framework.frame_time

        # 1. 프레임 타임(dt) 기반 시간 동기화 애니메이션 재생
        self.frame = (self.frame + self.frames_per_second * dt) % TOTAL_FRAMES

        # 2. 프레임 타임(dt) 기반 수평 이동
        self.x += self.dir * self.speed_pps * dt

        # 3. 화면 좌우 경계 도달 시 방향 반전 (Bounce)
        half_w = DRAW_W / 2
        canvas_w = get_canvas_width() if get_canvas_width() > 0 else 1600

        if self.x > canvas_w - half_w:
            self.x = canvas_w - half_w
            self.dir = -1
        elif self.x < half_w:
            self.x = half_w
            self.dir = 1

    def draw(self):
        idx = int(self.frame) % TOTAL_FRAMES
        left, bottom, width, height = FRAME_COORDS[idx]

        # 비행 방향에 따른 수평 반전 렌더링
        # 원본 스프라이트는 오른쪽(Right)을 바라보고 있으므로:
        # 오른쪽 비행(dir=1) 시 원본('', flip 없음), 왼쪽 비행(dir=-1) 시 수평 반전('h')
        flip = '' if self.dir == 1 else 'h'

        self.image.clip_composite_draw(
            left, bottom, width, height,
            0.0, flip,
            self.x, self.y,
            DRAW_W, DRAW_H
        )
