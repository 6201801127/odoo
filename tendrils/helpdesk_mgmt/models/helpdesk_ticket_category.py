"""
Module for Helpdesk Ticket Category Model.

This module contains the model definition for managing categories of helpdesk tickets in Odoo.

"""
from odoo import fields, models


class HelpdeskCategory(models.Model):
    """
    Model for Helpdesk Ticket Category.

    This class represents the model for managing categories of helpdesk tickets in Odoo.

    Attributes:
        _name (str): The technical name of the model ('helpdesk.ticket.category').
        _description (str): Description of the model ('Helpdesk Ticket Category').
        active (bool): Field for indicating whether the category is active or not.
        name (str): Field for storing the name of the category (required).

    """
    _name = 'helpdesk.ticket.category'
    _description = 'Helpdesk Ticket Category'

    active = fields.Boolean(string='Active', default=True)
    name = fields.Char(string='Name', required=True)
    category_code = fields.Char('Code',required=True)
    sub_category = fields.Many2one('helpdesk.ticket.subcategory')
    team = fields.Many2one(comodel_name='helpdesk.ticket.team', string="Team")
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env['res.company']._company_default_get('helpdesk.ticket')
    )
