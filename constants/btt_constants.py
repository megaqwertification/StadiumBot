# TODO: how to properly implement zelda/sheik vs zelda vs sheik based on mode
# have to fix zelda/sheik, maybe move to bottom
BTT_CHARACTERS = [
    "Dr. Mario",
    "Mario",
    "Luigi",
    "Bowser",
    "Peach",
    "Yoshi",
    "Donkey Kong",
    "Captain Falcon",
    "Ganondorf",
    "Falco",
    "Fox",
    "Ness",
    "Popo",
    "Ice Climbers",
    "Kirby",
    "Samus",
    "Sheik",
    "Link",
    "Young Link",
    "Pichu",
    "Pikachu",
    "Jigglypuff",
    "Mewtwo",
    "Mr. Game & Watch",
    "Marth",
    "Roy",
    "Zelda",    
    "Male Wireframe",
    "Female Wireframe",
    "Giga Bowser",
    "Master Hand",
    "Crazy Hand"
]

BTT_CHARS_STAGE_COMMAND = [
    "Dr. Mario",
    "Mario",
    "Luigi",
    "Bowser",
    "Peach",
    "Yoshi",
    "Donkey Kong",
    "Captain Falcon",
    "Ganondorf",
    "Falco",
    "Fox",
    "Ness",
    "Popo",
    "Kirby",
    "Samus",
    "Sheik",
    "Link",
    "Young Link",
    "Pichu",
    "Pikachu",
    "Jigglypuff",
    "Mewtwo",
    "Mr. Game & Watch",
    "Marth",
    "Roy",
]

BTT_STAGES = [
    "Dr. Mario",
    "Mario",
    "Luigi",
    "Bowser",
    "Peach",
    "Yoshi",
    "Donkey Kong",
    "Captain Falcon",
    "Ganondorf",
    "Falco",
    "Fox",
    "Ness",
    "Ice Climbers",
    "Kirby",
    "Samus",
    "Zelda",
    "Link",
    "Young Link",
    "Pichu",
    "Pikachu",
    "Jigglypuff",
    "Mewtwo",
    "Mr. Game & Watch",
    "Marth",
    "Roy",
    "Seak"
]

BTT_SUS_TAGS = {
    'bair' : 'Back Aerial Only',
    'dair' : 'Down Aerial Only',
    'nair' : 'Neutral Aerial Only',
    'fair' : 'Forward Aerial Only',
    'uair' : 'Up Aerial Only',
    'nb' : 'Neutral B Only',
    'fb' : 'Forward B Only',
    'upb' : 'Up B Only',
    'downb' : 'Down B Only',
    'BMO' : 'B Moves Only',
    'AMO' : 'A Moves Only',
    'LTA' : 'Limited Time Attack',
    'FRO' : 'Facing Right Only',
    'RWO' : 'Reverse World Record Order',
    'TTB' : 'Top to Bottom',
    'BTT' : 'Bottom to Top',
    'RTL' : 'Right to Left',
    'LTR' : 'Left to Right',
    'BSS' : 'Bottom Side Suicide',
    'RSS' : 'Right Side Suicide',
    'TSS' : 'Top Side Suicide',
    'LSS' : 'Left Side Suicide',
    'NCS' : 'No Control Stick',
    'NJA' : 'No Jump Allowed',
    'OHO' : 'One Hand Only',
    '1T' : 'One Target (T10 of current WR)',
    '999%' : 'Attain 999% Damage and complete the stage',
    'zair' : 'Hookshot/grapple only',
    'misfire' : 'Misfire only (no code)',
    # 'Mismatch' : 'Char != Stage',
    'AR' : "Action Replay / Gecko Coded Runs",
    'Grounded' : 'All targets must be broken while grounded', # double check this definition
    'Riddle' : 'tbd',
    'Ledge Riddle' : 'tbd',
    'Riddle Glitchless' : 'tbd',
    'FZI' : 'Fully Zoomed In',
    'blindfolded' : 'Blindfolded run',


    # 'NCS BSS' # NCS is its own categore, make sure NCS runs dont get categorized with suicide runs or completions
    # e.g. if a NCS luigi exists, make sure the separate NCS and BSS tags dont interfere with it.
    # 'no upb, no air dodge, 9 targets (x targets), no neuitral b, mr saturn, beam sword, bomb, no turnips, ar bomb, ar pokebolls , no upb, no pressing down, no nb,  '
    # 'top target first, all blocks/targets, no glitch'
    # 'full charge shot, bomb riddle', 'only zelda,', '5 ze 5sheik', 'no forward b', 'no projectiles hookshot','no damage', ''

}

# ============================================================================
# TAS MM Bounty System Constants
# ============================================================================

