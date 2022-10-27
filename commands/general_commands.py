from interactions import Client, CommandContext
import embeds

from typing import List
from interactions import CommandContext, Option, OptionType, Choice

from constants import ALIASES, BTT_STAGES, BTT_CHARACTERS, BTT_SUS_TAGS, HRC_CHARACTERS, PERSONAL_GUILD_ID, STADIUM_GUILD_ID
from formulas import get_char_name, time_to_frames, frames_to_time_string

from db import connect
import random

def register_general_commands(bot: Client):
    @bot.command(
        name='random',
        description='Query a random record',
        scope=[PERSONAL_GUILD_ID],
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
            )
        ] 
    )

    async def _random(ctx: CommandContext, mode: str = 'btt', **kwargs):

        if mode == 'btt':
            return None
