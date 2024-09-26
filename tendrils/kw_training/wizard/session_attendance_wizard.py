from datetime import date, timedelta, datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import calendar


class SessionAttendanceWizard(models.TransientModel):
    _name = 'session_attendance_wizard'
    _description = 'Session Attendance wizard'


    financial_year = fields.Many2one('account.fiscalyear',"Financial Year")
    training_id = fields.Many2one('kw_training', "Training",)


    def show_session_attendance_report(self):
        self.env['kw_session_attendance_report'].with_context(year_data=self.financial_year,training_data= self.training_id.id).init()
        view_id = self.env.ref('kw_training.kw_session_attendance_report_view_pivot').id
        return {
            'name':f'{self.training_id.name}',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'pivot',
            'views': [(view_id, 'pivot')],
            'res_model': 'kw_session_attendance_report',
            'view_id': view_id,
            'context': {'search_default_session_wise_report':1},
            'target': 'current',
        }
    
