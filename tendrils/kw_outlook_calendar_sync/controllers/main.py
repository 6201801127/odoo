# -*- coding: utf-8 -*-

import odoo
from odoo import http
from odoo.http import request, Response
from base64 import b64encode
import json, requests
import werkzeug


# class OutlookCalendar(http.Controller):

#     @http.route(['/get_callback_google'], type='http', auth="none")
#     def callback_google(self, code=None, **kw):
#         redirect_url = "/web#id=%i&model=res.company&view_type=form" % 1
#         return werkzeug.utils.redirect(redirect_url or '', 301)
