# -*- coding: utf-8 -*-


from odoo import models, fields


class IrActionsServer(models.Model):
    _inherit = 'ir.actions.server'

    is_workflow = fields.Boolean(string='Is Workflow Server Action')
