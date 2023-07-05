from db import connect
from constants.btt_constants import BTT_CHARS_STAGE_COMMAND, BTT_STAGES
from formulas import time_to_frames, frames_to_time_string
from interactions import CommandContext

def filter_btt_tags(tags_list: list, cur) -> list:
    '''
    Filter tags

    Riddle if the riddle run is not a complete....how to do this?

    '''
    # Pre-processing for queried SuS tags
    filtered_list = list(cur)
    
    if tags_list:
        filtered_list = [record for record in filtered_list if set(tags_list).issubset(record[9])]

    if '1T' not in tags_list:
        filtered_list = [record for record in filtered_list if not set(['1T']).issubset(record[9])]
    if 'misfire' not in tags_list: # or 'misfire' not in tags_list or 'AR' not in tags_list:
        filtered_list = [record for record in filtered_list if not set(['misfire']).issubset(record[9])]
    if 'AR' not in tags_list:
        filtered_list = [record for record in filtered_list if not set(['AR']).issubset(record[9])]
    # more temporary filtering, probably a more efficient way to do things
    if 'LSS' not in tags_list:
        filtered_list = [record for record in filtered_list if not set(['LSS']).issubset(record[9])]
    if 'BSS' not in tags_list:
        filtered_list = [record for record in filtered_list if not set(['BSS']).issubset(record[9])]
    if 'RSS' not in tags_list:
        filtered_list = [record for record in filtered_list if not set(['RSS']).issubset(record[9])]
    if 'TSS' not in tags_list:
        filtered_list = [record for record in filtered_list if not set(['TSS']).issubset(record[9])]

    return filtered_list

def get_current_btt_wr(character, stage, is_TAS, tags_list):
    # same as btt-wr command



    conn = connect()
    sql_q = f'SELECT * FROM btt_table WHERE character=\'{character}\' AND stage=\'{stage}\' AND tas={is_TAS} ORDER BY score ASC, date ASC;'
    cur = conn.cursor()
    cur.execute(sql_q)
    
    cur = filter_btt_tags(tags_list, cur)



    if len(cur) == 0:
        description = f'Run DNE or not in database. Let mega know if this is a mistake'
        CommandContext.send(description, ephemeral=True)
        return None

    players = []
    curr_score = 999
    video = None
    for record in cur:
        if record[3] > curr_score:
            break
        players.append(record[2])
        if record[3] == curr_score:
            continue
        score = record[3]
        video = record[4] if video == None else video # what if no video for any record?

        curr_score = score
        current_btt_wr = record

    # Temp post check
    if len(video) != 0:
        video = video[0]
        
    players_string = ", ".join(players)

    # wr_string = f'{"(TAS)" if is_TAS else ""} {character}/{stage} {"(" + ",".join(tags_list) + ") " if tags_list else ""}- {score} by {players_string} at {video}'
    # CommandContext.send(wr_string)





    return current_btt_wr, players_string

def get_char_total(char_name, is_TAS):
    # if tags_list:
    #     return None
    conn = connect()
    current_char_total_frames = 0

    for stage in BTT_STAGES[:-1]:
        cur = conn.cursor()
        sql_q = f'SELECT * FROM btt_table WHERE character=\'{char_name}\' AND stage=\'{stage}\' AND tas={is_TAS} ORDER BY score ASC, date ASC;'
        # if stage_name == 'Seak' and char_input == None:
        #     continue
        cur.execute(sql_q)
        cur = filter_btt_tags([], cur)
        #print(cur)
        # process info
        players = []
        curr_score = 999
        char = ''
        video = None
        score_time = 0
        #print(cur)
        for record in cur:
        #     if record[1].strip() == 'Mario':
        #         print(record)
            if record[3] > curr_score:
                break
            elif record[3] == curr_score:
                players.append(record[2])
                continue
            #char = record[0]
            #stage = record[1]
            players.append(record[2])
            score_time = record[3]
            #print(stage)
            if len(record[4]) != 0:
                video = record[4][0] if video == None else video # what if no video for any record?

            curr_score = score_time



            # TEMP AGAIN JUST TO TEST CHAR QUERY
        current_char_total_frames += int(time_to_frames(score_time))   
        curr_score = 999

    current_char_total_time = frames_to_time_string(current_char_total_frames)

    conn.close()
    return (current_char_total_frames, current_char_total_time)



def get_stage_total(stage_name, is_TAS):
    # if tags_list:
    #     return None
    conn = connect()
    current_stage_total_frames = 0


    for character in BTT_CHARS_STAGE_COMMAND:
        cur = conn.cursor()
        sql_q = f'SELECT * FROM btt_table WHERE character=\'{character}\' AND stage=\'{stage_name}\' AND tas={is_TAS} ORDER BY score ASC, date ASC;'
        cur.execute(sql_q)
        cur = filter_btt_tags([], cur)

        players = []
        curr_score = 999
        char = ''
        video = None
        score_time = 0
        
        for record in cur:
            if record[3] > curr_score:
                break
            elif record[3] == curr_score:
                players.append(record[2])
                continue
            #char = record[0]
            #stage = record[1]
            players.append(record[2])
            score_time = record[3]
            if len(record[4]) != 0:
                video = record[4][0] if video == None else video # what if no video for any record?

            curr_score = score_time



        current_stage_total_frames += int(time_to_frames(score_time))   
        curr_score = 999

    current_stage_total_time = frames_to_time_string(current_stage_total_frames)

    conn.close()
    return (current_stage_total_frames, current_stage_total_time)