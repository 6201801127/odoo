"""
Module for Helpdesk Ticket Subcategory Model.

This module contains the model definition for managing subcategories of helpdesk tickets in Odoo.

"""
from odoo import fields, models, api


class HelpdeskSubcategory(models.Model):
    """
    Model for Helpdesk Ticket Subcategory.

    This class represents the model for managing subcategories of helpdesk tickets in Odoo.

    Attributes:
        _name (str): The technical name of the model ('helpdesk.ticket.subcategory').
        _description (str): Description of the model ('Helpdesk Ticket Sub Category').
        name (str): Field for storing the name of the subcategory (required).
        category_code_id (str): Field for storing the reference to the parent category.

    """
    _name = 'helpdesk.ticket.subcategory'
    _description = 'Helpdesk Ticket Sub Category'

    name = fields.Char(string='Name', required=True)
    category_code_id = fields.Many2one(string="Category",comodel_name='helpdesk.ticket.category',required=True)

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "{} ({})".format(record.name, record.category_code_id.category_code)))
            # print("result......", result)
        return result
