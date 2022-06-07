from constants import HRC_CHARACTERS, PERSONAL_GUILD_ID, VERSIONS
from db import connect

from interactions import Client, CommandContext, Permissions, Option, OptionType

# TODO: verify insertions are valid. eg. make sure it's ntsc1.02 and not ntsc 1.02
# can cross-ref with constants

# HELPER functions

# GENERAL
#def check_sources(sources: list ) -> :
#    check_src_sql = 

# HRC



def register_owner_commands(bot: Client):
    @bot.command(
        name='add-hrc-record',
        description='Add a record to one of the modes',
        scope=[PERSONAL_GUILD_ID],
        options=[
            Option(
                name='character',
                description='Choose your character',
                type=OptionType.STRING,
                required=True,
            ),
            Option(
                name='player',
                description='what name',
                type=OptionType.STRING,
                required=True,
            ),
            # require at least one of the two
            Option(
                name='score_ft',
                description='Feet score',
                type=OptionType.NUMBER,
                required=True,                
            ),
            Option(
                name='score_m',
                description='metre_score',
                type=OptionType.NUMBER,
                required=True,                
            ),
            Option(
                name='sources',
                description='sources ',
                type=OptionType.STRING,
                required=False,                
            ),
            Option(
                name='tas',
                description='test',
                type=OptionType.BOOLEAN,
                required=False,                
            ),
            Option(
                name='emulator',
                description='Played on emu',
                type=OptionType.BOOLEAN,
                required=False,                
            ),
            Option(
                name='date',
                description='yyyy mm dd',
                type=OptionType.STRING,
                required=False,                
            ),
            Option(
                name='tags',
                description='add tags',
                type=OptionType.STRING,
                required=False,                
            ),
            Option(
                name='ver',
                description='version',
                type=OptionType.STRING,
                required=False,                
            ),
        ],

        default_member_permissions=Permissions.ADMINISTRATOR    
    )

    async def _add_hrc_record(ctx: CommandContext, **kwargs):
        char = kwargs.get("character")
        # TODO: raise error if character isn't in database
        # TODO: allow for zelda and sheik individual records 
        if char not in HRC_CHARACTERS:
            raise ValueError(f'Please select a valid character')
        
        player = kwargs.get("player")
        # TODO: have to raise some sort of exception if player doesn't exist.... in database table?
        
        score_ft = kwargs.get("score_ft") # if score m isn't given or something
        score_m = kwargs.get("score_m") # verify score and you only need one tbh
        # TODO: verify metre and feet scores
        

        sources = kwargs.get('sources', '') 
        # TODO: add check_source function and update source function
        
        date = kwargs.get('date', '') # default system time so it auto corrects to UTC+00:00, when you're submitting. otherwise unknown
        # TODO: add check_date function

        is_tas = kwargs.get('tas', False)
        is_emulator = kwargs.get('emulator', False)
        tags = kwargs.get('tags', '') 
        # TODO: make a check tags function and update tags function

        ver = kwargs.get('ver', '')
        # TODO: add regex for all of these (e.g. match NTSC1.02 with ntsc1.02 with NTSC 1.02 etc.)
        if ver not in VERSIONS:
            raise ValueError(f'Please select a valid version')
        
        
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
        sql_q = f"INSERT INTO hrc_table VALUES('{char}', '{player}', {score_ft}, {score_m}, '{sources_str}', '{date}', {is_tas}, {is_emulator}, '{tags_str}', '{ver}');"
        cur = conn.cursor()
        cur.execute(sql_q)

        # TODO: test None/NULL values, tags one is for sure wrong -> change to 'NULL' or empty sets
        # TODO: test datetime values

        video = sources.split(',')[0]
        conn.commit()
        description = f'Added HRC record: {char} - {score_ft}ft/{score_m}m by {player} at {video}'
        await ctx.send(description)


#how to add with default/null values?
# do i do this on the python level or DB level
    # @bot.command(
    #     name='add-btt-record',
    #     description='Add a record to one of the modes',
    #     scope=[PERSONAL_GUILD_ID],
    #     options=[
    #         Option(
    #             name='mode',
    #             description='Choose your mode',
    #             type=OptionType.STRING,
    #             required=True,
    #             # how to set the requirements
    #         ),
    #     ],
    #     default_member_permissions=Permissions.ADMINISTRATOR    
    # )
    # async def _add_btt_record(ctx: CommandContext, **kwargs):
    #     mode: str = kwargs['mode']
    #     # add to database
    #     # conn
        
    #     return None
    # @bot.command(
    #     name='add-10mm-record',
    #     description='Add a record to one of the modes',
    #     scope=[PERSONAL_GUILD_ID],
    #     options=[
    #         Option(
    #             name='mode',
    #             description='Choose your mode',
    #             type=OptionType.STRING,
    #             required=True,
    #             # how to set the requirements
    #         ),
    #     ],
    #     default_member_permissions=Permissions.ADMINISTRATOR    
    # )
    # async def _add_10mm_record(ctx: CommandContext, **kwargs):
    #     mode: str = kwargs['mode']
    #     # add to database
    #     # conn
        
    #     return None


    # @bot.command(
    #     name='add-event-record',
    #     description='Add a record to one of the modes',
    #     scope=[PERSONAL_GUILD_ID],
    #     options=[
    #         Option(
    #             name='mode',
    #             description='Choose your mode',
    #             type=OptionType.STRING,
    #             required=True,
    #             # how to set the requirements
    #         ),
    #     ],
    #     default_member_permissions=Permissions.ADMINISTRATOR    
    # )
    # async def _add_event_record(ctx: CommandContext, **kwargs):
    #     #mode: str = kwargs['mode']
    #     # add to database
    #     # conn
    #     # 
    #     return None