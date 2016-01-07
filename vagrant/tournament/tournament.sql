--- Delete the 'tournament' database if it already exists
DROP DATABASE IF EXISTS tournament;

--- Create new database 'tournament'
CREATE DATABASE tournament;

--- Connect to database 'tournanent'
\c tournament;

--- Create table 'players' that stores registered players
CREATE TABLE players (id SERIAL PRIMARY KEY, name varchar(40) NOT NULL);

--- Create table 'matches' that records the winner and loser in a given match
CREATE TABLE matches (winner int, FOREIGN KEY (winner) REFERENCES players (id),
    loser int, FOREIGN KEY (loser) REFERENCES players (id));

--- Create table 'standings' the records information on wins, losses and byes
--- for each player in the tournament
CREATE TABLE standings (player int, FOREIGN KEY (player) 
    REFERENCES players (id), wins int DEFAULT 0, losses int DEFAULT 0,
    byes int DEFAULT 0);

--- Create view 'omw_view' that stores the aggregated wins of all the
--- opponents that each player has encountered in the tournament at any point
CREATE VIEW omw_view AS SELECT a.player, sum(b.wins) AS opp_max_wins
    FROM standings as a, standings as b,
    (SELECT * from matches) AS subq 
    WHERE ((winner = b.player and loser = a.player) or 
           (winner = a.player and loser = b.player)) 
    GROUP BY a.player;