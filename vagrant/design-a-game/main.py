#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import webapp2
from google.appengine.api import mail, app_identity
from google.appengine.ext import ndb
from models import UserProfile, Game


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each user with a move pending.
        Called periodically using a cron job"""
        app_id = app_identity.get_application_id()
        q = Game.query()
        games = q.filter(ndb.AND(Game.game_over == False,
                Game.game_cancelled == False)
                ).fetch()

        for game in games:
            user = game.next_move_user.get()
            subject = 'TicTacToe game reminder'
            body = 'Hello {}, this is a gentle reminder '.format(user.name) + \
            'to make your move in game: {}'.format(game.key.urlsafe())
            mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                           user.email,
                           subject,
                           body)


class SendTurnNotification(webapp2.RequestHandler):
    def post(self):
        """Send turn notification email to user"""
        app_id = app_identity.get_application_id()
        email = self.request.get('email')
        subject = 'TicTacToe turn notification'
        body = 'Hi, it is your turn to make a move in game: {}'.format(
            self.request.get('game'))
        mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                       email,
                       subject,
                       body)

app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail),
    ('/tasks/send_turn_notification', SendTurnNotification),
], debug=True)
