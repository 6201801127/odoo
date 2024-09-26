from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


# for Passing Details(Specialization)
class kw_profile_specializations(models.Model):
    _name = 'kwmaster_specializations'
    _description = "A master model to create specializations according to streams."
    _order = 'name'

    name = fields.Char(string="Name", required=True, size=150)
    stream_id = fields.Many2one('kwmaster_stream_name', string="Stream", required=True)
    kw_id = fields.Integer(string='Tendrils ID')
    active = fields.Boolean('Active', default=True)

    @api.constrains('name', 'stream_id')
    def validate_specialization_name(self):
        if re.match("^[0-9a-zA-Z/\s\+-.()]+$", self.name) == None:
            raise ValidationError("Invalid specialization! Please provide a valid specialization.")
        # specializationlist = []
        # for data in self:
        #     specializationlist.append(str(data.name).lower)
        #     streamid = data.stream_id.id
        # temp = []
        # streamid = ''
        # for data in specializationlist:
        #     if data not in temp:
        #         temp.append(data)
        #     else:
        #         raise ValidationError("The specialization \"" + data + "\" already exists.")
        # record = self.env['kwmaster_specializations'].search([]) - self
        # for info in record:
        #     if (info.name.lower() in specializationlist) and (info.stream_id.id == streamid):
        #         raise ValidationError("The specialization \"" + self.name + "\" already exists.")

    # @api.constrains('name', 'stream_id')
    # def validate_stream(self):
    #     record = self.env['kwmaster_specializations'].search([]) - self
    #     for info in record:
    #         if (info.name.lower() == self.name.lower()) and (info.stream_id == self.stream_id):
    #             raise ValidationError("The Specializaion \"" + self.name + "\"  already exists.")

    @api.model
    def create(self, vals):
        record = super(kw_profile_specializations, self).create(vals)
        if record:
            self.env.user.notify_success(message='New Specialization created successfully.')
        else:
            self.env.user.notify_danger(message='New Specialization creation failed.')
        return record

    @api.multi
    def write(self, vals):
        res = super(kw_profile_specializations, self).write(vals)
        if res:
            self.env.user.notify_success(message='Specialization updated successfully.')
        else:
            self.env.user.notify_danger(message='Specialization updation failed.')
        return res
