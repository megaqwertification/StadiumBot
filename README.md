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
- RTTF and EFB records, credits as well
- NOT 2p-4p , I think that's better for a separate, larger database with its own functionality
- Pipe dream: a website with more database functionality

*idea being here does not mean I'll implement it. I do not want to oversaturate the bot with commands. Please make a feature request under github issues for a request

# Current checklist
- [x] Populate Vanilla RTA & TAS runs
- [x] Enable history commands
- [x] Populate current mismatch RTA history
- [x] Populate current mismatch TAS history
- [ ] Create script for each mode to add to database
- [ ] Crowdsource 10MM, HRC, and event match history into document
- [ ] Go through individual youtube channels (mimorox, LDA, etc.)
- [ ] Allow add command to check if run already exists (i.e. a proper function)
- [ ] Create google form for ALL run submissions, crowdsource help to fill the database. Check your youtube playlists + other saved resources
- [ ] Populate different modes' SuS categories
- [ ] Create website for people to filter runs to see all information
- [ ] Allow people to verify runs (tags, version, etc.)
- [ ] overhaul database to something better, migrate bot if heroku cost is too much
- [ ] Create a way for people to download runs as vids, be it a script or torrent file
