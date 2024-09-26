from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


class kw_institute_name(models.Model):
    _name = 'kwmaster_institute_name'
    _description = "A master model to create different institutes."

    name = fields.Char(string="Name", required=True, size=150)
    course_ids = fields.Many2one('kwmaster_course_name')
    kw_id = fields.Integer(string='Tendrils ID')
    inst_course_ids = fields.Many2many('kwmaster_course_name', 'institute_course_rel', string='Courses')
    active = fields.Boolean('Active', default=True)

    # @api.constrains('name')
    # def validate_institute_name(self):
    #     for rec in self:
    #         if re.match("^[a-zA-Z0-9 ,./()_-]+$", rec.name) == None:
    #             raise ValidationError("Invalid institute! Please provide a valid institute.")
    #         record = self.env['kwmaster_institute_name'].search([('name', '=', rec.name)]) - rec
    #         if record:
    #             raise ValidationError(f'The institute {rec.name} already exists.')
        # institutelist = []
        # courseid = ''
        # for data in self:
        #     institutelist.append(str(data.name).lower())
        #     courseid = data.course_ids.id
        # emptydata = []
        # for data in institutelist:
        #     if data not in emptydata:
        #         emptydata.append(data)
        #     else:
        #         raise ValidationError("The institute \"" + data + "\" already exists.")

        # record = self.env['kwmaster_institute_name'].search([]) - self
        # for info in record:
        #     if (info.name.lower() in institutelist) and (info.course_ids.id == courseid):
        #         raise ValidationError("The institute \"" + info.name + "\" already exists.")



    @api.model
    def create(self, vals):
        record = super(kw_institute_name, self).create(vals)
        if record:
            self.env.user.notify_success(message='New Institute created successfully.')
        else:
            self.env.user.notify_danger(message='New Institute creation failed.')
        return record

    @api.multi
    def write(self, vals):
        res = super(kw_institute_name, self).write(vals)
        if res:
            self.env.user.notify_success(message='Institute updated successfully.')
        else:
            self.env.user.notify_danger(message='Institute updation failed.')
        return res
