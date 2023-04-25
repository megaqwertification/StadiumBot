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
                video = random_btt_wr[0][4].pop()
                wr_string = f'{"(TAS)" if is_TAS else ""} {char_name} {"on " + stage_name} {"(" + ",".join(tags_list) + ") " if tags_list != [] else ""}- {score} by {players_string} at {video}'
                await ctx.send(wr_string)