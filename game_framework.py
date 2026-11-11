import time
import os
import sys

running = False
stack = []
frame_time = 0.0


def change_mode(mode):
    global stack
    if stack:
        stack.pop().finish()
    stack.append(mode)
    mode.init()


def push_mode(mode):
    global stack
    if stack:
        stack[-1].pause()
    stack.append(mode)
    mode.init()


def pop_mode():
    global stack
    if stack:
        stack.pop().finish()
    if stack:
        stack[-1].resume()
    else:
        quit()


def quit():
    global running
    running = False


def run(start_mode):
    global running, stack, frame_time
    running = True
    stack = [start_mode]
    frame_time = 0.0
    current_time = time.time()
    try:
        start_mode.init()
        while running:
            stack[-1].handle_events()
            stack[-1].update()
            if hasattr(stack[-1], 'render'):
                stack[-1].render()
            elif hasattr(stack[-1], 'draw'):
                stack[-1].draw()
            frame_time = time.time() - current_time
            frame_rate = 1.0 / frame_time if frame_time > 0 else 0.0
            current_time += frame_time
            print(f'Frame Time: {frame_time}, Frame Rate: {frame_rate}', flush=True)
    finally:
        while stack:
            stack.pop().finish()
        running = False


# VS Code에서 game_framework.py를 열어둔 채 실행(▶) 버튼을 눌렀을 때도 바로 실행되도록 지원
if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    sys.path.insert(0, script_dir)
    from pico2d import open_canvas, close_canvas
    import play_mode
    open_canvas(1800, 600)
    run(play_mode)
    close_canvas()
