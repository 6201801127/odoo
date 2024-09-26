# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class TrainingMaterial(models.Model):
    _name = 'kw_training_material'
    _rec_name = "description"
    _description = "Kwantify Training Material"
    
    training_id = fields.Many2one(
        'kw_training', string="Training", required=True, ondelete="cascade")
    material = fields.Binary(string="Attachment", attachment=True)
    description = fields.Char(string="Material Name")

    @api.constrains('description')
    def _check_description(self):
        for material in self:
            if re.match("^[a-zA-Z0-9 .]+$", material.description) == None:
                raise ValidationError("Invalid name! Please provide a valid name.")
            
    
