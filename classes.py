from typing import List
import time
import matplotlib.pyplot as plt
import json
import os


class Position:

    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = x
        self.y = y

class Player:

    players = {}

    @staticmethod
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

    def to_dict(self):
        return {
            "nfl_id": self.nfl_id,
            "name": self.name,
            "height": self.height,
            "weight": self.weight,
            "birth_date": self.birth_date,
            "plays_involved_in": self.plays_involved_in
        }
    
    @staticmethod
    def from_dict(data):
        return Player.get_player(
            nfl_id=data["nfl_id"]
        )

    def save(self, file_path):
        """Salva il singolo Player in un file JSON."""
        with open(file_path, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    @staticmethod
    def load(file_path):
        """Carica un singolo Player da un file JSON."""
        with open(file_path, "r") as f:
            data = json.load(f)
            return Player.from_dict(data)

    @staticmethod
    def save_all(players, folder_path):
        """Salva tutti i Player in una cartella, ogni player in un file separato."""
        os.makedirs(folder_path, exist_ok=True)
        for player in players:
            file_path = os.path.join(folder_path, f"player_{player.nfl_id}.json")
            player.save(file_path)

    @staticmethod
    def load_all(folder_path):
        """Carica tutti i Player da una cartella."""
        players = []
        for file_name in os.listdir(folder_path):
            if file_name.startswith("player_") and file_name.endswith(".json"):
                file_path = os.path.join(folder_path, file_name)
                players.append(Player.load(file_path))
        return players
    
    @staticmethod
    def save_all_players(folder_path="train_players"):
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, "all_players.json")
        all_players = [player.to_dict() for player in Player.players.values()]
        with open(file_path, "w") as f:
            json.dump(all_players, f, indent=4)

    @staticmethod
    def load_all_players(folder_path="train_players"):
        file_path = os.path.join(folder_path, "all_players.json")
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                players_data = json.load(f)
            for data in players_data:
                Player.get_player(
                    nfl_id=data["nfl_id"],
                    name=data.get("name"),
                    height=data.get("height"),
                    weight=data.get("weight"),
                    birth_date=data.get("birth_date"),
                    plays_involved_in=data.get("plays_involved_in", [])
                )


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

    def to_dict(self):
        d = self.player.to_dict()
        d.pop("plays_involved_in", None)
        return {
            "player": d,
            "side": self.side,
            "role": self.role,
            "position": {"x": self.position.x, "y": self.position.y},
            "speed": self.speed,
            "acc": self.acc,
            "dir": self.dir,
            "o": self.o,
            "to_predict": self.to_predict
        }

    @staticmethod
    def from_dict(data):
        player = Player.from_dict(data["player"])
        pos = data["position"]
        return ActivePlayer(
            player=player,
            side=data["side"],
            role=data["role"],
            x=pos["x"],
            y=pos["y"],
            s=data["speed"],
            a=data["acc"],
            dir=data["dir"],
            o=data["o"],
            to_predict=data["to_predict"]
        )
    
    def save(self, file_path):
        """Salva il singolo ActivePlayer in un file JSON."""
        with open(file_path, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    @staticmethod
    def load(file_path):
        """Carica un singolo ActivePlayer da un file JSON."""
        with open(file_path, "r") as f:
            data = json.load(f)
            return ActivePlayer.from_dict(data)

    @staticmethod
    def save_all(active_players, folder_path):
        """Salva tutti gli ActivePlayer in una cartella, ogni oggetto in un file separato."""
        os.makedirs(folder_path, exist_ok=True)
        for i, ap in enumerate(active_players):
            file_path = os.path.join(folder_path, f"active_player_{i}.json")
            ap.save(file_path)

    @staticmethod
    def load_all(folder_path):
        """Carica tutti gli ActivePlayer da una cartella."""
        active_players = []
        for file_name in os.listdir(folder_path):
            if file_name.startswith("active_player_") and file_name.endswith(".json"):
                file_path = os.path.join(folder_path, file_name)
                active_players.append(ActivePlayer.load(file_path))
        return active_players


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

    def to_dict(self):
        return {
            "game_id": self.game_id,
            "play_id": self.play_id,
            "input_file": self.input_file,
            "ball_position": {"x": self.ball_position.x, "y": self.ball_position.y} if self.ball_position else None,
            "ball_land": {"x": self.ball_land.x, "y": self.ball_land.y} if self.ball_land else None
        }


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

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "frames_until_throw": self.frames_until_throw,
            "direction": self.direction,
            "yardline_number": self.yardline_number
        })
        return d

    @staticmethod
    def from_dict(data):
        base = CurrentSituation.from_dict(data)
        return CurrentSituationBeforeThrow(
            game_id=base.game_id,
            play_id=base.play_id,
            defense=base.defense,
            offense=base.offense,
            frames_until_throw=data["frames_until_throw"],
            ball_position=base.ball_position,
            ball_land=base.ball_land,
            direction=data["direction"],
            yardline_number=data["yardline_number"],
            input_file=base.input_file
        )
    
    def save(self, folder_path):
        """Salva la situazione in una cartella, con tutti i giocatori in un unico JSON."""
        os.makedirs(folder_path, exist_ok=True)
        # Salva i dati principali (eccetto defense/offense)
        situation_data = self.to_dict().copy()
        with open(os.path.join(folder_path, "situation.json"), "w") as f:
            json.dump(situation_data, f, indent=4)
        # Salva tutti i giocatori (defense + offense) in un unico file
        all_players = [p.to_dict() for p in self.defense + self.offense]
        with open(os.path.join(folder_path, "players.json"), "w") as f:
            json.dump(all_players, f, indent=4)

    @staticmethod
    def load(folder_path):
        """Carica la situazione da una cartella, con tutti i giocatori da un unico JSON."""
        with open(os.path.join(folder_path, "situation.json"), "r") as f:
            data = json.load(f)
        with open(os.path.join(folder_path, "players.json"), "r") as f:
            players_data = json.load(f)
        # Ricostruisci ActivePlayer da dict
        active_players = [ActivePlayer.from_dict(p) for p in players_data]
        # Suddividi tra defense e offense in base alla lunghezza originale
        defense = []
        offense = []
        for p in active_players:
            if p.side == "Defense":
                defense.append(p)
            else:
                offense.append(p)
        ball_position = Position(**data["ball_position"]) if data["ball_position"] else None
        ball_land = Position(**data["ball_land"]) if data["ball_land"] else None
        return CurrentSituationBeforeThrow(
            game_id=data["game_id"],
            play_id=data["play_id"],
            defense=defense,
            offense=offense,
            frames_until_throw=data["frames_until_throw"],
            ball_position=ball_position,
            ball_land=ball_land,
            direction=data["direction"],
            yardline_number=data["yardline_number"],
            input_file=data["input_file"]
        )

    @staticmethod
    def save_all(situations, folder_path):
        """Salva tutte le situazioni in una cartella, ogni situazione in una sottocartella."""
        os.makedirs(folder_path, exist_ok=True)
        for i, situation in enumerate(situations):
            situation_folder = os.path.join(folder_path, f"situation_{i}")
            situation.save(situation_folder)

    @staticmethod
    def load_all(folder_path):
        """Carica tutte le situazioni da una cartella."""
        situations = []
        dirs = os.listdir(folder_path)
        for i in range(len(dirs)):
            name = "situation_" + str(i)
            situation_folder = os.path.join(folder_path, name)
            if os.path.isdir(situation_folder):
                situations.append(CurrentSituationBeforeThrow.load(situation_folder))
        return situations


