from typing import List

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

    def __init__(self, game_id: int, play_id: int, defense: List[Player], offense: List[Player],
                    frames_until_throw: int, frames_after_throw: int, is_before_throw: bool, direction: float, 
                    yardline_number: int, input_file: str):
        
        if frames_until_throw > 0 and frames_after_throw > 0:
            raise ValueError("Only one of frames_until_throw or frames_after_throw should be greater than zero.")
        
        if frames_until_throw > 0 and not is_before_throw:
            raise ValueError("If frames_until_throw is greater than zero, is_before_throw must be True.")
        
        if frames_after_throw > 0 and is_before_throw:
            raise ValueError("If frames_after_throw is greater than zero, is_before_throw must be False.")
        
        self.game_id: int = game_id
        self.play_id: int = play_id
        self.defense: List[Player] = defense
        self.offense: List[Player] = offense
        self.frames_until_throw: int = frames_until_throw
        self.frames_after_throw: int = frames_after_throw
        self.is_before_throw: bool = is_before_throw
        self.direction: float = direction
        self.yardline_number: int = yardline_number
        self.input_file: str = input_file


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


class Game:

    def __init__(self, game_id: int, plays: List[Play], input_file: str):
        self.game_id: int = game_id
        self.plays: List[Play] = plays
        self.input_file: str = input_file
