from collections import namedtuple
from enum import Enum
from random import randint

import pygame


BOARD_WIDTH = 10
BOARD_HEIGHT = 20
GRID_SIZE = 40

SCREEN_WIDTH = BOARD_WIDTH * GRID_SIZE
SCREEN_HEIGHT = BOARD_HEIGHT * GRID_SIZE

TETROMINO_I = (
    0, 0, 0, 0,
    1, 1, 1, 1,
    0, 0, 0, 0,
    0, 0, 0, 0,
    )
TETROMINO_J = (
    2, 0, 0,
    2, 2, 2,
    0, 0, 0,
    )
TETROMINO_L = (
    0, 0, 3,
    3, 3, 3,
    0, 0, 0,
    )
TETROMINO_O = (
    4, 4,
    4, 4,
    )
TETROMINO_S = (
    0, 5, 5,
    5, 5, 0,
    0, 0, 0,
    )
TETROMINO_T = (
    0, 6, 0,
    6, 6, 6,
    0, 0, 0,
    )
TETROMINO_Z = (
    7, 7, 0,
    0, 7, 7,
    0, 0, 0,
    )

TETROMINOES = (
    dict(data=TETROMINO_I, size=4),
    dict(data=TETROMINO_J, size=3),
    dict(data=TETROMINO_L, size=3),
    dict(data=TETROMINO_O, size=2),
    dict(data=TETROMINO_S, size=3),
    dict(data=TETROMINO_T, size=3),
    dict(data=TETROMINO_Z, size=3),
    )

COLOR_BLACK = (0, 0, 0)
COLOR_AQUA = (0, 255, 255)
COLOR_BLUE = (0, 0, 255)
COLOR_ORANGE = (255, 170, 0)
COLOR_YELLOW = (255, 255, 0)
COLOR_LIME = (0, 255, 0)
COLOR_PURPLE = (153, 0, 255)
COLOR_RED = (255, 0, 0)
COLOR_WHITE = (255, 255, 255)

COLORS = (
    COLOR_BLACK,
    COLOR_AQUA,
    COLOR_BLUE,
    COLOR_ORANGE,
    COLOR_YELLOW,
    COLOR_LIME,
    COLOR_PURPLE,
    COLOR_RED,
    COLOR_WHITE,
    )


Event = Enum('Event', (
    'ROTATE',
    'MOVE_LEFT',
    'MOVE_RIGHT',
    'MOVE_DOWN',
    'FORCE_DOWN',
    'HIGHLIGHT_ROWS',
    'CLEAR_ROWS',
    ))
PygameEvent = Enum('PygameEvent', (
    'FORCE_DOWN',
    'HIGHLIGHT_ROWS',
    'CLEAR_ROWS',
    ), start=pygame.USEREVENT+1)

Board = namedtuple('Board', ['tiles'])
Tetromino = namedtuple('Tetromino', ['shape', 'row', 'col', 'rotation'])


def main():
    pygame.init()
    pygame.time.set_timer(PygameEvent.FORCE_DOWN.value, 1000)

    screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
    clock = pygame.time.Clock()

    board = Board([0] * BOARD_WIDTH * BOARD_HEIGHT)
    tetromino = tetromino_create()
    running = True

    while running:
        events, running = get_events()
        board, tetromino = update(board, tetromino, events)

        screen.fill(COLOR_BLACK)
        draw_board(screen, board)
        draw_tetromino(screen, tetromino)
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()


def get_events() -> tuple[frozenset[Event], bool]:
    events, running = set(), True
    for event in pygame.event.get():
        if event.type == PygameEvent.FORCE_DOWN.value:
            events.add(Event.FORCE_DOWN)
        if event.type == PygameEvent.HIGHLIGHT_ROWS.value:
            events.add(Event.HIGHLIGHT_ROWS)
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
            if event.key == pygame.K_ESCAPE:
                running = False
    return frozenset(events), running


def update(
        b: Board, t: Tetromino,
        events: frozenset[Event]) -> tuple[Board, Tetromino]:
    if Event.CLEAR_ROWS in events:
        b = clear_rows(b, get_full_rows(b))
        return b, t
    if Event.HIGHLIGHT_ROWS in events:
        pygame.event.post(
            pygame.event.Event(
                PygameEvent.HIGHLIGHT_ROWS.value
            ))
        return b, t

    if Event.ROTATE in events:
        t = rotate(t, b)
    if Event.MOVE_LEFT in events:
        t = move_left(t, b)
    if Event.MOVE_RIGHT in events:
        t = move_right(t, b)

    if Event.MOVE_DOWN in events or Event.FORCE_DOWN in events:
        b, t = move_down(b, t)

        full_rows = get_full_rows(b)
        if len(full_rows):
            b = highlight_rows(b, full_rows)
            pygame.event.post(
                pygame.event.Event(
                    PygameEvent.HIGHLIGHT_ROWS.value
                ))
            pygame.time.set_timer(
                PygameEvent.CLEAR_ROWS.value,
                500,
                True,
                )

    return b, t