class CurrentSituationAfterThrow(CurrentSituation):

    def __init__(self, game_id: int, play_id: int, defense: List[ActivePlayer], offense: List[ActivePlayer],
                 ball_position: Position, ball_land: Position, frames_after_throw: int, input_file: str):
        
        super().__init__(game_id, play_id, defense, offense, input_file, ball_position, ball_land)
        
        self.frames_after_throw: int = frames_after_throw

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "frames_after_throw": self.frames_after_throw
        })
        return d

    @staticmethod
    def from_dict(data):
        base = CurrentSituation.from_dict(data)
        return CurrentSituationAfterThrow(
            game_id=base.game_id,
            play_id=base.play_id,
            defense=base.defense,
            offense=base.offense,
            ball_position=base.ball_position,
            ball_land=base.ball_land,
            frames_after_throw=data["frames_after_throw"],
            input_file=base.input_file
        )

    def save(self, folder_path):
        """Salva la situazione in una cartella, con tutti i giocatori (defense + offense) in un unico JSON."""
        os.makedirs(folder_path, exist_ok=True)
        # Salva i dati principali (eccetto defense/offense)
        situation_data = self.to_dict().copy()
        with open(os.path.join(folder_path, "situation.json"), "w") as f:
            json.dump(situation_data, f, indent=4)
        # Salva tutti i giocatori (defense + offense) in un unico file
        all_players = [p.to_dict() for p in self.defense + self.offense]
        with open(os.path.join(folder_path, "players.json"), "w") as f:
            json.dump(all_players, f, indent=4)

    @staticmethod
    def load(folder_path):
        """Carica la situazione da una cartella, con tutti i giocatori da un unico JSON."""
        with open(os.path.join(folder_path, "situation.json"), "r") as f:
            data = json.load(f)
        with open(os.path.join(folder_path, "players.json"), "r") as f:
            players_data = json.load(f)
        # Ricostruisci ActivePlayer da dict
        active_players = [ActivePlayer.from_dict(p) for p in players_data]
        # Suddividi tra defense e offense in base alla lunghezza originale
        defense = []
        offense = []
        for p in active_players:
            if p.side == "Defense":
                defense.append(p)
            else:
                offense.append(p)
        ball_position = Position(**data["ball_position"]) if data["ball_position"] else None
        ball_land = Position(**data["ball_land"]) if data["ball_land"] else None
        return CurrentSituationAfterThrow(
            game_id=data["game_id"],
            play_id=data["play_id"],
            defense=defense,
            offense=offense,
            ball_position=ball_position,
            ball_land=ball_land,
            frames_after_throw=data["frames_after_throw"],
            input_file=data["input_file"]
        )

    @staticmethod
    def save_all(situations, folder_path):
        """Salva tutte le situazioni in una cartella, ogni situazione in una sottocartella."""
        os.makedirs(folder_path, exist_ok=True)
        for i, situation in enumerate(situations):
            situation_folder = os.path.join(folder_path, f"situation_{i}")
            situation.save(situation_folder)

    @staticmethod
    def load_all(folder_path):
        """Carica tutte le situazioni da una cartella."""
        situations = []
        dirs = os.listdir(folder_path)
        for i in range(len(dirs)):
            name = "situation_" + str(i)
            situation_folder = os.path.join(folder_path, name)
            if os.path.isdir(situation_folder):
                situations.append(CurrentSituationAfterThrow.load(situation_folder))
        return situations


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

    def to_dict(self):
        return {
            "game_id": self.game_id,
            "id": self.id,
            "direction": self.direction,
            "yardline_number": self.yardline_number,
            "n_frames_output": self.n_frames_output,
            "ball_land": {"x": self.ball_land.x, "y": self.ball_land.y} if self.ball_land else None,
            "input_file": self.input_file
        }

    @staticmethod
    def from_dict(data):
        ball_land = Position(**data["ball_land"]) if data["ball_land"] else None
        return Play(
            game_id=data["game_id"],
            id=data["id"],
            direction=data["direction"],
            yardline_number=data["yardline_number"],
            situations_before_throw=[],  # verranno caricati dopo
            true_situations_after_throw=[],
            pred_situations_after_throw=[],
            n_frames_output=data["n_frames_output"],
            ball_land=ball_land,
            input_file=data["input_file"]
        )

    def save(self, folder_path):
        play_folder = os.path.join(folder_path, f"play_{self.id}")
        os.makedirs(play_folder, exist_ok=True)
        # Salva i dati principali della play
        with open(os.path.join(play_folder, "play.json"), "w") as f:
            json.dump(self.to_dict(), f, indent=4)
        # Salva le situations
        CurrentSituationBeforeThrow.save_all(self.situations_before_throw, os.path.join(play_folder, "situations_before"))
        CurrentSituationAfterThrow.save_all(self.true_situations_after_throw, os.path.join(play_folder, "situations_true_after"))
        CurrentSituationAfterThrow.save_all(self.pred_situations_after_throw, os.path.join(play_folder, "situations_pred_after"))

    @staticmethod
    def load(folder_path, play_id):
        play_folder = os.path.join(folder_path, f"play_{play_id}")
        with open(os.path.join(play_folder, "play.json"), "r") as f:
            data = json.load(f)
        play = Play.from_dict(data)
        play.situations_before_throw = CurrentSituationBeforeThrow.load_all(os.path.join(play_folder, "situations_before"))
        play.true_situations_after_throw = CurrentSituationAfterThrow.load_all(os.path.join(play_folder, "situations_true_after"))
        play.pred_situations_after_throw = CurrentSituationAfterThrow.load_all(os.path.join(play_folder, "situations_pred_after"))
        return play

    @staticmethod
    def save_all(plays, folder_path):
        for play in plays:
            play.save(folder_path)

    @staticmethod
    def load_all(folder_path):
        plays = []
        for name in os.listdir(folder_path):
            if name.startswith("play_") and os.path.isdir(os.path.join(folder_path, name)):
                play_id = int(name.split("_")[1])
                plays.append(Play.load(folder_path, play_id))
        return plays
    

