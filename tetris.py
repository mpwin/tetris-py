from collections import namedtuple

import pygame


BOARD_WIDTH = 10
BOARD_HEIGHT = 20
GRID_SIZE = 40

SCREEN_WIDTH = BOARD_WIDTH * GRID_SIZE
SCREEN_HEIGHT = BOARD_HEIGHT * GRID_SIZE

TETROMINO_I = [
    0, 0, 0, 0,
    1, 1, 1, 1,
    0, 0, 0, 0,
    0, 0, 0, 0,
    ]
TETROMINO_J = [
    2, 0, 0,
    2, 2, 2,
    0, 0, 0,
    ]
TETROMINO_L = [
    0, 0, 3,
    3, 3, 3,
    0, 0, 0,
    ]
TETROMINO_O = [
    4, 4,
    4, 4,
    ]
TETROMINO_S = [
    0, 5, 5,
    5, 5, 0,
    0, 0, 0,
    ]
TETROMINO_T = [
    0, 6, 0,
    6, 6, 6,
    0, 0, 0,
    ]
TETROMINO_Z = [
    7, 7, 0,
    0, 7, 7,
    0, 0, 0,
    ]

TETROMINOES = [
    dict(data=TETROMINO_I, size=4),
    dict(data=TETROMINO_J, size=3),
    dict(data=TETROMINO_L, size=3),
    dict(data=TETROMINO_O, size=2),
    dict(data=TETROMINO_S, size=3),
    dict(data=TETROMINO_T, size=3),
    dict(data=TETROMINO_Z, size=3),
]


Board = namedtuple('Board', ['board'])
Tetromino = namedtuple('Tetromino', ['index', 'row', 'col', 'rotation'])


def main():
    pygame.init()
    screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

    board = Board([0] * BOARD_WIDTH * BOARD_HEIGHT)
    tetromino = Tetromino(0, 0, 0, 0)
    running = True

    while running:
        input = set()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_UP:
                    input.add('up')
                if event.key == pygame.K_DOWN:
                    input.add('down')
                if event.key == pygame.K_LEFT:
                    input.add('left')
                if event.key == pygame.K_RIGHT:
                    input.add('right')

        board, tetromino = update(board, tetromino, input)

        screen.fill((0, 0, 0))
        draw_board(screen, board)
        draw_tetromino(screen, tetromino)
        pygame.display.flip()

    pygame.quit()


def update(board, tetromino, input):
    u_tetromino = tetromino

    if 'up' in input:
        rotation = (tetromino.rotation + 1) % 4
        u_tetromino = u_tetromino._replace(rotation=rotation)
    if 'left' in input:
        col = tetromino.col - 1
        u_tetromino = u_tetromino._replace(col=col)
    if 'right' in input:
        col = tetromino.col + 1
        u_tetromino = u_tetromino._replace(col=col)

    if tetromino_valid(u_tetromino, board):
        tetromino = u_tetromino

    if 'down' in input:
        board, tetromino = tetromino_drop(tetromino, board)

    return board, tetromino


def board_get_tile(b: Board, row: int, col: int) -> int:
    return b.board[row * BOARD_WIDTH + col]


def board_set_tile(b: Board, row: int, col: int, val: int) -> Board:
    board = list(b.board)
    board[row * BOARD_WIDTH + col] = val
    return Board(board)


def board_update(b: Board, t: Tetromino) -> Board:
    data = TETROMINOES[t.index]['data']
    size = TETROMINOES[t.index]['size']

    for row in range(0, size):
        for col in range(0, size):
            val = tetromino_get(data, size, row, col, t.rotation)
            if val > 0:
                b_row = row + t.row
                b_col = col + t.col
                b = board_set_tile(b, b_row, b_col, val)

    return b


def tetromino_drop(tetromino, board):
    tetromino_down = tetromino._replace(row=tetromino.row+1)

    if not tetromino_valid(tetromino_down, board):
        board = board_update(board, tetromino)
        Tetromino = namedtuple('Tetromino', ['index', 'row', 'col', 'rotation'])
        return board, Tetromino(0, 0, 0, 0)

    return board, tetromino_down


def tetromino_get(data, size, row, col, rotation):
    match rotation:
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


def tetromino_valid(tetromino, board):
    data = TETROMINOES[tetromino.index]['data']
    size = TETROMINOES[tetromino.index]['size']

    for row in range(0, size):
        for col in range(0, size):
            value = tetromino_get(data, size, row, col, tetromino.rotation)
            if value > 0:
                board_row = row + tetromino.row
                board_col = col + tetromino.col

                if board_row >= BOARD_HEIGHT:
                    return False
                if board_col < 0:
                    return False
                if board_col >= BOARD_WIDTH:
                    return False

    return True


def draw_board(screen, board):
    for row in range(0, BOARD_HEIGHT):
        for col in range(0, BOARD_WIDTH):
            value = board_get_tile(board, row, col)
            if value > 0:
                draw_rect(
                    screen,
                    col * GRID_SIZE,
                    row * GRID_SIZE,
                    GRID_SIZE,
                    GRID_SIZE,
                    )


def draw_tetromino(screen, tetromino):
    data = TETROMINOES[tetromino.index]['data']
    size = TETROMINOES[tetromino.index]['size']

    for row in range(0, size):
        for col in range(0, size):
            value = tetromino_get(data, size, row, col, tetromino.rotation)
            if value > 0:
                draw_rect(
                    screen,
                    (col + tetromino.col) * GRID_SIZE,
                    (row + tetromino.row) * GRID_SIZE,
                    GRID_SIZE,
                    GRID_SIZE,
                    )


def draw_rect(screen, x: int, y: int, w: int, h: int):
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, (255, 255, 255), rect)


if __name__ == '__main__':
    main()
