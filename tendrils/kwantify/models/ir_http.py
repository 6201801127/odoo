from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super(IrHttp, self).session_info()
        result['some_key'] = get_some_value_from_db()
        return result
    # var session = require('web.session');
    # var myValue = session.some_key;
