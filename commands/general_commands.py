from interactions import Client, CommandContext
import embeds

from typing import List
from interactions import CommandContext, Option, OptionType, Choice

from constants.general_constants import ALIASES, GUILD_IDS
from constants.btt_constants import BTT_STAGES, BTT_CHARACTERS, BTT_SUS_TAGS
from constants.hrc_constants import HRC_CHARACTERS
from constants.event_constants import EVENTS, SCORED_EVENTS, NO_TAS_EVENT_WRS
from constants.ten_mm_constants import TENMM_CHARACTERS

from formulas import get_char_name, time_to_frames, frames_to_time_string

from helper_functions.btt_helper_functions import filter_btt_tags, get_current_btt_wr
from helper_functions.hrc_helper_functions import get_current_hrc_wr
from helper_functions.event_helper_functions import get_current_event_wr, get_event_type
from helper_functions.ten_mm_helper_functions import get_current_10mm_wr

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
                tags_list = [random.choice(list(BTT_SUS_TAGS.keys()))]
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
                description='Choose your mode (BTT, HRC, Events, 10MM)',
                type=OptionType.STRING,
                choices=[
                    Choice(
                        name='BTT',
                        value='btt'
                    ),
                    Choice(
                        name='HRC',
                        value='hrc'
                    ),
                    Choice(
                        name='Events',
                        value='events'
                    ),
                    Choice(
                        name='10MM',
                        value='10mm'
                    ),
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

    async def _recordcount(ctx: CommandContext, mode: str, **kwargs):
        if mode == 'btt':
            await ctx.defer()

            is_TAS =  kwargs.get('tas', False)
            
            description_lines = [
                f'Break the Targets {"TAS" if is_TAS else "RTA"} World Record Count\n'
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

        elif mode == 'hrc':
            await ctx.defer()

            is_TAS =  kwargs.get('tas', False)
            
            description_lines = [
                f'Home Run Contest {"TAS" if is_TAS else "RTA"} World Record Count\n'
            ]
            
            record_count_dict = {}
            
            conn = connect()
            cur = conn.cursor()

            
            for char in HRC_CHARACTERS:
                players = get_current_hrc_wr(char, is_TAS)[3].split(', ')
            
                for player in players:
                    if (char == "Ganondorf" or char == "Ice Climbers") and not is_TAS:
                        if player not in ['HRCtypo', 'Freezard']: # hard-code for now. Would need updating if other WR holders appear
                            # alternatively, can do these characters last or something
                            continue
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

            if not is_TAS:
                description_lines.extend((
                    f'\nPlayers with only Ganondorf and/or Ice Climbers WRs excluded',
                    f'To see all WRs with ties, see the [score database](https://docs.google.com/spreadsheets/d/15wdkLsmSU2T9Os1j-lISe-XmXH-l3Awk9xBipYnTQCI/edit#gid=1511527150)'
                ))

            await embeds.send_embeds(description_lines, ctx)
            cur.close()
            conn.close()
            

        elif mode == 'events':
            await ctx.defer()

            is_TAS =  kwargs.get('tas', False)
            
            description_lines = [
                f'Event Match {"TAS" if is_TAS else "RTA"} World Record Count\n'
            ]
            
            record_count_dict = {}
            
            conn = connect()
            cur = conn.cursor()

           
            for i in range(len(EVENTS)):
                if i+1 == 17 or i+1 == 32: # I should have a separate loop later that adds counts for 17 and 32 if and only if the players on the list have it ... ?
                    continue
                players = get_current_event_wr(i+1, is_TAS)[1] # already a list lol it's not like the case in others
            
                for player in players:
                    if player not in record_count_dict:
                        record_count_dict[player] = 1
                    else:
                        record_count_dict[player] += 1
            
            # E17 and E32 processing 
            for i in [17, 32]:
                if i == 17 and is_TAS:
                    continue
                players = get_current_event_wr(i, is_TAS)[1] # already a list lol it's not like the case in others
            
                for player in players:
                    if player not in record_count_dict:
                        # they only have E17 or E32, ignore the addition
                        continue
                    else:
                        record_count_dict[player] += 1

            # Sort by value https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
            result = dict(sorted(record_count_dict.items(), key=lambda item:item[1], reverse=True))

            for player in result:
                description_lines.append(
                    f"{player} - {result[player]}"
                )
            
            if not is_TAS:
                description_lines.extend((
                    f'\nPlayers with only Event 17 or Event 32 WRs excluded',
                    f'To see all WRs with ties, see the [score database](https://docs.google.com/spreadsheets/d/15wdkLsmSU2T9Os1j-lISe-XmXH-l3Awk9xBipYnTQCI/edit#gid=1817938638)'
                ))


            await embeds.send_embeds(description_lines, ctx)
            cur.close()
            conn.close()

        elif mode == '10mm':
            await ctx.defer()

            is_TAS =  kwargs.get('tas', False)
            
            description_lines = [
                f'10-Man Melee {"TAS" if is_TAS else "RTA"} World Record Count\n'
            ]
            
            record_count_dict = {}
            
            conn = connect()
            cur = conn.cursor()

            for char in TENMM_CHARACTERS:
                players = get_current_10mm_wr(char, is_TAS)[1].split(', ')
            
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

    @bot.command(
        name='latest',
        description='Query the latest world records',
        scope=GUILD_IDS,
        options=[
            Option(
                name='mode',
                description='Choose your mode (BTT, HRC, 10MM, Events)',
                type=OptionType.STRING,
                choices=[
                    Choice(name='BTT', value='BTT'),
                    Choice(name='HRC', value='HRC'),
                    Choice(name='10MM', value='10MM'),
                    Choice(name='Events', value='Event')
                ],
                required=False,
            ),
            Option(
                name='rta_tas',
                description='Filter by RTA or TAS',
                type=OptionType.STRING,
                choices=[
                    Choice(name='RTA', value='rta'),
                    Choice(name='TAS', value='tas')
                ],
                required=False,
            ),
            Option(
                name='is_mismatch',
                description='default: False (Only available when selecting BTT mode)',
                type=OptionType.BOOLEAN,
                required=False,
            )
        ]
    )

    async def latest(ctx: CommandContext, **kwargs):
        mode = kwargs.get('mode', None)
        rta_tas = kwargs.get('rta_tas', None)
        is_mm = kwargs.get('is_mismatch', False)
        if is_mm and mode != 'BTT':
            await ctx.defer(ephemeral=True)
            description = f'Cannot only select mismatch flag if BTT is the mode selected'
            await ctx.send(description, ephemeral=True)
            return

        await ctx.defer()

        conn = connect()
        cur = conn.cursor()

        # Base query
        query = """
        (
            -- BTT mode: Only rows where character = stage
            SELECT 
                'BTT' AS mode,
                TRIM(character) AS character,
                score AS score,
                player AS player,
                date::date AS date,
                sources AS sources,
                tas AS tas,
                tags AS tags,
                NULL AS extras
            FROM btt_table
            WHERE (character = stage 
                OR (character = 'Sheik' AND stage = 'Zelda') 
                OR (character = 'Popo' AND stage = 'Ice Climbers')) 
           AND NOT (character = 'Zelda' AND stage = 'Zelda') 
           AND NOT (character = 'Ice Climbers' AND stage = 'Ice Climbers') 
               AND date IS NOT NULL
        )
        UNION ALL
        (
            -- Event mode: Use event_id as character
            SELECT 
                'Event' AS mode,
                event_id::text AS character,
                score AS score,
                player AS player,
                date::date AS date,
                sources AS sources,
                tas AS tas,
                tags AS tags,
                type::text AS extras
            FROM event_table
            WHERE date IS NOT NULL
        )
        UNION ALL
        (
            -- HRC mode: Use score_ft as score
            SELECT 
                'HRC' AS mode,
                TRIM(character) AS character,
                score_ft AS score,
                player AS player,
                date::date AS date,
                sources AS sources,
                tas AS tas,
                tags AS tags,
                score_m::text AS extras
            FROM hrc_table
            WHERE date IS NOT NULL
        )
        UNION ALL
        (
            -- 10MM mode: Use default format
            SELECT 
                '10MM' AS mode,
                TRIM(character) AS character,
                score AS score,
                player AS player,
                date::date AS date,
                sources AS sources,
                tas AS tas,
                tags AS tags,
                NULL AS extras
            FROM ten_mm_table
            WHERE date IS NOT NULL
        )
        """

        # Apply the mode filter if provided
        if mode:
            if mode == 'BTT' and is_mm:
                base_mm_query = """
                (
                    -- BTT mode: Only rows with mismatch enabled (allows zelda, dual ICs, and char != stage)
                    SELECT 
                        'BTT' AS mode,
                        TRIM(character) AS character,
                        TRIM(stage) AS stage,
                        score AS score,
                        player AS player,
                        date::date AS date,
                        sources AS sources,
                        tas AS tas,
                        tags AS tags,
                        NULL AS extras
                    FROM btt_table
                    WHERE date IS NOT NULL
                )
                """
                query = f"""
                SELECT * FROM ({base_mm_query}) AS mode_filtered
                WHERE mode = '{mode}'
                """
            else:
                query = f"""
                SELECT * FROM ({query}) AS mode_filtered
                WHERE mode = '{mode}'
                """

        # Apply the RTA/TAS filter if provided
        if rta_tas:
            tas_filter = "true" if rta_tas == "tas" else "false"
            query = f"""
            SELECT * FROM ({query}) AS rta_tas_filtered
            WHERE tas = {tas_filter}
            """

        # Fetch the ten most recent records
        query += """
        ORDER BY date DESC
        LIMIT 10;
        """

        cur.execute(query)
        records = cur.fetchall()
        # filter out sus tags for btt
        if mode == 'BTT':
            # TODO: filter_btt_tags doesn't apply here well, need to filter manually. Refactor eventually
            # records = filter_btt_tags([], records)
            tags_to_filter = ['1T', 'AR', 'LSS','BSS', 'RSS', 'TSS']
            btt_filtered_records = list(cur)
            for tag in tags_to_filter:
                btt_filtered_records = [record for record in btt_filtered_records if not set(list(tag)).issubset(record[tags])]

        description_lines = [f'Latest {"Mismatch" if is_mm else ""} {mode if mode else ""} {rta_tas.upper() if rta_tas else ""} World Records\n']

        for record in records:
            if is_mm and mode == 'BTT':
                mode, character, stage, score, player, date, sources, tas, tags, extras = record
            else:
                mode, character, score, player, date, sources, tas, tags, extras = record

            extra = ""
            if mode == "Event" and extras == "scored":
                extra = " KOs"
            elif mode == "HRC":
                extra = f"ft/{extras}m"

            video = sources[0] if sources else False
            formatted_score = f'[{score}{extra}]({video})' if video else f'{score}{extra}'

            # add different formatting for mismatch btt
            if is_mm and mode == 'BTT':
                description_lines.append(
                    f'{mode} {character}/{stage} - {formatted_score} - {player}{" [TAS]" if tas else ""} ({date})'
                )
            else:
                description_lines.append(
                    f'{mode} {character} - {formatted_score} - {player}{" [TAS]" if tas else ""} ({date})'
                )


        await embeds.send_embeds(description_lines, ctx)
        cur.close()
        conn.close()
