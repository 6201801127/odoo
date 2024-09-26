# -*- coding: utf-8 -*-

from odoo import models, api, fields
from odoo.exceptions import ValidationError


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
        '|',
        ('model', '=ilike', 'kw_dms.%'),
        ('model', '=ilike', 'res.%'),
        ('model', '=ilike', 'ir.%'),
        ('model', '=ilike', 'odoo.workflow%'),
        ('model', '=ilike', 'bus.%'),
        ('model', '=ilike', 'base.%'),
        ('model', '=ilike', 'base_%'),
        ('model', '=', 'base'),
        ('model', '=', '_unknown'),
    ]"""

class Directory_integration(models.Model):

    _inherit = 'kw_dms.directory'


    ##for file downloading count
    # directory_model_integration_ids = fields.Many2many('ir.model',
    #     string      =u'Model Integration',
    #     comodel_name='ir.model',
    #     relation    ='kw_dms_directory_model_rel',
    #     column1     ='dir_id',
    #     column2     ='model_id',
    #     domain      =MODEL_DOMAIN,
    # )

    model_id = fields.Many2one('ir.model',
        string      =u'Model Integration',
        domain      =MODEL_DOMAIN,
    )


    @api.constrains('model_id')
    def validation(self):

        for rec in self:
            # Check if there is no duplicate 
            if rec.model_id:
                res = self.search_count([
                    ('id', '!=', rec.id),
                    ('model_id', '=', rec.model_id.id),
                ])

                if res:
                    raise ValidationError("The selected model has been tagged with another directory. Duplicate tagging is not allowed ")


    