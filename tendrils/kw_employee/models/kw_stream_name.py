from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


#   For Stream Details
class kw_stream_name(models.Model):
    _name = 'kwmaster_stream_name'
    _description = "A master model to create different streams."

    name = fields.Char(string="Name", required=True, size=100)
    course_id = fields.Many2one('kwmaster_course_name', string="Course", required=True)
    specialization_ids = fields.One2many('kwmaster_specializations', 'stream_id')
    kw_id = fields.Integer(string='Tendrils ID')
    active = fields.Boolean('Active', default=True)

    @api.constrains('name', 'course_id')
    def validate_stream_name(self):
        # print(re.match("^[0-9a-zA-Z/\s-.()]+$", self.name))
        if re.match("^[0-9a-zA-Z/\s\+-.()]+$", self.name) == None:
            raise ValidationError("Invalid stream! Please provide a valid stream.")
        streamlist = []
        courseid = ''
        for data in self:
            streamlist.append(str(data.name).lower())
            courseid = data.course_id.id
        emptydata = []
        for data in streamlist:
            if data not in emptydata:
                emptydata.append(data)
            else:
                raise ValidationError("The stream \"" + data + "\" already exists.")

        record = self.env['kwmaster_stream_name'].search([]) - self
        for info in record:
            if (info.name.lower() in streamlist) and (info.course_id.id == courseid):
                raise ValidationError("The stream \"" + info.name + "\" already exists.")

    @api.model
    def create(self, vals):
        record = super(kw_stream_name, self).create(vals)
        if record:
            self.env.user.notify_success(message='New Stream created successfully.')
        else:
            self.env.user.notify_danger(message='New Stream creation failed.')
        return record

    @api.multi
    def write(self, vals):
        res = super(kw_stream_name, self).write(vals)
        if res:
            self.env.user.notify_success(message='Stream updated successfully.')
        else:
            self.env.user.notify_danger(message='Stream updation failed.')
        return res
        #   For Institute Details
