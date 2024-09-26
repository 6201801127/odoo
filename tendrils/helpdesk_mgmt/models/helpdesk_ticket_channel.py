"""
Module for Helpdesk Ticket Channel Model.

This module contains the model definition for managing channels of helpdesk tickets in Odoo.

"""
from odoo import models, fields


class HelpdeskTicketChannel(models.Model):
    """
    Model for Helpdesk Ticket Channel.

    This class represents the model for managing channels of helpdesk tickets in Odoo.

    Attributes:
        _name (str): The technical name of the model ('helpdesk.ticket.channel').
        _description (str): Description of the model ('Helpdesk Ticket Channel').
        name (str): Field for storing the name of the channel (required).
        active (bool): Field for indicating whether the channel is active or not.

    """
    _name = 'helpdesk.ticket.channel'
    _description = 'Helpdesk Ticket Channel'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env['res.company']._company_default_get('helpdesk.ticket')
    )
