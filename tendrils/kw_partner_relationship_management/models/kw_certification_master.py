# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.      
# Create By: Asish Kumar Nayak, On -1st Oct 2020                          #
###############################################################################
import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class KwCertificationMaster(models.Model):
    _name = 'kw_certification_master'
    _description = 'Certification Master Model'
    _order = 'name ASC'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('unique_type_name', 'unique(name)', 'The Certifications type already exists')
    ]

    @api.multi
    def unlink(self):
        partner_rec = self.env['res.partner'].sudo().search([('certification_ids', 'in', self.ids)])
        if partner_rec:
            raise ValidationError("You are trying to delete a record that is still referenced!")
        result = super(KwCertificationMaster, self).unlink()
        self.env.user.notify_success("Certification record deleted successfully.")
        return result

    @api.constrains('name')
    def name_constratints(self):
        if not re.findall('[A-Za-z0-9]', self.name):
            raise ValidationError("Invalid Certification Name")