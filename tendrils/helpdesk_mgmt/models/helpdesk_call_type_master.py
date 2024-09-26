"""
Module for Helpdesk Call Type Master Model.

This module contains the model definition for managing helpdesk call types in Odoo.

"""
from odoo import fields, models


class HelpdeskCalltypeMaster(models.Model):
    """
    Model for Helpdesk Call Type Master.

    This class represents the helpdesk call type master in Odoo.

    Attributes:
        _name (str): The technical name of the model ('helpdesk.calltype.master').
        _description (str): Description of the model ('Helpdesk call type Master').
        _rec_name (str): Field used as the record name (in this case, 'call_name').

    """

    _name = 'helpdesk.calltype.master'
    _description = 'Helpdesk call type Master'
    _rec_name = 'call_name'

    call_name = fields.Char(string='Name')
    