# List of (character, stage) tuples that are impossible to complete in
#
# Format: [('Character Name', 'Stage Name'), ...]
#
# These pairings will be excluded when randomly selecting new bounties.
# Generated from RTA mismatch sheet - pairings with target counts instead of times
IMPOSSIBLE_PAIRINGS = [
    # Dr. Mario impossible pairings
    (BTT_CHARACTERS[0], BTT_STAGES[17]),   # Dr. Mario × Young Link (1 target)

    # Luigi impossible pairings
    (BTT_CHARACTERS[2], BTT_STAGES[17]),   # Luigi × Young Link (1 target)

    # Bowser impossible pairings
    (BTT_CHARACTERS[3], BTT_STAGES[5]),    # Bowser × Yoshi (9 targets)
    (BTT_CHARACTERS[3], BTT_STAGES[17]),   # Bowser × Young Link (1 target)
    (BTT_CHARACTERS[3], BTT_STAGES[20]),   # Bowser × Jigglypuff (8 targets)

    # Yoshi impossible pairings
    (BTT_CHARACTERS[5], BTT_STAGES[17]),   # Yoshi × Young Link (1 target)
    (BTT_CHARACTERS[5], BTT_STAGES[20]),   # Yoshi × Jigglypuff (9 targets)

    # Donkey Kong impossible pairings
    (BTT_CHARACTERS[6], BTT_STAGES[5]),    # Donkey Kong × Yoshi (9 targets)
    (BTT_CHARACTERS[6], BTT_STAGES[17]),   # Donkey Kong × Young Link (1 target)

    # Captain Falcon impossible pairings
    (BTT_CHARACTERS[7], BTT_STAGES[20]),   # Captain Falcon × Jigglypuff (9 targets)

    # Ganondorf impossible pairings
    (BTT_CHARACTERS[8], BTT_STAGES[0]),    # Ganondorf × Dr. Mario (9 targets)
    (BTT_CHARACTERS[8], BTT_STAGES[17]),   # Ganondorf × Young Link (0 targets)
    (BTT_CHARACTERS[8], BTT_STAGES[20]),   # Ganondorf × Jigglypuff (8 targets)

    # Falco impossible pairings
    (BTT_CHARACTERS[9], BTT_STAGES[17]),   # Falco × Young Link (9 targets)

    # Fox impossible pairings
    (BTT_CHARACTERS[10], BTT_STAGES[17]),  # Fox × Young Link (9 targets)

    # Ness impossible pairings
    (BTT_CHARACTERS[11], BTT_STAGES[17]),  # Ness × Young Link (6 targets)

    # Popo impossible pairings
    (BTT_CHARACTERS[12], BTT_STAGES[5]),   # Popo × Yoshi (9 targets)
    (BTT_CHARACTERS[12], BTT_STAGES[17]),  # Popo × Young Link (1 target)
    (BTT_CHARACTERS[12], BTT_STAGES[20]),  # Popo × Jigglypuff (8 targets)

    # Kirby impossible pairings
    (BTT_CHARACTERS[14], BTT_STAGES[17]),  # Kirby × Young Link (1 target)

    # Pikachu impossible pairings
    (BTT_CHARACTERS[20], BTT_STAGES[17]),  # Pikachu × Young Link (1 target)

    # Mr. Game & Watch impossible pairings
    (BTT_CHARACTERS[23], BTT_STAGES[17]),  # Mr. Game & Watch × Young Link (1 target)
    (BTT_CHARACTERS[23], BTT_STAGES[20]),  # Mr. Game & Watch × Jigglypuff (9 targets)

    # Marth impossible pairings
    (BTT_CHARACTERS[24], BTT_STAGES[17]),  # Marth × Young Link (1 target)

    # Roy impossible pairings
    (BTT_CHARACTERS[25], BTT_STAGES[17]),  # Roy × Young Link (1 target)
    (BTT_CHARACTERS[25], BTT_STAGES[20]),  # Roy × Jigglypuff (9 targets)

    # Zelda impossible pairings
    (BTT_CHARACTERS[26], BTT_STAGES[17]),  # Zelda × Young Link (0 targets)
    (BTT_CHARACTERS[26], BTT_STAGES[20]),  # Zelda × Jigglypuff (9 targets)

    # Male Wireframe impossible pairings
    (BTT_CHARACTERS[27], BTT_STAGES[17]),  # Male Wireframe × Young Link (1 target)
    (BTT_CHARACTERS[27], BTT_STAGES[20]),  # Male Wireframe × Jigglypuff (9 targets)

    # Female Wireframe impossible pairings
    (BTT_CHARACTERS[28], BTT_STAGES[17]),  # Female Wireframe × Young Link (1 target)
    (BTT_CHARACTERS[28], BTT_STAGES[20]),  # Female Wireframe × Jigglypuff (8 targets)

    # Giga Bowser impossible pairings
    (BTT_CHARACTERS[29], BTT_STAGES[17]),  # Giga Bowser × Young Link (1 target)
]
