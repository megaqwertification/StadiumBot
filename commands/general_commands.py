from interactions import Client, CommandContext
import embeds

from typing import List
from interactions import CommandContext, Option, OptionType, Choice

from constants.general_constants import ALIASES, GUILD_IDS
from constants.btt_constants import BTT_STAGES, BTT_CHARACTERS, BTT_SUS_TAGS
from formulas import get_char_name, time_to_frames, frames_to_time_string
from helper_functions.btt_helper_functions import filter_btt_tags, get_current_btt_wr

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

        await ctx.defer()
        
        if mode == 'btt':
            char_name = random.choice(BTT_CHARACTERS) 
            #char_name = 'Zelda/Sheik'
            # temp lol unbelievably scuffed
            stage_name = random.choice(BTT_STAGES)
            is_TAS = kwargs.get('tas', False)
            if is_SuS:
                tags_list = [random.choice(list(BTT_SUS_TAGS.keys()) + [''])]
            else:
                tags_list = []
            # Need to get ANY random record with this tag in its tag list

            random_btt_wr = get_current_btt_wr(char_name, stage_name, is_TAS, tags_list)

            # same logic from WR query, needs to be cleaned up
            if random_btt_wr is None:
                wr_string = f'{"(TAS)" if is_TAS else ""} {char_name} {"on " + stage_name} {"(" + ",".join(tags_list) + ") " if tags_list != [] else ""}'
                await ctx.send(wr_string)
            else:
                score = random_btt_wr[0][3]
                players_string = random_btt_wr[1]
                video = random_btt_wr[0][4].pop(0)
                wr_string = f'{"(TAS)" if is_TAS else ""} {char_name} {"on " + stage_name} {"(" + ",".join(tags_list) + ") " if tags_list != [] else ""}- {score} by {players_string} at {video}'
                await ctx.send(wr_string)

    @bot.command(
        name='recordcount',
        description='Query number of world records per player',
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
            )
        ] 
    )

    async def _recordcount(ctx: CommandContext, mode: str = 'btt', **kwargs):
        await ctx.defer()

        is_TAS =  kwargs.get('tas', False)
        
        description_lines = [
            f'Break the Targets {"TAS " if is_TAS else "RTA "} World Record Count\n'
        ]
        
        record_count_dict = {}
        
        conn = connect()
        cur = conn.cursor()
        

        for stage in BTT_STAGES:
            cur = conn.cursor()
            sql_q = f'SELECT * FROM btt_table WHERE character=\'{stage}\' AND stage=\'{stage}\' AND tas={is_TAS} ORDER BY score ASC, date ASC;'

            if stage == 'Ice Climbers':
                # TEMP
                char = 'Popo'
                sql_q = f'SELECT * FROM btt_table WHERE character=\'{char}\' AND stage=\'{stage}\' AND tas={is_TAS} ORDER BY score ASC, date ASC;'
            elif stage == 'Zelda':
                # TEMP: only for vanilla query
                char = 'Sheik'
                sql_q = f'SELECT * FROM btt_table WHERE character=\'{char}\' AND stage=\'{stage}\' AND tas={is_TAS} ORDER BY score ASC, date ASC;'
                         
            if stage == 'Seak':
                continue


            cur.execute(sql_q)
            
            cur = filter_btt_tags([], cur)


            # process info
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
                char = record[0]
                stage = record[1]
                players.append(record[2])
                score_time = record[3]
                #print(stage)
                if len(record[4]) != 0:
                    video = record[4][0] if video == None else video # what if no video for any record?

                curr_score = score_time
                # TEMP, should only access under vanilla query
                if stage.strip() == 'Ice Climbers':
                    char = 'Ice Climbers' 

            for player in players:
                if player not in record_count_dict:
                    record_count_dict[player] = 1
                else:
                    record_count_dict[player] += 1

        # Sort by value https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
        result = dict(sorted(record_count_dict.items(), key=lambda item:item[1], reverse=True))


        for player in result:
            description_lines.append(
                f"{player} - {result[player]}"
            )

        await embeds.send_embeds(description_lines, ctx)
        cur.close()
        conn.close()