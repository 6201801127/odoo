# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import date, datetime, time
from ast import literal_eval


class ResConfigSettingsCanteen(models.TransientModel):
    _inherit = 'res.config.settings'

    head_cook_ids = fields.Many2many('hr.employee','kw_canteen_employee_rel','employee_id','canteen_id',string='Cook')
    notify_cook_ids = fields.Many2many('hr.employee','kw_canteen_notify_employee_rel','employee_id','canteen_id',string='Notify Cook')
    
    
    
  

    def set_values(self):
        res = super(ResConfigSettingsCanteen, self).set_values()
        self.env['ir.config_parameter'].set_param('kw_canteen.canteen', self.head_cook_ids.ids)
        self.env['ir.config_parameter'].set_param('kw_canteen.notify_cook_ids', self.notify_cook_ids.ids)
        
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettingsCanteen, self).get_values()
        canteen_ids = self.env['ir.config_parameter'].sudo().get_param('kw_canteen.canteen')
        lines = False
        if canteen_ids != False:
            lines = [(6, 0, literal_eval(canteen_ids))]
        notification_cook_ids = self.env['ir.config_parameter'].sudo().get_param('kw_canteen.notify_cook_ids')
        cclines = False
        if notification_cook_ids != False:
            cclines = [(6, 0, literal_eval(notification_cook_ids))]
        res.update(
            head_cook_ids=lines,
            notify_cook_ids = cclines
        )
        return res

    
    