# -*- coding: utf-8 -*-
from odoo import models, api


class OdooWorkflowUpdateWizard(models.TransientModel):
    _name = 'odoo.workflow.update.wizard'
    _description = 'Workflow Update Wizard'

    @api.multi
    def btn_update(self):
        from odoo.addons import kw_dynamic_workflow
        return kw_dynamic_workflow.update_workflow_reload(self)
