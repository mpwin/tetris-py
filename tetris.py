import copy

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


def main():
    pygame.init()
    screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

    game = Game()
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
                if event.key == pygame.K_LEFT:
                    input.add('left')
                if event.key == pygame.K_RIGHT:
                    input.add('right')

        game.update(input)
        screen.fill((0, 0, 0))
        draw_tetromino(screen, game.tetromino)
        pygame.display.flip()

    pygame.quit()


class Game:

    def __init__(self):
        self.board = [0] * BOARD_WIDTH * BOARD_HEIGHT
        self.tetromino = Tetromino(TETROMINOES[0])

    def board_get(self, row, col):
        return self.board[row * BOARD_WIDTH + col]

    def update(self, input):
        tetromino = copy.deepcopy(self.tetromino)

        if 'up' in input:
            tetromino.rotation = (self.tetromino.rotation + 1) % 4
        if 'left' in input:
            tetromino.col -= 1
        if 'right' in input:
            tetromino.col += 1

        if tetromino.valid():
            self.tetromino = tetromino


class Tetromino:

    def __init__(self, tetromino):
        self.data = tetromino['data']
        self.size = tetromino['size']
        self.row = 0
        self.col = 0
        self.rotation = 0

    def get(self, row: int, col: int) -> int:
        match self.rotation:
            case 0:
                return self.data[
                    row *
                    self.size + col
                    ]
            case 1:
                return self.data[
                    (self.size - col - 1) *
                    self.size + row
                    ]
            case 2:
                return self.data[
                    (self.size - row - 1) *
                    self.size + (self.size - col - 1)
                    ]
            case 3:
                return self.data[
                    col *
                    self.size + (self.size - row - 1)
                    ]

    def valid(self):
        for row in range(0, self.size):
            for col in range(0, self.size):
                value = self.get(row, col)
                if value > 0:
                    board_row = row + self.row
                    board_col = col + self.col

                    if board_col < 0:
                        return False
                    if board_col >= BOARD_WIDTH:
                        return False

        return True


def draw_rect(screen, x: int, y: int, w: int, h: int):
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, (255, 255, 255), rect)


def draw_tetromino(screen, tetromino: Tetromino):
    for row in range(0, tetromino.size):
        for col in range(0, tetromino.size):
            value = tetromino.get(row, col)
            if value > 0:
                draw_rect(
                    screen,
                    (col + tetromino.col) * GRID_SIZE,
                    (row + tetromino.row) * GRID_SIZE,
                    GRID_SIZE,
                    GRID_SIZE,
                    )


if __name__ == '__main__':
    main()
