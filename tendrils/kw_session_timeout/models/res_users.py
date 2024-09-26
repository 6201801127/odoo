import logging

from os.path import getmtime
from time import time
from os import utime

from odoo import api, http, models
from odoo.http import SessionExpiredException

from datetime import datetime
import pytz

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model_cr_context
    def _auth_timeout_get_ignored_urls(self):
        """Pluggable method for calculating ignored urls
        Defaults to stored config param
        """
        params = self.env['ir.config_parameter']
        return params._auth_timeout_get_parameter_ignored_urls()

    @api.model_cr_context
    def _auth_timeout_deadline_calculate(self):
        """Pluggable method for calculating timeout deadline
        Defaults to current time minus delay using delay stored as config
        param.
        """
        params = self.env['ir.config_parameter']
        delay = params._auth_timeout_get_parameter_delay()
        # print("Delay Is...", delay)
        if delay <= 0:
            return False
        return time() - delay

    @api.model_cr_context
    def _auth_timeout_session_terminate(self, session):
        """Pluggable method for terminating a timed-out session

        This is a late stage where a session timeout can be aborted.
        Useful if you want to do some heavy checking, as it won't be
        called unless the session inactivity deadline has been reached.

        Return:
            True: session terminated
            False: session timeout cancelled
        """
        if session.db and session.uid:
            session.logout(keep_db=True)
        return True

    @api.model_cr_context
    def _auth_timeout_check(self):
        """Perform session timeout validation and expire if needed."""

        if not http.request:
            return

        session = http.request.session

        # Calculate deadline
        deadline = self._auth_timeout_deadline_calculate()

        # Check if past deadline
        expired = False
        if deadline is not False:
            path = http.root.session_store.get_session_filename(session.sid)
            try:
                tz_india = pytz.timezone('Asia/Kolkata')

                expired = getmtime(path) < deadline

                current_date = datetime.now(tz_india).date()
                session_modified_date = datetime.fromtimestamp(getmtime(path)).replace(tzinfo=pytz.utc).astimezone(
                    tz_india).date()

                date_changed = current_date > session_modified_date

                # print("Today date object is --------------  ", current_date)
                # print("User Session Modified date object is --------- ", session_modified_date)
            except OSError:
                _logger.exception(
                    'Exception reading session file modified time.',
                )
                # Force expire the session. Will be resolved with new session.
                expired = True

        # Try to terminate the session
        terminated = False
        if date_changed:
            terminated = self._auth_timeout_session_terminate(session)
        elif expired:
            terminated = self._auth_timeout_session_terminate(session)

        # If session terminated, all done
        if terminated:
            raise SessionExpiredException("Session expired")

        # Else, conditionally update session modified and access times
        ignored_urls = self._auth_timeout_get_ignored_urls()

        if http.request.httprequest.path not in ignored_urls:
            if 'path' not in locals():
                path = http.root.session_store.get_session_filename(
                    session.sid,
                )
            try:
                utime(path, None)
            except OSError:
                _logger.exception(
                    'Exception updating session file access/modified times.',
                )
