from interactions import Client, CommandContext
import embeds

from typing import List
from interactions import CommandContext, Option, OptionType, Choice

from constants import ALIASES, BTT_SUS_TAGS, BTT_STAGES, BTT_CHARACTERS, HRC_CHARACTERS, PERSONAL_GUILD_ID, STADIUM_GUILD_ID
from formulas import get_char_name, time_to_frames, frames_to_time_string

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
                name='stage',
                description='stage (leave blank for vanilla)',
                type=OptionType.STRING,
                required=False
            ),
            Option(
                name='tas',
                description='default: RTA',
                type=OptionType.BOOLEAN,
                required=False,
            ),
            Option(
                name='tags',
                description='SuS tags (comma separated, case sensitive)',
                type=OptionType.STRING,
                required=False
            )
        ] 
    )

    async def _btt_wr(ctx: CommandContext, **kwargs):
        char_input = kwargs.get("character")
        char_name = get_char_name(char_input, ALIASES)
        if char_name not in BTT_CHARACTERS:
            raise ValueError(f'Please select a valid character')



        stage_input = kwargs.get('stage', char_name)
        stage_name = get_char_name(stage_input, ALIASES)

        # catch all if "ICs" is only inputted for vanilla
        if kwargs.get('stage') == None and char_name == 'Ice Climbers':
            char_name = 'Sopo'
            stage_name = 'Ice Climbers'
        
        # temp catch for sheik/zelda stage name
        if stage_name == 'Sheik':
            stage_name = 'Zelda'
            original_stage_name = 'Sheik'

        # Catch all if "Sopo" is only inputted for vanilla
        if stage_name == 'Sopo':
            stage_name = 'Ice Climbers'

        is_TAS = kwargs.get('tas', False)

        sus_tags = kwargs.get('tags', [])
        tags_list = sus_tags.split(',') if sus_tags else []
        if not set(tags_list).issubset(set(BTT_SUS_TAGS.keys())):
            raise ValueError('One or more sus tags DNE')

        conn = connect()
        sql_q = f'SELECT * FROM btt_table WHERE character=\'{char_name}\' AND stage=\'{stage_name}\' AND tas={is_TAS} ORDER BY score ASC, date ASC;'
        cur = conn.cursor()
        cur.execute(sql_q)

        # pre-processing for sus tags
        if tags_list:
            cur = [record for record in cur if set(tags_list).issubset(record[9])]

        players = []
        curr_score = 0
        video = None
        for record in cur:
            if record[3] < curr_score:
                break
            players.append(record[2])
            score = record[3]
            video = record[4][0] if video == None else video # what if no video for any record?

            curr_score = score

        players_string = ", ".join(players)

        wr_string = f'{"(TAS)" if is_TAS else ""} {char_name} {"on " + stage_name if char_name != stage_name else ""} {"(" + ",".join(tags_list) + ") " if tags_list else ""}- {score} by {players_string} at {video}'
        await ctx.send(wr_string)

    @bot.command(
        name='btt-wr-list',
        description='Display the list of current BtT WRs',
        scope=[PERSONAL_GUILD_ID, STADIUM_GUILD_ID],
        options=[
            # TODO: add parameters in case you want a char or stage total
            Option(
                name='tas',
                description='default: RTA',
                type=OptionType.BOOLEAN,
                required=False,
            ),
        ]   
    )

    async def _btt_wr_list(ctx: CommandContext, **kwargs):
        is_TAS =  kwargs.get('tas', False)

        description_lines = [
            f'Break the Targets {"TAS " if is_TAS else "RTA "}World Records\n'
        ]
        total_high_score_f = 0
        
        conn = connect()
        cur = conn.cursor()

        for stage in BTT_STAGES[:-1]:
            # query each stage's WR
            # TODO: how do i go through each stage char, parameter if individual stage or char is selected

            sql_q = f'SELECT * FROM btt_table WHERE character=\'{stage}\' AND stage=\'{stage}\' AND tas={is_TAS} ORDER BY score ASC, date ASC;'
            # TODO: add clause to make sure sheik shows up on zelda
            # TODO: coloquially, ICs vanilla is referred to as Ice Climbers instead of Sopo for vanilla ...
            if stage == 'Ice Climbers':
                # TEMP
                char = 'Popo'
                sql_q = f'SELECT * FROM btt_table WHERE character=\'{char}\' AND stage=\'{stage}\' AND tas={is_TAS} ORDER BY score ASC, date ASC;'
            elif stage == 'Zelda':
                # TEMP: only for vanilla query
                char = 'Sheik'
                sql_q = f'SELECT * FROM btt_table WHERE character=\'{char}\' AND stage=\'{stage}\' AND tas={is_TAS} ORDER BY score ASC, date ASC;'
            cur.execute(sql_q)
            
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
                video = record[4][0] if video == None else video # what if no video for any record?

                curr_score = score_time
                # TEMP, should only access under vanilla query
                if stage.strip() == 'Ice Climbers':
                    char = 'Ice Climbers' 

            description_lines.append(
                f"{char.strip()} - [{score_time}]({video}) - {', '.join(players)}"
            )

            total_high_score_f += int(time_to_frames(score_time))
            curr_score = 999


        total_high_score = frames_to_time_string(total_high_score_f)
        total_high_score_desc = f'\nTotal High Score: [{total_high_score}]({"https://www.youtube.com/playlist?list=PLP-fO_NfCBaqcicPbCvGQOCIN1pL9hZyA" if is_TAS else "https://www.youtube.com/playlist?list=PLZmpvgqEAI7DioaEmIJG832_XKVpJHhy_"})'
        description_lines.append(total_high_score_desc)

        await embeds.send_embeds(description_lines, ctx)
        cur.close()
        conn.close()


