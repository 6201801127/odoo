# -*- coding: utf-8 -*-

from odoo import models, fields

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


class kw_whatsapp_template(models.Model):
    _name = 'kw_whatsapp_template'
    _description = 'Kwantify whatsApp Templates'

    model_id = fields.Many2one('ir.model', string='Application Model', domain=MODEL_DOMAIN,
                               help="Enter business model you would like to integrate whatsApp notification.")

    name = fields.Char(string='Template Name', required=True)
    message = fields.Text(string='Message', required=True)
