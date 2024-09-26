from odoo import models, fields, api,_

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    interest = fields.Float(string="Interest")
    pf_number = fields.Char(string="PF Number")
    eps_deduct = fields.Boolean('EPS Deduction')

    @api.model
    def create(self, vals):
        res = super(HrEmployee, self).create(vals)
        self.env['pf.employee'].sudo().create({
            'employee_id': res.id,
            'branch_id': res.branch_id.id,
        })
        return res

class PreviousOccupationInherit(models.Model):
    _inherit = 'employee.previous.occupation'

    previous_pf = fields.Char(string="Previous PF Number")