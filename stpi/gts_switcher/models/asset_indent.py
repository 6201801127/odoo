from odoo import models, tools, fields, api, _
from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from odoo.http import request
import jwt


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def asset_indent_action(self):
        asset_id = self.coe_asset_id
        connection_rec = self.env['server.connection'].search([], limit=1)
        key = ",jy`\;4Xpe7%KKL$.VNJ'.s6)wErQa"
        if not connection_rec:
            raise UserError(_('No Server Connection setup !'))
        encoded_jwt = jwt.encode({'token': self.env.user.token}, key)
        action = {
                'name': connection_rec.name,
                'type': 'ir.actions.act_url',
                'url': str(connection_rec.url).strip() + "/asset/indent?login=" + str(self.env.user.login) + "&password=" + str(encoded_jwt.decode("utf-8")) +"&menu_id=" + str(asset_id),
                'target': 'new',
                }
        return action