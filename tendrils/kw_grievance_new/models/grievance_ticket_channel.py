from odoo import models, fields


class GrievanceTicketChannel(models.Model):
    _name = 'grievance.ticket.channel'
    _description = 'Grievance Ticket Channel'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env['res.company']._company_default_get('grievance.ticket')
    )
