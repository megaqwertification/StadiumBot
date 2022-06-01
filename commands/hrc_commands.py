
from interactions import Client, CommandContext
import embeds

from typing import List
from interactions import CommandContext, Option, OptionType, Choice

from constants import HRC_CHARACTERS, PERSONAL_GUILD_ID, STADIUM_GUILD_ID
from formulas import m_to_ft

from db import connect
# TODO: raise exceptions

def register_hrc_commands(bot: Client):
    @bot.command(
        name='hrc-wr',
        description='Query a character\'s current WR',
        scope=[PERSONAL_GUILD_ID],
        options=[
            Option(
                name='character',
                description='Choose your character',
                type=OptionType.STRING,
                required=True,
            ),
            # option: TAS, can't do until i figure out how to deal with num-frames to hit the limit
            # option: version, more relevant for HRC tbh; make this a "choices" option
            # if tas is specified, dont specify version in the SQL query..... unless?
            # ugh i guess if people want it they can have it
        ]
    )
    
    async def _hrc_wr(ctx: CommandContext, **kwargs):
        # TODO: Add TAS flag functionality
        # TODO: tas wrs are ones with lowest frames for maxed things -_-, can just order by date....??????????????? how would i say numframes????
        # TODO: learn why this is async, relearn async/await lmfao
        char_name = kwargs.get("character")
        is_tas = kwargs.get('tas', False)

        conn = connect()

        sql_q = f'SELECT * FROM hrc_table WHERE score_ft = (SELECT MAX(score_ft) FROM hrc_table WHERE character=\'{char_name}\' AND tas={is_tas}) AND character=\'{char_name}\' AND tas={is_tas} ORDER BY date ASC;' # 
        # issue if WR tie happens on same day, would have to look at timestamp
        # idk what this situation is for HRC, but defs needs to happen for BtT
        # or can just add a time column but would have to play around with the indexes...shoud
        
        # if run / other columns dont exist what do? video record?

        cur = conn.cursor()
        cur.execute(sql_q)

        # consultation from typo
        # command should have both NTSC and PAL WRs, can easily do and post the first people with both to get it
        # should ideally sort by which is larger tho, i can figure that out
        # do version differences still matter in 2022?

        # SCUFFED METHOD. see cursor object documetnation
        counter = 0
        players = []
        for record in cur:
            if counter > 0:
                # get vid if it doesn't appear for first WR holder
                players.append(record[1])
                continue
            players.append(record[1])
            score_ft = record[2]
            score_m = record[3]
            video = record[4][0] # what if there's no source on main vid...? shoudl have helper function to get the YT vid     
            # if no vid and no other WR holders, we need to get_video_record()... i guess.
            # ugh, code this later lol       
            version = record[9] # decide if this is necessary
            counter += 1
        # TODO: make sure "video" gets first source and not all sources
        # TODO: organize ties
        players_string = ", ".join(players)

            

        

        wr_string = f'{char_name} - {score_ft}ft/{score_m}m by {players_string} at {video}'
        await ctx.send(wr_string)
    
    @bot.command(
        name='hrc-wr-list',
        description='Display the list of current WRs',
        scope=[PERSONAL_GUILD_ID],
        options=[
            Option(
                name='tas',
                description='default: RTA',
                type=OptionType.BOOLEAN,
                required=False,
            ),
        ]    # make one of the options just WRs, instead of a command like this.... actually that would complicate the fuck out of this
    )

    # how to do optional commands? with default values?
    # refactor to get the highest distance(s) in the database
    async def _hrc_wr_list(ctx: CommandContext, **kwargs):
        is_TAS = kwargs.get("tas", False)
        conn = connect()
        #hrcwrs_sql = f'SELECT * FROM hrc_table WHERE character='{}' ORDER BY score_ft DESC LIMIT 1'
        # option 1: a master query that simply filters out for the best times per char
        # option 2: loop through all 25 chars to get the wrs
        # option 3: store all WRs in a separate table
        # Consider also storing over limit WRs for 
        # remember to think about ties, except ganon/ICs/Peach
        #is_TAS=True
        description_lines = [
            f'Home-Run Contest {"TAS " if is_TAS else "RTA "}World Records (ft/m)\n'
        ]
        metre_sum = 0
        cur = conn.cursor()

        for item in HRC_CHARACTERS:
            # god knows why this query works
            query = f'SELECT * FROM hrc_table WHERE score_ft = (SELECT MAX(score_ft) FROM hrc_table WHERE character=\'{item}\' AND tas={is_TAS}) AND character=\'{item}\' AND tas={is_TAS};'
            cur.execute(query)
        
            # there is 1000% a way to just query and get the top row(s) of world records, will look into it
            # TODO: handle WR ties; add player name to side, video too?

            counter = 0
            for record in cur:
                
                if counter > 0:
                    description_lines[-1] += f', {record[1]}'
                    continue
                details = {
                    "char": record[0],
                    "player" : record[1],
                    "score_ft" : record[2],
                    "score_m" : record[3],
                    "sources" : record[4],
                    "date" : record[5],
                    "tas" : record[6],
                    "emulator" : record[7],
                    "tags" : record[8],
                    "version" : record[9]
                }
                # don't need all these details
                char = details["char"]
                score_ft = details["score_ft"]
                score_m = details["score_m"]
                player = details["player"]
                if len(details['sources']) != 0: # should just make this "not empty" or something lol
                    video = details["sources"][0]
                else:
                    video = "a" # temporary 
                
                metre_sum += float(score_m)
                
                # Hardcode Ganon/ICs RTA ties for readability
                if (char.strip() == "Ganondorf" or char.strip() == "Ice Climbers") and not is_TAS: # strip newlines
                    player = "many"

                # TODO: Limit WRs TAS implementation, even if scuffed
                # if limit in tags, 
                # limit_WRs = { "Ganondorf" : 476, "Ice Climbers" : 406, "Peach" : 600}

                description_lines.append(
                    f"{char} - [{score_ft}ft/{score_m}m]({video}) - \t {player}"
                    # mobile formatting is weird  :(
                )
                counter += 1

        metre_sum = round(metre_sum,1)
        ft_sum = m_to_ft(metre_sum)

        # TODO: add YT playlist links? 

        total_distance = f'\nTotal Distance (ft/m): {ft_sum}/{metre_sum}'
        description_lines.append(total_distance)

        await embeds.send_embeds(description_lines, ctx)
        cur.close()
        conn.close()

    @bot.command(
        name='hrc-history',
        description='Display WR history for HRC character', # should i add WR ties lol. if possible? who knows at this point
        scope=[PERSONAL_GUILD_ID],
        options=[
            # TODO: evalute if choices can be from list
            Option(
                name='character',
                description='Choose your character',
                type=OptionType.STRING,
                required=True,
                #choices = [Choice(name="character", value=char ) for char in HRC_CHARACTERS]
            ),
            # TODO: Add TAS option flag
            Option(
                name='tas',
                description='RTA vs. TAS (default RTA)', # TODO: standardize descriptions of parameters
                type=OptionType.BOOLEAN,
                required=False,
            )
        ],
    )

    async def _hrc_history(ctx: CommandContext, **kwargs):
        # TODO: add TAS flag (switch case which just affects the query "AND tas=false")
        # TODO: experiment with a date argument so that you can get the history of the record at a certain date
        # TODO: raise value errors
        char_name = kwargs.get("character")
        is_TAS = kwargs.get('tas', False)
        conn = connect()

        # option 1: a master query that simply filters out for the best times per char
        # option 2: loop through all 25 chars to get the wrs
        # option 3: store all WRs in a separate table
        # remember to think about ties, except ganon/ICs

        sql_q = f'SELECT * FROM hrc_table WHERE character=\'{char_name}\' and tas={is_TAS} ORDER BY date ASC;'
        cur = conn.cursor()
        cur.execute(sql_q) # make an f-string that gets the best score for each char, what about WR ties? can
        # i hard code "many" for ICs and Ganon? and just link to marth1 / joe bushman's vids?
        # TODO: get this working for each character
        # TODO: get this working so you dont have to grammatically be correct for each char
        # TODO: add error exception if someone enters an unknown character
        # TODO: make sure ties are not included in this, 
        # TODO: decide if you're going to include WR ties with links
        # TODO: add dates to front? or elsewhere? if so do i do it for each tie? would get preeeetty hectic but its the point of a history command
        # TODO: make this into a table format of some sort

        description_lines = []

        metre_sum = 0
        prev_score = 0

        for record in cur:
            details = {
                # possible to index by sql column name instead of integer?
                "char": record[0],
                "player" : record[1],
                "score_ft" : record[2],
                "score_m" : record[3],
                "sources" : record[4],
                "date" : record[5].date(),
        #         "tas" : record[6],
        #         "emulator" : record[7],
        #         "tags" : record[8],
        #         "version" : record[9]
            }
            #print(details['sources'])
            char = details["char"]
            score_ft = details["score_ft"]
            score_m = details["score_m"]
            player = details["player"]
            date = details["date"]

            if len(details['sources']) != 0: # should just make this "not empty" or something lol
                video = details["sources"][0]
            else:
                video = None
            tied_player = None
            #     metre_sum += float(score_m)

            #     description_lines.append(
            #         f"{char} - \t [{score_ft}ft/{score_m}m]({video}) - \t {player}"


            # running max
            #prev_score = score_ft
            #print(description_lines[-1])
            if score_ft <= prev_score: # use '<' if including ties
                #prev_score = score_ft
                continue
            # REMOVE TIES
            #elif score_ft == prev_score:
            #    # encountered a tie, append player name
            #    tied_player = record[1]

            prev_score = score_ft
            if video == None:
                description_lines.append(
                    f'({date}) - \t {score_ft}ft/{score_m}m - {player}'# ({date})'
                    # no video shows up weird on mobile
                )    
            else:
                description_lines.append(
                    f'({date}) - [{score_ft}ft/{score_m}m]({video}) - {player}' # ({date})'
                    # no video shows up weird on mobile
                )

            #if tied_player != None:
            #    description_lines.pop()
            #    description_lines[-1] += f', {tied_player}'
            #    # SCUFFED. I AM A SCUFFED PROGRAMMER
            #    #description_lines[-1] = description_lines[0:-13] + f', {tied_player}' + description_lines[-13::]
            #tied_player = None
        
        #     )

        metre_sum = round(metre_sum,1)
        const = 3.2809688582
        ft_sum =  (metre_sum * const * 10 )// 10 # temp, need precise

        description_lines.append(f'{"(TAS) " if is_TAS else ""}History of {char_name} HRC WRs (ft/m) (YYYY/MM/DD)\n')
        # reverse list
        description_lines.reverse()

        # add to front of list
        #description_lines.insert(0, f"History of {char_name} HRC WRs (ft/m) (YYYY/MM/DD)\n")

        #print(description_lines)

        await embeds.send_embeds(description_lines, ctx)
        # TODO: add links to history sheet?

        cur.close()
        conn.close()
       

    





        


# future commands
# top 10 char lookup (doable, just limit 10. would need to format "ties" tho looool)
    # i.e. make sure if you have 12 people total, you format that
# player lookup (not just hrc but for each mode? nah)
# top 10 THS lookup (ugh)
# general ft->m and m->ft formula

# add record -> no source? add_source(). wrong version? change_version() update tags? update_tags(). no date? update datetime()
# any other things? if it was wrongly attribute to like, emu you should just change manually