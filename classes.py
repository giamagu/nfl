from typing import List
import time
import matplotlib.pyplot as plt

class Position:

    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = x
        self.y = y

class Player:

    players = {}

    def get_player(nfl_id: int, name: str = None, height: float = None, weight: float = None, birth_date: str = None, plays_involved_in: List[int] = []):
        if nfl_id in Player.players:
            return Player.players.get(nfl_id, None)
        else:
            player = Player(nfl_id, name, height, weight, birth_date, plays_involved_in)
            Player.players[nfl_id] = player
            return player

    def __init__(self, nfl_id: int, name: str, height: float, weight: float, birth_date: str, plays_involved_in: List[int] = []):
            
        self.nfl_id: int = nfl_id
        self.name: str = name
        self.height: float = height
        self.weight: float = weight
        self.birth_date: str = birth_date
        self.plays_involved_in: List[int] = plays_involved_in
        Player.players[nfl_id] = self

    def add_play(self, play_id: int):
        if play_id not in self.plays_involved_in:
            self.plays_involved_in.append(play_id)


class ActivePlayer():

    def __init__(self, player: Player, side: str, role: str, x: float, y: float, s:float,
                 a: float, dir: float, o: float, to_predict: bool):
        
        self.player: Player = player
        self.position: Position = Position(x, y)
        self.side: str = side
        self.role: str = role
        self.speed: float = s
        self.acc: float = a
        self.dir: float = dir
        self.o: float = o
        self.to_predict: bool = to_predict


class CurrentSituation:

    def __init__(self, game_id: int, play_id: int, defense: List[ActivePlayer], offense: List[ActivePlayer], input_file: str, ball_position: Position, ball_land: Position):

        self.game_id: int = game_id
        self.play_id: int = play_id
        self.defense: List[ActivePlayer] = defense
        self.offense: List[ActivePlayer] = offense
        self.input_file: str = input_file
        self.ball_position = ball_position
        self.ball_land = ball_land

    def show(self, ax=None, clear_ax=True, xlim=None, ylim=None):
        # Defense: blu, Offense: rosso, ball_position: verde, ball_land: croce nera
        if ax is None:
            fig, ax = plt.subplots(figsize=(12,6))
        if clear_ax:
            ax.clear()
        def_x = [p.position.x for p in self.defense]
        def_y = [p.position.y for p in self.defense]
        off_x = [p.position.x for p in self.offense]
        off_y = [p.position.y for p in self.offense]
        ax.scatter(def_x, def_y, c='blue', label='Defense', edgecolors='k', s=100, alpha=0.8)
        ax.scatter(off_x, off_y, c='red', label='Offense', edgecolors='k', s=100, alpha=0.8)
        if not self.ball_position is None:
            ax.scatter([self.ball_position.x], [self.ball_position.y], c='green', label='Ball position', s=150, edgecolors='k', marker='o')
        ax.scatter([self.ball_land.x], [self.ball_land.y], c='black', label='Ball land', s=200, marker='x', linewidths=3)
        ax.set_xlabel('Field X')
        if xlim:
            ax.set_xlim(xlim)
        if ylim:
            ax.set_ylim(ylim)
        ax.set_ylabel('Field Y')
        ax.set_title(f'CurrentSituation: Game {self.game_id}, Play {self.play_id}')
        ax.legend()
        ax.grid(True)
        plt.pause(0.001)


class CurrentSituationBeforeThrow(CurrentSituation):

    def __init__(self, game_id: int, play_id: int, defense: List[ActivePlayer], offense: List[ActivePlayer],
                    frames_until_throw: int, ball_position: Position, ball_land: Position, direction: float, 
                    yardline_number: int, input_file: str):
        
        super().__init__(game_id, play_id, defense, offense, input_file, ball_position, ball_land)
        
        self.frames_until_throw: int = frames_until_throw
        self.ball_position: Position = ball_position
        self.ball_land: Position = ball_land
        self.direction: float = direction
        self.yardline_number: int = yardline_number


class CurrentSituationAfterThrow(CurrentSituation):

    def __init__(self, game_id: int, play_id: int, defense: List[ActivePlayer], offense: List[ActivePlayer],
                 ball_position: Position, ball_land: Position, frames_after_throw: int, input_file: str):
        
        super().__init__(game_id, play_id, defense, offense, input_file, ball_position, ball_land)
        
        self.frames_after_throw: int = frames_after_throw


class Play:

    def __init__(self, game_id: int, id: int, direction: float, yardline_number: int,
                    situations_before_throw: List[CurrentSituation], true_situations_after_throw: List[CurrentSituation],
                    pred_situations_after_throw: List[CurrentSituation], n_frames_output: int,
                    ball_land: Position, input_file: str):
        
        self.game_id: int = game_id
        self.id: int = id
        self.direction: float = direction
        self.yardline_number: int = yardline_number
        self.situations_before_throw: List[CurrentSituation] = situations_before_throw
        self.true_situations_after_throw: List[CurrentSituation] = true_situations_after_throw
        self.pred_situations_after_throw: List[CurrentSituation] = pred_situations_after_throw
        self.n_frames_output: int = n_frames_output
        self.ball_land: Position = ball_land
        self.input_file: str = input_file

    def show_animation(self, sleep_time: float = 0.1, use_predicted: bool = False):
        plt.ion()
        fig, ax = plt.subplots(figsize=(12,6))
        # Calcola limiti da tutte le situazioni
        all_situations = self.situations_before_throw + (self.pred_situations_after_throw if use_predicted else self.true_situations_after_throw)
        all_x = []
        all_y = []
        for situation in all_situations:
            all_x += [p.position.x for p in situation.defense] + [p.position.x for p in situation.offense]
            all_y += [p.position.y for p in situation.defense] + [p.position.y for p in situation.offense]
            all_x.append(situation.ball_land.x)
            all_y.append(situation.ball_land.y)
        if all_x and all_y:
            x_margin = (max(all_x) - min(all_x)) * 0.05 if max(all_x) != min(all_x) else 1
            y_margin = (max(all_y) - min(all_y)) * 0.05 if max(all_y) != min(all_y) else 1
            xlim = (min(all_x) - x_margin, max(all_x) + x_margin)
            ylim = (min(all_y) - y_margin, max(all_y) + y_margin)
        else:
            xlim = None
            ylim = None
        # Mostra tutte le situazioni prima del lancio
        for situation in self.situations_before_throw:
            situation.show(ax=ax, clear_ax=True, xlim=xlim, ylim=ylim)
            plt.draw()
            plt.pause(sleep_time)
        # Mostra tutte le situazioni dopo il lancio (true o predette)
        situations = self.pred_situations_after_throw if use_predicted else self.true_situations_after_throw
        for situation in situations:
            situation.show(ax=ax, clear_ax=True, xlim=xlim, ylim=ylim)
            plt.draw()
            plt.pause(sleep_time)
        plt.ioff()
        plt.show()


class Game:

    def __init__(self, game_id: int, plays: List[Play], input_file: str):
        self.game_id: int = game_id
        self.plays: List[Play] = plays
        self.input_file: str = input_file
