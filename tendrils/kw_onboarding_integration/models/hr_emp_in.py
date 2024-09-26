from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kw_hr_emp_in(models.Model):
    _inherit = 'hr.employee'

    workstation_id = fields.Many2one('kw_workstation_master', string="Workstation")
    infra_id = fields.Many2one('kw_workstation_infrastructure', string="Infrastructure")
    infra_unit_loc_id = fields.Many2one('kw_res_branch_unit', string='Infra Unit Location')

    @api.onchange('job_branch_id')
    def onchange_job_branch(self):
        self.infra_id = False
        domain = {}
        for rec in self:
            domain['infra_id'] = [('address_id', '=', rec.job_branch_id.id)]
            return {'domain': domain}

    @api.onchange('infra_unit_loc_id')
    def onchange_infra_unit_loc_id(self):
        self.infra_id = False
        domain = {}
        for rec in self:
            domain['infra_id'] = [('branch_unit_id', '=', rec.infra_unit_loc_id.id)]
            return {'domain': domain}

    @api.onchange('infra_id')
    def onchange_infra_id(self):
        self.workstation_id = False
        domain = {}
        for rec in self:
            domain['workstation_id'] = [('infrastructure', '=', rec.infra_id.id)]
            return {'domain': domain}

    @api.onchange('location')
    def _onchange_location(self):
        self.infra_id = False
        self.workstation_id = False
        self.client_location = False
