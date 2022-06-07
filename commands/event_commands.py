from interactions import Client, CommandContext, Embed, Option, OptionType
from constants import EVENTS, PERSONAL_GUILD_ID, STADIUM_GUILD_ID
from db import connect

def get_event_type(id):
    if id in ['11', '13', '19', '31', '32']:
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
        if event_id not in range(1,2):
            raise ValueError(f'Please select a valid Event Match ID')
        is_TAS = kwargs.get("tas", False)
        event_type = get_event_type(event_id)

        conn = connect()
        if event_type == 'timed':
            sql_q = f'SELECT * FROM event_table WHERE score = (SELECT MIN(score) FROM event_table WHERE event_id=\'{event_id}\' AND tas={is_TAS}) AND tas={is_TAS} ORDER BY date ASC;'
        else:
            sql_q = f'SELECT * FROM event_table WHERE score = (SELECT MAX(score) FROM event_table WHERE event_id=\'{event_id}\' AND tas={is_TAS}) AND tas={is_TAS} ORDER BY date ASC;'
        
        cur = conn.cursor()
        cur.execute(sql_q)

        # TODO: handle video records + records with no sources
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

        wr_string = f'{"(TAS)" if is_TAS else ""} Event {event_id}: {event_name} - {score} {"KOs" if event_type == "scored" else ""} by {players_string} {f"at {video}" if video else ""}'

        await ctx.send(wr_string)



#def
    # event totals timed + KOs
    
    # def insert -> if event id == 11 or 13 or 19 or 31 or 32 then store as scored

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