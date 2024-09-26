from odoo import models, fields, api, _
from datetime import date, datetime


class FD_BG_Report_Wizard(models.TransientModel):
    _name = "fd_bg_report_wizard"
    _description = "FD & BG Report Wizard"

    date = fields.Date(string="Date", default=date.today())
    type = fields.Selection([('fd','FD'),('bg','BG')],string="Report Type")


    def action_run_report_fd_bg(self):
        ctx = self.env.context.copy()
        ctx.update({'report_date': self.date,'search_default_ageing_group': 1})
        fd_tree_view_id = self.env.ref('kw_accounting.view_fd_reports_tree').id
        if self.type == 'fd':
            self.env['fd_reports'].with_context(report_date=self.date).init()
            return {
            'type': 'ir.actions.act_window',
            'name': _('FD Report on %s') % self.date.strftime("%d-%b-%Y"),
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': fd_tree_view_id,
            'res_model': 'fd_reports',
            'target': 'self',
            'search_view_id': (self.env.ref('kw_accounting.view_fd_reports_search').id,),
            'context':ctx,
        }

        bg_tree_view_id = self.env.ref('kw_accounting.view_bg_reports_tree').id
        if self.type == 'bg':
            self.env['bg_reports'].with_context(report_date=self.date).init()
            return {
            'type': 'ir.actions.act_window',
            'name': _('BG Report on %s') % self.date.strftime("%d-%b-%Y"),
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': bg_tree_view_id,
            'res_model': 'bg_reports',
            'target': 'self',
            'search_view_id': (self.env.ref('kw_accounting.view_bg_reports_search').id,),
            'context':ctx,
        }

