# -*- coding: utf-8 -*-

from odoo import api, SUPERUSER_ID

from . import models
from . import wizard


def uninstall_hook(cr, registry):
    """
    Unfortunately, the grid view is defined in enterprise, and the
    timesheet actions (community) are inherited in enterprise to
    add the grid view in the view_modes.
    As they override view_mode directly instead of creating
    ir.actions.act_window.view that would be unlinked properly
    when uninstalling timesheet_grid, here we clean the view_mode
    manually.

    YTI TODO: But in master, define ir.actions.act_window.view instead,
    so that they are removed with the module installation.
    """

    env = api.Environment(cr, SUPERUSER_ID, {})

    actions = env['ir.actions.act_window'].search([
        ('res_model', '=', 'account.analytic.line')
    ]).filtered(
        lambda action: action.xml_id.startswith('hr_timesheet.') and 'grid' in action.view_mode)
    for action in actions:
        action.view_mode = ','.join(view_mode for view_mode in action.view_mode.split(',') if view_mode != 'grid')
