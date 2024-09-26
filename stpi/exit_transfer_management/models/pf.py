from odoo import models, fields, api
# PF Request
class PendingPFRequest(models.Model):
    _name = "pending.pf.request"
    _description = "Pending PF Request"

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    pf_id = fields.Many2one('pf.widthdrawl', string='PF Request_Id')
    employee_id = fields.Many2one('hr.employee', string='Requested By')
    advance_amount = fields.Float(string="Advance Amount")
    purpose = fields.Text(string="Purpose")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected')
    ], string='Status')

    def pf_approved(self):
        if self.pf_id:
            self.pf_id.button_approved()
            self.state = self.pf_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'PF Withdrawl',
                "module_id": str(self.pf_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()

    def pf_rejected(self):
        if self.pf_id:
            self.pf_id.button_reject()
            self.state = self.pf_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'PF Withdrawl',
                "module_id": str(self.pf_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()

class SubmittedPFRequest(models.Model):
    _name = "submitted.pf.request"
    _description = "Submitted PF Request"

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    pf_id = fields.Many2one('pf.widthdrawl', string='PF Request_Id')
    employee_id = fields.Many2one('hr.employee', string='Requested By')
    advance_amount = fields.Float(string="Advance Amount")
    purpose = fields.Text(string="Purpose")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected')
    ], string='Status')

    def pf_cancel(self):
        if self.pf_id:
            self.pf_id.button_reject()
            self.state = self.pf_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'PF Withdrawl',
                "module_id": str(self.pf_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()


class UpcomingPFRequest(models.Model):
    _name = "upcoming.pf.request"
    _description = "Upcoming PF Request"

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    pf_id = fields.Many2one('pf.widthdrawl', string='PF Request_Id')
    employee_id = fields.Many2one('hr.employee', string='Requested By')
    advance_amount = fields.Float(string="Advance Amount")
    purpose = fields.Text(string="Purpose")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected')
    ], string='Status')

