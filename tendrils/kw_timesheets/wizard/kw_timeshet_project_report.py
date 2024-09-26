from odoo import models, fields, api
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


class TimesheetProjectReport(models.TransientModel):
    _name = 'timesheet_project_report_wizard'
    _description = "Timesheet Fill Report Wizard"

    @api.model
    def get_year(self):
        current_year = date.today().year
        list_years = []
        for year in range(current_year, current_year - 5, -1):
            list_years.append((str(year),year))
        return list_years
        
    @api.model
    def start_date_(self):
        today = date.today()
        start_date = today - timedelta(days=today.weekday())
        return start_date
        
    @api.model
    def end_date_(self):
        today = date.today()
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
        return end_date

    select_type = fields.Selection([('month', 'Month'), ('week', 'Week'), ('date', 'Date')], string="Select Type", default="week")
    year = fields.Selection(get_year, string="Year")
    month = fields.Selection([('01', 'January'), ('02', 'February'),
                              ('03', 'March'), ('04', 'April'),
                              ('05', 'May'), ('06', 'June'),
                              ('07', 'July'), ('08', 'August'),
                              ('09', 'September'), ('10', 'October'),
                              ('11', 'November'), ('12', 'December')], string="Month")
    date = fields.Date(string="Date")
    from_date = fields.Date(string='From Date', default=start_date_)
    to_date = fields.Date(string='To Date', default=end_date_)

    @api.onchange('select_type')
    def false_value(self):
        self.month = False
        self.year = False
        self.date = False
        
    @api.multi
    def view_report(self):
        if self.select_type == 'date':
            from_date = self.date
            to_date = self.date

        elif self.select_type == 'month':
            str_year = self.year
            str_month = self.month
            converted_start_date = date(month=int(str_month), year=int(str_year), day=1)
            to_date = converted_start_date + relativedelta(months=1) - relativedelta(days=1)
            from_date = converted_start_date
            # to_date = to_date
        elif self.select_type == 'week':
            from_date = self.from_date
            to_date = self.to_date
        self.env['kw_timesheet_project_report_view'].with_context(from_date=from_date,to_date=to_date).init()
        tree_view_id = self.env.ref('kw_timesheets.view_kw_timesheet_project_report_tree').id
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Timesheet Fill Report',
            'views': [(tree_view_id, 'tree')],
            'view_mode': 'tree',
            'view_type': 'form',
            'res_model': 'kw_timesheet_project_report_view',
            'target': 'main',
        }
        return action

