from main import reset_game
import pytest


def test_reset_game():
    assert reset_game() == 0
