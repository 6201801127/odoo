from odoo import models, fields, api

#LTC and Request

class PendingEmployeeLtcRequest(models.Model):
    _name = 'pending.employee.ltc.request'
    _description = 'Ltc Request and Claim'

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    ltc_sequence_id = fields.Many2one("employee.ltc.advance", string='LTC number',readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Requested By')
    place_of_trvel = fields.Selection(
        [('hometown', 'Hometown'), ('india', 'Anywhere in India'), ('conversion', 'Conversion of Hometown')],
        default='hometown', string='Place of Travel', track_visibility='always')

    block_year_id = fields.Many2one('block.year', string='Block year')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('cancel', 'Cancelled'),
        ('rejected', 'Rejected')
    ], string='Status')

    def ltc_approved(self):
        if self.ltc_sequence_id:
            self.ltc_sequence_id.button_approved()
            self.state = self.ltc_sequence_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Employee Ltc Advance',
                "module_id": str(self.ltc_sequence_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()

    def ltc_rejected(self):
        if self.ltc_sequence_id:
            self.ltc_sequence_id.button_reject()
            self.state = self.ltc_sequence_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Employee Ltc Advance',
                "module_id": str(self.ltc_sequence_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()

class EmployeeLtcRequest(models.Model):
    _name = 'employee.ltc.request'
    _description = 'Ltc Request and Claim'

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    ltc_sequence_id = fields.Many2one("employee.ltc.advance", string='LTC number',readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Requested By')
    place_of_trvel = fields.Selection(
        [('hometown', 'Hometown'), ('india', 'Anywhere in India'), ('conversion', 'Conversion of Hometown')],
        default='hometown', string='Place of Travel', track_visibility='always')

    block_year_id = fields.Many2one('block.year', string='Block year')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected')
    ], string='Status')

    def ltc_cancel(self):
        if self.ltc_sequence_id:
            self.ltc_sequence_id.button_cancel()
            self.state = self.ltc_sequence_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Employee Ltc Advance',
                "module_id": str(self.ltc_sequence_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()



class UpcomingEmployeeLtcRequest(models.Model):
    _name = 'upcoming.employee.ltc.request'
    _description = 'Ltc Request and Claim'

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    ltc_sequence_id = fields.Many2one("employee.ltc.advance", string='LTC number',readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Requested By')
    place_of_trvel = fields.Selection(
        [('hometown', 'Hometown'), ('india', 'Anywhere in India'), ('conversion', 'Conversion of Hometown')],
        default='hometown', string='Place of Travel', track_visibility='always')

    block_year_id = fields.Many2one('block.year', string='Block year')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected')
    ], string='Status')

    def leave_cancel(self):
        if self.ltc_sequence_id:
            self.ltc_sequence_id.button_cancel()
            self.state = self.ltc_sequence_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Employee Ltc Advance',
                "module_id": str(self.ltc_sequence_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()


# LTC Claim

class PendingLTCClaimRequest(models.Model):
    _name = 'pending.ltc.claim.request'
    _description = 'Pending Ltc Claim Request'

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    ltc_availed_for_id = fields.Many2one('employee.ltc.claim','LTC Claim ID',readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Requested By')
    place_of_trvel = fields.Selection(
        [('hometown', 'Hometown'), ('india', 'Anywhere in India'), ('conversion', 'Conversion of Hometown')],
         string='Place of Travel')
    total_claimed_amount = fields.Float('Total Claimed Amount')
    balance_left = fields.Float('Balance Left')
    ltc_availed_for_m2o = fields.Many2one('employee.ltc.advance','LTC availed for')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected')
    ], string='Status')

    def claim_approved(self):
        if self.ltc_availed_for_id:
            self.ltc_availed_for_id.button_approved()
            self.state = self.ltc_availed_for_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Employee Ltc Claim',
                "module_id": str(self.ltc_availed_for_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()

    def claim_rejected(self):
        if self.ltc_availed_for_id:
            self.ltc_availed_for_id.button_reject()
            self.state = self.ltc_availed_for_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Employee Ltc Claim',
                "module_id": str(self.ltc_availed_for_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()

class LTCClaimRequest(models.Model):
    _name = 'ltc.claim.request'
    _description = 'Ltc Claim Request'

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    ltc_availed_for_id = fields.Many2one('employee.ltc.claim','LTC_Claim_ID',readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Requested By')
    place_of_trvel = fields.Selection(
        [('hometown', 'Hometown'), ('india', 'Anywhere in India'), ('conversion', 'Conversion of Hometown')],
         string='Place of Travel')
    total_claimed_amount = fields.Float('Total Claimed Amount')
    balance_left = fields.Float('Balance Left')
    ltc_availed_for_m2o = fields.Many2one('employee.ltc.advance','LTC availed for')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected')
    ], string='Status')

    def claim_cancel(self):
        if self.ltc_availed_for_id:
            self.ltc_availed_for_id.button_reject()
            self.state = self.ltc_availed_for_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Employee Ltc Claim',
                "module_id": str(self.ltc_availed_for_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()



class UpcomingLTCClaimRequest(models.Model):
    _name = 'upcoming.ltc.claim.request'
    _description = 'Upcoming Ltc Claim Request'

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    ltc_availed_for_id = fields.Many2one('employee.ltc.claim','LTC_Claim_ID',readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Requested By')
    place_of_trvel = fields.Selection(
        [('hometown', 'Hometown'), ('india', 'Anywhere in India'), ('conversion', 'Conversion of Hometown')],
         string='Place of Travel')
    total_claimed_amount = fields.Float('Total Claimed Amount')
    ltc_availed_for_m2o = fields.Many2one('employee.ltc.advance','LTC availed for')
    balance_left = fields.Float('Balance Left')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected')
    ], string='Status')