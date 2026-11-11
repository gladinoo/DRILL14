import os
import sys

# 실행 위치와 관계없이 파일이 위치한 디렉터리를 작업 디렉터리로 자동 설정
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
sys.path.insert(0, script_dir)

from pico2d import open_canvas, close_canvas
import game_framework
import play_mode

# 10마리 새떼 비행을 쾌적하게 시뮬레이션하기 위한 1600x600 캔버스
open_canvas(1600, 600)
game_framework.run(play_mode)
close_canvas()
