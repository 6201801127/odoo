from odoo import fields, models


class GrievanceTicketTag(models.Model):
    _name = 'grievance.ticket.tag'
    _description = 'Grievance Ticket Tag'

    name = fields.Char(string='Name')
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env['res.company']._company_default_get('grievance.ticket')
    )
