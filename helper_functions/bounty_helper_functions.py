"""
Bounty System Helper Functions

This module provides helper functions for the bounty run feature,
including bounty selection, querying, and completion checking.
"""

import secrets
from db import connect
from constants.btt_constants import BTT_CHARACTERS, BTT_STAGES, IMPOSSIBLE_PAIRINGS


def get_uncompleted_tas_mismatches():
    """
    Query all mismatch pairings (character != stage) that do NOT have
    any TAS records in btt_table.

    Returns:
        list: List of (character, stage) tuples representing uncompleted tas mm
            Empty list if all tas mm are completed
    """
    conn = connect()
    cur = conn.cursor()

    # Get all possible mismatch pairings (character != stage)
    # Use special characters (30) and standard stages (25)
    characters = BTT_CHARACTERS[:30]
    standard_stages = BTT_STAGES[:25]

    all_mismatches = [
        (char, stage)
        for char in characters
        for stage in standard_stages
        if char != stage  # Exclude matching pairings
    ]

    # Remove impossible pairings from consideration
    impossible_mm = set(IMPOSSIBLE_PAIRINGS)
    possible_mismatches = [
        pairing for pairing in all_mismatches
        if pairing not in impossible_mm
    ]

    # Query database for all mismatch pairings that already have TAS records
    sql = """
        SELECT DISTINCT character, stage
        FROM btt_table
        WHERE tas = TRUE
        AND character != stage
    """
    cur.execute(sql)
    completed_pairings = set((row[0], row[1]) for row in cur.fetchall())

    conn.close()

    # Return only pairings that have NOT been completed
    uncompleted = [
        pairing for pairing in possible_mismatches
        if pairing not in completed_pairings
    ]

    return uncompleted


def select_new_bounty():
    """
    Randomly select a new bounty from uncompleted TAS mismatches and
    save it to the database.

    Returns:
        tuple or None: (character, stage) of the new bounty, or None if all
            tas mm have been completed
    """
    uncompleted = get_uncompleted_tas_mismatches()

    if not uncompleted:
        # All tas mm have been completed!
        return None

    new_bounty = secrets.choice(uncompleted)

    conn = connect()
    cur = conn.cursor()

    # # Update database with new tas mm bounty
    sql = """
        UPDATE bounty_state
        SET character = %s, stage = %s, created_date = NOW()
        WHERE id = 1
    """
    cur.execute(sql, (new_bounty[0], new_bounty[1]))
    conn.commit()
    conn.close()

    return new_bounty


def get_current_bounty():
    """
    Retrieve the current active bounty pairing from the database.
    """
    conn = connect()
    cur = conn.cursor()

    sql = """
        SELECT character, stage, created_date
        FROM bounty_state
        WHERE id = 1
    """
    cur.execute(sql)
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return {
        'character': row[0],
        'stage': row[1],
        'created_date': row[2]
    }


def initialize_bounty():
    """
    Initialize the bounty system by inserting the first random bounty.

    This should only be called once during setup, or if the bounty_state
    table is empty.
    """
    uncompleted = get_uncompleted_tas_mismatches()

    if not uncompleted:
        # All bounties already completed (unlikely on first init)
        return None

    first_bounty = secrets.choice(uncompleted)

    conn = connect()
    cur = conn.cursor()

    sql = """
        INSERT INTO bounty_state (id, character, stage, created_date)
        VALUES (1, %s, %s, NOW())
    """
    cur.execute(sql, (first_bounty[0], first_bounty[1]))
    conn.commit()
    conn.close()

    return first_bounty


def matches_current_bounty(character, stage):
    current = get_current_bounty()

    if not current:
        return False

    return (current['character'] == character and current['stage'] == stage)


def get_bounty_progress():
    """
    Calculate how many bounties have been completed vs total possible.

    Returns:
        dict: Dictionary with keys:
            - 'completed': Number of completed TAS mismatch records
            - 'total': Total possible (725 minus impossible pairings)
            - 'remaining': Number of uncompleted runs

    Example:
        >>> progress = get_bounty_progress()
        >>> print(f"{progress['completed']}/{progress['total']} bounties completed")
    """
    uncompleted = get_uncompleted_tas_mismatches()
    remaining = len(uncompleted)
    total_possible = 725 - len(IMPOSSIBLE_PAIRINGS)
    completed = total_possible - remaining

    return {
        'completed': completed,
        'total': total_possible,
        'remaining': remaining
    }


def is_bounty_already_completed():
    """
    Check if the current active bounty already has TAS records in the database.

    This can happen if:
    - The database was manually edited
    - A record was added but the bounty wasn't updated
    - There's a data inconsistency
    """
    current = get_current_bounty()

    if not current:
        return False

    conn = connect()
    cur = conn.cursor()

    sql = """
        SELECT COUNT(*) FROM btt_table
        WHERE character = %s AND stage = %s AND tas = TRUE
    """
    cur.execute(sql, (current['character'], current['stage']))
    count = cur.fetchone()[0]
    conn.close()

    return count > 0
