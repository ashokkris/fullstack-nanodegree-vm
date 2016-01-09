--- Delete the 'tournament' database if it already exists
DROP DATABASE IF EXISTS tournament;

--- Create new database 'tournament'
CREATE DATABASE tournament;

--- Connect to database 'tournanent'
\c tournament;

--- Create table 'players' that stores registered players
CREATE TABLE players (id serial PRIMARY KEY, name varchar(40) NOT NULL);

--- Create table 'matches' that records the winner and loser in a given match
CREATE TABLE matches (winner int, FOREIGN KEY (winner) REFERENCES players (id),
    loser int, FOREIGN KEY (loser) REFERENCES players (id));

--- Create view 'standings_view' to aggregates wins, total-matches played 
--- for each player in the tournament
CREATE VIEW standings_view AS SELECT p_id, p_name, n_wins, (n_wins + n_losses)
    AS n_matches FROM
    (SELECT p1.id AS p_id, name as p_name, count(winner) AS n_wins
    	FROM players AS p1 LEFT JOIN
    	matches ON p1.id = winner GROUP BY p1.id) AS subq1,
    (SELECT p2.id AS p2_id, count(loser) AS n_losses
    	FROM players AS p2 LEFT JOIN matches on p2.id = loser
    	GROUP BY p2.id) AS subq2
    WHERE p_id = p2_id ORDER BY p_id;

--- Create view 'omw_view' that stores the aggregated wins of all the
--- opponents that each player has encountered in the tournament at any point
CREATE VIEW omw_view AS SELECT a.p_id, sum(b.n_wins) AS opp_max_wins
    FROM standings_view as a, standings_view as b,
    (SELECT * from matches) AS subq 
    WHERE ((winner = b.p_id and loser = a.p_id) or 
           (winner = a.p_id and loser = b.p_id)) 
    GROUP BY a.p_id;