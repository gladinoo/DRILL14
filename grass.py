from pico2d import load_image


class Grass:
    def __init__(self):
        self.image = load_image('grass.png')

    def draw(self):
        # 1600 캔버스 폭을 채우기 위해 800px 잔디 2개 렌더링
        self.image.draw(400, 30)
        self.image.draw(1200, 30)

    def update(self):
        pass
