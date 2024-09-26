# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class OccasionMaster(models.Model):
    _name = 'kw_occasion_master'
    _description = "Occasion"

    name = fields.Char("Name", required=True)
    code = fields.Char("Code", )
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer(
        "Sequence", default=10,
        help="Gives the sequence order of qualification.")

    @api.constrains('name')
    def check_duplicate(self):
        existing = self.env['kw_occasion_master'].sudo().search([]) - self
        for record in self:
            for data in existing:
                if record.name.lower() == data.name.lower():
                    raise ValidationError(f"The name {record.name} is already exists.")
                # if record.code.lower() == data.code.lower():
                #     raise ValidationError(f"The code {record.code} is already exists.")


class GuestMaster(models.Model):
    _inherit = "res.partner"

    is_guest = fields.Boolean('Guest')
    dept_sbu = fields.Many2one('kw_corp_sbu_master', string='Department/SBU')
    dept = fields.Char('Department')
    address = fields.Char('Address', compute='_compute_address', )
    delivery_boy = fields.Many2one('kw_corp_delivery_master', string="Delivered By")
    organisation = fields.Many2one('kw_corp_organization_master', string='Organisation')

    def _compute_address(self):
        for add in self:
            street = street2 = city = state = country = zip = ''
            if add.street: street = add.street
            if add.street2: street2 = add.street2
            if add.city: city = add.city
            if add.state_id: state = add.state_id.name
            if add.country_id: country = add.country_id.name
            if add.zip: zip = add.zip
            add.address = street + " " + street2 + " " + city + " " + state + " " + country + " " + zip


class TagMaster(models.Model):
    _name = 'kw_corp_tag_master'
    _description = "Tag"

    name = fields.Char("Name", required=True)
    code = fields.Char("Code", )
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer(
        "Sequence", default=10,
        help="Gives the sequence order of qualification.")

    @api.constrains('name')
    def check_duplicate(self):
        existing = self.env['kw_corp_tag_master'].sudo().search([]) - self
        for record in self:
            for data in existing:
                if record.name.lower() == data.name.lower():
                    raise ValidationError(f"The name {record.name} is already exists.")


class SBUMaster(models.Model):
    _name = 'kw_corp_sbu_master'
    _description = "SBU"

    name = fields.Char("Name", required=True)
    code = fields.Char("Code", )
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer(
        "Sequence", default=10,
        help="Gives the sequence order of qualification.")

    @api.constrains('name')
    def check_duplicate(self):
        existing = self.env['kw_corp_sbu_master'].sudo().search([]) - self
        for record in self:
            for data in existing:
                if record.name.lower() == data.name.lower():
                    raise ValidationError(f"The name {record.name} is already exists.")


class CategoryMaster(models.Model):
    _name = 'kw_corp_category_master'
    _description = "Category Master"

    name = fields.Char("Name", required=True)
    code = fields.Char("Code", )
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer(
        "Sequence", default=10,
        help="Gives the sequence order of qualification.")

    @api.constrains('name')
    def check_duplicate(self):
        existing = self.env['kw_corp_category_master'].sudo().search([]) - self
        for record in self:
            for data in existing:
                if record.name.lower() == data.name.lower():
                    raise ValidationError(f"The name {record.name} is already exists.")


class GiftMaster(models.Model):
    _name = 'kw_corp_gift_master'
    _description = "Gift Master"

    name = fields.Char("Name", required=True)
    code = fields.Char("Code", )
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer(
        "Sequence", default=10,
        help="Gives the sequence order of qualification.")

    @api.constrains('name')
    def check_duplicate(self):
        existing = self.env['kw_corp_gift_master'].sudo().search([]) - self
        for record in self:
            for data in existing:
                if record.name.lower() == data.name.lower():
                    raise ValidationError(f"The name {record.name} is already exists.")


class DeliveryMaster(models.Model):
    _name = 'kw_corp_delivery_master'
    _description = "Delivery Master"

    name = fields.Char("Name", required=True)
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer(
        "Sequence", default=10,
        help="Gives the sequence order of qualification.")
    employee_id = fields.Many2one('hr.employee', string="Employee")


class DeliveryMaster(models.Model):
    _name = 'kw_corp_organization_master'
    _description = "Delivery Master"

    name = fields.Char("Name", required=True)
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer(
        "Sequence", default=10,
        help="Gives the sequence order of qualification.")
