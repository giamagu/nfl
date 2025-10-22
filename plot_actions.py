import polars as pl
from pathlib import Path
from classes import *    

game_id = "2023090700"
game = Game.load("train_games", game_id)
for play in game.plays:
    play.show_animation()
    a = 1
    #chiudi immagine per proseguire