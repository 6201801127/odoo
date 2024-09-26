# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from math import modf

class kw_feedback_weightage_master(models.Model):
    _name = 'kw_feedback_weightage_master'
    _description = 'Assessment feedback configuration weightage master.'

    name = fields.Char(string='Name', required=True,autocomplete="off")
    value = fields.Char(string='Value', required=True,autocomplete="off")
    from_range = fields.Float(string='From Range (in %)', default=0.0, required=True)
    to_range = fields.Float(string='To Range (in %)', default=0.0, required=True)
    remark = fields.Char(string='Remark',autocomplete="off")

    @api.constrains('value','name')
    def check_value(self):
        record = self.env['kw_feedback_weightage_master'].search([]) - self
        for info in record:

            if info.value.lower() == self.value.lower():
                raise ValidationError('Exists! Already a same weightage value exist.')

            if info.name.lower() == self.name.lower():
                raise ValidationError('Exists! Already a same weightage name exist.')
            
    @api.multi
    def name_get(self):
        result = []
        for record in self:
            record_name = str(record.value) + ' (' + str(record.name) + ')'
            result.append((record.id, record_name))

        return result


    '''Render form_range or to_range as integer or float to web template '''
    def render_float_or_int(self,value):
        x = modf(value)
        dec = str(value).split('.')[-1]
        if int(dec) != 0 :
            return value
        else :
            return int(value)
        #     print('Decimal')
        # print('Range Value',dec)
        # return value