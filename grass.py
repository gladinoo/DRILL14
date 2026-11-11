from pico2d import load_image


class Grass:
    def __init__(self):
        self.image = load_image('grass.png')
        self.ruler_image = load_image('ruler.png')

    def draw(self):
        # 잔디 배경 (1600px 캔버스 너비)
        self.image.draw(400, 30)
        self.image.draw(1200, 30)
        # 소년 위쪽에 50m 눈금자 지도 렌더링 (y=350)
        self.ruler_image.draw(800, 350)

    def update(self):
        pass
