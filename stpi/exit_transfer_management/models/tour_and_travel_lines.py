from odoo import models, fields, api


class PendingTourAndTravelLine(models.Model):
    _name = 'pending.tour.request'
    _description = 'Pending Tours request'

    exit_transfer_id = fields.Many2one("exit.transfer.management", string ="Exit/Transfer Id", readonly=True)
    employee_id = fields.Many2one('hr.employee', string="Requested By")
    tour_request_id = fields.Many2one("tour.request",string="Tour Request Id")
    purpose = fields.Char("Purpose")
    request_date = fields.Date("Requester Date")
    state = fields.Selection(
        [('draft', 'Draft'), ('waiting_for_approval', 'Waiting for Approval'), ('approved', 'Approved'),
         ('rejected', 'Rejected'), ('cancelled', 'Cancelled')
         ], string='Status')

    def tour_approved(self):
        if self.tour_request_id:
            self.tour_request_id.button_approved()
            self.state = self.tour_request_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Tour Request',
                "module_id": str(self.tour_request_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()

    def tour_rejected(self):
        if self.tour_request_id:
            self.tour_request_id.button_reject()
            self.state = self.tour_request_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Tour Request',
                "module_id": str(self.tour_request_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()

class SubmittedTourAndTravelLine(models.Model):
    _name = 'submitted.tour.request'
    _description = 'Pending Tours request'

    exit_transfer_id = fields.Many2one("exit.transfer.management", string ="Exit/Transfer Id", readonly=True)
    tour_request_id = fields.Many2one("tour.request",string="Tour Request Id")
    purpose = fields.Char("Purpose")
    request_date = fields.Date("Requester Date")

    state = fields.Selection([('draft', 'Draft'), ('waiting_for_approval', 'Waiting for Approval'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('cancelled', 'Cancelled')
                               ],string='Status')




    def tour_cancel(self):
        if self.tour_request_id:
            self.tour_request_id.button_cancel()
            self.state = self.tour_request_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Tour Request',
                "module_id": str(self.tour_request_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.exit_transfer_id.employee_id.id)
            })
            self.sudo().unlink()

class upcomingTourAndTravelLine(models.Model):
    _name = 'upcoming.tour.request'
    _description = 'Pending Tours request'

    exit_transfer_id = fields.Many2one("exit.transfer.management", string ="Exit/Transfer Id", readonly=True)
    tour_request_id = fields.Many2one("tour.request",string="Tour Request Id")
    purpose = fields.Char("Purpose")
    request_date = fields.Date("Requester Date")
    state = fields.Selection(
        [('draft', 'Draft'), ('waiting_for_approval', 'Waiting for Approval'), ('approved', 'Approved'),
         ('rejected', 'Rejected'), ('cancelled', 'Cancelled')
         ], string='Status')
#Tour Claim
class PendingTourClaimRequest(models.Model):
    _name = "pending.tour.claim.request"
    _description = "Pending Tour Claim Request"

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Requested By')
    tour_claim_id = fields.Many2one('employee.tour.claim', string='Tour Claim Id')
    total_claimed_amount = fields.Float('Total Claimed Amount')
    balance_left = fields.Float(string="Balance left")
    state = fields.Selection([("draft", "Draft"),
                              ("submitted", "Waiting For Approval"),
                              ("approved", "Approved"),
                              ("rejected", "Rejected"),
                              ], string="Status")
    def tourclaim_approved(self):
        if self.tour_claim_id:
            self.tour_claim_id.button_approved()
            self.state = self.tour_claim_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Tour Claim',
                "module_id": str(self.tour_claim_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()



    def tourclaim_rejected(self):
        if self.tour_claim_id:
            self.tour_claim_id.button_reject()
            self.state = self.tour_claim_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Tour Claim',
                "module_id": str(self.tour_claim_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()


class SubmittedTourClaimRequest(models.Model):
    _name = "submitted.tour.claim.request"
    _description = "Pending Tour Claim Request"

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Requested By')
    tour_claim_id = fields.Many2one('employee.tour.claim', string='Tour Claim Id')
    total_claimed_amount = fields.Float('Total Claimed Amount')
    balance_left = fields.Float(string="Balance left")
    state = fields.Selection([("draft", "Draft"),
                              ("submitted", "Waiting For Approval"),
                              ("approved", "Approved"),
                              ("rejected", "Rejected"),
                              ], string="Status")

    def tourclaim_cancel(self):
        if self.tour_claim_id:
            self.tour_claim_id.button_reject()
            self.state = self.tour_claim_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Tour Claim',
                "module_id": str(self.tour_claim_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()


class UpcomingTourClaimRequest(models.Model):
    _name = "upcoming.tour.claim.request"
    _description = "Pending Tour Claim Request"

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Requested By')
    tour_claim_id = fields.Many2one('employee.tour.claim', string='Tour Claim Id')
    total_claimed_amount = fields.Float('Total Claimed Amount')
    balance_left = fields.Float(string="Balance left")
    state = fields.Selection([("draft", "Draft"),
                              ("submitted", "Waiting For Approval"),
                              ("approved", "Approved"),
                              ("rejected", "Rejected"),
                              ], string="Status")

class ClaimLines(models.Model):
    _name = 'claim.lines1'
    _description = 'claim Lines'
    exit_transfer_id = fields.Many2one("exit.transfer.management", string ="Exit/Transfer Id", readonly=True)
