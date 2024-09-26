from odoo import http, tools, SUPERUSER_ID, _
from odoo.addons.website.controllers.main import Website
from odoo.http import request
import json, sys, base64, pytz
from datetime import datetime, date, timedelta
from functools import reduce
from odoo import http
import logging, uuid, werkzeug
import base64


_logger = logging.getLogger(__name__)


class Maincontroller(Website):

    @http.route('/getApiUrl', type='http', auth="public", website=True, csrf=False)
    def getApiUrl(self, **kw):
        if kw.get('courses_id'):
            my_url = request.env['op.admission.register'].sudo().search(
                [('iframe_dashboard', '=', int(kw.get('my_url')))])
            getApiUrl = ""
            if my_url:
                getApiUrl = my_url.iframe_dashboard
            return json.dumps(dict(getApiUrl=str(getApiUrl)))
