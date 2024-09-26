from odoo import models, fields,api


class kw_adv_buffer_master(models.Model):
    _name = 'kw_advance_buffer_period_master'
    _description = 'Buffer Period Master'

    @api.onchange('buffer_period')
    def _compute_name(self):
        self.name = str(self.buffer_period) + " Months"

    buffer_period = fields.Integer(string='Buffer Period',required=True)
    name = fields.Char(string='Buffered Months', compute= _compute_name,store=True,readonly=True)
