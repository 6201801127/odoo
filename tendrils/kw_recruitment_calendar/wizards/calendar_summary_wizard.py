import calendar
from odoo import fields, models,_
import datetime
from datetime import date

class CalendarSummaryReport(models.TransientModel):
    _name = 'kw_calendar_summary_report_wizard'
    _description = 'Calendar Summery Report'

    date_from = fields.Date('Date From', help="Choose a Starting date to get the salary advance at that date", required=True)
    date_to = fields.Date('Date To', help="Choose a Ending date to get the salary advance at that date", required=True)

    def search_calendar_summery(self):
        self.ensure_one()
        dt1 = self.date_from
        dt2 = self.date_to
        record_data = self.env['kw_calendar_summary'].sudo().search([])
        if record_data:
            for data in record_data:
                tree_view_id = self.env.ref('kw_recruitment_calendar.kw_calendar_summary_tree').id
                return {
                        'type': 'ir.actions.act_window',
                        'views': [(tree_view_id, 'tree')],
                        'view_mode': 'tree,form',
                        'name': ('Calendar Summary Report'),
                        'res_model': 'kw_calendar_summary',
                        'domain':[('create_date', '>=', dt1),('create_date', '<=', dt2)],
                        'target':'main',
                    }