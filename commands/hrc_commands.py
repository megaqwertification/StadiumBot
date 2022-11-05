
from interactions import Client, CommandContext
import embeds

from typing import List
from interactions import CommandContext, Option, OptionType, Choice

from constants import ALIASES, HRC_SUS_TAGS, HRC_CHARACTERS, PERSONAL_GUILD_ID, STADIUM_GUILD_ID
from formulas import m_to_ft, get_char_name

from db import connect

def register_hrc_commands(bot: Client):
    @bot.command(
        name='hrc-wr',
        description='Query a character\'s current WR',
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
                description='RTA vs. TAS (default RTA)',
                type=OptionType.BOOLEAN,
                required=False
            ),
            # Option(
            #     name='tags',
            #     description='SuS Tag(s) (separate by comma, case sensitive)',
            #     type=OptionType.STRING,
            #     required=False
            # )
        ]
    )
    
    async def _hrc_wr(ctx: CommandContext, **kwargs):
        char_input = kwargs.get("character")
        char_name = get_char_name(char_input, ALIASES)
        if char_name not in HRC_CHARACTERS:
            raise ValueError(f'Please select a valid character')
        is_TAS = kwargs.get('tas', False)

        # TODO: add error checking for SuS Tags
        sus_tags = kwargs.get("tags", None)
        tags_list = [tag.strip() for tag in sus_tags.split(',')] if sus_tags else []
        if not set(tags_list).issubset(set(HRC_SUS_TAGS.keys())):
            raise ValueError('One or more sus tags DNE')

        conn = connect()
        sql_q = f'SELECT * FROM hrc_table WHERE character=\'{char_name}\' AND tas={is_TAS} ORDER BY score_ft DESC, date ASC;'
        cur = conn.cursor()
        cur.execute(sql_q)

        # pre-processing for sus tags
        if tags_list:
            cur = [record for record in cur if set(tags_list).issubset(record[8])]

        players = []
        curr_score_ft = 0
        video = None
        for record in cur:
            if record[2] < curr_score_ft:
                break
            players.append(record[1])
            score_ft = record[2]
            score_m = record[3]
            video = record[4][0] if video == None else video # what if no video for any record?

            curr_score_ft = score_ft

        players_string = ", ".join(players)

        wr_string = f'{"(TAS)" if is_TAS else ""} {char_name} {"(" + ",".join(tags_list) + ") " if tags_list else ""}- {score_ft}ft/{score_m}m by {players_string} at {video}'
        await ctx.send(wr_string)
    
    @bot.command(
        name='hrc-wr-list',
        description='Display the list of current WRs',
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

    async def _hrc_wr_list(ctx: CommandContext, **kwargs):
        is_TAS = kwargs.get("tas", False)
        conn = connect()

        description_lines = [
            f'Home-Run Contest {"TAS " if is_TAS else "RTA "}World Records\n'
        ]
        metre_sum = 0
        cur = conn.cursor()

        for item in HRC_CHARACTERS[:-2]:
            query = f'SELECT * FROM hrc_table WHERE score_ft = (SELECT MAX(score_ft) FROM hrc_table WHERE character=\'{item}\' AND tas={is_TAS}) AND character=\'{item}\' AND tas={is_TAS};'
            cur.execute(query)
            
            counter = 0
            for record in cur:
                if counter > 0:
                    description_lines[-1] += f', {record[1]}'
                    continue
                # TODO: consolidate this
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
                char = char.strip()
                score_ft = details["score_ft"]
                score_m = details["score_m"]
                player = details["player"]
                if len(details['sources']) != 0: # should just make this "not empty" or something lol
                    video = details["sources"][0]
                else:
                    # TODO: implement video record rather than "none"
                    video = None # temporary 
                    
                
                metre_sum += float(score_m)
                
                # Hardcode Ganon/ICs RTA ties for readability
                if (char.strip() == "Ganondorf" or char.strip() == "Ice Climbers") and not is_TAS:
                    player = "many"

                description_lines.append(
                    f"{char} - [{score_ft}ft/{score_m}m]({video}) - {player}"
                )
                counter += 1

        metre_sum = round(metre_sum,1)
        ft_sum = m_to_ft(metre_sum)

        total_distance = f'\nTotal Distance: [{ft_sum}ft/{metre_sum}m]({"https://www.youtube.com/playlist?list=PLP-fO_NfCBaqUn-Ffu9prgx7n7Qu-e5HJ" if is_TAS else "https://www.youtube.com/playlist?list=PLP-fO_NfCBar7sV9wCR0G0aJHDDDru-T3"})'
        description_lines.append(total_distance)

        await embeds.send_embeds(description_lines, ctx)
        cur.close()
        conn.close()

    # @bot.command(
    #     name='hrc-history',
    #     description='Display WR history for HRC character', # should i add WR ties lol. if possible? who knows at this point
    #     scope=[PERSONAL_GUILD_ID],
    #     options=[
    #         # TODO: evalute if choices can be from list
    #         Option(
    #             name='character',
    #             description='Choose your character',
    #             type=OptionType.STRING,
    #             required=True,
    #             #choices = [Choice(name="character", value=char ) for char in HRC_CHARACTERS]
    #         ),
    #         Option(
    #             name='tas',
    #             description='RTA vs. TAS (default RTA)', # TODO: standardize descriptions of parameters
    #             type=OptionType.BOOLEAN,
    #             required=False,
    #         )
    #     ],
    # )

    # async def _hrc_history(ctx: CommandContext, **kwargs):
    #     # TODO: add TAS flag (switch case which just affects the query "AND tas=false")
    #     # TODO: experiment with a date argument so that you can get the history of the record at a certain date
    #     # TODO: raise value errors
    #     char_name = kwargs.get("character")
    #     is_TAS = kwargs.get('tas', False)
    #     conn = connect()

    #     # option 1: a master query that simply filters out for the best times per char
    #     # option 2: loop through all 25 chars to get the wrs
    #     # option 3: store all WRs in a separate table
    #     # remember to think about ties, except ganon/ICs

    #     sql_q = f'SELECT * FROM hrc_table WHERE character=\'{char_name}\' and tas={is_TAS} ORDER BY date ASC;'
    #     cur = conn.cursor()
    #     cur.execute(sql_q) # make an f-string that gets the best score for each char, what about WR ties? can
    #     # i hard code "many" for ICs and Ganon? and just link to marth1 / joe bushman's vids?
    #     # TODO: get this working for each character
    #     # TODO: get this working so you dont have to grammatically be correct for each char
    #     # TODO: add error exception if someone enters an unknown character
    #     # TODO: make sure ties are not included in this, 
    #     # TODO: decide if you're going to include WR ties with links
    #     # TODO: add dates to front? or elsewhere? if so do i do it for each tie? would get preeeetty hectic but its the point of a history command
    #     # TODO: make this into a table format of some sort

    #     description_lines = []

    #     prev_score = 0

    #     for record in cur:
    #         details = {
    #             # possible to index by sql column name instead of integer?
    #             "char": record[0],
    #             "player" : record[1],
    #             "score_ft" : record[2],
    #             "score_m" : record[3],
    #             "sources" : record[4],
    #             "date" : record[5].date(),
    #     #         "tas" : record[6],
    #     #         "emulator" : record[7],
    #     #         "tags" : record[8],
    #     #         "version" : record[9]
    #         }
    #         #print(details['sources'])
    #         char = details["char"]
    #         score_ft = details["score_ft"]
    #         score_m = details["score_m"]
    #         player = details["player"]
    #         date = details["date"]

    #         if len(details['sources']) != 0: # should just make this "not empty" or something lol
    #             video = details["sources"][0]
    #         else:
    #             video = None
    #         tied_player = None
    #         #     metre_sum += float(score_m)

    #         #     description_lines.append(
    #         #         f"{char} - \t [{score_ft}ft/{score_m}m]({video}) - \t {player}"


    #         # running max
    #         #prev_score = score_ft
    #         #print(description_lines[-1])
    #         if score_ft <= prev_score: # use '<' if including ties
    #             #prev_score = score_ft
    #             continue
    #         # REMOVE TIES
    #         #elif score_ft == prev_score:
    #         #    # encountered a tie, append player name
    #         #    tied_player = record[1]

    #         prev_score = score_ft
    #         if video == None:
    #             description_lines.append(
    #                 f'({date}) - {score_ft}ft/{score_m}m - {player}'
    #             )    
    #         else:
    #             description_lines.append(
    #                 f'({date}) - [{score_ft}ft/{score_m}m]({video}) - {player}'
    #             )

    #         #if tied_player != None:
    #         #    description_lines.pop()
    #         #    description_lines[-1] += f', {tied_player}'
    #         #    # SCUFFED. I AM A SCUFFED PROGRAMMER
    #         #    #description_lines[-1] = description_lines[0:-13] + f', {tied_player}' + description_lines[-13::]
    #         #tied_player = None
        
    #     #     )

    #     description_lines.append(f'{"(TAS) " if is_TAS else ""}History of {char_name} HRC WRs (ft/m) (YYYY/MM/DD)\n')
    #     # reverse list
    #     description_lines.reverse()

    #     # add to front of list
    #     #description_lines.insert(0, f"History of {char_name} HRC WRs (ft/m) (YYYY/MM/DD)\n")

    #     #print(description_lines)
        
    #     # TODO: add links to history sheet? Only applicable for RTA for HRC
    #     if not is_TAS:
    #         description_lines.append(f'\n [Full HRC RTA History Sheet](https://docs.google.com/spreadsheets/d/1qbd8nquan3mGl87Ja1ogwK1SQIE_Fa-Yki-8wRbm9BY/edit#gid=0)')

    #     await embeds.send_embeds(description_lines, ctx)
        

    #     cur.close()
    #     conn.close()
       

    





        


# future commands
# top 10 char lookup (doable, just limit 10. would need to format "ties" tho looool)
    # i.e. make sure if you have 12 people total, you format that
# player lookup (not just hrc but for each mode? nah)
# top 10 THS lookup (ugh)
# general ft->m and m->ft formula

# add record -> no source? add_source(). wrong version? change_version() update tags? update_tags(). no date? update datetime()
# any other things? if it was wrongly attribute to like, emu you should just change manually