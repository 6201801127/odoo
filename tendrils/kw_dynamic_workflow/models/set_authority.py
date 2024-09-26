# -*- coding: utf-8 -*-
from odoo import models, fields, api

MODEL_DOMAIN = """[
        ('state', '=', 'base'),
        ('transient', '=', False),
        '!',
        '|',
        '|',
        '|',
        '|',
        '|',
        '|',
        '|',
        ('model', '=ilike', 'res.%'),
        ('model', '=ilike', 'ir.%'),
        ('model', '=ilike', 'odoo.workflow%'),
        ('model', '=ilike', 'bus.%'),
        ('model', '=ilike', 'base.%'),
        ('model', '=ilike', 'base_%'),
        ('model', '=', 'base'),
        ('model', '=', '_unknown'),
    ]"""


class OdooSetAuthority(models.Model):
    _name = 'odoo.setauthority'
    _description = 'Odoo Set Authority'

    name = fields.Char(string='Name', help="Give authority setting a name.")
    model_id = fields.Many2one('ir.model', string='Model', domain=MODEL_DOMAIN,
                               help="Enter business model you would like to set authority.")
    location_id = fields.Many2one('res_country', string='Location')
    authority_ids = fields.One2many('odoo_authorities', 'authority_id', string='Authority')


class odoo_authorities(models.Model):
    _name = 'odoo_authorities'
    _description = 'Odoo Workflow set authority groups'

    name = fields.Many2one('res.groups', string='Authority/Role')
    authority_id = fields.Many2one('odoo.setauthority', string='Authority')
    # category_id     = fields.Many2one('ir.model', string='Model', domain="[('state','=','base')]")
    # readonly        = fields.Boolean(string='Readonly')
    # required        = fields.Boolean(string='Required')
    # invisible       = fields.Boolean(string='Invisible')

    designation_ids = fields.Many2many('hr.job', string='Designation')
    group_ids = fields.Many2many('res.groups', string='Groups')
    user_ids = fields.Many2many('res.users', string='Users')
