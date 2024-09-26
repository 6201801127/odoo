from odoo import api, fields, models
from datetime import datetime, timedelta


class LostAndFoundReports(models.TransientModel):
    _name = 'lost_found_reports'
    _description = 'Lost and Found reports'


    from_date = fields.Date(string="From Date", required=False, autocomplete="off")
    to_date = fields.Date(string="To Date", required=False, autocomplete="off")

    def get_lost_found_report(self):
        tree_view_id = self.env.ref('kw_lost_and_found.kw_reports_lost_and_found_list').id
        form_view_id = self.env.ref('kw_lost_and_found.kw_reports_reports_item_view_form').id
        domain = []
        if self.from_date and self.to_date:
            domain = [('date_time','>=',self.from_date),('date_time','<=',self.to_date)]
        elif not self.from_date and not self.to_date:
            domain = []
        elif self.from_date and not self.to_date:
            domain = [('date_time','>=',self.from_date)]
        elif not self.from_date and self.to_date:
            domain = [('date_time','<=',self.to_date)]
        action = {
            'name': "Lost & Found Reports",
            'type': 'ir.actions.act_window',
            'res_model': 'kw_lost_and_found',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(tree_view_id, 'tree'),(form_view_id, 'form')],
            'target': 'main',
            'domain': domain,
            'view_id': tree_view_id
        }
        return action