class Game:

    def __init__(self, game_id: int, plays: List[Play], input_file: str):
        self.game_id: int = game_id
        self.plays: List[Play] = plays
        self.input_file: str = input_file

    def to_dict(self):
        return {
            "game_id": self.game_id,
            "input_file": self.input_file
        }

    @staticmethod
    def from_dict(data):
        return Game(
            game_id=data["game_id"],
            plays=[],  # verranno caricati dopo
            input_file=data["input_file"]
        )

    def save(self, folder_path):
        game_folder = os.path.join(folder_path, f"game_{self.game_id}")
        os.makedirs(game_folder, exist_ok=True)
        # Salva i dati principali della partita
        with open(os.path.join(game_folder, "game.json"), "w") as f:
            json.dump(self.to_dict(), f, indent=4)
        # Salva tutte le Play
        Play.save_all(self.plays, game_folder)

    @staticmethod
    def load(folder_path, game_id):
        game_folder = os.path.join(folder_path, f"game_{game_id}")
        with open(os.path.join(game_folder, "game.json"), "r") as f:
            data = json.load(f)
        game = Game.from_dict(data)
        game.plays = Play.load_all(game_folder)
        return game

    @staticmethod
    def save_all(games, folder_path):
        for game in games:
            game.save(folder_path)

    @staticmethod
    def load_all(folder_path):
        games = []
        for name in os.listdir(folder_path):
            if name.startswith("game_") and os.path.isdir(os.path.join(folder_path, name)):
                game_id = int(name.split("_")[1])
                games.append(Game.load(folder_path, game_id))
        return games

    @staticmethod
    def list_game_play_ids(games_folder):
        index = []
        for name in os.listdir(games_folder):
            if name.startswith("game_") and os.path.isdir(os.path.join(games_folder, name)):
                game_id = int(name.split("_")[1])
                game_folder = os.path.join(games_folder, name)
                for play_name in os.listdir(game_folder):
                    if play_name.startswith("play_") and os.path.isdir(os.path.join(game_folder, play_name)):
                        play_id = int(play_name.split("_")[1])
                        index.append((game_id, play_id))
        return index


# Funzioni per salvare/caricare tutti i player
def save_players(players, file_path):
    Player.save_all(players, file_path)

def load_players(file_path):
    return Player.load_all(file_path)