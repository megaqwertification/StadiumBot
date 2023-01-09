from interactions import Client, CommandContext
import embeds

from typing import List
from interactions import CommandContext, Option, OptionType, Choice

from constants import ALIASES, BTT_SUS_TAGS, BTT_STAGES, BTT_CHARACTERS, HRC_CHARACTERS, GUILD_IDS
from formulas import get_char_name, time_to_frames, frames_to_time_string

from .helper_functions import filter_btt_tags

from db import connect

def register_btt_commands(bot: Client):
    @bot.command(
        name='btt-wr',
        description='Query a BtT WR',
        scope=GUILD_IDS,
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
            description = f'Please select a valid character'
            await ctx.send(description, ephemeral=True)
            return None



        stage_input = kwargs.get('stage', char_name)
        stage_name = get_char_name(stage_input, ALIASES)
        # if stage_name not in BTT_CHARACTERS:
        #     description = f'Please select a valid stage'
        #     await ctx.send(description, ephemeral=True)
        #     return None

        # catch all if "ICs" is only inputted for vanilla
        if kwargs.get('stage') == None and char_name == 'Ice Climbers':
            char_name = 'Popo'
            stage_name = 'Ice Climbers'
        
        # temp catch for sheik/zelda stage name
        if stage_name == 'Sheik':
            stage_name = 'Zelda'
            original_stage_name = 'Sheik'

        # Catch all if "Sopo" is only inputted for vanilla
        if stage_name == 'Popo':
            stage_name = 'Ice Climbers'

        is_TAS = kwargs.get('tas', False)

        sus_tags = kwargs.get('tags', [])
        tags_list = sus_tags.split(',') if sus_tags else []
        if not set(tags_list).issubset(set(BTT_SUS_TAGS.keys())):
            description = f'Please select a valid SuS tag (case sensitive for now)'
            await ctx.send(description, ephemeral=True)
            return None

        conn = connect()
        sql_q = f'SELECT * FROM btt_table WHERE character=\'{char_name}\' AND stage=\'{stage_name}\' AND tas={is_TAS} ORDER BY score ASC, date ASC;'
        cur = conn.cursor()
        cur.execute(sql_q)

        # pre-processing for sus tags
        if tags_list:
            cur = [record for record in cur if set(tags_list).issubset(record[9])]

        # filter out 1T tag or sub-10 target tags
        # Temp if conditions, need to make it better
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



        if len(cur) == 0:
            description = f'Run DNE or not in database. Let mega know if this is a mistake'
            await ctx.send(description, ephemeral=True)
            return None

        players = []
        curr_score = 999
        video = None
        for record in cur:
            if record[3] > curr_score:
                break
            players.append(record[2])
            score = record[3]
            video = record[4] if video == None else video # what if no video for any record?

            curr_score = score

        # Temp post check
        if len(video) != 0:
            video = video[0]
            
        players_string = ", ".join(players)

        wr_string = f'{"(TAS)" if is_TAS else ""} {char_name}/{stage_name} {"(" + ",".join(tags_list) + ") " if tags_list else ""}- {score} by {players_string} at {video}'
        await ctx.send(wr_string)

    @bot.command(
        name='btt-wr-list',
        description='Display the list of current BtT WRs',
        scope=GUILD_IDS,
        options=[
            # TODO: add parameters in case you want a stage total
            Option(
                name='tas',
                description='default: RTA',
                type=OptionType.BOOLEAN,
                required=False,
            ),
            Option(
                name='char',
                description='For same char on all stages',
                type=OptionType.STRING,
                required=False
            ),
        ]   
    )

    async def _btt_wr_list(ctx: CommandContext, **kwargs):
        is_TAS =  kwargs.get('tas', False)
        char_input = kwargs.get('char', None)
        if char_input != None:
            char_name = get_char_name(char_input, ALIASES)
            if char_name not in BTT_CHARACTERS:
                description = f'Please select a valid character'
                await ctx.send(description, ephemeral=True)
                return None
        
        description_lines = [
            f'Break the Targets {"TAS " if is_TAS else "RTA "}World Records\n'
        ]
        if char_input != None:
            description_lines.append(char_name + ' Mismatch\n')
        total_high_score_f = 0
        
        conn = connect()
        cur = conn.cursor()
        # TODO: add option for specific char or stage
        # should be doable and keep the code clean

        for stage in BTT_STAGES:
            cur = conn.cursor()
            # query each stage's WR
            # TODO: how do i go through each stage char, parameter if individual stage or char is selected
            #print(char_name)
            if char_input != None:
                # char_name was assigned
                sql_q = f'SELECT * FROM btt_table WHERE character=\'{char_name}\' AND stage=\'{stage}\' AND tas={is_TAS} ORDER BY score ASC, date ASC;'
            else:
                sql_q = f'SELECT * FROM btt_table WHERE character=\'{stage}\' AND stage=\'{stage}\' AND tas={is_TAS} ORDER BY score ASC, date ASC;'
            # TODO: add clause to make sure sheik shows up on zelda
            # TODO: coloquially, ICs vanilla is referred to as Ice Climbers instead of Sopo for vanilla ...
            if stage == 'Ice Climbers':
                # TEMP
                char = 'Popo'
                if char_input != None:
                    char = char_name
                sql_q = f'SELECT * FROM btt_table WHERE character=\'{char}\' AND stage=\'{stage}\' AND tas={is_TAS} ORDER BY score ASC, date ASC;'
            elif stage == 'Zelda':
                # TEMP: only for vanilla query
                char = 'Sheik'
                if char_input != None:
                    char = char_name
                sql_q = f'SELECT * FROM btt_table WHERE character=\'{char}\' AND stage=\'{stage}\' AND tas={is_TAS} ORDER BY score ASC, date ASC;'
            
                
            if stage == 'Seak' and char_input == None:
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

            description_lines.append(
                f"{char.strip()} - [{score_time}]({video}) - {', '.join(players)}"
            )

            # TEMP AGAIN JUST TO TEST CHAR QUERY
            if char_input != None:
                description_lines.pop()
                description_lines.append(
                    f"{stage.strip()} - [{score_time}]({video}) - {', '.join(players)}"
                )
            if stage.strip() != 'Seak': # have to strip bcs we're getting from the database instead of the list .... bad design idiot rename ur vars rofl
                total_high_score_f += int(time_to_frames(score_time))
            curr_score = 999


        total_high_score = frames_to_time_string(total_high_score_f)

        vanilla_RTA_playlist = "https://www.youtube.com/playlist?list=PLZmpvgqEAI7DioaEmIJG832_XKVpJHhy_"
        vanilla_TAS_playlist = "https://www.youtube.com/playlist?list=PLP-fO_NfCBaqcicPbCvGQOCIN1pL9hZyA"
        mismatch_RTA_sheet = "https://docs.google.com/spreadsheets/d/18NJ1IP7Z43l_FRe7sZnMQPte-sKn1Ddf82iiJODNo_s/edit#gid=0"
        mismatch_TAS_sheet = "https://docs.google.com/spreadsheets/d/1Nr1PDHO3UeH3oQSeEjeFNdEKrfEdsc9GxbsEWvEuFuo/edit#gid=1672544190"
        
        if not is_TAS and char_input == None:
            hyperlink = vanilla_RTA_playlist
        elif not is_TAS and char_input != None:
            hyperlink = mismatch_RTA_sheet
        elif is_TAS and char_input == None:
            hyperlink = vanilla_TAS_playlist
        elif is_TAS and char_input != None:
            hyperlink = mismatch_TAS_sheet

        total_high_score_desc = f'\nTotal High Score: [{total_high_score}]({hyperlink})'
        description_lines.append(total_high_score_desc)

        await embeds.send_embeds(description_lines, ctx)
        cur.close()
        conn.close()


    @bot.command(
        name='btt-wr-history',
        description='Display the history of a BtT pairing (includes ties)',
        scope=GUILD_IDS,
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
          
    async def _btt_wr_history(ctx: CommandContext, **kwargs):
        char_input = kwargs.get("character")
        char_name = get_char_name(char_input, ALIASES)
        if char_name not in BTT_CHARACTERS:
            description = f'Please select a valid character'
            await ctx.send(description, ephemeral=True)
            return None

        stage_input = kwargs.get('stage', char_name)
        stage_name = get_char_name(stage_input, ALIASES)

        # catch all if "ICs" is only inputted for vanilla
        if kwargs.get('stage') == None and char_name == 'Ice Climbers':
            char_name = 'Popo'
            stage_name = 'Ice Climbers'
        
        # temp catch for sheik/zelda stage name
        if stage_name == 'Sheik':
            stage_name = 'Zelda'
            original_stage_name = 'Sheik'

        # Catch all if "Sopo" is only inputted for vanilla
        if stage_name == 'Popo':
            stage_name = 'Ice Climbers'

        if stage_name not in BTT_STAGES:
            description = f'Please select a valid stage'
            await ctx.send(description, ephemeral=True)
            return None

        is_TAS = kwargs.get('tas', False)

        sus_tags = kwargs.get('tags', [])
        tags_list = sus_tags.split(',') if sus_tags else []
        if not set(tags_list).issubset(set(BTT_SUS_TAGS.keys())):
            description = f'Please select a valid SuS tag (case sensitive for now)'
            await ctx.send(description, ephemeral=True)
            return None

        conn = connect()
        sql_q = f'SELECT * FROM btt_table WHERE character=\'{char_name}\' AND stage=\'{stage_name}\' AND tas={is_TAS} ORDER BY date ASC, score DESC;' #score DESC, date ASC;'
        cur = conn.cursor()
        cur.execute(sql_q)

        if cur.rowcount == 0:
            description='Sorry, DB not filled out yet or record DNE. Please ping mega if you think there is an error'
            await ctx.send(description, ephemeral=True)
            return None

        # pre-processing for sus tags
        if tags_list:
            cur = [record for record in cur if set(tags_list).issubset(record[9])]
        # filter out 1T tag or sub-10 target tags
        # Temp if conditions, need to make it better
        if '1T' not in tags_list:
            cur = [record for record in cur if not set(['1T']).issubset(record[9])]
        if 'misfire' not in tags_list and char_name == 'Luigi': # or 'misfire' not in tags_list or 'AR' not in tags_list:
            cur = [record for record in cur if not set(['misfire']).issubset(record[9])]
        if 'AR' not in tags_list and not is_TAS:
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

        description_lines = []
        prev_score = 999

        for record in cur:
            sources = record[4]
            if len(sources) != 0:
                video = sources[0] 
            else:
                video = None
            tied_player = None
            player = record[2]
            score = record[3]
            if score >= prev_score:
                continue
            prev_score = score
            # TODO: compare date and add to history if record was beaten in the same day AND does not have timestamp
            # maybe can check YT source of video
            date = record[5].date()
            if video == None:
                description_lines.append(
                    f'({date}) - {score} - {player}'
                )
            else:
                description_lines.append(
                    f'({date}) - [{score}]({video}) - {player}'
                )
            # have to think about ties with Debug vs non debug, since they'll be same # of frames but diff displayed time
            
            # i do not think this does anything
            if tied_player != None:
               description_lines.pop()
               description_lines[-1] += f', {tied_player}'
               # SCUFFED. I AM A SCUFFED PROGRAMMER :happysquare:
               #description_lines[-1] = description_lines[0:-13] + f', {tied_player}' + description_lines[-13::]
            tied_player = None
        
        #     )
        if tags_list:
            tags_str = ",".join(tags_list)
            description_lines.append(f'SuS Tags: {tags_str}\n')
        description_lines.append(f'{"(TAS) " if is_TAS else ""}History of {char_name}/{stage_name} BTT WRs (YYYY-MM-DD)\n')
        
        # reverse list
        description_lines.reverse()

        # add to front of list
        #description_lines.insert(0, f"History of {char_name} HRC WRs (ft/m) (YYYY/MM/DD)\n")

        #print(description_lines)
        
        # TODO: handle vanilla and mm history sheet appending
        #if char_name:
        #   description_lines.append(f'\n [Full BTT RTA History Sheet](https://docs.google.com/spreadsheets/d/1oenxMdKsnD9uppK01fPtp4dD6jpqYMv4w2DKXI6plqE/edit#gid=0)')
        

        await embeds.send_embeds(description_lines, ctx)
        

        #cur.close() # not necessary if we're changing cur from cur to list
        conn.close()