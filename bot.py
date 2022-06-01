import os
from interactions import Client, Intents

# from commands.hrc_commands import register_hrc_commands
# from commands.btt_commands import register_btt_commands
# from commands.event_commands import register_event_commands
# from commands.ten_mm_commands import register_10mm_commands
# from commands.owner_commands import register_owner_commands

STADIUM_BOT_TOKEN = os.getenv('STADIUM_BOT_TOKEN')
bot = Client(token=STADIUM_BOT_TOKEN, intents=Intents.DEFAULT, disable_sync=True)

@bot.event
async def on_read():
    res = await bot._http.get_self_guilds()
    print(res)
# register_owner_commands(bot)
# register_hrc_commands(bot)
# register_btt_commands(bot)
# register_10mm_commands(bot)
# register_event_commands(bot)
bot.start()