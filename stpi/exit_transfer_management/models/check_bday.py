from odoo import models, fields, api

class PendingCheckBirthday(models.Model):
    _name = "pending.check.birthday"
    _description = "Pending Cheque Birthday"

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    check_id = fields.Many2one("cheque.requests", string="Check Id")
    employee_id = fields.Many2one('hr.employee', string="Employee Id")
    name = fields.Char(string='Employee Name')
    birthday = fields.Date('Date of Birth') #groups="hr.group_hr_user
    state = fields.Selection(
        [('draft', 'Draft'),
         ('to_approve', 'To Approve'),
         ('approved', 'Approved'),
         ('rejected', 'Rejected')
         ], required=True, default='draft')

    def button_approved(self):
        if self.check_id:
            self.check_id.sudo().button_approved()
            self.state = self.check_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Cheque Request',
                "module_id": str(self.check_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })

    def button_reject(self):
        if self.check_id:
            self.check_id.sudo().button_reject()
            self.state = self.check_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Cheque Request',
                "module_id": str(self.check_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()

class SubmittedCheckBirthday(models.Model):
    _name = "submitted.check.birthday"
    _description = "Submitted Cheque Birthday"

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    check_id = fields.Many2one("cheque.requests", string="Check Id")
    employee_id = fields.Many2one('hr.employee', string="Employee Id")
    name = fields.Char(string='Employee Name')
    birthday = fields.Date('Date of Birth') #groups="hr.group_hr_user
    state = fields.Selection(
        [('draft', 'Draft'),
         ('to_approve', 'To Approve'),
         ('approved', 'Approved'),
         ('rejected', 'Rejected')
         ], required=True, default='draft')

    def button_reject(self):
        if self.check_id:
            self.check_id.sudo().button_reject()
            self.state = self.check_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Cheque Request',
                "module_id": str(self.check_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()


class UpcomingCheckBirthday(models.Model):
    _name = "upcoming.check.birthday"
    _description = "Upcoming Cheque Birthday"

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    check_id = fields.Many2one("cheque.requests", string="Check Id")
    employee_id = fields.Many2one('hr.employee', string="Employee Id")
    name = fields.Char(string='Employee Name')
    birthday = fields.Date('Date of Birth') #groups="hr.group_hr_user
    state = fields.Selection(
        [('draft', 'Draft'),
         ('to_approve', 'To Approve'),
         ('approved', 'Approved'),
         ('rejected', 'Rejected')
         ], required=True, default='draft')