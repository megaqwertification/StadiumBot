from db import connect
from formulas import m_to_ft
from constants.hrc_constants import HRC_CHARACTERS

def get_current_hrc_wr(char, is_TAS):
    # TODO: add tags_list parameter
    conn = connect()
    sql_q = f'SELECT * FROM hrc_table WHERE character=\'{char}\' AND tas={is_TAS} ORDER BY score_ft DESC, date ASC;'
    cur = conn.cursor()
    cur.execute(sql_q)

    players = []
    curr_score_ft = 0
    video = None

    for record in cur:
        if record[2] < curr_score_ft:
            break
        players.append(record[1])
        score_ft = record[2]
        score_m = record[3]
        video = record[4][0] if video == None else video
        
        curr_score_ft = score_ft
        curr_score_m = score_m
        cur_hrc_wr = record
    
    players_string = ", ".join(players)
    curr_score_m = round(curr_score_m,1)
    curr_score_ft = m_to_ft(float(curr_score_m))


    return (cur_hrc_wr, curr_score_ft, curr_score_m, players_string) # object of record?




def get_hrc_total(is_TAS):
    total_distance_m = 0

    for char in HRC_CHARACTERS:
        current_hrc_wr = get_current_hrc_wr(char, is_TAS)
        score_m = current_hrc_wr[2]
        


        total_distance_m += float(score_m)

    total_distance_m = round(total_distance_m,1)
    total_distance_ft = m_to_ft(total_distance_m)


    return (total_distance_ft, total_distance_m)