import string
from unicodedata import category
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class kw_grievance_spoc_master(models.Model):

    _name = 'kw_grievance_spoc_master'
    _description = 'A model to manage spoc commite'
    _rec_name = 'spoc_person_id'


    spoc_person_id = fields.Many2one(string="SPOC Person",comodel_name='hr.employee') 


    @api.constrains('spoc_person_id')
    def _check_category(self):
        for rec in self:
            record = self.env['kw_grievance_spoc_master'].search(
                [('spoc_person_id', '=', rec.spoc_person_id.id)]) - self
            if record:
                raise ValidationError(f'This Record is  already exists .')
    
    
        
  