from odoo import _, api, fields, models

class HREmployee(models.Model):
    _inherit = 'hr.employee'

    def _employee_domain(self):
        return [('id','in',self.env.user.branch_ids.ids)]

    branch_id = fields.Many2one('res.branch', 'Center', 
                                default=lambda self: self.env['res.users']._get_default_branch(),domain=_employee_domain)