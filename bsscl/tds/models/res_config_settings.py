# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import date, datetime, time


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tds_start_date = fields.Date(string='Start Date')
    enable_tds = fields.Boolean(string='Enable TDS')
    actual_start_date=fields.Date(string='Actual Start Date')
    actual_end_date=fields.Date(string='Actual End Date')
    company_pan = fields.Char(string='PAN')
    company_tan = fields.Char(string='TAN')
    from_day = fields.Char(string='From Day')
    to_day = fields.Char(string='To Day')
    start_month = fields.Selection([('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
                              ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
                              ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December'), ],
                             string="Month")
    start_day = fields.Char(string='Visible Day')
    end_month = fields.Selection([('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
                              ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
                              ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December'), ],
                             string="Month")
    end_day = fields.Char(string='Visible Day')

    def set_values(self):
        super().set_values()
        param = self.env['ir.config_parameter'].sudo()

        field1 = self.tds_start_date or False
        field2 = self.enable_tds or False
        field3 = self.actual_start_date or False
        field4 = self.actual_end_date or False
        field5 = self.company_pan or False
        field6 = self.company_tan or False
        field7 = self.from_day or False
        field8 = self.to_day or False
        field9 = self.start_month or False
        field10 = self.start_day or False
        field11 = self.end_month or False
        field12 = self.end_day or False

        param.set_param('tds.run_esi_schedule_start_date', field1)
        param.set_param('tds.enable_tds', field2)
        param.set_param('tds.actual_start_date', field3)
        param.set_param('tds.actual_end_date', field4)
        param.set_param('tds.company_pan', field5)
        param.set_param('tds.company_tan', field6)
        param.set_param('tds.from_day', field7)
        param.set_param('tds.to_day', field8)
        param.set_param('tds.start_month', field9)
        param.set_param('tds.start_day', field10)
        param.set_param('tds.end_month', field11)
        param.set_param('tds.end_day', field12)




    @api.model
    def get_values(self):
        res = super().get_values()
        res.update(
            tds_start_date=self.env['ir.config_parameter'].sudo().get_param('tds.run_esi_schedule_start_date'),
            enable_tds=self.env['ir.config_parameter'].sudo().get_param('tds.enable_tds'),
            actual_start_date=self.env['ir.config_parameter'].sudo().get_param('tds.actual_start_date'),
            actual_end_date=self.env['ir.config_parameter'].sudo().get_param('tds.actual_end_date'),
            company_pan=self.env['ir.config_parameter'].sudo().get_param('tds.company_pan'),
            company_tan=self.env['ir.config_parameter'].sudo().get_param('tds.company_tan'),
            from_day=self.env['ir.config_parameter'].sudo().get_param('tds.from_day'),
            to_day=self.env['ir.config_parameter'].sudo().get_param('tds.to_day'),
            start_month = self.env['ir.config_parameter'].sudo().get_param('tds.start_month'),
            start_day = self.env['ir.config_parameter'].sudo().get_param('tds.start_day'),
            end_month = self.env['ir.config_parameter'].sudo().get_param('tds.end_month'),
            end_day = self.env['ir.config_parameter'].sudo().get_param('tds.end_day')

        )

        return res
