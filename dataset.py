import polars as pl
from pathlib import Path
from classes import *

def create_situation_before_throw_from_players(player_frames, play_id, frames_until_throw):

    ball_position = None
    defense = []
    offense = []
    for i in range(len(player_frames)):
        player: Player = Player.get_player(nfl_id = player_frames["nfl_id"][i],
                                    name = player_frames["player_name"][i],
                                    height = player_frames["player_height"][i],
                                    weight = player_frames["player_weight"][i],
                                    birth_date = player_frames["player_birth_date"][i])
        player.add_play(play_id)
        active_player = ActivePlayer(player=player,
                                    side=player_frames["player_side"][i],
                                    role=player_frames["player_role"][i],
                                    x=player_frames["x"][i],
                                    y=player_frames["y"][i],
                                    s=player_frames["s"][i],
                                    a=player_frames["a"][i],
                                    dir=player_frames["dir"][i],
                                    o=player_frames["o"][i],
                                    to_predict=player_frames["player_to_predict"][i])

        
        if active_player.side == "Defense":
            defense.append(active_player)
        else:
            offense.append(active_player)

        if player_frames["player_role"][i] == "Passer":
            ball_position = Position(player_frames["x"][i], player_frames["y"][i])

    ball_land = Position(player_frames["ball_land_x"][i], player_frames["ball_land_y"][i])
    
    situation = CurrentSituationBeforeThrow(
        game_id, play_id, defense, offense, frames_until_throw=frames_until_throw,
        direction=player_frames["play_direction"][i],
        ball_land=ball_land,ball_position=ball_position,
        yardline_number=player_frames["absolute_yardline_number"][i], input_file=game_id_to_file[game_id]
    )

    return situation, ball_land

def create_situation_after_throw_from_players(player_frames, play_id, frames_after_throw,
                                              ball_position, ball_land, defense, offense, sides, roles):
    defense = []
    offense = []
    for i in range(len(player_frames)):
        player: Player = Player.get_player(nfl_id = player_frames["nfl_id"][i])
        player.add_play(play_id)
        active_player = ActivePlayer(player=player,
                                        side=sides[player_frames["nfl_id"][i]],
                                        role=roles[player_frames["nfl_id"][i]],
                                        x=player_frames["x"][i],
                                        y=player_frames["y"][i],
                                        s=None,
                                        a=None,
                                        dir=None,
                                        o=None,
                                        to_predict=True)
        
        if active_player.side in defense:
            defense.append(active_player)
        else:
            offense.append(active_player)
        
    situation = CurrentSituationAfterThrow(
        game_id, play_id, defense, offense,
        ball_position, ball_land,
        frames_after_throw, game_id_to_file[game_id]
    )

    return situation

# Percorso della cartella contenente i file
data_folder = Path("raw_data/train")

# Lista di file input e output
input_files = sorted(data_folder.glob("input_2023_w*.csv"))
output_files = sorted(data_folder.glob("output_2023_w*.csv"))

# Leggi e concatena tutti i file input
input_dfs = [pl.read_csv(file) for file in input_files]
input_data = pl.concat(input_dfs)

# Crea un dizionario per associare game_id al nome del file di input
game_id_to_file = {}

# Itera su ogni file CSV
for file in input_files:
    # Leggi il file CSV con Polars
    df = pl.read_csv(file)
    
    # Estrai i valori unici della colonna game_id
    unique_game_ids = df["game_id"].unique().to_list()
    
    # Aggiungi ogni game_id al dizionario con il nome del file
    for game_id in unique_game_ids:
        game_id_to_file[game_id] = file.name

# Leggi e concatena tutti i file output
output_dfs = [pl.read_csv(file) for file in output_files]
output_data = pl.concat(output_dfs)

# Estrai tutti gli ID delle partite
game_ids = input_data["game_id"].unique().to_list()

# Lista di tutte le partite
games = []

# Cicla su ogni partita
for game_id in game_ids:
    # Filtra i dati per la partita corrente
    game_input_data = input_data.filter(pl.col("game_id") == game_id)
    game_output_data = output_data.filter(pl.col("game_id") == game_id)
    
    # Estrai tutti gli ID delle azioni (play_id)
    play_ids = game_input_data["play_id"].unique().to_list()
    
    # Lista delle azioni per questa partita
    plays = []
    
    # Cicla su ogni azione
    for play_id in play_ids:
        # Filtra i dati per l'azione corrente
        play_input_data = game_input_data.filter(pl.col("play_id") == play_id)
        play_output_data = game_output_data.filter(pl.col("play_id") == play_id)
        
        # Estrai i frame di input e output
        input_frame_ids = play_input_data["frame_id"].unique().to_list()
        output_frame_ids = play_output_data["frame_id"].unique().to_list()
        
        # Liste per le situazioni di gioco
        situations_before_throw = []
        true_situations_after_throw = []
        
        # Cicla sui frame di input (prima del throw)
        frames_before_throw = len(input_frame_ids) - 1
        for frame in input_frame_ids:
            frame_input_data = play_input_data.filter(pl.col("frame_id") == frame)
            situation, ball_land = create_situation_before_throw_from_players(frame_input_data, play_id, frames_before_throw)
            situations_before_throw.append(situation)
            frames_before_throw -+ 1

        sides = {}
        roles = {}
        for i in range(len(frame_input_data)):
            sides[frame_input_data["nfl_id"][i]] = frame_input_data["player_side"][i]
            roles[frame_input_data["nfl_id"][i]] = frame_input_data["player_role"][i]
        
        # Cicla sui frame di input (prima del throw)
        defense = situations_before_throw[-1].defense
        offense = situations_before_throw[-1].offense
        frames_after_throw = 0
        for frame in output_frame_ids:
            frames_after_throw += 1
            frame_output_data = play_output_data.filter(pl.col("frame_id") == frame)
            situation = create_situation_after_throw_from_players(frame_output_data, play_id, frames_after_throw,
                                                                  None, ball_land, defense, offense, sides, roles)
            true_situations_after_throw.append(situation)
        
        # Crea la Play
        play = Play(
            game_id, play_id, direction=play_input_data[0]["play_direction"],
            yardline_number=play_input_data[0]["absolute_yardline_number"],
            situations_before_throw=situations_before_throw,
            true_situations_after_throw=true_situations_after_throw,
            pred_situations_after_throw=[], n_frames_output=play_input_data[0]["num_frames_output"],
            ball_land=Position(play_input_data[0]["ball_land_x"], play_input_data[0]["ball_land_y"]),
            input_file=game_id_to_file[game_id],
        )
        plays.append(play)
        play.show_animation()
    
    # Crea la partita
    game = Game(game_id, plays=plays, input_file=game_id_to_file[game_id])
    games.append(game)

a = 1