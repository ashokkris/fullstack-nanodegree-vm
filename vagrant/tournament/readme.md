# Fullstack Nanodegree Project #2 - Tournament Results

### What’s Included
```
tournament/    
|---- tournament.sql    
|---- tournament.py    
|---- tournament_test.py    
|---- readme.md    
```

### Dependencies
1. PostgresSQL database
2. Python version 2.7 or later

### Quick Start
1. cd to the ‘tournament’ folder
2. To build the database, tables and views, run from command line:  
**>>psql \i tournament.sql**
3. To execute the series of tests, run from command line:  
**>>python tournament_test.py**
4. Inspect the output to verify that all tests passed

###Documentation
* _tournament.sql_ - contains psql commands to create the SQL database for our  
tournament project
* _tournament.py_ - python module that contains the various functions to run a  
tournament based on swiss pairings
* _tournament_test.py_ - python program that runs unit tests for testing the  
various functions in the tournament module (above)

###Features
* Implements Swiss system for pairing up players in each round of a tournament
* Prevents rematches between players
* Allows even or odd number of players in the tournament. If there is an odd  
number of players, program assigns one player a "bye" which counts as a win
* Ensures that a player will not receive more than one bye
* When two players have the same number of wins, ranks them according to OMW,  
that is, Opponent Maximum Wins - total number of wins by players they have  
played against  

