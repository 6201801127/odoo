from odoo import models, fields, api

#Income Tax
class PendingIncomeTaxRequest(models.Model):
    _name = 'pending.income.tax.request'
    _description = 'Income Tax Request'

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Requested By')
    running_fy_id = fields.Many2one("hr.declaration", string="IT Declaration")
    date_range_id = fields.Many2one("date.range", string="Financial Year")
    total_gross =fields.Float(string='Yearly Gross')
    taxable_income =fields.Float(string='Taxable Income')
    tax_payable = fields.Float('Tax Payable')
    tax_paid = fields.Float(string='Tax Paid')
    total_rem = fields.Float(string='Pending Tax')
    state = fields.Selection(
        [('draft', 'Draft'), ('to_approve', 'To Approve'), ('approved', 'Approved'), ('rejected', 'Rejected'),
         ('verified', 'Verified')
         ],string='Status')

    def tax_approved(self):
        if self.running_fy_id:
            self.running_fy_id.button_approved()
            self.state = self.running_fy_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'HR Declaration',
                "module_id": str(self.running_fy_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()

    def tax_rejected(self):
        if self.running_fy_id:
            self.running_fy_id.button_reject()
            self.state = self.running_fy_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'HR Declaration',
                "module_id": str(self.running_fy_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()

class SubmittedIncomeTaxRequest(models.Model):
    _name = 'submitted.income.tax.request'
    _description = 'Income Tax Request'

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Requested By')
    running_fy_id = fields.Many2one("hr.declaration", string="IT Declaration")
    date_range_id = fields.Many2one("date.range", string="Financial Year")
    total_gross =fields.Float(string='Yearly Gross')
    taxable_income =fields.Float(string='Taxable Income')
    tax_payable = fields.Float('Tax Payable')
    tax_paid = fields.Float(string='Tax Paid')
    total_rem = fields.Float(string='Pending Tax')
    state = fields.Selection(
        [('draft', 'Draft'), ('to_approve', 'To Approve'), ('approved', 'Approved'), ('rejected', 'Rejected'),
         ('verified', 'Verified')
         ], required=True, default='draft', string='Status', track_visibility='always')

    def tax_rejected(self):
        if self.running_fy_id:
            self.running_fy_id.button_reject()
            self.state = self.running_fy_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'HR Declaration',
                "module_id": str(self.running_fy_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()

class UpcomingIncomeTaxRequest(models.Model):
    _name = 'upcoming.income.tax.request'
    _description = 'Income Tax Request'

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Requested By')
    running_fy_id = fields.Many2one("hr.declaration", string="IT Declaration")
    date_range_id = fields.Many2one("date.range", string="Financial Year")
    total_gross =fields.Float(string='Yearly Gross')
    taxable_income =fields.Float(string='Taxable Income')
    tax_payable = fields.Float('Tax Payable')
    tax_paid = fields.Float(string='Tax Paid')
    total_rem = fields.Float(string='Pending Tax')
    state = fields.Selection(
        [('draft', 'Draft'), ('to_approve', 'To Approve'), ('approved', 'Approved'), ('rejected', 'Rejected'),
         ('verified', 'Verified')
         ], required=True, default='draft', string='Status', track_visibility='always')