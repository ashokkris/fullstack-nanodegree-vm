"""models.py - This file contains the class definitions for the Datastore
entities used by TicTacToe game api. Because these classes are also regular
Python classes they can include methods."""

from protorpc import messages
from google.appengine.ext import ndb


class UserProfile(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)
    num_won = ndb.IntegerProperty(default=0)
    num_drawn = ndb.IntegerProperty(default=0)
    num_lost = ndb.IntegerProperty(default=0)
    win_ratio = ndb.ComputedProperty(lambda self: self.compute_win_ratio())

    def compute_win_ratio(self):
        """Calculates a ratio representing games won to games played"""
        total_played = self.num_won + self.num_drawn + self.num_lost
        if total_played > 0:
            # A win gets 1 point, a draw 0.5 points and loss 0 points
            return (self.num_won + self.num_drawn * 0.5) / total_played
        else:
            return 0.0

    def to_form(self, message):
        """Returns a UserProfileForm representation of the UserProfile"""
        form = UserProfileForm()
        form.name = self.name
        form.email = self.email
        form.urlsafe_key = self.key.urlsafe()
        form.message = message
        return form

    def record_win(self):
        """Increments user wins"""
        self.num_won = self.num_won + 1
        self.put()

    def record_loss(self):
        """Increments user losses"""
        self.num_lost = self.num_lost + 1
        self.put()

    def record_draw(self):
        """Increments user draws"""
        self.num_drawn = self.num_drawn + 1
        self.put()

    def to_WinRatioForm(self):
        """Copy user's name and performance info to UserWinRatioForm"""
        return UserWinRatioForm(name=self.name, win_ratio=self.win_ratio)
    

class Game(ndb.Model):
    """Game object"""
    user1 = ndb.KeyProperty(required=True, kind='UserProfile')
    user2 = ndb.KeyProperty(required=True, kind='UserProfile')
    next_move_user = ndb.KeyProperty(required=True, kind='UserProfile')
    user1_squares = ndb.IntegerProperty(repeated=True)
    user2_squares = ndb.IntegerProperty(repeated=True)
    game_over = ndb.BooleanProperty(default=False)
    game_cancelled = ndb.BooleanProperty(default=False)
    winner = ndb.KeyProperty(kind='UserProfile')

    @classmethod
    def new_game(cls, user_1, user_2):
        """Creates and returns a new game"""
        game = Game(user1=user_1,
                    user2=user_2,
                    next_move_user=user_1)
        game.put()
        return game

    def end_game(self, winner=None):
        """Ends the game and record the winner. If winner is None, it implies
        that game ended in a draw"""
        self.game_over = True
        if winner is not None:
            self.winner = winner
        self.put()

    def cancel_game(self):
        """Aborts the game"""
        self.game_cancelled = True
        self.put()

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user1_name = self.user1.get().name
        form.user2_name = self.user2.get().name
        form.user1_squares = self.user1_squares
        form.user2_squares = self.user2_squares
        form.game_over = self.game_over
        form.game_cancelled = self.game_cancelled
        form.message = message
        return form


class UserProfileForm(messages.Message):
    """UserProfileForm -- UserProfile outbound form message"""
    name = messages.StringField(1, required=True)
    email = messages.StringField(2, required=True)
    urlsafe_key = messages.StringField(3, required=True)
    message = messages.StringField(4, required=True)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    user1_name = messages.StringField(2, required=True)
    user2_name = messages.StringField(3, required=True)
    user1_squares = messages.IntegerField(4, repeated=True)
    user2_squares = messages.IntegerField(5, repeated=True)
    game_over = messages.BooleanField(6, required=True)
    game_cancelled = messages.BooleanField(7, required=True)
    message = messages.StringField(8, required=True)
    next_move_user_name = messages.StringField(9)


class NewGameForm(messages.Message):
    """Used to create a new game - inbound form message"""
    user1_safe_key = messages.StringField(1, required=True)
    user2_safe_key = messages.StringField(2, required=True)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    square = messages.IntegerField(1, required=True)


class GamesListForm(messages.Message):
    """List of active games of a user - outbound form message"""
    url_safe_game_keys = messages.StringField(1, repeated=True)


class GameStepForm(messages.Message):
    """Outbound message representing a single move of the game"""
    name = messages.StringField(1, required=True)
    move = messages.IntegerField(2, required=True)


class GameHistoryForm(messages.Message):
    "Outbound message capturing step-by-step history of game's progress"
    moves = messages.MessageField(GameStepForm, 1, repeated=True)
    status = messages.StringField(2, required=True)


class UserWinRatioForm(messages.Message):
    """User performance metric outbound form message"""
    name = messages.StringField(1, required=True)
    win_ratio = messages.FloatField(2, required=True)


class UserWinRatioForms(messages.Message):
    """Multiple UserWinRatioForm outbound form message"""
    items = messages.MessageField(UserWinRatioForm, 1, repeated=True)
