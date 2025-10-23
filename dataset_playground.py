import os
import random
from classes import *
from data_loader import PlayDataLoader
import polars as pl

# Carica 20 azioni di esempio usando PlayDataLoader
loader = PlayDataLoader("train_games")
examples = [loader[i] for i in range(500)]  # Ogni elemento è (situations_before_throw, situations_after_throw)

diffs_before = []
diffs_after = []
diffs_mean = []

for situations_before, _ in examples:
    # situations_before è una lista di CurrentSituationBeforeThrow ordinata per frame
    for idx in range(1, len(situations_before) - 1):
        prev_sit = situations_before[idx - 1]
        curr_sit = situations_before[idx]
        next_sit = situations_before[idx + 1]
        # Tutti i player (offense + defense) nel frame corrente
        all_players = curr_sit.offense + curr_sit.defense
        for player in all_players:
            # Cerca lo stesso player nei frame precedente e successivo
            prev_player = next((p for p in prev_sit.offense + prev_sit.defense if p.player.nfl_id == player.player.nfl_id), None)
            next_player = next((p for p in next_sit.offense + next_sit.defense if p.player.nfl_id == player.player.nfl_id), None)
            if prev_player and next_player:
                # Calcola il vettore velocità per prev e next
                v_prev = prev_player.get_speed_vector()
                v_next = next_player.get_speed_vector()
                delta_v = v_next - v_prev
                delta_v_mod = np.linalg.norm(delta_v)
                # Accelerazione stimata (prima, dopo, media)
                acc_prev = prev_player.acc / 10 * 2.08 + 0.14
                acc_next = next_player.acc / 10 * 2.08 + 0.14
                acc_mean = ((prev_player.acc + next_player.acc) / 2) / 10 * 2.08 + 0.14
                # Differenze
                dif_before = delta_v_mod - acc_prev
                dif_after = delta_v_mod - acc_next
                dif_mean = delta_v_mod - acc_mean
                diffs_before.append(dif_before)
                diffs_after.append(dif_after)
                diffs_mean.append(dif_mean)

def stats(arr):
    arr = np.array(arr)
    return arr.mean(), arr.var()

mean_before, var_before = stats(diffs_before)
mean_after, var_after = stats(diffs_after)
mean_mean, var_mean = stats(diffs_mean)

a = 1