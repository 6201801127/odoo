# -*- coding: utf-8 -*-

from odoo import models, fields, api
import pytz

class kw_office_coordinates(models.Model):
    _name           = 'kw_office_coordinates'
    _description    = "A model to create office co-ordinate."
    _rec_name       = 'office_name'
    # _inherit        = "res.partner"

    country         = fields.Many2one('res.country', string="Country", required=True)
    city            = fields.Many2one('kw_city_master', string="City", required=True)
    office_name     = fields.Char(string="Office Name", required=True)
    office_addr     = fields.Text(string="Office Address")
    office_phone    = fields.One2many('kw_office_phone','tele_ph_num', string="Telephone Number", required=True)
    email           = fields.Char(string="Email Id")
    emp_code_prefix = fields.Char(string="Prefix for employee code")
    timezone        = fields.Selection('_tz_get', string='Timezone', required=True, default=lambda self: self.env.user.tz or 'UTC')
    currency        = fields.Char(string="Currency")
    photo           = fields.Binary(string="Upload Photo")
    brief_profile   = fields.Text(string="Brief profile")
    company_id      = fields.Many2one('res.partner', string="Company Name", domain=[('is_company', '=', True)])

    @api.model
    def _tz_get(self):
        return [(x, x) for x in pytz.all_timezones]


    @api.onchange('company_id')
    def _change_addr(self):
        if self.company_id:
            partner = self.company_id.id
            self.country = False
            self.city = False
            self.office_name = False
            return {'domain': {'country': ([('id', '=', partner)]),'city': ([('id', '=', partner)]),'office_name': ([('display_name', '=', partner)])}}
        