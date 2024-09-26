# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.      
# Create By: Asish Kumar Nayak, On -1st Oct 2020                          #
###############################################################################
import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class KwProductMaster(models.Model):
    _name = 'kw_product_master'
    _description = 'Product Master Model'
    _order = 'name ASC'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('unique_type_name', 'unique(name)', 'The product name already exists')
    ]

    @api.multi
    def unlink(self):
        partner_master_rec = self.env['kw_partner_master_rel']
        obj = partner_master_rec.sudo().search([('prduct_id', 'in', self.ids)])
        if obj:
            raise ValidationError("You are trying to delete a record that is still referenced!")
        result = super(KwProductMaster, self).unlink()
        self.env.user.notify_success("Product Record deleted successfully.")
        return result

    @api.constrains('name')
    def name_constratints(self):
        if not re.findall('[A-Za-z0-9]', self.name):
            raise ValidationError("Invalid Product Name")