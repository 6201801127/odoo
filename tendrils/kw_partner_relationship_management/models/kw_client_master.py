# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.      
# Create By: Asish Kumar Nayak, On -1st Oct 2020                          #
###############################################################################
import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class KwClientMaster(models.Model):
    _name = 'kw_client_master'
    _description = 'Client Master Model'
    _order = 'name ASC'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('unique_type_name', 'unique(name)', 'The client name already exists')
    ]

    @api.multi
    def unlink(self):
        partner_master_rec = self.env['kw_partner_master_rel']
        obj = partner_master_rec.sudo().search([('major_client', 'in', self.ids)])
        if obj:
            raise ValidationError("You are trying to delete a record that is still referenced!")
        result = super(KwClientMaster, self).unlink()
        self.env.user.notify_success("Client Record deleted successfully.")
        return result

    @api.constrains('name')
    def name_constratints(self):
        if not re.findall('[A-Za-z0-9]', self.name):
            raise ValidationError("Invalid Client Name")