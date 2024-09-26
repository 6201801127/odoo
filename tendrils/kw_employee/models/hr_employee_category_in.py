from odoo import models, fields, api


class hr_employee_category(models.Model):
    _inherit = "hr.employee.category"

    name = fields.Char(string=u'Employee Tag', size=100, required=True)
    kw_id = fields.Integer(string='Tendrils ID')

    @api.constrains('name')
    def check_name(self):
        exists_name = self.env['hr.employee.category'].search([('name', '=', self.name), ('id', '!=', self.id)])
        if exists_name:
            raise ValueError("This Employee tag \"" + self.name + "\" already exists.")

    @api.model
    def create(self, vals):
        record = super(hr_employee_category, self).create(vals)
        if record:
            self.env.user.notify_success(message='Employee Tag created successfully.')
        else:
            self.env.user.notify_danger(message='Employee Tag creation failed.')
        return record

    @api.multi
    def write(self, vals):
        res = super(hr_employee_category, self).write(vals)
        if res:
            self.env.user.notify_success(message='Employee Tag updated successfully.')
        else:
            self.env.user.notify_danger(message='Employee Tag update failed.')
        return res
