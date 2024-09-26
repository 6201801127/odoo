from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kwemp_onboarding_checklist_in(models.Model):
    _inherit = 'kw_employee_onboarding_checklist'

    infra_id = fields.Many2one('kw_workstation_infrastructure', string="Infrastructure")
    workstation_id = fields.Many2one('kw_workstation_master', string="Workstation Link")
    client_location = fields.Char('Client Location')
    wfa_city = fields.Many2one('res.city', string="City")

    @api.onchange('location')
    def _onchange_location(self):
        self.infra_id = False
        self.workstation_id = False
        self.client_location = False
