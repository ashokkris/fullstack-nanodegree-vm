#Full Stack Nanodegree Project 4 - 'Design a Game'

##TicTacToe Game Description:
A TicTacToe game implementation has been deployed to Google appspot with the name  
**'tictactoe-ashok'**. Two individuals with Google accounts are needed to play an instance  
of this game. The users have to first register with the app to play. A game instance can  
be created for two registered users who then take turns to play their moves.  
  
A player makes a move by selecting a square in a 3×3 grid which are uniquely identified  
by numbers 1 thru' 9. The square on row 1-column 1 is '1', the square on row 1-column 2 is '2',  
the square on row 1-column 3 is '3', the square on row 2-column 1 is '4' and so on.  
The player that succeeds in filling squares that are in a horizontal, vertical, or diagonal  
row wins the game. The game returns a 'Game Won' message when a winning move is played by a user.  
A game may end in a 'draw' if neither player is able to fill squares that match a winning row  
pattern as noted above.  

The app maintains a record of games won, drawn and lost by each user. It uses this information to  
compute a 'rank' for each player that is based on the ratio of games won to games played. A 'draw'  
is considered to be a 'half win'.  

##Instructions for Playing the game:
Let's refer to the two users playing the game as user1 and user2.  
The steps below instruct how to play the game using APIs Explorer:
 
1. Both user1 and user2 sign in to to their google accounts and using web browser
like Chrome they navigate to the url shown below:  
    https://tictactoe-ashok.appspot.com/_ah/api/explorer
2. Under 'Services', select the service named 'TicTacToe Game API'
3. Both user1 and user2 should then execute the api method **register_user**.  
Note: This method requires authorized requests (using OAuth 2.0)  
Successful execution of this method will create a new UserProfile instance in DataStore  
for each user.
4. Next, one user, say user1, creates a new game instance by executing method **new_game**.  
This method will require the url-safe-key of user1 and user2 to be passed with the request.  
Successful execution of this method will add the new game to DataStore. It will also  
send an email notification to user1 to make the first move. This email will include  
the url-safe-key of the game just created.  
5. Next, user1 should make the first move by invoking method **make_move**  
This method takes the game's url-safe-key as path parameter and an integer representing  
the 'square' property value as part of the request. This has to be an interger from 1 to 9.  
Successful execution of this method will send email to user2 notifying that it is  
user2's turn to make the next game move.  
6. This way user1 and user2 alternate to fill the squares of the tictactoe board  
until the game is won or ends in a draw.  


##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration for sending reminder email to users with incomplete games.
 - main.py: Handlers for taskqueue task and cron job.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper functions used by code in api.py and main.py.
 - index.yaml: Index file generated when app was run on dev_appserver.
 - README.md: "This" file.

##Endpoints Included:
 - **register_user**
    - Path: 'user'
    - Method: POST
    - Parameters: None
    - Returns: UserProfileForm containing user's url-safe key, name, email and status message.
    - Description: Registers a new User. Requires authorization using OAuth2. A UserProfile  
    is created for the user and saved to datastore. Will raise UnauthorizedException if user  
    authorization is not obtained.
    
 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: url-safe keys of two users previously registered. 
    - Returns: GameForm with initial game state. Also has url-safe game key.
    - Description: Creates a new Game. Will raise a NotFoundException if UserProfile  
    objects for input keys are not found in datastore. Also adds a task to a task queue  
    to send email notification to one user to start the game.
     
 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game. Will raise NotFoundException if  
    game is not found in datastore
    
 - **make_move**
    - Path: 'game/move/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, move
    - Returns: GameForm with new game state.
    - Description: Accepts a 'move' that identifies one of the nine squares of a tictactoe  
    board with a number from 1 thru 9. Returns the updated state of the game. Will raise
    BadRequestException if the game currently is in completed or cancelled state OR if  
    the turn is played by a user that is not expected to make the move. Will raise  
    UnautorizedException if user authorization is not obtained. If game is not won or drawn  
    adds a task to task queue to send turn notification email to the other user.
    
 - **get_user_games**
    - Path: 'user/{urlsafe_user_key}'
    - Method: GET
    - Parameters: urlsafe_user_key
    - Returns: GamesListForm. 
    - Description: Returns all active games of the provided player (unordered).
    
 - **cancel_game**
    - Path: 'game/cancel/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Cancels game. Will raise UnauthorizedException if OAuth2 autorization  
    is not obtained. Will raise BadRequestException if game is already in completed or  
    cancelled state OR if the cancellation attempt is made by anyone other than the two  
    users playing the game.

 - **get_user_rankings**
    - Path: 'rankings'
    - Method: GET
    - Parameters: None
    - Returns: UserWinRatioForms which is composed of zero or more UserWinRatioForm
    - Description: Returns user rankings based on computed win ratio (sorted highest to lowest).
    
 - **get_game_history**
    - Path: 'game/history/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameHistoryForm which is composed of zero or more GameStepForm.  
    - Description: Returns 'history' of moves for input game and a game status message.


##Models Included:
 - **UserProfile**
    - Stores user name, email and information on number of games won, drawn and lost.
 - **Game**
    - Stores game state and the two players' key as properties.
    
##Forms Included:
 - **UserProfileForm**
    - Representation of a registered user (urlsafe_key, name, email, message).
 - **GameForm**
    - Representation of a Game instance (urlsafe_key, user1_name, user2_name, user1_squares,  
    user2_squares, game_over flag, game_cancelled flag, next_move_user_name, message).
 - **NewGameForm**
    - Used to create a new game (user1_safe_key, user2_safe_key)
 - **MakeMoveForm**
    - Inbound make move form (integer field representing square selection).
 - **GamesListForm**
    - Outbound form containing game keys (url_safe_game_keys).
 - **GameStepForm**
    - Outbound message representing a single move in a game.
 - **GameHistoryForm**
    - Outbound form containing ordered GameStepForm messages.
 - **UserWinRatioForm**
    - Outbound message representing a single user's performance metric (name, win_ratio).
 - **UserWinRatioForms**
    - Multiple UserWinRatioForm representing ordered rankings of all users.