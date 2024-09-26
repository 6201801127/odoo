# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError


class PfGet(models.TransientModel):
    """
    This wizard will confirm the all the selected draft invoices
    """

    _name = "pf.withdrawal.get"
    _description = "PF"




    @api.multi
    def get_pf_wizs_action_button(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for employee in self.env['pf.employee'].browse(active_ids):
            employee.sudo().get_pf_details()
