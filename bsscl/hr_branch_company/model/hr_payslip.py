from odoo import _, api, fields, models

class HRPayslip(models.Model):
    _inherit = 'hr.payslip'

    branch_id = fields.Many2one('res.branch', 'Center')
    
    @api.constrains('employee_id')
    @api.onchange('employee_id')
    def get_onchnage_branch(self):
        for s in self:
            s.branch_id = s.employee_id.branch_id
#             print("//////////@api.constrains('slip_ids.employee_id')////////////////////")
    

class HRPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'   
    
    
    branch_id = fields.Many2one('res.branch', 'Center', domain=lambda self: [('id', 'in', self.env.user.branch_ids.mapped('id'))])
    
