#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    DB = connect()
    cursor = DB.cursor()
    try:
        cursor.execute("DELETE FROM matches")
        cursor.execute("DELETE FROM standings")
        DB.commit()
    except Exception as e:
        print "deleteMatches: " + str(e)
        DB.rollback()
    DB.close()


def deletePlayers():
    """Remove all the player records from the database."""
    DB = connect()
    cursor = DB.cursor()
    try:
        cursor.execute("DELETE FROM matches")
        cursor.execute("DELETE FROM standings")
        cursor.execute("DELETE FROM players")
        cursor.execute("ALTER SEQUENCE players_id_seq RESTART WITH 1")
        DB.commit()
    except Exception as e:
        print "deletePlayers: " + str(e)
        DB.rollback()
    DB.close()


def countPlayers():
    """Returns the number of players currently registered."""
    DB = connect()
    cursor = DB.cursor()
    cursor.execute("SELECT count(*) FROM players")
    (num_players,) = cursor.fetchone()
    DB.close()
    return num_players


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    DB = connect()
    cursor = DB.cursor()
    try:
        cursor.execute("INSERT INTO players (name) VALUES (%s)  \
            RETURNING id", (name,))
        (player_id,) =  cursor.fetchone()
        cursor.execute(
            "INSERT INTO standings (player) VALUES (%s)", (player_id,))
        DB.commit()
    except Exception as e:
        print "registerPlayers: " + str(e)
        DB.rollback()
    DB.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.
       For players with same number of wins, they will be sorted based on
       OMW (opponent maximum wins). The OMW information is held in omw_view.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won. Bye counts as win
        matches: the number of matches the player has played not counting byes
    """
    DB = connect()
    cursor = DB.cursor()

    cursor.execute("SELECT standings.player, name, wins, losses, byes \
        FROM standings JOIN players ON standings.player = players.id \
        LEFT JOIN omw_view ON standings.player = omw_view.player \
        ORDER BY wins DESC, omw_view.opp_max_wins DESC")

    rows = cursor.fetchall()
    results = [(row[0], row[1], row[2]+row[4], row[2]+row[3]) for row in rows]
    DB.close()
    return results


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost

    Note:
      This method should be called only after first checking if the
      two players can be paired by calling the function canPair()
    """
    DB = connect()
    cursor = DB.cursor()
    try:
        cursor.execute("INSERT INTO matches VALUES (%s, %s)", 
            (winner, loser))
        cursor.execute("UPDATE standings SET wins = wins + 1 \
            WHERE player = %s", (winner,))
        cursor.execute("UPDATE standings SET losses = losses + 1 \
            WHERE player = %s", (loser,))
        DB.commit()
    except Exception as e:
        print "reportMatch: " + str(e)
        DB.rollback()
    DB.close()


def reportBye(player_id):
    """Records a bye given to a player.

    Args:
      player_id: the id number of the player who got a bye.

    Note:
      See method getCandidateForBye that was used to determine who gets bye
    """
    DB = connect()
    cursor = DB.cursor()
    try:
        cursor.execute("UPDATE standings SET byes = byes + 1 \
            WHERE player = %s", (player_id,))
        DB.commit()
    except Exception as e:
        print "reportBye: " + str(e)
        DB.rollback()
    DB.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    results = []
    standings = playerStandings()

    # First, determine who gets a bye if we have odd number of players
    num_players = len(standings)
    if (num_players % 2 != 0):
        index = getCandidateForBye(standings)
        if(index < num_players):
            row = standings[index]
             # Not being paired with another player implies a bye
            results.append((row[0], row[1], None, None))
            standings.remove(row)

    # Now that we know there are even number of players in standings list
    # we can go ahead making the pairings
    index_1 = 0
    while index_1 < len(standings):
        row_1 = standings[index_1]
        index_2 = index_1 + 1
        while index_2 < len(standings):
            row_2 = standings[index_2]
            # Pair the players only if they have not played each other
            if canPair(row_1[0], row_2[0]):
                results.append((row_1[0], row_1[1], row_2[0], row_2[1]))
                standings.remove(row_1)
                standings.remove(row_2)
                index_1 = 0
                break
            index_2 = index_2 + 1

    return results


def getCandidateForBye(standings):
    """Determines which player can be given a bye starting from the top
       of the standings list. This will be called only when ther are an
       odd number of players in the tournament

       Args:
         standings: The list that was obtained by calling playerStandings()

       Returns:
         The list index in standings for player who can get a bye
    """
    DB = connect()
    cursor = DB.cursor()

    index = 0
    while index < len(standings):
        row = standings[index]
        cursor.execute("SELECT byes FROM standings \
            WHERE player = %s", (row[0],))
        (bye_count,) = cursor.fetchone()
        if int(bye_count) == 0:  # this player is a valid candidate for bye
            break
        index = index + 1        # move on the next player down in standings

    DB.close()
    return index    


def canPair(player_1, player_2):
    """Determines if two players can be paired up in a round based on whether
       or not they have already played each other before.

       Args:
         player_1: id of one  player
         player_2: id of another player

       Returns:
        True if the players can be paired; Else, returns False
    """
    DB = connect()
    cursor = DB.cursor()

    cursor.execute("SELECT count(*) FROM matches \
        WHERE (winner = %s and loser = %s) or \
        (winner = %s and loser = %s)", \
        (player_1, player_2, player_2, player_1))

    (count,) =  cursor.fetchone()

    DB.close()

    if count == 0:  # no previous encounter; the two players can be paired
        return True
    
    return False





