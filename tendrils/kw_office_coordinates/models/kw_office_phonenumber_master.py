from odoo import models, fields, api

class kw_office_phone(models.Model):
    _name           = 'kw_office_phone'
    _description    ="A model to add phone numbers with ISD code."
    _rec_name       = 'tele_ph_num'

    isd_code        = fields.Char(string="Isd Code")
    tele_ph_num     = fields.Char(string="Telephone Number")