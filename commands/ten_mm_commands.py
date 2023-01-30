from interactions import Client, CommandContext
import embeds

from typing import List
from interactions import CommandContext, Option, OptionType, Choice
from constants import ALIASES, PERSONAL_GUILD_ID, STADIUM_GUILD_ID
from constants_WIP.ten_mm_constants import TENMM_CHARACTERS

from formulas import get_char_name, frames_to_time_string, time_to_frames
from db import connect

def register_10mm_commands(bot: Client):
    @bot.command(
        name='10mm-wr',
        description='Query a 10mm current WR',
        scope=[PERSONAL_GUILD_ID, STADIUM_GUILD_ID],
        options=[
            Option(
                name='character',
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

    async def _10mm_wr(ctx: CommandContext, **kwargs):
        char_input = kwargs.get("character")
        char_name = get_char_name(char_input, ALIASES)
        if char_name not in TENMM_CHARACTERS:
            raise ValueError(f'Please select a valid character')
        is_TAS = kwargs.get('tas', False)

        conn = connect()
        sql_q = f'SELECT * FROM ten_mm_table WHERE score = (SELECT MIN(score) FROM ten_mm_table WHERE character=\'{char_name}\' AND tas={is_TAS} ) AND character=\'{char_name}\' AND tas={is_TAS} ORDER BY date ASC;' # 
        cur = conn.cursor()
        cur.execute(sql_q)

        counter = 0
        players = []
        for record in cur:
            if counter > 0:
                # get vid if it doesn't appear for first WR holder
                players.append(record[1])
                continue
            players.append(record[1])
            score = record[2]
            video = record[3][0] if record[3] else ''
            counter += 1
        players_string = ", ".join(players)

        wr_string = f'{"(TAS)" if is_TAS else ""} {char_name} - {score} by {players_string} at {video}'
        await ctx.send(wr_string)

    @bot.command(
        name='10mm-wr-list',
        description='Query for 10mm WR list',
        scope=[PERSONAL_GUILD_ID, STADIUM_GUILD_ID],
        options=[
            Option(
                name='tas',
                description='RTA or TAS',
                type=OptionType.BOOLEAN,
                required=False,
            ),
        ]
    )

    async def _10mm_wr_list(ctx: CommandContext, **kwargs):
        await ctx.defer()
        is_TAS = kwargs.get("tas", False)
        
        description_lines = [
            f'10-Man Melee {"TAS" if is_TAS else "RTA"} World Records\n'
        ]
        ten_mm_time_sum_f = 0
        conn = connect()

        for char_alias in TENMM_CHARACTERS[:-8]:
            char = get_char_name(char_alias, ALIASES)
            cur = conn.cursor()
            query = f'SELECT * FROM ten_mm_table WHERE score = (SELECT MIN(score) FROM ten_mm_table WHERE character=\'{char}\' AND tas={is_TAS}) AND character=\'{char}\' AND tas={is_TAS};'
            cur.execute(query)

            counter = 0
            players = []
            for record in cur:
                if counter > 0:
                    if video == None:
                        if len(record[3]) != 0:
                            video = record[3][0]
                        else:
                            video = None
                    players.append(record[1])
                    continue
                
                players.append(record[1])
                score = record[2]
                video = record[3][0] if record[3] else None

                ten_mm_time_sum_f += int(time_to_frames(float(score)))  #tabbed left once?

            players_string = ", ".join(players)
            description_lines.append(
                f"{char} - [{score}]({video}) - {players_string}"
            )
            
            counter += 1
        
        total_time = frames_to_time_string(ten_mm_time_sum_f)
        totals_str = f'\nTotal Time: [{total_time}]({"https://www.youtube.com/playlist?list=PLPCRoOSMSXFwY-PfF681qtbEJbMZpsEk2" if is_TAS else "https://www.youtube.com/playlist?list=PLPCRoOSMSXFzcla8fKt1lF8V8-SrFTzBS"})'
        description_lines.append(totals_str)

        await embeds.send_embeds(description_lines, ctx)
        cur.close()
        conn.close()