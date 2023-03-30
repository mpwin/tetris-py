from collections import namedtuple
from enum import Enum
from random import randint
from typing import Optional

import pygame


BOARD_WIDTH = 10
BOARD_HEIGHT = 20
GRID_SIZE = 40

SCREEN_WIDTH = BOARD_WIDTH * GRID_SIZE
SCREEN_HEIGHT = BOARD_HEIGHT * GRID_SIZE


Shape = namedtuple('Shape', ['tiles', 'size'])

SHAPE_I = Shape((
    0, 0, 0, 0,
    1, 1, 1, 1,
    0, 0, 0, 0,
    0, 0, 0, 0,
    ), 4)
SHAPE_J = Shape((
    2, 0, 0,
    2, 2, 2,
    0, 0, 0,
    ), 3)
SHAPE_L = Shape((
    0, 0, 3,
    3, 3, 3,
    0, 0, 0,
    ), 3)
SHAPE_O = Shape((
    4, 4,
    4, 4,
    ), 2)
SHAPE_S = Shape((
    0, 5, 5,
    5, 5, 0,
    0, 0, 0,
    ), 3)
SHAPE_T = Shape((
    0, 6, 0,
    6, 6, 6,
    0, 0, 0,
    ), 3)
SHAPE_Z = Shape((
    7, 7, 0,
    0, 7, 7,
    0, 0, 0,
    ), 3)
SHAPES = (
    SHAPE_I,
    SHAPE_J,
    SHAPE_L,
    SHAPE_O,
    SHAPE_S,
    SHAPE_T,
    SHAPE_Z,
    )


Color = namedtuple('Color', ['name', 'rgb'])

COLOR_BLACK = Color('Black', (0, 0, 0))
COLOR_GRAY = Color('Gray', (128, 128, 128))
COLOR_WHITE = Color('White', (255, 255, 255))
TILE_COLORS = (
    COLOR_BLACK,
    Color('Aqua', (0, 255, 255)),
    Color('Blue', (0, 0, 255)),
    Color('Orange', (255, 170, 0)),
    Color('Yellow', (255, 255, 0)),
    Color('Lime', (0, 255, 0)),
    Color('Purple', (153, 0, 255)),
    Color('Red', (255, 0, 0)),
    )


Event = Enum('Event', (
    'ROTATE',
    'MOVE_LEFT',
    'MOVE_RIGHT',
    'MOVE_DOWN',
    'DROP',
    'CLEAR_ROWS',
    ))
PygameEvent = Enum('PygameEvent', (
    'FORCE_DOWN',
    'CLEAR_ROWS',
    ), start=pygame.USEREVENT+1)

State = Enum('State', (
    'PLAY',
    'FULL_ROWS',
    'GAME_OVER',
    ))

Board = namedtuple('Board', ['tiles', 'state', 'full_rows'])
Tetromino = namedtuple('Tetromino', ['shape', 'row', 'col', 'rotation'])


def main():
    pygame.init()
    pygame.time.set_timer(PygameEvent.FORCE_DOWN.value, 1000)

    screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
    clock = pygame.time.Clock()

    board = Board([0] * BOARD_WIDTH * BOARD_HEIGHT, State.PLAY, ())
    tetromino = create_tetromino()
    running = True

    while running:
        events, running = get_events()
        board, tetromino = update(board, tetromino, events)
        draw(screen, board, tetromino)
        clock.tick(60)

    pygame.quit()


def get_events() -> tuple[frozenset[Event], bool]:
    events, running = set(), True
    for event in pygame.event.get():
        if event.type == PygameEvent.FORCE_DOWN.value:
            events.add(Event.MOVE_DOWN)
        if event.type == PygameEvent.CLEAR_ROWS.value:
            events.add(Event.CLEAR_ROWS)
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                events.add(Event.ROTATE)
            if event.key == pygame.K_DOWN:
                events.add(Event.MOVE_DOWN)
            if event.key == pygame.K_LEFT:
                events.add(Event.MOVE_LEFT)
            if event.key == pygame.K_RIGHT:
                events.add(Event.MOVE_RIGHT)
            if event.key == pygame.K_SPACE:
                events.add(Event.DROP)
            if event.key == pygame.K_ESCAPE:
                running = False
    return frozenset(events), running


def update(
        b: Board, t: Tetromino,
        events: frozenset[Event]) -> tuple[Board, Tetromino]:
    if Event.CLEAR_ROWS in events:
        b = clear_full_rows(b, b.full_rows)
        return b, t
    if b.state in (State.FULL_ROWS, State.GAME_OVER):
        return b, t

    if Event.ROTATE in events:
        t = rotate(t, b)
    if Event.MOVE_LEFT in events:
        t = move_left(t, b)
    if Event.MOVE_RIGHT in events:
        t = move_right(t, b)
    if Event.MOVE_DOWN in events:
        b, t = move_down(b, t)
    if Event.DROP in events:
        b, t = drop(b, t)

    b = check_full_rows(b)

    if b.state == State.FULL_ROWS:
        pygame.time.set_timer(PygameEvent.CLEAR_ROWS.value, 100, True)
        return b, t

    b = check_game_over(b, t)

    return b, t


