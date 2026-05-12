"""
俄罗斯方块小游戏
使用 pygame 实现，支持方块下落、左右移动、旋转、消行、计分、加速等基本玩法。

操作说明：
    ← / →   : 左右移动
    ↓       : 加速下落（软降）
    空格    : 直接落底（硬降）
    ↑ / X   : 顺时针旋转
    Z       : 逆时针旋转
    P       : 暂停 / 继续
    R       : 游戏结束后重新开始
    ESC     : 退出游戏
"""

import random
import sys

import pygame

# ---------- 基础配置 ----------
COLS = 10                 # 棋盘列数
ROWS = 20                 # 棋盘行数
CELL_SIZE = 30            # 每个方格的像素大小
SIDE_PANEL_WIDTH = 200    # 右侧信息面板宽度

PLAYFIELD_WIDTH = COLS * CELL_SIZE
PLAYFIELD_HEIGHT = ROWS * CELL_SIZE
SCREEN_WIDTH = PLAYFIELD_WIDTH + SIDE_PANEL_WIDTH
SCREEN_HEIGHT = PLAYFIELD_HEIGHT

FPS = 60

# 颜色 (R, G, B)
BLACK = (15, 15, 20)
GRID_LINE = (40, 40, 55)
WHITE = (240, 240, 240)
GRAY = (120, 120, 130)
RED = (220, 70, 70)

# 7 种俄罗斯方块及其颜色
# 形状用 4x4 网格的相对坐标表示
SHAPES = {
    "I": {
        "color": (0, 200, 230),
        "rotations": [
            [(0, 1), (1, 1), (2, 1), (3, 1)],
            [(2, 0), (2, 1), (2, 2), (2, 3)],
            [(0, 2), (1, 2), (2, 2), (3, 2)],
            [(1, 0), (1, 1), (1, 2), (1, 3)],
        ],
    },
    "O": {
        "color": (240, 220, 70),
        "rotations": [
            [(1, 0), (2, 0), (1, 1), (2, 1)],
        ],
    },
    "T": {
        "color": (160, 80, 200),
        "rotations": [
            [(0, 1), (1, 1), (2, 1), (1, 0)],
            [(1, 0), (1, 1), (1, 2), (2, 1)],
            [(0, 1), (1, 1), (2, 1), (1, 2)],
            [(1, 0), (1, 1), (1, 2), (0, 1)],
        ],
    },
    "S": {
        "color": (80, 210, 100),
        "rotations": [
            [(1, 1), (2, 1), (0, 2), (1, 2)],
            [(1, 0), (1, 1), (2, 1), (2, 2)],
        ],
    },
    "Z": {
        "color": (230, 80, 80),
        "rotations": [
            [(0, 1), (1, 1), (1, 2), (2, 2)],
            [(2, 0), (1, 1), (2, 1), (1, 2)],
        ],
    },
    "J": {
        "color": (70, 110, 230),
        "rotations": [
            [(0, 1), (1, 1), (2, 1), (2, 2)],
            [(1, 0), (1, 1), (1, 2), (2, 0)],
            [(0, 0), (0, 1), (1, 1), (2, 1)],
            [(0, 2), (1, 0), (1, 1), (1, 2)],
        ],
    },
    "L": {
        "color": (240, 150, 50),
        "rotations": [
            [(0, 1), (1, 1), (2, 1), (0, 2)],
            [(1, 0), (1, 1), (1, 2), (2, 2)],
            [(2, 0), (0, 1), (1, 1), (2, 1)],
            [(0, 0), (1, 0), (1, 1), (1, 2)],
        ],
    },
}


class Piece:
    """正在下落的方块。"""

    def __init__(self, shape_key: str):
        self.shape_key = shape_key
        self.rotations = SHAPES[shape_key]["rotations"]
        self.color = SHAPES[shape_key]["color"]
        self.rotation = 0
        # 初始位置：棋盘顶部居中
        self.x = COLS // 2 - 2
        self.y = -1

    @property
    def blocks(self):
        return self.rotations[self.rotation]

    def cells(self, dx: int = 0, dy: int = 0, rotation: int | None = None):
        rot = self.rotation if rotation is None else rotation
        for cx, cy in self.rotations[rot]:
            yield self.x + cx + dx, self.y + cy + dy


def new_piece() -> Piece:
    return Piece(random.choice(list(SHAPES.keys())))


def create_board():
    return [[None for _ in range(COLS)] for _ in range(ROWS)]


def valid_position(board, piece: Piece, dx: int = 0, dy: int = 0, rotation: int | None = None) -> bool:
    for x, y in piece.cells(dx, dy, rotation):
        if x < 0 or x >= COLS or y >= ROWS:
            return False
        if y >= 0 and board[y][x] is not None:
            return False
    return True


