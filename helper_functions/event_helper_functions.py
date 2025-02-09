from interactions import Client, CommandContext, Embed, Option, OptionType
from constants.event_constants import EVENTS, SCORED_EVENTS, NO_TAS_EVENT_WRS, RTA_BEATS_TAS_EVENTS
from db import connect
from formulas import frames_to_time_string, time_to_frames
import embeds



def get_event_type(id):
    if int(id) in [11, 13, 19, 31, 32]:
        event_type = 'scored'
    else:
        event_type = 'timed'
    return event_type

def get_current_event_wr(event_id, is_TAS):
    if int(event_id) not in range(1,52):
        description = f'Please select a valid Event Match ID'
        CommandContext.send(description, ephemeral=True)
        return None

    event_type = get_event_type(event_id)
    
    # no_tas_event_wr = [4,11,14,17,25,27,35,38,43,46,47]
    # if (event_id in no_tas_event_wr) and is_TAS:
    #     is_TAS=False
    if is_TAS is True:
        # account for TAS wrs that were beaten by RTA
        if event_id in (NO_TAS_EVENT_WRS + RTA_BEATS_TAS_EVENTS):
            is_TAS = False
        else:
            is_TAS = True

    conn = connect()
    if event_type == 'timed':
        sql_q = f'SELECT * FROM event_table WHERE event_id=\'{event_id}\' AND score = (SELECT MIN(score) FROM event_table WHERE event_id=\'{event_id}\' AND tas={is_TAS}) AND tas={is_TAS} ORDER BY date ASC;'
    else:
        sql_q = f'SELECT * FROM event_table WHERE event_id=\'{event_id}\' AND score = (SELECT MAX(score) FROM event_table WHERE event_id=\'{event_id}\' AND tas={is_TAS}) AND tas={is_TAS} ORDER BY date ASC;'
    
    cur = conn.cursor()
    cur.execute(sql_q)

    # TODO: handle video records + records with no sources
    # if vid still none at end, get 2nd max, recursive
    # TODO: query for RTA if no TAS exists or RTA better than TAS
    counter = 0
    players = []
    for record in cur:
        if counter > 0:
            players.append(record[1])
            continue
        players.append(record[1])
        score = record[3]
        if len(record[4]) != 0:
            video = record[4][0]
        else:
            video = None
        counter += 1 # probably a better way to do this with len or something...
        current_event_wr = record

    players_string = ", ".join(players)
    event_name = EVENTS[int(event_id)-1]

    #wr_string = f'{"(TAS)" if is_TAS else ""} Event {event_id}: {event_name} - {score} {"KOs " if event_type == "scored" else ""}by {players_string} {f"at {video}" if video else ""}'
    # TODO: add clause for "many" for events with many ties (10+)
    #CommandContext.send(wr_string)




    return current_event_wr, players




def get_event_total(event_type, is_TAS):
    conn = connect()
    curr_total = 0
    original_is_TAS = is_TAS

    if event_type == 'timed':
        for event_id in range(1,52):
            if event_id in SCORED_EVENTS:
                continue

            if is_TAS is True:
                # account for TAS wrs that were beaten by RTA
                if event_id in NO_TAS_EVENT_WRS:
                    is_TAS = False
                else:
                    is_TAS = True

            sql_q = f'SELECT * FROM event_table WHERE event_id=\'{event_id}\' AND score = (SELECT MIN(score) FROM event_table WHERE event_id=\'{event_id}\' AND tas={is_TAS}) AND tas={is_TAS} ORDER BY date ASC;'
            cur = conn.cursor()
            cur.execute(sql_q)

            # TODO: handle video records + records with no sources
            # if vid still none at end, get 2nd max, recursive
            # TODO: query for RTA if no TAS exists or RTA better than TAS
            counter = 0
            players = []
            for record in cur:
                if counter > 0:
                    players.append(record[1])
                    continue
                players.append(record[1])
                score = record[3]
                curr_total += int(time_to_frames(float(score)))
                if len(record[4]) != 0:
                    video = record[4][0]
                else:
                    video = None
                counter += 1 # probably a better way to do this with len or something...

            players_string = ", ".join(players)
            is_TAS = original_is_TAS
        return frames_to_time_string(curr_total)
        

    else:
        for event_id in SCORED_EVENTS:
            if is_TAS is True:
                # account for TAS wrs that were beaten by RTA
                if event_id in NO_TAS_EVENT_WRS:
                    is_TAS = False
                else:
                    is_TAS = True

            sql_q = f'SELECT * FROM event_table WHERE event_id=\'{event_id}\' AND score = (SELECT MAX(score) FROM event_table WHERE event_id=\'{event_id}\' AND tas={is_TAS}) AND tas={is_TAS} ORDER BY date ASC;'
            cur = conn.cursor()
            cur.execute(sql_q)

            # TODO: handle video records + records with no sources
            # if vid still none at end, get 2nd max, recursive
            # TODO: query for RTA if no TAS exists or RTA better than TAS
            counter = 0
            players = []
            for record in cur:
                if counter > 0:
                    players.append(record[1])
                    continue
                players.append(record[1])
                score = record[3]
                curr_total += int(score)
                if len(record[4]) != 0:
                    video = record[4][0]
                else:
                    video = None
                counter += 1 # probably a better way to do this with len or something...

            players_string = ", ".join(players)
            is_TAS = original_is_TAS

        return curr_total
    

def event_history_sort(cur_handle, event_id):
    '''
    For the event history command
    '''
    description_lines = []

    if int(event_id) in SCORED_EVENTS:
        prev_score = 0
        
        for record in cur_handle:
            query_event_id, query_player, query_type, query_score, query_sources, query_date, query_tas, query_ver = record
            sources = query_sources
            if len(sources) != 0:
                video = sources[0] 
            else:
                video = None
            tied_player = None
            player = query_player
            score = int(query_score)
            if score <= prev_score:
                continue
            prev_score = score
            # TODO: compare date and add to history if record was beaten in the same day AND does not have timestamp
            # maybe can check YT source of video
            date = query_date.date()
            score_str = str(score)
            
            if video == None:
                description_lines.append(
                    f'({date}) - {score_str + " KOs"} - {player}'
                )
            else:
                description_lines.append(
                    f'({date}) - [{score_str + " KOs" }]({video}) - {player}'
                )
    else:
        prev_score = 999

        for record in cur_handle:
            query_event_id, query_player, query_type, query_score, query_sources, query_date, query_tas, query_ver = record
            sources = query_sources
            if len(sources) != 0:
                video = sources[0] 
            else:
                video = None
            tied_player = None
            player = query_player
            score = float(query_score)
            if score >= prev_score:
                continue
            prev_score = score
            # TODO: compare date and add to history if record was beaten in the same day AND does not have timestamp
            # maybe can check YT source of video
            date = query_date.date()
            score_str = "{:.2f}".format(score)

            if video == None:
                description_lines.append(
                    f'({date}) - {score_str} - {player}'
                )
            else:
                description_lines.append(
                    f'({date}) - [{score_str}]({video}) - {player}'
                )




    return description_lines