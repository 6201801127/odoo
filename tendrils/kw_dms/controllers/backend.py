

import logging

from odoo import _, http
from odoo.http import request

_logger = logging.getLogger(__name__)

class BackendController(http.Controller):

    @http.route('/config/kw_dms.forbidden_extensions', type='json', auth="user")
    def forbidden_extensions(self, **kw):
        params = request.env['ir.config_parameter'].sudo()
        return {
            'forbidden_extensions': params.get_param("kw_dms.forbidden_extensions", default="")
        }


