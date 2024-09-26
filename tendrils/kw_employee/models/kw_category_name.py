from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


# For category
class kw_category_name(models.Model):
    _name = 'kwmaster_category_name'
    _description = "A master model to create different categories according to roles."
    _order = "name asc"

    name = fields.Char(string="Name", required=True, size=100)
    code = fields.Char(string="Code")
    role_ids = fields.Many2one('kwmaster_role_name')
    kw_id = fields.Integer(string='Tendrils ID')
    active = fields.Boolean('Active', default=True)

    @api.constrains('name', 'role_ids')
    def validate_category(self):
        if re.match("^[0-9a-zA-Z/\s\+-.()&]+$", self.name) == None:
            raise ValidationError("Invalid category! Please provide a valid category.")
        categorylist = []
        for data in self:
            categorylist.append(str(data.name).lower())
            roleid = data.role_ids.id
        temp = []
        for data in categorylist:
            if data not in temp:
                temp.append(data)
            else:
                raise ValidationError("The category \"" + data + "\" already exists.")

        record = self.env['kwmaster_category_name'].search([]) - self
        for info in record:
            if (info.name.lower() in categorylist) and (info.role_ids.id == roleid):
                raise ValidationError("The category " + info.name + " already exists.")

    @api.model
    def create(self, vals):
        record = super(kw_category_name, self).create(vals)
        if record:
            self.env.user.notify_success(message='New Employee category created successfully.')
        else:
            self.env.user.notify_danger(message='New Employee category creation failed.')
        return record

    @api.multi
    def write(self, vals):
        res = super(kw_category_name, self).write(vals)
        if res:
            self.env.user.notify_success(message='Employee category updated successfully.')
        else:
            self.env.user.notify_danger(message='Employee category updation failed.')
        return res
