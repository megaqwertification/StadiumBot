from constants import BTT_CHARACTERS, HRC_CHARACTERS, TENMM_CHARACTERS, GUILD_IDS, VERSIONS, ALIASES, BTT_STAGES
from formulas import get_char_name

from db import connect

from helper_functions_WIP.btt_helper_functions import get_stage_total, get_char_total, get_current_btt_wr
import embeds

from interactions import Client, CommandContext, Permissions, Option, OptionType, Choice

# TODO: verify insertions are valid. eg. make sure it's ntsc1.02 and not ntsc 1.02
# can cross-ref with constants

# HELPER functions

# GENERAL
#def check_sources(sources: list ) -> :
#    check_src_sql = 

# HRC



def register_owner_commands(bot: Client):
    @bot.command(
        name='add-btt-record',
        description='Add BTT record',
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
                description='Choose your stage',
                type=OptionType.STRING,
                required=True,
            ),
            Option(
                name='player',
                description='Player',
                type=OptionType.STRING,
                required=True,
            ),
            # require at least one of the two
            Option(
                name='score',
                description='Score decimal',
                type=OptionType.NUMBER,
                required=True,                
            ),
            Option(
                name='sources',
                description='sources',
                type=OptionType.STRING,
                required=False,                
            ),
            Option(
                name='date',
                description='yyyy-mm-dd',
                type=OptionType.STRING,
                required=False,                
            ),
            Option(
                name='tas',
                description='tas (default False)',
                type=OptionType.BOOLEAN,
                required=False,                
            ),
            Option(
                name='emulator',
                description='Played on emu (default True)',
                type=OptionType.BOOLEAN,
                required=False,                
            ),
            Option(
                name='debug',
                description='Played on debug (default False)',
                type=OptionType.BOOLEAN,
                required=False,                
            ),
            Option(
                name='tags',
                description='add tags (case sensitive, CSV)',
                type=OptionType.STRING,
                required=False,                
            ),
            Option(
                name='ver',
                description='version (default NTSC1.02)',
                type=OptionType.STRING,
                choices=[
                    Choice(
                        name='NTSC1.02',
                        value='NTSC1.02',
                    ),
                    Choice(
                        name='PAL',
                        value='PAL',
                    ),
                    Choice(
                        name='NTSC1.00',
                        value='NTSC1.00',
                    ),
                    Choice(
                        name='NTSC1.01',
                        value='NTSC1.01',
                    ),
                ],
                required=False,                
            ),
        ],

        #default_member_permissions=Permissions.ADMINISTRATOR    
    )

    async def _add_btt_record(ctx: CommandContext, **kwargs):
        if ctx.author.id != str(199563168345882624):
            description = f'Unauthorized use of command, only the bot owner can add records'
            await ctx.send(description, ephemeral=True)
            return None
        await ctx.defer()

        char_input = kwargs.get("character")
        char = get_char_name(char_input, ALIASES)
        # TODO: raise error if character isn't in database
        # TODO: allow for zelda and sheik individual records 
        if char not in BTT_CHARACTERS:
            description = f'Please select a valid char ({char} invalid)'
            await ctx.send(description, ephemeral=True)
            return None

        stage_input = kwargs.get('stage')
        stage = get_char_name(stage_input, ALIASES)
        if stage not in BTT_STAGES:
            description = f'Please select a valid stage ({stage} invalid)'
            await ctx.send(description, ephemeral=True)
            return None
        player = kwargs.get("player")
        # TODO: have to raise some sort of exception if player doesn't exist.... in database table?
        
        score = kwargs.get("score") # if score m isn't given or something


        sources = kwargs.get('sources', '') 
        # TODO: add check_source function and update source function
        
        date = kwargs.get('date', '') # default system time so it auto corrects to UTC+00:00, when you're submitting. otherwise unknown
        # TODO: add check_date function

        is_tas = kwargs.get('tas', False)
        is_emulator = kwargs.get('emulator', True)
        is_debug = kwargs.get('debug', False)
        tags = kwargs.get('tags', '') 
        # TODO: make a check tags function and update tags function

        ver = kwargs.get('ver', 'NTSC1.02')
        
        score_str = '{:.2f}'.format(score)
        # TODO: raise exceptions
        # TODO: check if already in the database by comparing char, player, score_ft, score_m, and ver... and emu?? let's add this functionality later
        # TODO: check if you're adding a new source 
        # TODO: if exists, update source and other null values using pqsl UPDATE
        # TODO: check if it's a tie (actually dont have to if you properly implement the hrc commands)
        # TODO: if tas, has to be equal to or greater than RTA, actually no bcs wak's old link TAS is worse than RTA
        # so maybe compare dates idk. unless an RTA record is maxed , 

        sources_str = "{" + sources + "}"
        tags_str = "{" + tags + "}"

        video = sources.split(',')[0]
        description_lines = []


        # Obtain Previous WR details
        prev_wr = get_current_btt_wr(char, stage, is_tas, tags)
        old_stage_total = get_stage_total(stage, is_tas)
        old_char_total = get_char_total(char, is_tas)


        conn = connect()
        sql_q = f"INSERT INTO btt_table VALUES('{char}', '{stage}', '{player}', {score_str}, '{sources_str}', '{date}', {is_tas}, {is_emulator}, {is_debug}, '{tags_str}', '{ver}');"
        cur = conn.cursor()
        cur.execute(sql_q)
        conn.commit()

        improved_str = f'Improved BTT{" TAS" if is_tas else ""} record: {char}/{stage} from [{prev_wr[3]} by {prev_wr[2]}]({prev_wr[4].pop()}) to [{score_str} by {player}]({video}) {tags if tags != "" else ""}'
        description_lines.append(improved_str)


        # Obtain new WR details
        new_char_total = get_char_total(char, is_tas)
        new_stage_total = get_stage_total(stage, is_tas)

        char_total_str = f'{char} character{" TAS" if is_tas else ""} total improved from {old_char_total[1]} to {new_char_total[1]}'
        description_lines.append(char_total_str)
        stage_total_str = f'{stage} stage{" TAS" if is_tas else ""} total improved from {old_stage_total[1]} to {new_stage_total[1]}'
        description_lines.append(stage_total_str)

        # TODO: test None/NULL values, tags one is for sure wrong -> change to 'NULL' or empty sets
        # TODO: test datetime values

        
        conn.commit()
        # TODO: update desc if it needs tags or something
        #description = f'Added BTT{" TAS" if is_tas else ""} record: {char}/{stage} - {score_str} by {player} at <{video}> ({tags})'
        await embeds.send_embeds(description_lines, ctx)


    @bot.command(
        name='add-hrc-record',
        description='Add HRC record',
        scope=GUILD_IDS,
        options=[
            Option(
                name='character',
                description='Choose your character',
                type=OptionType.STRING,
                required=True,
            ),
            Option(
                name='player',
                description='Player',
                type=OptionType.STRING,
                required=True,
            ),
            # require at least one of the two
            Option(
                name='score_ft',
                description='Score decimal',
                type=OptionType.NUMBER,
                required=True,                
            ),
            Option(
                name='score_m',
                description='Score decimal',
                type=OptionType.NUMBER,
                required=True,                
            ),
            Option(
                name='sources',
                description='sources',
                type=OptionType.STRING,
                required=False,                
            ),
            Option(
                name='date',
                description='yyyy-mm-dd',
                type=OptionType.STRING,
                required=False,                
            ),
            Option(
                name='tas',
                description='tas (default False)',
                type=OptionType.BOOLEAN,
                required=False,                
            ),
            Option(
                name='emulator',
                description='Played on emu (default True)',
                type=OptionType.BOOLEAN,
                required=False,                
            ),
            Option(
                name='tags',
                description='add tags (case sensitive, CSV)',
                type=OptionType.STRING,
                required=False,                
            ),
            Option(
                name='ver',
                description='version (default NTSC1.02)',
                type=OptionType.STRING,
                choices=[
                    Choice(
                        name='NTSC1.02',
                        value='NTSC1.02',
                    ),
                    Choice(
                        name='PAL',
                        value='PAL',
                    ),
                    Choice(
                        name='NTSC1.00',
                        value='NTSC1.00',
                    ),
                    Choice(
                        name='NTSC1.01',
                        value='NTSC1.01',
                    ),
                ],
                required=False,                
            ),
        ],

        #default_member_permissions=Permissions.ADMINISTRATOR    
    )

    async def _add_hrc_record(ctx: CommandContext, **kwargs):
        if ctx.author.id != str(199563168345882624):
            description = f'Unauthorized use of command, only the bot owner can add records'
            await ctx.send(description, ephemeral=True)
            return None
        char_input = kwargs.get("character")
        char = get_char_name(char_input, ALIASES)
        # TODO: raise error if character isn't in database
        # TODO: allow for zelda and sheik individual records 
        if char not in HRC_CHARACTERS:
            description = f'Please select a valid char ({char} invalid)'
            await ctx.send(description, ephemeral=True)
            return None

        player = kwargs.get("player")
        # TODO: have to raise some sort of exception if player doesn't exist.... in database table?
        
        score_ft = kwargs.get("score_ft") # if score m isn't given or something
        score_m = kwargs.get("score_m")

        sources = kwargs.get('sources', '') 
        # TODO: add check_source function and update source function
        
        date = kwargs.get('date', '') # default system time so it auto corrects to UTC+00:00, when you're submitting. otherwise unknown
        # TODO: add check_date function

        is_tas = kwargs.get('tas', False)
        is_emulator = kwargs.get('emulator', True)
        tags = kwargs.get('tags', '') 
        # TODO: make a check tags function and update tags function

        ver = kwargs.get('ver', 'NTSC1.02')
        
        score_ft_str = '{:.1f}'.format(score_ft)
        score_m_str = '{:.1f}'.format(score_m)

        # TODO: raise exceptions
        # TODO: check if already in the database by comparing char, player, score_ft, score_m, and ver... and emu?? let's add this functionality later
        # TODO: check if you're adding a new source 
        # TODO: if exists, update source and other null values using pqsl UPDATE
        # TODO: check if it's a tie (actually dont have to if you properly implement the hrc commands)
        # TODO: if tas, has to be equal to or greater than RTA, actually no bcs wak's old link TAS is worse than RTA
        # so maybe compare dates idk. unless an RTA record is maxed , 

        sources_str = "{" + sources + "}"
        tags_str = "{" + tags + "}"

        conn = connect()
        sql_q = f"INSERT INTO hrc_table VALUES('{char}', '{player}', {score_ft_str}, {score_m_str}, '{sources_str}', '{date}', {is_tas}, {is_emulator}, '{tags_str}', '{ver}');"
        cur = conn.cursor()
        cur.execute(sql_q)

        # TODO: test None/NULL values, tags one is for sure wrong -> change to 'NULL' or empty sets
        # TODO: test datetime values

        video = sources.split(',')[0]
        conn.commit()
        # TODO: update desc if it needs tags or something
        description = f'Added HRC{" TAS" if is_tas else ""} record: {char} - {score_ft_str}ft/{score_m_str}m by {player} at <{video}> ({tags})'
        await ctx.send(description)
    
    
    # add 10mm record
    @bot.command(
        name='add-10mm-record',
        description='Add 10MM record',
        scope=GUILD_IDS,
        options=[
            Option(
                name='character',
                description='Choose your character',
                type=OptionType.STRING,
                required=True,
            ),
            Option(
                name='player',
                description='Player',
                type=OptionType.STRING,
                required=True,
            ),
            # require at least one of the two
            Option(
                name='score',
                description='Score decimal',
                type=OptionType.NUMBER,
                required=True,                
            ),
            Option(
                name='sources',
                description='sources',
                type=OptionType.STRING,
                required=False,                
            ),
            Option(
                name='date',
                description='yyyy-mm-dd',
                type=OptionType.STRING,
                required=False,                
            ),
            Option(
                name='tas',
                description='tas (default False)',
                type=OptionType.BOOLEAN,
                required=False,                
            ),
            Option(
                name='emulator',
                description='Played on emu (default True)',
                type=OptionType.BOOLEAN,
                required=False,                
            ),
            Option(
                name='tags',
                description='add tags (case sensitive, CSV)',
                type=OptionType.STRING,
                required=False,                
            ),
            Option(
                name='ver',
                description='version (default NTSC1.02)',
                type=OptionType.STRING,
                choices=[
                    Choice(
                        name='NTSC1.02',
                        value='NTSC1.02',
                    ),
                    Choice(
                        name='PAL',
                        value='PAL',
                    ),
                    Choice(
                        name='NTSC1.00',
                        value='NTSC1.00',
                    ),
                    Choice(
                        name='NTSC1.01',
                        value='NTSC1.01',
                    ),
                ],
                required=False,                
            ),
        ],

        #default_member_permissions=Permissions.ADMINISTRATOR    
    )

    async def _add_10mm_record(ctx: CommandContext, **kwargs):
        if ctx.author.id != str(199563168345882624):
            description = f'Unauthorized use of command, only the bot owner can add records'
            await ctx.send(description, ephemeral=True)
            return None

        char_input = kwargs.get("character")
        char = get_char_name(char_input, ALIASES)
        # TODO: raise error if character isn't in database
        # TODO: allow for zelda and sheik individual records 
        if char not in TENMM_CHARACTERS:
            description = f'Please select a valid char ({char} invalid)'
            await ctx.send(description, ephemeral=True)
            return None

        player = kwargs.get("player")
        # TODO: have to raise some sort of exception if player doesn't exist.... in database table?

        score = kwargs.get("score")
        score_str = '{:.2f}'.format(score)

        sources = kwargs.get('sources', '') 
        # TODO: add check_source function and update source function
        
        date = kwargs.get('date', '') # default system time so it auto corrects to UTC+00:00, when you're submitting. otherwise unknown
        # TODO: add check_date function

        is_tas = kwargs.get('tas', False)
        is_emulator = kwargs.get('emulator', True)
        tags = kwargs.get('tags', '') 
        # TODO: make a check tags function and update tags function

        ver = kwargs.get('ver', 'NTSC1.02')
        


        # TODO: raise exceptions
        # TODO: check if already in the database by comparing char, player, score_ft, score_m, and ver... and emu?? let's add this functionality later
        # TODO: check if you're adding a new source 
        # TODO: if exists, update source and other null values using pqsl UPDATE
        # TODO: check if it's a tie (actually dont have to if you properly implement the hrc commands)
        # TODO: if tas, has to be equal to or greater than RTA, actually no bcs wak's old link TAS is worse than RTA
        # so maybe compare dates idk. unless an RTA record is maxed , 

        sources_str = "{" + sources + "}"
        tags_str = "{" + tags + "}"

        conn = connect()
        sql_q = f"INSERT INTO ten_mm_table VALUES('{char}', '{player}', {score_str}, '{sources_str}', '{date}', {is_tas}, {is_emulator}, '{tags_str}', '{ver}');"
        cur = conn.cursor()
        cur.execute(sql_q)

        # TODO: test None/NULL values, tags one is for sure wrong -> change to 'NULL' or empty sets
        # TODO: test datetime values

        video = sources.split(',')[0]
        conn.commit()
        # TODO: update desc if it needs tags or something
        description = f'Added 10MM{" TAS" if is_tas else ""} record: {char} - {score_str} by {player} at <{video}> ({tags})'
        await ctx.send(description)

    @bot.command(
        name='add-event-record',
        description='Add Event Match record',
        scope=GUILD_IDS,
        options=[
            Option(
                name='event-id',
                description='Choose event ID',
                type=OptionType.NUMBER,
                required=True,
            ),
            Option(
                name='player',
                description='Player',
                type=OptionType.STRING,
                required=True,
            ),
            # require at least one of the two
            Option(
                name='type',
                description='timed or scored',
                type=OptionType.STRING,
                choices=[
                    Choice(
                        name='timed',
                        value='timed',
                    ),
                    Choice(
                        name='scored',
                        value='scored',
                    ),
                ],
                required=True,                
            ),
            Option(
                name='score',
                description='Score decimal for timed, int for KOs',
                type=OptionType.NUMBER,
                required=True,                
            ),
            Option(
                name='sources',
                description='sources',
                type=OptionType.STRING,
                required=False,                
            ),
            Option(
                name='date',
                description='yyyy-mm-dd',
                type=OptionType.STRING,
                required=False,                
            ),
            Option(
                name='tas',
                description='tas (default False)',
                type=OptionType.BOOLEAN,
                required=False,                
            ),
            Option(
                name='emulator',
                description='Played on emu (default True)',
                type=OptionType.BOOLEAN,
                required=False,                
            ),
            Option(
                name='tags',
                description='add tags (case sensitive, CSV)',
                type=OptionType.STRING,
                required=False,                
            ),
            Option(
                name='ver',
                description='version (default NTSC1.02)',
                type=OptionType.STRING,
                choices=[
                    Choice(
                        name='NTSC1.02',
                        value='NTSC1.02',
                    ),
                    Choice(
                        name='PAL',
                        value='PAL',
                    ),
                    Choice(
                        name='NTSC1.00',
                        value='NTSC1.00',
                    ),
                    Choice(
                        name='NTSC1.01',
                        value='NTSC1.01',
                    ),
                ],
                required=False,                
            ),
        ],

        #default_member_permissions=Permissions.ADMINISTRATOR    
    )

    async def _add_event_record(ctx: CommandContext, **kwargs):
        if ctx.author.id != str(199563168345882624):
            description = f'Unauthorized use of command, only the bot owner can add records'
            await ctx.send(description, ephemeral=True)
            return None

        event_id = int(kwargs.get('event-id'))
        if event_id not in range(1,52):
            description = f'Please select a valid event ID'
            await ctx.send(description, ephemeral=True)
            return None

        player = kwargs.get("player")
        # TODO: have to raise some sort of exception if player doesn't exist.... in database table?
        
        event_type = kwargs.get("type")
        score = kwargs.get("score")
        if event_type == 'scored':
            score = int(score)
        else:
            score = '{:.2f}'.format(score)

        sources = kwargs.get('sources', '') 
        # TODO: add check_source function and update source function
        
        date = kwargs.get('date', '') # default system time so it auto corrects to UTC+00:00, when you're submitting. otherwise unknown
        # TODO: add check_date function

        is_tas = kwargs.get('tas', False)
        is_emulator = kwargs.get('emulator', True)
        tags = kwargs.get('tags', '') 
        # TODO: make a check tags function and update tags function

        ver = kwargs.get('ver', 'NTSC1.02')
        


        # TODO: raise exceptions
        # TODO: check if already in the database by comparing char, player, score_ft, score_m, and ver... and emu?? let's add this functionality later
        # TODO: check if you're adding a new source 
        # TODO: if exists, update source and other null values using pqsl UPDATE
        # TODO: check if it's a tie (actually dont have to if you properly implement the hrc commands)
        # TODO: if tas, has to be equal to or greater than RTA, actually no bcs wak's old link TAS is worse than RTA
        # so maybe compare dates idk. unless an RTA record is maxed , 

        sources_str = "{" + sources + "}"
        tags_str = "{" + tags + "}"

        conn = connect()
        sql_q = f"INSERT INTO event_table VALUES({event_id}, '{player}', '{event_type}', {score}, '{sources_str}', '{date}', {is_tas}, {is_emulator}, '{tags_str}', '{ver}');"
        cur = conn.cursor()
        cur.execute(sql_q)

        # TODO: test None/NULL values, tags one is for sure wrong -> change to 'NULL' or empty sets
        # TODO: test datetime values

        video = sources.split(',')[0]
        conn.commit()
        # TODO: update desc if it needs tags or something
        description = f'Added Event {event_id}{" TAS" if is_tas else ""} record: {score} {"KOs" if event_type=="scored" else ""}by {player} at <{video}>' # TODO: add TAGS in print statement like the other commands
        await ctx.send(description)