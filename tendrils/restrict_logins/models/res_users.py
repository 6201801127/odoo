# -*- coding: utf-8 -*-


import logging
from datetime import datetime, timedelta

from odoo import SUPERUSER_ID
from odoo import fields, api
from odoo import models
from odoo.exceptions import AccessDenied
from odoo.http import request
from ..controllers.main import clear_session_history

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    sid = fields.Char('Session ID')
    exp_date = fields.Datetime('Expiry Date')
    logged_in = fields.Boolean('Logged In')
    last_update = fields.Datetime(string="Last Connection Updated")
    verification_code = fields.Char(string="Verification Code")
    verification_expiry = fields.Datetime(string="Verification Expire Time")

    def with_user(self, user):
        """ with_user(user)
        Return a new version of this recordset attached to the given user, in
        non-superuser mode, unless `user` is the superuser (by convention, the
        superuser is always in superuser mode.)
        """
        if not user:
            return self
        return self.with_env(self.env(user=user))

    @classmethod
    # @api.model
    def _login(cls, db, login, password):
        if not password:
            raise AccessDenied()
        ip = request.httprequest.environ['REMOTE_ADDR'] if request else 'n/a'
        try:
            with cls.pool.cursor() as cr:
                self = api.Environment(cr, SUPERUSER_ID, {})[cls._name]
                with self._assert_can_auth():
                    user = self.search(self._get_login_domain(login))
                    if not user:
                        raise AccessDenied()
                    user = user.with_user(user)
                    user._check_credentials(password)
                    # check sid and exp date
                    if user.exp_date and user.sid and user.logged_in:
                        _logger.warning("User %s is already logged in "
                                        "into the system!. Multiple "
                                        "sessions are not allowed for "
                                        "security reasons!" % user.name)
                        request.uid = user.id
                        raise AccessDenied("already_logged_in")
                    # save user session detail if login success
                    # print(request.session.sid)
                    user._save_session()
                    user._update_last_login()
        except AccessDenied:
            _logger.info("Login failed for db:%s login:%s from %s", db, login, ip)
            raise
        _logger.info("Login successful for db:%s login:%s from %s", db, login, ip)
        return user.id

    def _clear_session(self):
        """
            Function for clearing the session details for user
        """
        self.write({'sid': False, 'exp_date': False, 'logged_in': False, 'last_update': datetime.now()})
        # print("inside clear session")

    def _save_session(self):
        """
            Function for saving session details to corresponding user
        """
        exp_date = datetime.utcnow() + timedelta(minutes=120)  # 2 hrs
        sid = request.httprequest.session.sid

        # print("inside save session "+sid)
        self.with_user(SUPERUSER_ID).write({'sid': sid, 'exp_date': exp_date,
                                            'logged_in': True,
                                            'last_update': datetime.now()})

    def _validate_sessions(self):
        """
            Function for validating user sessions
        """
        users = self.search([('exp_date', '!=', False)])
        for user in users:
            if user.exp_date < datetime.utcnow():
                # clear session session file for the user
                session_cleared = clear_session_history(user.sid)
                if session_cleared:
                    # clear user session
                    _logger.info("Cron _validate_session: "
                                 "cleared session user: %s" % (user.name))
                    # print("Cron _validate_session: "
                    #              "cleared session user: %s" % (user.name))
                else:
                    _logger.info("Cron _validate_session: failed to clear session user: %s" % (user.name))
                    # print("Cron _validate_session: failed to clear session user: %s" % (user.name))
                user._clear_session()

    # #log-out from all devices : By : T Ketaki Debadarshini
    def action_log_out_from_all_devices(self):
        session_cleared = clear_session_history(self.sid)
        # if session_cleared:
        #     # clear user session
        #     # print("Cron _validate_session: cleared session user: %s" % (self.name))
        #     pass
        # else:
        #     # print("Cron _validate_session: failed to clear session user: %s" % (self.name))
        #     pass
        self._clear_session()
