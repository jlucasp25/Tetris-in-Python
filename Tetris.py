import sys
import time
from random import randint
from typing import List, Optional

import pygame
from pygame import Surface, mixer, QUIT, KEYDOWN, K_ESCAPE, K_LEFT, K_s, K_RIGHT, Rect

from Tetromino import Tetromino
from globals import GAME_COLORS, SQUARE_SIZE, MUSIC_FILENAME, TETROMINO_COLORS, MAX_X_AXIS, MAX_Y_AXIS


class Tetris:
    """
    Singleton that represents the game itself.
    :arg window (Window/Surface object of the game)
    :arg spawn_piece (Should a piece be spawned?)
    :arg pieces (Pieces currently in the game)
    :arg can_move (Controls the event handler to stop the user from making invalid inputs)
    """
    window: Surface = None
    should_spawn_piece: bool = True
    pieces: List[Tetromino] = []
    current_piece: Optional[Tetromino] = None
    can_move = True

    def __init__(self, window: Surface):
        self.window = window
        mixer.music.load(MUSIC_FILENAME)
        mixer.music.play()

    def start_game_loop(self):
        """
        Executes the main game loop.
        """
        self._clear_window()
        while True:
            self._handle_player_events()
            if self.should_spawn_piece:
                # Generate a new piece on top of the window in the center of the X axis.
                self._spawn_piece()
            # Draw all the game pieces
            self._draw_pieces()
            # if the current piece has hit the bottom => spawn new piece
            # OR the current piece has hit another piece => spawn new piece
            if self.current_piece.check_bottom_collision() or self.check_ingame_pieces_collision():
                self.should_spawn_piece = True
                self._check_filled_lines()
            else:
                # Drop the current piece
                self._drop_current_piece()
            # Wait
            time.sleep(1)
            # Disable last frame
            self._clear_window()
            self.can_move_piece = True

    def check_ingame_pieces_collision(self):
        """
        Checks if the current piece is colliding with any of the drawn pieces on the window.
        """
        collisions: List[Optional[bool]] = []
        # Obtain the current piece rects
        current_piece_rects = self.current_piece.sprite
        # For each piece ingame
        for piece in self.pieces:
            # if it isnt the current playable piece...
            if piece != self.current_piece:
                # Get the current piece as rects
                piece_rects = piece.sprite
                # For rect in the current piece
                for rect in piece_rects:
                    # for rect in current game piece rects
                    for current_rect in current_piece_rects:
                        collisions.append(self._check_rect_collision(current_rect, rect))
        return any(collisions)

    def _check_rect_collision(self, pivot_rect: Rect, other_rect: Rect):
        """
        Given two Rect objects, checks for collision between them.
        :param pivot_rect: Current rect
        :param other_rect: Target rect to evaluate against
        :return: True if they collide.
        """
        if pivot_rect.bottom == other_rect.top:  # same Y
            if pivot_rect.left == other_rect.left:  # Same X
                return True
        return False

    def _check_filled_lines(self):
        """
        Checks if there is any filled lines.
        :return:
        """
        pass

    def _clear_window(self):
        """
        Clears the game window (Surface).
        :return:
        """
        self.window.fill(GAME_COLORS["BLACK"])

    def _drop_current_piece(self):
        """
        Drops the current piece.
        """
        self._drop_piece(piece=self.current_piece)

    def _drop_piece(self, piece: Tetromino):
        """
        Drops piece by a SQUARE_SIZE value.
        """
        piece.set_position(left=piece.left, top=piece.top + SQUARE_SIZE)
        # Rebuild sprite
        piece.build_sprite()

    def _spawn_piece(self):
        """
        Generates a Tetromino object, adds it to the game and stops more pieces from spawning.
        """
        # Convert dict to list
        available_colors = list(TETROMINO_COLORS.values())
        # Generate random index to choose colors
        color_idx = randint(0, len(available_colors) - 1)
        self.current_piece = Tetromino(top=0, left=MAX_X_AXIS / 3, color=available_colors[color_idx])
        self.pieces.append(self.current_piece)
        self.should_spawn_piece = False

    def _draw_piece(self, piece: Tetromino):
        """
        Given a Tetromino object, draw it on the pygame window.
        :arg piece Tetromino Object
        """
        # For every rect, draw it on the window with the piece color.
        for rect in piece.sprite:
            rect_kwargs = {
                'surface': self.window,
                'color': piece.color,
                'rect': rect
            }
            pygame.draw.rect(**rect_kwargs)  # Draw Rectangle

    def _draw_pieces(self):
        """
        Draws all the game window pieces.
        """
        for piece in self.pieces:
            self._draw_piece(piece=piece)
        pygame.display.flip()  # Update the game surface

    def _handle_player_events(self):
        """
        Handles user keyboard events.
        """

        for event in pygame.event.get():
            # if the event is to quit or press Esc
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                sys.exit(0)
            elif event.type == KEYDOWN:
                if self.can_move_piece:
                    key = event.key
                    if key == K_LEFT:
                        self.current_piece.move_left()
                    elif key == K_RIGHT:
                        self.current_piece.move_right()
                    elif key == K_s:
                        time.sleep(10)
                    self.can_move_piece = False
