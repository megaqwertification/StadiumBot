from interactions import Client, CommandContext, Embed, Option, OptionType
from constants import EVENTS, PERSONAL_GUILD_ID, STADIUM_GUILD_ID
from db import connect
from formulas import frames_to_time_string, time_to_frames
import embeds

def get_event_type(id: int) -> str:
    if id in [11, 13, 19, 31, 32]:
        event_type = 'scored'
    else:
        event_type = 'timed'
    return event_type

def register_event_commands(bot: Client):
    @bot.command(
        name='event-wr',
        description='Query an event\'s current WR',
        scope=[PERSONAL_GUILD_ID],
        options=[
            Option(
                name='event_id',
                description='Choose your character',
                type=OptionType.STRING,
                required=True,
            ),
            #option: TAS
            Option(
                name='tas',
                description='RTA or TAS',
                type=OptionType.BOOLEAN,
                required=False,
            ),
        ]
    )
    
    async def _event_wr(ctx: CommandContext, **kwargs):
        event_id = kwargs.get("event_id")
        if int(event_id) not in range(1,52):
            raise ValueError(f'Please select a valid Event Match ID')
        is_TAS = kwargs.get("tas", False)
        event_type = get_event_type(event_id)

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

        players_string = ", ".join(players)
        event_name = EVENTS[int(event_id)-1]

        wr_string = f'{"(TAS)" if is_TAS else ""} Event {event_id}: {event_name} - {score} {"KOs" if event_type == "scored" else ""}by {players_string} {f"at {video}" if video else ""}'
        # TODO: add clause for "many" for events with many ties (10+)
        await ctx.send(wr_string)


    @bot.command(
        name='event-wr-list',
        description='Query for event WR list',
        scope=[PERSONAL_GUILD_ID],
        options=[
            Option(
                name='tas',
                description='RTA or TAS',
                type=OptionType.BOOLEAN,
                required=False,
            ),
        ]
    )
    
    async def _event_wr_list(ctx: CommandContext, **kwargs):
        # TODO: add functionality if there's no TAS WR
        await ctx.defer()
        is_TAS = kwargs.get("tas", False)

        description_lines = [
            f'Event Match {"TAS" if is_TAS else "RTA"} World Records\n'
        ]
        event_time_sum_f = 0
        event_KO_sum = 0
        for event_id in range(1,len(EVENTS)+1):
            event_type = get_event_type(event_id)
            
            conn = connect()
            if event_type == 'timed':
                sql_q = f'SELECT * FROM event_table WHERE event_id=\'{event_id}\' AND score = (SELECT MIN(score) FROM event_table WHERE event_id=\'{event_id}\' AND tas={is_TAS}) AND tas={is_TAS} ORDER BY date ASC;'
            else:
                sql_q = f'SELECT * FROM event_table WHERE event_id=\'{event_id}\' AND score = (SELECT MAX(score) FROM event_table WHERE event_id=\'{event_id}\' AND tas={is_TAS}) AND tas={is_TAS} ORDER BY date ASC;'
            # there HAS to be a way to just get the lowest timed event scores, highest KO scores, then do some sort of table join, process,
            # then embed the lines

            cur = conn.cursor()
            cur.execute(sql_q)

            # TODO: handle video records + records with no sources
            # TODO: handle records with no TAS/faster RTA than TAS
            counter = 0
            players = []
            for record in cur:
                if counter > 0:
                    # description_lines[-1] += f', {record[1]}'
                    # TODO: if no vid, update the vid here
                    # nested ifs :withered:
                    if video == None:
                        if len(record[4]) != 0:
                            video = record[4][0]
                        else:
                            video = None
                    players.append(record[1])
                    continue
                    # TODO: implement video record if no WR holder(s) have video
                    # TODO: implement E17/32 "many" holders, or just for WR holders where it's more than 5
                players.append(record[1])
                score = record[3]
                if event_type == 'timed':
                    event_time_sum_f += int(time_to_frames(float(score))) # TODO: make t_to_f return an int...depends on case
                else:
                    event_KO_sum += int(score)

                if len(record[4]) != 0:
                    video = record[4][0]
                else:
                    video = None
                counter += 1 # probably a better way to do this with len or something...

            players_string = ", ".join(players)
            KO_string = " KOs" if event_type == "scored" else ""
            description_lines.append( 
                f'Event {event_id} - {f"[{str(score) + KO_string}]({video})" if video else f"{score}"}  - {players_string}'
            
            )
            counter += 1

    
        total_time = frames_to_time_string(event_time_sum_f)
        totals_str = f'\nTotal Time/KOs: [{total_time}/{event_KO_sum} KOs]({"https://www.youtube.com/playlist?list=PLRSZTIKPRRKT46gHOHtlY3oQQrSzvmJ5I" if is_TAS else "https://www.youtube.com/playlist?list=PLRSZTIKPRRKS-tQnuNrQggYtbvXnUm4j6"})'
        description_lines.append(totals_str)

        await embeds.send_embeds(description_lines, ctx)
        cur.close()
        conn.close()

    #def history
        

    #events w/o TAS or ties RTA:
    #4
    #11
    #14
    #17 (lol)
    #25
    #27
    #35
    #38
    #43
    #46
    #47