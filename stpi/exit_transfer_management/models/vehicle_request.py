from odoo import models, fields, api

# Vehicle Request
class PendingVehicleRequest(models.Model):
    _name = "pending.vehicle.request"
    _description = "Pending Vehicle Request"

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Requested By')
    vehicle_id =fields.Many2one('employee.fleet', string='Vehicle Request_Id')
    from_location = fields.Char(string="From Location")
    to_location = fields.Char(string="To Location")
    state = fields.Selection([('draft', 'Draft'), ('waiting', 'Waiting for Approval'), ('cancel', 'Cancel'),
                              ('confirm', 'Approved'), ('reject', 'Rejected'), ('return', 'Returned')],
                             string="State", default="draft")
    def vehicle_approved(self):
        if self.vehicle_id:
            self.vehicle_id.sudo().approve()#button_approved
            self.state = self.vehicle_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Vehicle Request',
                "module_id": str(self.vehicle_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()

    def vehicle_rejected(self):
        if self.vehicle_id:
            self.vehicle_id.sudo().reject()#button_reject
            self.state = self.vehicle_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Vehicle Request',
                "module_id": str(self.vehicle_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()

class SubmittedVehicleRequest(models.Model):
    _name = "submitted.vehicle.request"
    _description = "Submitted Vehicle Request"

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Requested By')
    vehicle_id = fields.Many2one('employee.fleet', string='Vehicle Request_Id')
    from_location = fields.Char(string="From Location")
    to_location = fields.Char(string="To Location")
    state = fields.Selection([('draft', 'Draft'), ('waiting', 'Waiting for Approval'), ('cancel', 'Cancel'),
                              ('confirm', 'Approved'), ('reject', 'Rejected'), ('return', 'Returned')],
                             string="State", default="draft")

    def vehicle_cancel(self):
        if self.vehicle_id:
            self.vehicle_id.sudo().cancel() #
            self.state = self.vehicle_id.state
            me = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['exit.management.report'].sudo().create({
                "exit_transfer_id": self.exit_transfer_id.id,
                "employee_id": self.exit_transfer_id.employee_id.id,
                "exit_type": self.exit_transfer_id.exit_type,
                "module": 'Vehicle Request',
                "module_id": str(self.vehicle_id.id),
                "action_taken_by": (me.id),
                "action_taken_on": (self.employee_id.id)
            })
            self.sudo().unlink()


class UpcomingVehicleRequest(models.Model):
    _name = "upcoming.vehicle.request"
    _description = "Upcoming Vehicle Request"

    exit_transfer_id = fields.Many2one("exit.transfer.management", string="Exit/Transfer Id", readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Requested By')
    vehicle_id = fields.Many2one('employee.fleet', string='Vehicle Request_Id')
    from_location = fields.Char(string="From Location")
    to_location = fields.Char(string="To Location")
    state = fields.Selection([('draft', 'Draft'), ('waiting', 'Waiting for Approval'), ('cancel', 'Cancel'),
                              ('confirm', 'Approved'), ('reject', 'Rejected'), ('return', 'Returned')],
                             string="State", default="draft")
