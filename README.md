# StadiumBot

A bot for querying WRs and history for the [Smash Stadium Discord](https://discord.gg/3D6YjWJ). You can see the list of commands by using '/' in the Discord.

## Issues/Feature Requests:  
Please open an issue on github or DM me on Discord megaqwertification#3976. You may submit a PR too and let me know if there are issues I need to sort out.

## Thanks to:
- IRL friend - you know who you are
- sockdude1 - mmbot plus helping
- Judge9 - additional help
- various stadium community members - for input
- Stadium Discord - Too many google sheets even though i dont want this to be the defacto tracker of things. just a tool to access things quickly

# IDEAS / TODO*:
- view_record command for arbitrary record (not priority, but still doable)
- recordcount command
- sus/mismatch command verification
- Add sus tags (and error-checking) for all mode WR list commands, all mode WR history commands, and individual WR query commands
- top 10 leaderboard per char
- BTT RTTF and EFB records
- NOT 2p-4p , I think that's better for a separate, larger database with its own functionality
- Pipe dream: a website with more database functionality

*idea being here does not mean I'll implement it. I do not want to oversaturate the bot with commands. Please make a feature request under github issues for an rquest

# Current checklist
- [ ] Populate Vanilla RTA & TAS runs
- [ ] Enable history commands
- [ ] Allow add command to check if run already exists
- [ ] Create google form for ALL run submissions, crowdsource help to fill the database. Check your youtube playlists + other saved resources
- [ ] Continue mm history work where you left off, should be easier to do from that point
- [ ] Create file which imports CSV and adds the runs
- [ ] Create website for people to filter runs to see all information
- [ ] Allow people to verify runs (tags, version, etc.)
- [ ] overhaul database to something better, migrate if heroku cost is too much
- [ ] Create a way for people to download runs as vids, be it a script or torrent file
