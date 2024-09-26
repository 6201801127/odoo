# -*- coding: utf-8 -*-
# ##############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.      
# Create By: T Ketaki Debadrashini, On -8th Sep 2020                          #
# ##############################################################################
import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class KwPartnerTypeMaster(models.Model):
    _name = 'kw_partner_type_master'
    _description = 'Partner Types for Partner Relationship Management'
    _order = 'name ASC'

    name = fields.Char(string='Type Name', required=True)
    alias = fields.Char(string='Alias')
    short_code = fields.Char(string="Short Code")
    renewal_month_period = fields.Integer(string="Renewal Period")
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('unique_type_name', 'unique(name)', 'The type name already exists'),
        ('unique_type_alias', 'unique(alias)', 'The alias already exists')
    ]

    @api.constrains('alias')
    def attendance_mode_validation(self):
        for record in self:

            if not (re.match('^[a-zA-Z0-9_]+$', record.alias)):
                raise ValidationError("Only alphanumeric and underscore characters are allowed in alias field.")


class KwPartnerTechMaster(models.Model):
    _name = 'kw_partner_tech_service_master'
    _description = 'Service Offerings & Technologies Master for PRM'
    _order = 'type,name'

    name = fields.Char(string='Service/Technology/Product', required=True)
    type = fields.Selection(string='Type', selection=[('1', 'Service'), ('2', 'Technology'), ('3', 'Product')],
                            required=True)
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        (
            'unique_service_tech_name',
            'unique(type,name)',
            _('The service/technology name already exists')
        )
    ]

    @api.multi
    def unlink(self):
        partner_rec = self.env['res.partner']
        obj = partner_rec.sudo().search(['|',('service_offering_ids', 'in', self.ids),('tech_ids', 'in', self.ids)])
        if obj:
            raise ValidationError("You are trying to delete a record that is still referenced!")
        result = super(KwPartnerTechMaster, self).unlink()
        return result

    @api.constrains('name')
    def name_constratints(self):
        if not re.findall('[A-Za-z0-9]', self.name):
            raise ValidationError("Invalid Service/Technology/Product Name")