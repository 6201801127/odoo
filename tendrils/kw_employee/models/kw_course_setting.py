from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kw_course_setting(models.Model):
    _name = 'kw_course_setting'
    _description = "A master model to created for courses year difference."
    _rec_name = "course_id"

    course_id = fields.Many2one('kwmaster_course_name', string='Course', required=True,
                                domain="[('course_type','=','1')]")
    child_id = fields.Many2one('kwmaster_course_name', string='Child Course Name', domain="[('course_type','=','1')]")
    diff_year = fields.Integer(string="Difference year")

    @api.constrains('course_id','diff_year')
    def check_course_id(self):
        record = self.env['kw_course_setting'].sudo().search([]) - self
        for data in record:
            if data.course_id.id == self.course_id.id:
                raise ValidationError("The Course ID already exists.")
            elif data.child_id.id == self.child_id.id:
                raise ValidationError("The Child course already exists.")
        for rec in self:
            if rec.diff_year < 0:
                raise ValidationError("Difference year can not be negative value")
