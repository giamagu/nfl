import os
import random
from classes import *
from data_loader import PlayDataLoader

def test_dataset_integrity(games_folder, input_csv_folder, output_csv_folder, n_tests=20):
    from classes import PlayDataLoader
    import polars as pl
    loader = PlayDataLoader(games_folder)
    # Prendi n_tests situation random
    for _ in range(n_tests):
        idx = random.randint(0, len(loader)-1)
        train, test = loader[idx]
        # Scegli random una situation (prima o dopo il throw)
        situations = train if random.random() < 0.5 else test
        if not situations:
            continue
        situation = random.choice(situations)
        # Scegli un player random
        all_players = situation.defense + situation.offense
        if not all_players:
            continue
        player = random.choice(all_players)
        nfl_id = player.player.nfl_id
        # Prendi il file csv originale
        input_file = situation.input_file
        if hasattr(situation, 'frames_until_throw'):
            # situation before throw
            csv_path = os.path.join(input_csv_folder, input_file)
            df = pl.read_csv(csv_path)
        else:
            # situation after throw
            csv_path = os.path.join(output_csv_folder, input_file.replace('input', 'output'))
            df = pl.read_csv(csv_path)
        # Cerca la riga corrispondente
        row = df.filter(pl.col('nfl_id') == nfl_id)
        if row.height == 0:
            print(f"Player {nfl_id} not found in {csv_path}")
            continue
        # Confronta alcune colonne
        x_ok = abs(row['x'][0] - player.position.x) < 1e-4
        y_ok = abs(row['y'][0] - player.position.y) < 1e-4
        print(f"Test: game_id={situation.game_id}, play_id={situation.play_id}, nfl_id={nfl_id}, x_ok={x_ok}, y_ok={y_ok}")
        assert x_ok and y_ok, f"Mismatch for player {nfl_id} in {csv_path}"
    print("Test completato!")

def test_player_consistency(games_folder, nfl_id):
    from classes import PlayDataLoader, Player
    loader = PlayDataLoader(games_folder)
    player_obj = Player.players.get(nfl_id, None)
    if player_obj is None:
        print(f"Player {nfl_id} non trovato nel dataset!")
        return
    print(f"Testing player {nfl_id}: {player_obj.name}, height={player_obj.height}, weight={player_obj.weight}, birth_date={player_obj.birth_date}")
    for idx in range(len(loader)):
        train, test = loader[idx]
        for situations in [train, test]:
            for situation in situations:
                all_players = situation.defense + situation.offense
                for p in all_players:
                    if p.player.nfl_id == nfl_id:
                        # Controlla che le caratteristiche siano sempre uguali
                        assert p.player.height == player_obj.height, f"Height mismatch in play {situation.play_id}"
                        assert p.player.weight == player_obj.weight, f"Weight mismatch in play {situation.play_id}"
                        assert p.player.birth_date == player_obj.birth_date, f"Birth date mismatch in play {situation.play_id}"
                        assert p.player.name == player_obj.name, f"Name mismatch in play {situation.play_id}"
    print("Test completato: tutte le caratteristiche sono coerenti!")