from odoo import models,fields,api
from odoo.exceptions import ValidationError


class kw_grade_pay(models.Model):
    _name = "kw_grade_pay"
    _description = "Grade Pay"
    _rec_name = 'grade'

    country = fields.Many2one('res.country', string="Country")
    grade = fields.Many2one('kwemp_grade_master', string="Grade")
    band = fields.Many2one('kwemp_band_master', string="Band")
    basic_min = fields.Float(string="Basic Minimum")
    basic_max = fields.Float(string="Basic Maximum")
    increment = fields.Float(string="Increment")
    has_band = fields.Boolean('Has Band')

    @api.onchange('grade','country')
    def _onchange_grade(self):
        if self.country and self.grade:
            record_id = self.env['kw_grade_pay'].sudo().search([])
            for record in record_id:
                if self.grade == record.grade and self.band == record.band and self.country == record.country:
                    raise ValidationError('A record with same Grade and Country already exist.')

    @api.onchange('grade')
    def onchange_grade(self):
        for rec in self:
            rec.band = False
            if rec.grade.has_band:
                rec.has_band = True
            else:
                rec.has_band = False