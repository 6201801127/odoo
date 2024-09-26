from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


class kw_course_name(models.Model):
    _name = 'kwmaster_course_name'
    _description = "A master model to create different courses."

    name = fields.Char(string="Name", required=True, size=100)
    code = fields.Char(string="Code", size=10)

    kw_id = fields.Integer(string='Tendrils ID')
    active = fields.Boolean('Active', default=True)

    course_type = fields.Selection(string=u'Category',
                                   selection=[('1', 'Educational Qualification'), ('2', 'Professional Qualification'),
                                              ('3', 'Training & Certification')], required=True)

    # description = fields.Char(string="Description")
    stream_ids = fields.One2many('kwmaster_stream_name', 'course_id')
    institute_ids = fields.One2many('kwmaster_institute_name', 'course_ids')

    @api.constrains('name', )
    def validate_course_name(self):
        if re.match("^[a-zA-Z0-9 ,./()_+-]+$", self.name) == None:
            raise ValidationError("Invalid course! Please provide a valid course.")

        record = self.env['kwmaster_course_name'].search([]) - self
        for info in record:
            if info.name.lower() == self.name.lower():
                raise ValidationError("The course \"" + self.name + "\" already exists.")

    @api.model
    def create(self, vals):
        record = super(kw_course_name, self).create(vals)
        if record:
            self.env.user.notify_success(message='New Course created successfully.')
        else:
            self.env.user.notify_danger(message='New Course creation failed.')
        return record

    @api.multi
    def write(self, vals):
        res = super(kw_course_name, self).write(vals)
        if res:
            self.env.user.notify_success(message='Course updated successfully.')
        else:
            self.env.user.notify_danger(message='Course updation failed.')
        return res
