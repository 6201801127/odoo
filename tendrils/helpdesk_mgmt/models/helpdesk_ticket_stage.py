"""
Module for Helpdesk Ticket Stage Model.

This module contains the model definition for managing stages of helpdesk tickets in Odoo.

"""
from odoo import fields, models


class HelpdeskTicketStage(models.Model):
    """
    Model for Helpdesk Ticket Stage.

    This class represents the model for managing stages of helpdesk tickets in Odoo.

    Attributes:
        _name (str): The technical name of the model ('helpdesk.ticket.stage').
        _description (str): Description of the model ('Helpdesk Ticket Stage').
        _order (str): Default order for records (by 'sequence' and 'id').
        name (str): Field for storing the name of the stage (required, translatable).

    """
    _name = 'helpdesk.ticket.stage'
    _description = 'Helpdesk Ticket Stage'
    _order = 'sequence, id'

    name = fields.Char(string='Stage Name', required=True, translate=True)
    description = fields.Html(translate=True, sanitize_style=True)
    sequence = fields.Integer(default=1)
    active = fields.Boolean(default=True)
    code = fields.Char('Code')
    unattended = fields.Boolean(string='Unattended')
    closed = fields.Boolean(string='Closed')
    portal_user_can_close = fields.Boolean()
    mail_template_id = fields.Many2one(
        'mail.template',
        string='Email Template',
        domain=[('model', '=', 'helpdesk.ticket')],
        help="If set an email will be sent to the "
             "customer when the ticket"
             "reaches this step.")
    fold = fields.Boolean(
        string='Folded in Kanban',
        help="This stage is folded in the kanban view.")
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env['res.company']._company_default_get('helpdesk.ticket')
    )
