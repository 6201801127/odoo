# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ForecastedReleaseReportWizard(models.TransientModel):
    _name = 'forecasted_release_report_wizard'
    _description = 'Forecasted Release Report Wizard'
    _rec_name = "fiscal_year"

    fiscal_year = fields.Selection(
        [(str(year), str(year)) for year in range(2000, 2030)],
        string='Fiscal Year',
        required=True
    )
    emp_category = fields.Many2one('kwmaster_category_name', string='Employee Category', domain=[('role_ids.code','=', 'DL')])

    def action_open_report(self):
        domain = []
        if self.emp_category:
            domain.append(('emp_category', '=', self.emp_category.id))
        if self.fiscal_year:
            domain.append(('year', '=', self.fiscal_year))

        # return {
        #     'name': 'Forecasted Release Report',
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'forecasted_release_report',
        #     'view_mode': 'pivot,tree',
        #     'view_type': 'form',
        #     'domain': domain,
        #     'context': self.env.context,
        # }

    
        return {
            'name': 'Forecasted Release Report',
            'type': 'ir.actions.client',
            'tag': 'forecasted_release_report_client_tag',
            'context': {'domain': domain},
            'target': 'current',
        }