def board_get_tile(b: Board, row: int, col: int) -> int:
    return b.tiles[row * BOARD_WIDTH + col]


def board_set_tile(b: Board, row: int, col: int, val: int) -> Board:
    tmp_tiles = list(b.tiles)
    tmp_tiles[row * BOARD_WIDTH + col] = val
    return b._replace(tiles=tmp_tiles)


def board_update(b: Board, t: Tetromino) -> Board:
    size = TETROMINOES[t.shape]['size']

    for row in range(0, size):
        for col in range(0, size):
            val = tetromino_get_tile(t, row, col)
            if val > 0:
                b_row = row + t.row
                b_col = col + t.col
                b = board_set_tile(b, b_row, b_col, val)

    return b


def tetromino_create() -> Tetromino:
    shape = randint(0, len(TETROMINOES) - 1)
    return Tetromino(shape, 0, 0, 0)


def tetromino_get_tile(t: Tetromino, row: int, col: int) -> int:
    data = TETROMINOES[t.shape]['data']
    size = TETROMINOES[t.shape]['size']

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


def rotate(t: Tetromino, b: Board) -> Tetromino:
    rotation = (t.rotation + 1) % 4
    tmp_t = t._replace(rotation=rotation)
    if tetromino_is_valid(tmp_t, b):
        return tmp_t
    return t


def move_left(t: Tetromino, b: Board) -> Tetromino:
    col = t.col - 1
    tmp_t = t._replace(col=col)
    if tetromino_is_valid(tmp_t, b):
        return tmp_t
    return t


def move_right(t: Tetromino, b: Board) -> Tetromino:
    col = t.col + 1
    tmp_t = t._replace(col=col)
    if tetromino_is_valid(tmp_t, b):
        return tmp_t
    return t


def move_down(b: Board, t: Tetromino) -> tuple[Board, Tetromino]:
    t = t._replace(row=t.row+1)

    if not tetromino_is_valid(t, b):
        t = t._replace(row=t.row-1)
        b = board_update(b, t)
        return b, tetromino_create()
    else:
        return b, t


def tetromino_is_valid(t: Tetromino, b: Board) -> bool:
    size = TETROMINOES[t.shape]['size']

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


def clear_rows(b: Board, rows: frozenset[int]) -> Board:
    tmp_tiles = []
    for row in reversed(range(BOARD_HEIGHT)):
        if row in rows:
            continue
        for col in reversed(range(BOARD_WIDTH)):
            tmp_tiles.append(board_get_tile(b, row, col))
    tmp_tiles.extend([0] * BOARD_WIDTH * len(rows))
    tmp_tiles.reverse()
    return Board(tmp_tiles)


def highlight_rows(b: Board, rows: frozenset[int]) -> Board:
    for row in rows:
        for col in range(BOARD_WIDTH):
            b = board_set_tile(b, row, col, 8)
    return b


def get_full_rows(b: Board) -> frozenset[int]:
    rows = set()
    for row in range(BOARD_HEIGHT):
        if is_row_full(b, row):
            rows.add(row)
    return frozenset(rows)


def is_row_full(b: Board, row: int) -> bool:
    for col in range(BOARD_WIDTH):
        if not board_get_tile(b, row, col):
            return False
    return True


def draw_board(screen: pygame.Surface, b: Board) -> None:
    for row in range(0, BOARD_HEIGHT):
        for col in range(0, BOARD_WIDTH):
            tile = board_get_tile(b, row, col)
            if tile > 0:
                draw_tile(screen, tile, row, col)


def draw_tetromino(screen: pygame.Surface, t: Tetromino) -> None:
    size = TETROMINOES[t.shape]['size']
    for row in range(0, size):
        for col in range(0, size):
            tile = tetromino_get_tile(t, row, col)
            if tile > 0:
                draw_tile(screen, tile, row + t.row, col + t.col)


def draw_tile(screen: pygame.Surface, tile: int, row: int, col: int) -> None:
    rect = pygame.Rect(
        col * GRID_SIZE, # x
        row * GRID_SIZE, # y
        GRID_SIZE,
        GRID_SIZE,
        )
    pygame.draw.rect(screen, COLORS[tile], rect)


if __name__ == '__main__':
    main()
