"""
Module for Helpdesk Ticket Tag Model.

This module contains the model definition for managing tags of helpdesk tickets in Odoo.

"""
from odoo import fields, models


class HelpdeskTicketTag(models.Model):
    """
    Model for Helpdesk Ticket Tag.

    This class represents the model for managing tags of helpdesk tickets in Odoo.

    Attributes:
        _name (str): The technical name of the model ('helpdesk.ticket.tag').
        _description (str): Description of the model ('Helpdesk Ticket Tag').
        name (str): Field for storing the name of the tag.
        color (int): Field for storing the color index of the tag.

    """
    _name = 'helpdesk.ticket.tag'
    _description = 'Helpdesk Ticket Tag'

    name = fields.Char(string='Name')
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env['res.company']._company_default_get('helpdesk.ticket')
    )
