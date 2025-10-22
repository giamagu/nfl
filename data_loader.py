import os
from classes import *

class PlayDataLoader:
    def __init__(self, games_folder):
        self.games_folder = games_folder
        self.index = Game.list_game_play_ids(games_folder)

    def __len__(self):
        return len(self.index)

    def __getitem__(self, idx):
        game_id, play_id = self.index[idx]
        play = Play.load(os.path.join(self.games_folder, f"game_{game_id}"), play_id)
        return play.situations_before_throw, play.true_situations_after_throw

    def __iter__(self):
        for game_id, play_id in self.index:
            play = Play.load(os.path.join(self.games_folder, f"game_{game_id}"), play_id)
            yield play.situations_before_throw, play.true_situations_after_throw