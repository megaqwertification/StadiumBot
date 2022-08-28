from interactions import Client, CommandContext
import embeds

from typing import List
from interactions import CommandContext, Option, OptionType, Choice

from constants import ALIASES, HRC_CHARACTERS, PERSONAL_GUILD_ID, STADIUM_GUILD_ID
from formulas import m_to_ft, get_char_name

from db import connect

def register_btt_commands(bot: Client):
    @bot.command(
        name='btt-wr',
        description='Query a BtT WR',
        scope=[PERSONAL_GUILD_ID, STADIUM_GUILD_ID],
        options=[
            Option(
                name='character',
                description='Choose your character',
                type=OptionType.STRING,
                required=True,
            ),
            Option(
                name='tas',
                description='default: RTA',
                type=OptionType.BOOLEAN,
                required=False,
            ),
            Option(
                name='tags',
                description='SuS tags',
                type=OptionType.STRING,
                required=False
            )
        ] 
    )

    async def _btt_wr(ctx: CommandContext, **kwargs):
        char_input = kwargs.get("character")
        char_name = get_char_name(char_input, ALIASES)
        
        is_TAS = kwargs.get('tas', False)

        sus_tags = kwargs.get('tags', [])
        tags_list = sus_tags.split(',') if sus_tags else []

        return None

    @bot.command(
        name='btt-wr-list',
        description='Display the list of current BtT WRs',
        scope=[PERSONAL_GUILD_ID, STADIUM_GUILD_ID],
        options=[
            Option(
                name='tas',
                description='default: RTA',
                type=OptionType.BOOLEAN,
                required=False,
            ),
        ]   
    )

    async def _btt_wr_list(ctx: CommandContext, **kwargs):
        return None


