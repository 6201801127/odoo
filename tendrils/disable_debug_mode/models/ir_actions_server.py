"""
Module for Custom Odoo Models and Fields.

This module contains custom models, fields, and APIs for extending Odoo functionality.

"""
from odoo import models, fields, api

class IrActionsServerInherited(models.Model):
    """
    Model for Inheriting 'ir.actions.server'.

    This class inherits from 'ir.actions.server' to extend its functionality.

    Attributes:
        _inherit (str): The name of the model being inherited ('ir.actions.server').
        DEFAULT_PYTHON_CODE (str): Default Python code template for the action.

    """
    _inherit = 'ir.actions.server'

    DEFAULT_PYTHON_CODE = """# Available variables:
#  - env: Odoo Environment on which the action is triggered
#  - model: Odoo Model of the record on which the action is triggered; is a void recordset
#  - record: record on which the action is triggered; may be void
#  - records: recordset of all records on which the action is triggered in multi-mode; may be void
#  - time, datetime, dateutil, timezone: useful Python libraries
#  - log: log(message, level='info'): logging function to record debug information in ir.logging table
#  - Warning: Warning Exception to use with raise
# To return an action, assign: action = {...}\n\n\n\n"""

    code = fields.Text(string='Python Code', groups='base.group_system,disable_debug_mode.group_developer',
                       default=DEFAULT_PYTHON_CODE,
                       help="Write Python code that the action will execute. Some variables are "
                            "available for use; help about python expression is given in the help tab.")
