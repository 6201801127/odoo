from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class PendingIndentRequest(models.Model):
    _name = "pending.indent.request"
    _description ="Pending Indent Request"

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    number = fields.Char('Indent Number')
    indent_id = fields.Many2one("indent.request", string="Indent Request")
    employee_id = fields.Many2one('hr.employee', string='Employee')
    indent_type = fields.Selection([('issue', 'Issue'), ('grn', 'GRN')
                                    ],string='Type')
    serial_number = fields.Many2one('indent.serialnumber',string='Serial Number')
    state = fields.Selection(
        [('draft', 'Draft'), ('to_approve', 'To Approve'), ('approved', 'Approved'), ('rejected', 'Rejected')
         ], string='Status')

    def button_approved(self):
        if self.indent_id:
            self.indent_id.button_approved()
            self.state = self.indent_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Indent Request',
                "module_id": str(self.indent_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()

    def button_reject(self):
        if self.indent_id:
            self.indent_id.button_reject()
            self.state = self.indent_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Indent Request',
                "module_id": str(self.indent_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()

class SubmittedIndentRequest(models.Model):
    _name = "submitted.indent.request"
    _description =" Submitted Indent Request"

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    number = fields.Char('Indent Number')
    indent_id = fields.Many2one("indent.request", string="Indent Request")
    employee_id = fields.Many2one('hr.employee', string='Employee')
    indent_type = fields.Selection([('issue', 'Issue'), ('grn', 'GRN')
                                    ], track_visibility='always', string='Type')
    state = fields.Selection(
        [('draft', 'Draft'), ('to_approve', 'To Approve'), ('approved', 'Approved'), ('rejected', 'Rejected')
         ], required=True, default='draft', track_visibility='always', string='Status')

    indent_return = fields.Selection([('yes', 'Yes'), ('no', 'No')
                                    ], track_visibility='always', string='Indent Returned?',default='no')
    serial_number = fields.Many2one('indent.serialnumber',string='Serial Number')

    def button_reject(self):
        if self.indent_id:
            self.indent_id.button_reject()
            self.state = self.indent_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Indent Request',
                "module_id": str(self.indent_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()

class UpcomingIndentRequest(models.Model):
    _name = "upcoming.indent.request"
    _description =" Upcoming Indent Request"

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    number = fields.Char('Indent Number')
    indent_id = fields.Many2one("indent.request", string="Indent Request")
    employee_id = fields.Many2one('hr.employee', string='Employee')
    indent_type = fields.Selection([('issue', 'Issue'), ('grn', 'GRN')
                                    ], track_visibility='always', string='Type')
    state = fields.Selection(
        [('draft', 'Draft'), ('to_approve', 'To Approve'), ('approved', 'Approved'), ('rejected', 'Rejected')
         ], required=True, default='draft', track_visibility='always', string='Status')

#GRN
class PendingGRN(models.Model):
    _name = "pending.grn"
    _description = "Pending GRN "

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    number = fields.Char('Number')
    indent_id = fields.Many2one("indent.request", string="Indent Request")
    employee_id = fields.Many2one('hr.employee', string='Employee')
    indent_type = fields.Selection([('issue', 'Issue'), ('grn', 'GRN')
                                    ], track_visibility='always', string='Type')
    state = fields.Selection(
        [('draft', 'Draft'), ('to_approve', 'To Approve'), ('approved', 'Approved'), ('rejected', 'Rejected')
         ], required=True, default='draft', track_visibility='always', string='Status')

    def button_approved(self):
        if self.indent_id:
            self.indent_id.button_approved()
            self.state = self.indent_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Indent Request',
                "module_id": str(self.indent_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()

    def button_reject(self):
        if self.indent_id:
            self.indent_id.button_reject()
            self.state = self.indent_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Indent Request',
                "module_id": str(self.indent_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()

class SubmittedGRN(models.Model):
    _name = "submitted.grn"
    _description = "Submitted GRN "

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    number = fields.Char('Number')
    indent_id = fields.Many2one("indent.request", string="Indent Request")
    employee_id = fields.Many2one('hr.employee', string='Employee')
    indent_type = fields.Selection([('issue', 'Issue'), ('grn', 'GRN')
                                    ], track_visibility='always', string='Type')
    state = fields.Selection(
        [('draft', 'Draft'), ('to_approve', 'To Approve'), ('approved', 'Approved'), ('rejected', 'Rejected')
         ], required=True, default='draft', track_visibility='always', string='Status')

    def button_reject(self):
        if self.indent_id:
            self.indent_id.button_reject()
            self.state = self.indent_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Indent Request',
                "module_id": str(self.indent_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()

class UpcomingGRN(models.Model):
    _name = "upcoming.grn"
    _description = "Upcoming GRN "

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    number = fields.Char('Number')
    indent_id = fields.Many2one("indent.request", string="Indent Request")
    employee_id = fields.Many2one('hr.employee', string='Employee')
    indent_type = fields.Selection([('issue', 'Issue'), ('grn', 'GRN')
                                    ], track_visibility='always', string='Type')
    state = fields.Selection(
        [('draft', 'Draft'), ('to_approve', 'To Approve'), ('approved', 'Approved'), ('rejected', 'Rejected')
         ], required=True, default='draft', track_visibility='always', string='Status')

#Issuse Request
class PendingIssueRequest(models.Model):
    _name = "pending.issue.request"
    _description ="Pending Issues Request"

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    issue_id = fields.Many2one("issue.request", string="Issue Request")
    indent_grn = fields.Many2one('indent.request', string='Indent/GRN')
    item_category_id = fields.Many2one('indent.stock', string='Item Category')
    item_id = fields.Many2one('child.indent.stock', string='Item')
    requested_quantity = fields.Integer('Requested Quantity')
    approved_quantity = fields.Integer('Approved Quantity')
    serial_number = fields.Many2one('indent.serialnumber',string='Serial Number')
    state = fields.Selection(
        [('draft', 'Draft'), ('to_approve_proceed', 'To Approve 1'), ('to_approve', 'To Approve'),
         ('approved', 'Approved'), ('rejected', 'Rejected')
         ], string='Status')

    def button_approved(self):
        if self.issue_id:
            if self.issue_id.serial_bool and not self.serial_number:
                raise ValidationError(_("Serial Number is Required!."))
            if self.approved_quantity == 0:
                raise ValidationError(_("Approved Quantity must be greater than zero!."))
            self.issue_id.issue_state = 'approved'
            self.issue_id.approved_quantity = self.approved_quantity
            self.issue_id.serial_number = self.serial_number.id
            self.state = self.issue_id.issue_state
            to_approve = self.indent_grn.issue_id.filtered( lambda r: not r.issue_state)
            if not to_approve:
                self.indent_grn.button_grant()
            
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Issue Request',
                "module_id": str(self.issue_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()

    def button_reject(self):
        if self.issue_id:
            self.indent_grn.button_reject()
            self.state = self.issue_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Issue Request',
                "module_id": str(self.issue_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()

class SubmittedIssueRequest(models.Model):
    _name = "submitted.issue.request"
    _description ="Submitted Issues Request"

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    issue_id = fields.Many2one("issue.request", string="Issue Request")
    indent_grn = fields.Many2one('indent.request', string='Indent/GRN')
    item_category_id = fields.Many2one('indent.stock', string='Item Category')
    item_id = fields.Many2one('child.indent.stock', string='Item')
    requested_quantity = fields.Integer('Requested Quantity')
    approved_quantity = fields.Integer('Approved Quantity')
    serial_number = fields.Many2one('indent.serialnumber',string='Serial Number')
    state = fields.Selection(
        [('draft', 'Draft'), ('to_approve_proceed', 'To Approve 1'), ('to_approve', 'To Approve'),
         ('approved', 'Approved'), ('rejected', 'Rejected')
         ], string='Status')

    def button_reject(self):
        if self.issue_id:
            self.issue_id.button_reject()
            self.state = self.issue_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Issue Request',
                "module_id": str(self.issue_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()

class UpcomingIssueRequest(models.Model):
    _name = "upcoming.issue.request"
    _description ="Upcoming Issues Request"

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    issue_id = fields.Many2one("issue.request", string="Issue Request")
    indent_grn = fields.Many2one('indent.request', string='Indent/GRN')
    item_category_id = fields.Many2one('indent.stock', string='Item Category')
    item_id = fields.Many2one('child.indent.stock', string='Item')
    requested_quantity = fields.Integer('Requested Quantity')
    approved_quantity = fields.Integer('Approved Quantity')
    state = fields.Selection(
        [('draft', 'Draft'), ('to_approve_proceed', 'To Approve 1'), ('to_approve', 'To Approve'),
         ('approved', 'Approved'), ('rejected', 'Rejected')
         ], string='Status')







# GRN Request
class PendingGRNRequest(models.Model):
    _name = "pending.grn.request"
    _description ="GRN Request"

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    issue_id = fields.Many2one("issue.request", string="Issue Request")
    indent_grn = fields.Many2one('indent.request', string='Indent/GRN')
    item_category_id = fields.Many2one('indent.stock', string='Item Category')
    item_id = fields.Many2one('child.indent.stock', string='Item')
    requested_quantity = fields.Integer('Requested Quantity')
    approved_quantity = fields.Integer('Approved Quantity')
    serial_number = fields.Many2one('indent.serialnumber',string='Serial Number')

    state = fields.Selection(
        [('draft', 'Draft'), ('to_approve_proceed', 'To Approve 1'), ('to_approve', 'To Approve'),
         ('approved', 'Approved'), ('rejected', 'Rejected')
         ], string='Status')

    def button_approved(self):
        if self.issue_id:
            approved = self.issue_id.button_approved()
            if approved and self.issue_id.serial_bool:
                self.issue_id.serial_number = self.serial_number.id
            self.state = self.issue_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Issue Request',
                "module_id": str(self.issue_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()

    def button_reject(self):
        if self.issue_id:
            self.issue_id.button_reject()
            self.state = self.issue_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Issue Request',
                "module_id": str(self.issue_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()

class SubmittedGRNRequest(models.Model):
    _name = "submitted.grn.request"
    _description ="Submitted GRN Request"

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    issue_id = fields.Many2one("issue.request", string="Issue Request")
    indent_grn = fields.Many2one('indent.request', string='Indent/GRN')
    item_category_id = fields.Many2one('indent.stock', string='Item Category')
    item_id = fields.Many2one('child.indent.stock', string='Item')
    requested_quantity = fields.Integer('Requested Quantity')
    approved_quantity = fields.Integer('Approved Quantity')
    serial_number = fields.Many2one('indent.serialnumber',string='Serial Number')
    state = fields.Selection(
        [('draft', 'Draft'), ('to_approve_proceed', 'To Approve 1'), ('to_approve', 'To Approve'),
         ('approved', 'Approved'), ('rejected', 'Rejected')
         ], string='Status')

    def button_reject(self):
        if self.issue_id:
            self.issue_id.button_reject()
            self.state = self.issue_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Issue Request',
                "module_id": str(self.issue_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()

class UpcomingGRNRequest(models.Model):
    _name = "upcoming.grn.request"
    _description ="Upcoming GRN Request"

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    issue_id = fields.Many2one("issue.request", string="Issue Request")
    indent_grn = fields.Many2one('indent.request', string='Indent/GRN')
    item_category_id = fields.Many2one('indent.stock', string='Item Category')
    item_id = fields.Many2one('child.indent.stock', string='Item')
    requested_quantity = fields.Integer('Requested Quantity')
    approved_quantity = fields.Integer('Approved Quantity')

    state = fields.Selection(
        [('draft', 'Draft'), ('to_approve_proceed', 'To Approve 1'), ('to_approve', 'To Approve'),
         ('approved', 'Approved'), ('rejected', 'Rejected')
         ], string='Status')