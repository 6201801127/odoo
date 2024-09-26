"""
Module for Web Controllers Debug Mode.

This module contains web controllers for enabling debug mode in Odoo web interface.

"""
from odoo import http
from odoo.http import request
import werkzeug
from odoo.addons.web.controllers.main import Home


class HomeDebugModeEnable(Home):
    """
    Controller class for enabling debug mode in Odoo web interface.
    """
    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        debug = kw.get('debug', False) if 'debug' in kw.keys() else False
        user_id = request.context.get('uid', False)
        if debug or debug == '':
            if user_id:
                user = request.env['res.users'].sudo().browse(user_id)
                if not user.has_group('disable_debug_mode.group_debug_mode_enable'):
                    return werkzeug.utils.redirect('/web/session/logout')
        return super(HomeDebugModeEnable, self).web_client(s_action=s_action, **kw)
