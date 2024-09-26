# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class OdooWorkflowRefuseWizard(models.TransientModel):
    _name = 'odoo.workflow.refuse.wizard'
    _description = 'Workflow Refuse Wizard'

    reason = fields.Text(string='Reason')

    ##@api.multi
    def btn_submit(self):
        # Variables
        cx = self.env.context.copy() or {}
        # Write refuse message
        for wiz in self:
            if wiz.reason and cx.get('active_id', False) and cx.get('active_model', False):
                model_obj = self.env[cx.get('active_model')]
                rec_id = model_obj.browse(cx.get('active_id'))
                if hasattr(rec_id, 'message_post'):
                    rec_id.message_post(_("Reason of refusal is '%s'" % wiz.reason))