def draw(screen: pygame.Surface, b: Board, t: Tetromino) -> None:

    def draw_board(color: Optional[Color] = None) -> None:
        for row in range(0, BOARD_HEIGHT):
            for col in range(0, BOARD_WIDTH):
                tile = board_get_tile(b, row, col)
                if tile > 0:
                    draw_tile(row, col, color or TILE_COLORS[tile])

    def draw_tetromino() -> None:
        size = SHAPES[t.shape].size
        for row in range(0, size):
            for col in range(0, size):
                tile = tetromino_get_tile(t, row, col)
                if tile > 0:
                    draw_tile(row + t.row, col + t.col, TILE_COLORS[tile])

    def draw_tile(row: int, col: int, color: Color) -> None:
        rect = pygame.Rect(
            col * GRID_SIZE, # x
            row * GRID_SIZE, # y
            GRID_SIZE,
            GRID_SIZE,
            )
        pygame.draw.rect(screen, color.rgb, rect)

    def highlight_rows():
        for row in b.full_rows:
            for col in range(BOARD_WIDTH):
                draw_tile(row, col, COLOR_WHITE)

    screen.fill(COLOR_BLACK.rgb)

    match b.state:
        case State.PLAY:
            draw_board()
            draw_tetromino()
        case State.FULL_ROWS:
            draw_board()
            highlight_rows()
        case State.GAME_OVER:
            draw_board(COLOR_GRAY)

    pygame.display.flip()


def board_get_tile(b: Board, row: int, col: int) -> int:
    return b.tiles[row * BOARD_WIDTH + col]


def board_set_tile(b: Board, row: int, col: int, val: int) -> Board:
    tmp_tiles = list(b.tiles)
    tmp_tiles[row * BOARD_WIDTH + col] = val
    return b._replace(tiles=tmp_tiles)


def board_update(b: Board, t: Tetromino) -> Board:
    size = SHAPES[t.shape].size

    for row in range(0, size):
        for col in range(0, size):
            val = tetromino_get_tile(t, row, col)
            if val > 0:
                b_row = row + t.row
                b_col = col + t.col
                b = board_set_tile(b, b_row, b_col, val)

    return b


def tetromino_get_tile(t: Tetromino, row: int, col: int) -> int:
    data = SHAPES[t.shape].tiles
    size = SHAPES[t.shape].size

    match t.rotation:
        case 0:
            return data[
                row *
                size + col
                ]
        case 1:
            return data[
                (size - col - 1) *
                size + row
                ]
        case 2:
            return data[
                (size - row - 1) *
                size + (size - col - 1)
                ]
        case 3:
            return data[
                col *
                size + (size - row - 1)
                ]


def create_tetromino() -> Tetromino:
    shape = randint(0, len(SHAPES)-1)
    row = 0
    col = (BOARD_WIDTH // 2) - (SHAPES[shape].size // 2)
    rotation = randint(0, 3)
    return Tetromino(shape, row, col, rotation)


def rotate(t: Tetromino, b: Board) -> Tetromino:
    rotation = (t.rotation + 1) % 4
    tmp_t = t._replace(rotation=rotation)
    if is_valid(b, tmp_t):
        return tmp_t
    return t


def move_left(t: Tetromino, b: Board) -> Tetromino:
    col = t.col - 1
    tmp_t = t._replace(col=col)
    if is_valid(b, tmp_t):
        return tmp_t
    return t


def move_right(t: Tetromino, b: Board) -> Tetromino:
    col = t.col + 1
    tmp_t = t._replace(col=col)
    if is_valid(b, tmp_t):
        return tmp_t
    return t


def move_down(b: Board, t: Tetromino) -> tuple[Board, Tetromino]:
    t = t._replace(row=t.row+1)

    if not is_valid(b, t):
        t = t._replace(row=t.row-1)
        b = board_update(b, t)
        return b, create_tetromino()
    else:
        return b, t


def drop(b: Board, t: Tetromino) -> tuple[Board, Tetromino]:
    while is_valid(b, t):
        t = t._replace(row=t.row+1)
    t = t._replace(row=t.row-1)
    b = board_update(b, t)
    return b, create_tetromino()


def is_valid(b: Board, t: Tetromino) -> bool:
    size = SHAPES[t.shape].size

    for row in range(0, size):
        for col in range(0, size):
            val = tetromino_get_tile(t, row, col)
            if val > 0:
                b_row = row + t.row
                b_col = col + t.col

                if b_row >= BOARD_HEIGHT:
                    return False
                if b_col < 0:
                    return False
                if b_col >= BOARD_WIDTH:
                    return False
                if board_get_tile(b, b_row, b_col):
                    return False

    return True


def check_full_rows(b: Board) -> Board:
    rows = set()

    def is_row_full(b: Board, row: int) -> bool:
        for col in range(BOARD_WIDTH):
            if not board_get_tile(b, row, col):
                return False
        return True

    for row in range(BOARD_HEIGHT):
        if is_row_full(b, row):
            rows.add(row)

    if len(rows):
        return b._replace(state=State.FULL_ROWS, full_rows=frozenset(rows))
    else:
        return b


def clear_full_rows(b: Board, rows: frozenset[int]) -> Board:
    tmp_tiles = []
    for row in reversed(range(BOARD_HEIGHT)):
        if row in rows:
            continue
        for col in reversed(range(BOARD_WIDTH)):
            tmp_tiles.append(board_get_tile(b, row, col))
    tmp_tiles.extend([0] * BOARD_WIDTH * len(rows))
    tmp_tiles.reverse()
    return b._replace(tiles=tmp_tiles, state=State.PLAY, full_rows=())


def check_game_over(b: Board, t: Tetromino) -> Board:
    if not is_valid(b, t):
        b = board_update(b, t)
        b = b._replace(state=State.GAME_OVER)
    return b


if __name__ == '__main__':
    main()
