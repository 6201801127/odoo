# -*- coding: utf-8 -*-
# © 2011 Raphaël Valyi, Renato Lima, Guewen Baconnier, Sodexis
# © 2017 Mourad EL HADJ MIMOUNE, Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class TourClaimConfirm(models.TransientModel):
    _name = 'employee.tour.claim.confirm'
    _inherit = ['exception.rule.confirm']

    related_model_id = fields.Many2one('employee.tour.claim', 'Tour Claim')

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        if self.ignore:
            self.related_model_id.ignore_exception = True
        return super(TourClaimConfirm, self).action_confirm()
