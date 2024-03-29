from db import connect

from constants.ten_mm_constants import TENMM_CHARACTERS
from formulas import time_to_frames, frames_to_time_string

def get_current_10mm_wr(char, is_TAS):
    conn = connect()
    sql_q = f'SELECT * FROM ten_mm_table WHERE character=\'{char}\' AND tas={is_TAS} ORDER BY score ASC, date ASC;'
    cur = conn.cursor()
    cur.execute(sql_q)

    players = []
    cur_10mm_wr_score = 9999
    video = None

    for record in cur:
        if record[2] > cur_10mm_wr_score :
            break
        players.append(record[1])
        score = record[2]
        if len(record[3]) != 0:
            video = record[3][0]
        else:
            video = None

        cur_10mm_wr_score = score
        cur_10mm_wr = record
    
    players_string = ', '.join(players)
    


    return (cur_10mm_wr_score, players_string, video) # should return dict or something




def get_10mm_total(is_TAS):
    total_high_score_f = 0

    for char in TENMM_CHARACTERS:
        current_10mm_wr = get_current_10mm_wr(char, is_TAS)
        score = current_10mm_wr[0]
        total_high_score_f += int(time_to_frames(float(score)))

    total_high_score_time = frames_to_time_string(total_high_score_f)

    return total_high_score_time


def ten_mm_history_sort(cur_handle):
    description_lines = []
    prev_score = 999

    for record in cur_handle:
        sources = record[3]
        if len(sources) != 0:
            video = sources[0] 
        else:
            video = None
        tied_player = None
        player = record[1]
        score = record[2]
        if score >= prev_score:
            continue
        prev_score = score
        # TODO: compare date and add to history if record was beaten in the same day AND does not have timestamp
        # maybe can check YT source of video
        date = record[4].date()
        if video == None:
            description_lines.append(
                f'({date}) - {score} - {player}'
            )
        else:
            description_lines.append(
                f'({date}) - [{score}]({video}) - {player}'
            )




    return description_lines