# -*- coding: utf-8 -*-`
"""api.py - Create and configure TicTacToe game API exposing the resources.
This also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""

import itertools
import logging
import endpoints
from protorpc import remote, messages, message_types
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from models import UserProfile, Game
from models import UserProfileForm, NewGameForm, GameForm, MakeMoveForm,\
     GamesListForm, UserWinRatioForms, GameStepForm, GameHistoryForm
from utils import get_by_urlsafe, getUserId, gameWon

EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID
NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)
USER_GAMES_REQUEST = endpoints.ResourceContainer(
    urlsafe_user_key=messages.StringField(1),)

@endpoints.api(name='tic_tac_toe', version='v1',
    allowed_client_ids=[API_EXPLORER_CLIENT_ID],
    scopes=[EMAIL_SCOPE])
class TicTacToeApi(remote.Service):
    """TicTacToe Game API"""
    @endpoints.method(request_message=message_types.VoidMessage,
                      response_message=UserProfileForm,
                      path='user',
                      name='register_user',
                      http_method='POST')
    def register_user(self, request):
        """Register a user and return user profile"""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        # Check if user's profile already exists in datastore
        user_id = getUserId(user)
        p_key = ndb.Key(UserProfile, user_id)
        profile = p_key.get()
        # create and save a new Profile if not found; if found, raise exception
        if not profile:
            profile = UserProfile(
                key = p_key,
                name = user.nickname(),
                email = user.email()
            )
            profile.put()
        else:
            raise endpoints.ConflictException('User is already registered!')

        return profile.to_form(message='User successfully registered!')

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        user1 = get_by_urlsafe(request.user1_safe_key, UserProfile)
        if not user1:
            raise endpoints.NotFoundException('User1 not found!')
        user2 = get_by_urlsafe(request.user2_safe_key, UserProfile)
        if not user1:
            raise endpoints.NotFoundException('User2 not found!')

        game = Game.new_game(user1.key, user2.key)

        # Use a task queue to send email notification to user1 
        # to make the first move
        taskqueue.add(params={'email': user1.email,
            'name': user1.name, 'game': game.key.urlsafe()},
            url='/tasks/send_turn_notification')
        return game.to_form('New TicTacToe game created!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            if game.game_over:
                return game.to_form('Game was completed!')
            elif game.game_cancelled:
                return game.to_form('Game was cancelled!')
            else:
                return game.to_form('Game is in progress!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/move/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    @ndb.transactional(xg=True)
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            raise endpoints.BadRequestException(
              'Moves not allowed in a completed game!')
        elif game.game_cancelled:
            raise endpoints.BadRequestException(
              'Moves not allowed in a cancelled game!')
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        # Check if user's Profile already exists datastore
        user_id = getUserId(user)
        p_key = ndb.Key(UserProfile, user_id)
        user = p_key.get()
        if not user:
            raise endpoints.UnauthorizedException('Unregistered user!')
        if game.next_move_user != user.key:
            raise endpoints.BadRequestException('Wrong user attempting move!')
        current_move = request.square
        if current_move < 1 and current_move > 9:
            raise endpoints.BadRequestException('Input outside range 1 to 9')
        # Check if current move has already been played by either users
        if current_move in game.user1_squares or \
        current_move in game.user2_squares:
            raise endpoints.BadRequestException('Square already filled!')
        # Record the move by inserting it into the current player's squares.
        # Then, switch the current player by updating game's next_move_user.
        # Also, if move resulted in win or draw, increment #win, #loss, #draw
        # stats appropriately in each of the two UserProfile objects
        other_user = None
        if user.key == game.user1:
            # This means move has been made by user1
            game.user1_squares.append(current_move)
            other_user = game.user2.get()
            game.next_move_user = other_user.key
            if gameWon(game.user1_squares):
                # user1 has won
                game.end_game(game.user1)
                user.record_win()
                other_user.record_loss()
                return game.to_form('Game Won!')
            elif len(game.user2_squares) == 9:
                # Game has ended in draw
                game.end_game()
                user.record_draw()
                other_user.record_draw()
                return game.to_form('Game Drawn!')
        else:
            # Move made by user2
            game.user2_squares.append(current_move)
            other_user = game.user1.get()
            game.next_move_user = other_user.key
            if gameWon(game.user2_squares):
                # user2 has won
                game.end_game(game.user2)
                user.record_win()
                other_user.record_loss()
                return game.to_form('Game Won!')
            elif len(game.user1_squares) == 9:
                # Game has ended in draw
                game.end_game()
                user.record_draw()
                other_user.record_draw()
                return game.to_form('Game Drawn!')
        # Save game status to datastore so that game can be continued
        game.put()
        # Use task queue to send turn notification to game.next_move_user
        if other_user != None:
            taskqueue.add(params={'email': other_user.email,
            'name': other_user.name, 'game': game.key.urlsafe()},
            url='/tasks/send_turn_notification')
        # Return game status with message that move was successful
        return game.to_form('Move was successfully recorded!')

    @endpoints.method(request_message=USER_GAMES_REQUEST,
                      response_message=GamesListForm,
                      path='user/{urlsafe_user_key}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Returns all of a User's active games"""
        user = get_by_urlsafe(request.urlsafe_user_key, UserProfile)
        if user:
            q = Game.query(ndb.OR(Game.user1 == user.key,
                                  Game.user2 == user.key))
            games = q.filter(ndb.AND(Game.game_over == False,
                Game.game_cancelled == False)).fetch(keys_only=True)
            return GamesListForm(url_safe_game_keys=[gameKey.urlsafe()
                for gameKey in games]) 

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/cancel/{urlsafe_game_key}',
                      name='cancel_game',
                      http_method='PUT')
    def cancel_game(self, request):
        """Allows either user to cancel active game. Returns game state"""
        # make sure user is authed
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        # Check if user's Profile already exists datastore
        user_id = getUserId(user)
        p_key = ndb.Key(UserProfile, user_id)
        user = p_key.get()
        if not user:
            raise endpoints.UnauthorizedException('Unregistered user!')
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        # Only games in progress can be cancelled
        if game.game_over == True or game.game_cancelled  == True:
            raise endpoints.BadRequestException(
              'Attempt to cancel a completed game!')
        # Only the two users playing the game can cancel it
        if game.user1 == user.key or game.user2 == user.key:
            game.cancel_game()
            return game.to_form('Game successfully cancelled!')

        raise endpoints.BadRequestException(
          'Attempt to cancel by user not playing the game!')
        

    @endpoints.method(request_message=message_types.VoidMessage,
                      response_message=UserWinRatioForms,
                      path='rankings',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Returns user rankings based on computed win ratio"""
        # Order users based on computed winRatio property. Use num_won
        # property as secondary sort order
        users = UserProfile.query().order(-UserProfile.win_ratio,
          -UserProfile.num_won).fetch()
        return UserWinRatioForms(items=[user.to_WinRatioForm() 
          for user in users])

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameHistoryForm,
                      path='game/history/{urlsafe_game_key}',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Return 'history' of moves for given game"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            user1_name = game.user1.get().name
            user2_name = game.user2.get().name
            steps = []
            # Itereate the moves played by the two users to populate response
            for m1,m2 in itertools.izip_longest(game.user1_squares,
              game.user2_squares):
                steps.append(GameStepForm(name=user1_name, move=m1))
                # Account for user2 having made one less move than user1
                if m2 != None:
                    steps.append(GameStepForm(name=user2_name, move=m2))
            outcome = ''
            if game.user1 == game.winner:
                outcome = 'User {} won!'.format(user1_name)
            elif game.user2 == game.winner:
                outcome =  'User {} won!'.format(user2_name)
            elif game.game_over == True:
                outcome = 'Game was drawn!'
            elif game.game_cancelled == True:
                outcome = 'Game was cancelled!'
            else:
                outcome = 'Game still in progress!'
            return GameHistoryForm(moves=[step for step in steps],
                                    status=outcome)
        else:
            raise endpoints.NotFoundException('Game not found!')

api = endpoints.api_server([TicTacToeApi])
