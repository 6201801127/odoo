"""
Module for Custom User Models and Fields.

This module contains custom user models and fields for extending the functionality of user management in Odoo.

"""
from odoo import api, fields, models

class ResUsers(models.Model):
    """
    Model for Inheriting 'res.users'.

    This class inherits from 'res.users' to extend its functionality.

    Attributes:
        _inherit (str): The name of the model being inherited ('res.users').

    """
    _inherit = 'res.users'

    #Developer: Surya Prasad Tripathy
    """
        Override _is_admin() to access by both groups ('base.group_erp_manager','disable_debug_mode.group_developer')
    """
    @api.multi
    def _is_admin(self):
        self.ensure_one()
        return self._is_superuser() or self.has_group('base.group_erp_manager') or self.has_group('disable_debug_mode.group_developer')
