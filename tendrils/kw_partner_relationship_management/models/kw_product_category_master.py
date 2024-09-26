# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.      
# Create By: Asish Kumar Nayak, On -1st Oct 2020                          #
###############################################################################
import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class KwProductCategoryMaster(models.Model):
    _name = 'kw_product_category_master'
    _description = 'Product Category Master Model'
    _order = 'name ASC'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('unique_type_name', 'unique(name)', 'The product category already exists')
    ]


    @api.multi
    def unlink(self):
        partner_rec = self.env['kw_partner_master_rel'].sudo().search([('product_category', 'in', self.ids)])
        if partner_rec:
            raise ValidationError("You are trying to delete a record that is still referenced!")
        result = super(KwProductCategoryMaster, self).unlink()
        self.env.user.notify_success("Product Category record deleted successfully.")
        return result


    @api.constrains('name')
    def name_constratints(self):
        if not re.findall('[A-Za-z0-9]', self.name):
            raise ValidationError("Invalid Product Category Name")