def lock_piece(board, piece: Piece) -> bool:
    """把当前方块锁定到棋盘上，返回是否游戏结束（顶出棋盘）。"""
    game_over = False
    for x, y in piece.cells():
        if y < 0:
            game_over = True
            continue
        board[y][x] = piece.color
    return game_over


def clear_lines(board) -> int:
    new_board = [row for row in board if any(cell is None for cell in row)]
    cleared = ROWS - len(new_board)
    for _ in range(cleared):
        new_board.insert(0, [None for _ in range(COLS)])
    board[:] = new_board
    return cleared


def compute_drop_y(board, piece: Piece) -> int:
    """计算硬降时落点的 y 偏移量。"""
    dy = 0
    while valid_position(board, piece, dy=dy + 1):
        dy += 1
    return dy


def draw_cell(surface, x_px, y_px, color, border=True):
    rect = pygame.Rect(x_px, y_px, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(surface, color, rect)
    if border:
        pygame.draw.rect(surface, BLACK, rect, 1)
        inner = rect.inflate(-8, -8)
        lighter = tuple(min(255, c + 40) for c in color)
        pygame.draw.rect(surface, lighter, inner, 2)


def draw_board(surface, board):
    for y in range(ROWS):
        for x in range(COLS):
            px = x * CELL_SIZE
            py = y * CELL_SIZE
            color = board[y][x]
            if color is None:
                pygame.draw.rect(surface, BLACK, (px, py, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(surface, GRID_LINE, (px, py, CELL_SIZE, CELL_SIZE), 1)
            else:
                draw_cell(surface, px, py, color)


def draw_piece(surface, piece: Piece, ghost: bool = False, offset=(0, 0)):
    ox, oy = offset
    for x, y in piece.cells():
        if y < 0:
            continue
        px = (x + ox) * CELL_SIZE
        py = (y + oy) * CELL_SIZE
        if ghost:
            rect = pygame.Rect(px, py, CELL_SIZE, CELL_SIZE)
            ghost_color = tuple(c // 3 for c in piece.color)
            pygame.draw.rect(surface, ghost_color, rect, 2)
        else:
            draw_cell(surface, px, py, piece.color)


def draw_ghost(surface, board, piece: Piece):
    dy = compute_drop_y(board, piece)
    if dy <= 0:
        return
    for x, y in piece.cells(dy=dy):
        if y < 0:
            continue
        px = x * CELL_SIZE
        py = y * CELL_SIZE
        rect = pygame.Rect(px, py, CELL_SIZE, CELL_SIZE)
        ghost_color = tuple(min(255, c // 2 + 30) for c in piece.color)
        pygame.draw.rect(surface, ghost_color, rect, 2)


def draw_next_piece(surface, piece: Piece, top_left):
    x0, y0 = top_left
    for cx, cy in piece.blocks:
        px = x0 + cx * CELL_SIZE
        py = y0 + cy * CELL_SIZE
        draw_cell(surface, px, py, piece.color)


def draw_side_panel(surface, font_big, font_small, score, level, lines, next_piece, paused, game_over):
    panel_x = PLAYFIELD_WIDTH
    pygame.draw.rect(surface, (25, 25, 35), (panel_x, 0, SIDE_PANEL_WIDTH, SCREEN_HEIGHT))
    pygame.draw.line(surface, GRAY, (panel_x, 0), (panel_x, SCREEN_HEIGHT), 2)

    title = font_big.render("TETRIS", True, WHITE)
    surface.blit(title, (panel_x + 40, 20))

    labels = [
        ("Score", str(score)),
        ("Level", str(level)),
        ("Lines", str(lines)),
    ]
    y = 90
    for label, value in labels:
        lab = font_small.render(label, True, GRAY)
        val = font_big.render(value, True, WHITE)
        surface.blit(lab, (panel_x + 20, y))
        surface.blit(val, (panel_x + 20, y + 20))
        y += 70

    nxt_label = font_small.render("Next", True, GRAY)
    surface.blit(nxt_label, (panel_x + 20, y))
    draw_next_piece(surface, next_piece, (panel_x + 30, y + 25))

    help_lines = [
        "←/→ Move",
        "↓ Soft drop",
        "Space Hard drop",
        "↑/X Rotate CW",
        "Z   Rotate CCW",
        "P Pause   R Restart",
        "ESC Quit",
    ]
    hy = SCREEN_HEIGHT - len(help_lines) * 18 - 10
    for line in help_lines:
        text = font_small.render(line, True, GRAY)
        surface.blit(text, (panel_x + 15, hy))
        hy += 18

    if paused:
        draw_center_message(surface, font_big, "PAUSED", WHITE)
    elif game_over:
        draw_center_message(surface, font_big, "GAME OVER", RED, sub_text="Press R to restart")


def draw_center_message(surface, font, text, color, sub_text: str | None = None):
    overlay = pygame.Surface((PLAYFIELD_WIDTH, PLAYFIELD_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))
    msg = font.render(text, True, color)
    rect = msg.get_rect(center=(PLAYFIELD_WIDTH // 2, PLAYFIELD_HEIGHT // 2))
    surface.blit(msg, rect)
    if sub_text:
        small = pygame.font.SysFont("Arial", 18)
        sub = small.render(sub_text, True, WHITE)
        sub_rect = sub.get_rect(center=(PLAYFIELD_WIDTH // 2, PLAYFIELD_HEIGHT // 2 + 40))
        surface.blit(sub, sub_rect)


def compute_drop_interval(level: int) -> int:
    """根据等级返回下落间隔（毫秒），等级越高越快。"""
    base = 500
    interval = int(base * (0.85 ** (level - 1)))
    return max(60, interval)


def compute_score(cleared_lines: int, level: int) -> int:
    table = {1: 100, 2: 300, 3: 500, 4: 800}
    return table.get(cleared_lines, 0) * level


def main():
    pygame.init()
    pygame.display.set_caption("俄罗斯方块 Tetris")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    font_big = pygame.font.SysFont("Arial", 28, bold=True)
    font_small = pygame.font.SysFont("Arial", 16)

    def reset():
        return {
            "board": create_board(),
            "current": new_piece(),
            "next": new_piece(),
            "score": 0,
            "lines": 0,
            "level": 1,
            "drop_timer": 0,
            "game_over": False,
            "paused": False,
        }

    state = reset()

    while True:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if event.key == pygame.K_r and state["game_over"]:
                    state = reset()
                    continue
                if event.key == pygame.K_p and not state["game_over"]:
                    state["paused"] = not state["paused"]
                    continue
                if state["paused"] or state["game_over"]:
                    continue

                piece = state["current"]
                board = state["board"]

                if event.key == pygame.K_LEFT:
                    if valid_position(board, piece, dx=-1):
                        piece.x -= 1
                elif event.key == pygame.K_RIGHT:
                    if valid_position(board, piece, dx=1):
                        piece.x += 1
                elif event.key == pygame.K_DOWN:
                    if valid_position(board, piece, dy=1):
                        piece.y += 1
                        state["score"] += 1
                elif event.key in (pygame.K_UP, pygame.K_x):
                    next_rot = (piece.rotation + 1) % len(piece.rotations)
                    for kick in (0, -1, 1, -2, 2):
                        if valid_position(board, piece, dx=kick, rotation=next_rot):
                            piece.x += kick
                            piece.rotation = next_rot
                            break
                elif event.key == pygame.K_z:
                    next_rot = (piece.rotation - 1) % len(piece.rotations)
                    for kick in (0, -1, 1, -2, 2):
                        if valid_position(board, piece, dx=kick, rotation=next_rot):
                            piece.x += kick
                            piece.rotation = next_rot
                            break
                elif event.key == pygame.K_SPACE:
                    drop = compute_drop_y(board, piece)
                    piece.y += drop
                    state["score"] += drop * 2
                    state["drop_timer"] = compute_drop_interval(state["level"])

        if not state["paused"] and not state["game_over"]:
            state["drop_timer"] += dt
            interval = compute_drop_interval(state["level"])
            while state["drop_timer"] >= interval:
                state["drop_timer"] -= interval
                piece = state["current"]
                board = state["board"]
                if valid_position(board, piece, dy=1):
                    piece.y += 1
                else:
                    over = lock_piece(board, piece)
                    cleared = clear_lines(board)
                    state["lines"] += cleared
                    state["score"] += compute_score(cleared, state["level"])
                    state["level"] = 1 + state["lines"] // 10
                    state["current"] = state["next"]
                    state["next"] = new_piece()
                    if over or not valid_position(board, state["current"]):
                        state["game_over"] = True
                        break

        screen.fill(BLACK)
        draw_board(screen, state["board"])
        if not state["game_over"]:
            draw_ghost(screen, state["board"], state["current"])
        draw_piece(screen, state["current"])
        draw_side_panel(
            screen,
            font_big,
            font_small,
            state["score"],
            state["level"],
            state["lines"],
            state["next"],
            state["paused"],
            state["game_over"],
        )
        pygame.display.flip()


if __name__ == "__main__":
    main()
