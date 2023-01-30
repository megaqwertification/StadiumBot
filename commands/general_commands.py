from interactions import Client, CommandContext
import embeds

from typing import List
from interactions import CommandContext, Option, OptionType, Choice

from constants import ALIASES, HRC_CHARACTERS, GUILD_IDS
from constants_WIP.btt_constants import BTT_STAGES, BTT_CHARACTERS, BTT_SUS_TAGS
from formulas import get_char_name, time_to_frames, frames_to_time_string
from .helper_functions import filter_btt_tags

from db import connect
import random

def register_general_commands(bot: Client):
    @bot.command(
        name='random',
        description='Query a random record',
        scope=GUILD_IDS,
        options=[
            Option(
                name='mode',
                description='Choose your mode (BTT, HRC, 10MM, Events)',
                type=OptionType.STRING,
                choices=[
                    Choice(
                        name='BTT',
                        value='btt'
                    )
                ],
                required=True,
            ),
            Option(
                name='tas',
                description='default: RTA',
                type=OptionType.BOOLEAN,
                required=False,
            ),
            Option(
                name='sus',
                description='Query a random SuS record',
                type=OptionType.BOOLEAN,
                required=False,
            )
        ] 
    )

    async def _random(ctx: CommandContext, mode: str = 'btt', **kwargs):
        is_SuS = kwargs.get('sus', False)
        
        if mode == 'btt':
            char_name = random.choice(BTT_CHARACTERS) 
            #char_name = 'Zelda/Sheik'
            # temp lol unbelievably scuffed
            if char_name == 'Zelda/Sheik':
                char_name = random.choice(['Zelda', 'Sheik'])
            stage_name = random.choice(BTT_STAGES)
            is_TAS = kwargs.get('tas', False)
            if is_SuS:
                tags_list = [random.choice(list(BTT_SUS_TAGS.keys()) + [''])]
            else:
                tags_list = ['']
            # Need to get ANY random record with this tag in its tag list

            # same logic from WR query, needs to be cleaned up
            conn = connect()
            sql_q = f'SELECT * FROM btt_table WHERE character=\'{char_name}\' AND stage=\'{stage_name}\' AND tas={is_TAS} ORDER BY score ASC, date ASC;'
            cur = conn.cursor()
            cur.execute(sql_q)

            if is_SuS:
                cur = [record for record in cur if set(tags_list).issubset(record[9])]
            else:
                # Temp if conditions, need to make it better or make a general helper function that includes riddle
                if '1T' not in tags_list:
                    cur = [record for record in cur if not set(['1T']).issubset(record[9])]
                if 'misfire' not in tags_list and char_name == 'Luigi': # or 'misfire' not in tags_list or 'AR' not in tags_list:
                    cur = [record for record in cur if not set(['misfire']).issubset(record[9])]
                if 'AR' not in tags_list:
                    cur = [record for record in cur if not set(['AR']).issubset(record[9])]
                # more temporary filtering, probably a more efficient way to do things
                if 'LSS' not in tags_list:
                    cur = [record for record in cur if not set(['LSS']).issubset(record[9])]
                if 'BSS' not in tags_list:
                    cur = [record for record in cur if not set(['BSS']).issubset(record[9])]
                if 'RSS' not in tags_list:
                    cur = [record for record in cur if not set(['RSS']).issubset(record[9])]
                if 'TSS' not in tags_list:
                    cur = [record for record in cur if not set(['TSS']).issubset(record[9])]

            # get the record, now pick a random one from this list....but it should pick out the record.....
            # if there's no video (i.e. red square... what do?)
            if len(cur) != 0:
                players = []
                curr_score = 999
                video = None
                for record in cur:
                    if record[3] > curr_score:
                        break
                    players.append(record[2])
                    score = record[3]
                    video = record[4][0] if video == None else video # what if no video for any record?
                    break
                curr_score = score

                players_string = ", ".join(players)

                wr_string = f'{"(TAS)" if is_TAS else ""} {char_name} {"on " + stage_name} {"(" + ",".join(tags_list) + ") " if tags_list != [""] else ""}- {score} by {players_string} at {video}'
                await ctx.send(wr_string)
            else:
                wr_string = f'{"(TAS)" if is_TAS else ""} {char_name} {"on " + stage_name} {"(" + ",".join(tags_list) + ") " if tags_list != [""] else ""}'
                await ctx.send(wr_string)