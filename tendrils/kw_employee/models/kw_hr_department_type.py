from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError, Warning


class kw_hr_department_type(models.Model):
    _name = "kw_hr_department_type"
    _description = "Department Type"

    name = fields.Char("Name", required=True)
    code = fields.Char("Code", required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id)
    branch_id = fields.Many2one('kw_res_branch', default=lambda self: self.env.user.branch_id)
    department_id = fields.Many2one('hr.department', domain="[('parent_id', '=', False)]")
    parent_id = fields.Many2one('kw_hr_department_type')
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer("Sequence", default=10, help="Gives the sequence order of department type.")
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', store=True)

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for department in self:
            if department.parent_id:
                department.complete_name = '%s / %s' % (department.parent_id.complete_name, department.name)
            else:
                department.complete_name = department.name

    @api.constrains('name', 'code')
    def check_duplicate(self):
        existing = self.env['kw_hr_department_type'].sudo().search([]) - self
        for record in self:
            for data in existing:
                if record.name.lower() == data.name.lower():
                    raise ValidationError(f"The name {record.name} is already exists.")
                if record.code.lower() == data.code.lower():
                    raise ValidationError(f"The code {record.code} is already exists.")

    @api.model
    def create(self, vals):
        record = super(kw_hr_department_type, self).create(vals)
        if record:
            self.env.user.notify_success(message='Department Hierarchy created successfully.')
        else:
            self.env.user.notify_danger(message='Department Hierarchy creation failed.')
        return record

    @api.multi
    def write(self, vals):
        res = super(kw_hr_department_type, self).write(vals)
        if res:
            self.env.user.notify_success(message='Department Hierarchy updated successfully.')
        else:
            self.env.user.notify_danger(message='Department Hierarchy updation failed.')
        return res
