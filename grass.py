from pico2d import load_image


class Grass:
    def __init__(self):
        self.image = load_image('grass.png')

    def draw(self):
        # 1600 캔버스 폭 전체를 채우는 잔디 배경 (800px 잔디 2개)
        self.image.draw(400, 30)
        self.image.draw(1200, 30)

    def update(self):
        pass
