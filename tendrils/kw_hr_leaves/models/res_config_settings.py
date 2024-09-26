from odoo import api, fields, models
from odoo.addons.base.models.res_partner import _tz_get


class LeaveResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    on_tour = fields.Boolean(string="Enable to Escalate when On Tour")
    on_leave = fields.Boolean(string="Enable to Escalate when On Leave")
    half_day = fields.Float(string='Half Day(in hrs)')
    full_day = fields.Float(string='Full Day(in hrs)')

    @api.model
    def get_values(self):
        res = super(LeaveResConfigSettings, self).get_values()
        param = self.env['ir.config_parameter'].sudo()
        res.update(
            on_tour=param.get_param('kw_hr_leaves.on_tour'),
            on_leave=param.get_param('kw_hr_leaves.on_leave'),
            half_day=float(param.get_param('kw_hr_leaves.half_day')),
            full_day=float(param.get_param('kw_hr_leaves.full_day')),
        )
        return res

    @api.multi
    def set_values(self):
        super(LeaveResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
       
        param.set_param('kw_hr_leaves.on_tour', self.on_tour or False)
        param.set_param('kw_hr_leaves.on_leave',self.on_leave or False)
        param.set_param('kw_hr_leaves.half_day', self.half_day or False)
        param.set_param('kw_hr_leaves.full_day', self.full_day or False)
