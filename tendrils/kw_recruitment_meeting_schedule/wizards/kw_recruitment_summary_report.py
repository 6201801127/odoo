import calendar
from odoo import api, fields, models, _
import datetime
from datetime import date
# from dateutil.relativedelta import relativedelta
from dateutil import relativedelta


class kw_recruitment_summary_report(models.TransientModel):
    _name = 'kw_recruitment_summary_report_wizard'
    _description = 'Recruitment summary report'

    date_from = fields.Date('Date From', help="Choose a Starting date to get the applied at that date")
    date_to = fields.Date('Date To', help="Choose a Ending date to get the applied at that date")

    def search_recruitment_summery(self):
        self.ensure_one()
        dt1 = self.date_from
        dt2 = self.date_to
        meeting_ids = []
        applicant_list = []
        record_data = self.env['kw_meeting_events'].sudo().search([('meetingtype_code', '=', 'interview')])
        for record in record_data:
            if dt1 <= record.kw_start_meeting_date <= dt2:
                meeting_ids.append(record)
        for rec in meeting_ids:
            if rec.response_ids:
                for line in rec.response_ids:
                    applicant_list.append(line.id)
        if record_data and applicant_list:
            tree_view_id = self.env.ref(
                'kw_recruitment_meeting_schedule.kw_recruitment_candidate_interview_report_tree').id
            return {
                'type': 'ir.actions.act_window',
                'views': [(tree_view_id, 'tree')],
                'view_mode': 'tree,form',
                'name': _('Candidate Interview Report'),
                'res_model': 'survey.user_input',
                'domain': [('id', 'in', applicant_list)],
                'target': 'main'
            }


class kw_recruitment_interview_summary_report(models.TransientModel):
    _name = 'kw_recruitment_interview_summary_report'
    _description = 'Kw recruitment interview summery report'

    date_from = fields.Date('Date From', help="Choose a Starting date to get the salary advance at that date")
    date_to = fields.Date('Date To', help="Choose a Ending date to get the salary advance at that date")
    search_by = fields.Selection([
        ('dt', 'By Date'),
        ('applicant', 'By Resource'),
    ], string="Search By", default='dt')
    applicant_id = fields.Many2one('hr.applicant', string="Applicant", domain="['|', ('active','=',True), ('active','=',False)]")

    def search_interview_summery(self):
        self.ensure_one()
        dt1 = self.date_from
        dt2 = self.date_to
        record_list = []
        record_data = self.env['kw_interview_summary_report'].sudo().search([])
        if self.search_by == 'dt':
            for record in record_data:
                if dt1 <= record.interview_date <= dt2:
                    record_list.append(record.id)
            if record_data and record_list:
                tree_view_id = self.env.ref('kw_recruitment_meeting_schedule.kw_interview_summary_report_tree').id
                return {
                    'type': 'ir.actions.act_window',
                    'views': [(tree_view_id, 'tree')],
                    'view_mode': 'tree,form',
                    'name': _('Interview Summary Report'),
                    'res_model': 'kw_interview_summary_report',
                    'domain': [('id', 'in', record_list)],
                    'target': 'main'
                }
        if self.search_by == 'applicant':
            applicant_list = []
            for record in record_data:
                if record.applicant_id == self.applicant_id:
                    applicant_list.append(record.id)
            if record_data and applicant_list:
                tree_view_id = self.env.ref('kw_recruitment_meeting_schedule.kw_interview_summary_report_tree').id
                return {
                    'type': 'ir.actions.act_window',
                    'views': [(tree_view_id, 'tree')],
                    'view_mode': 'tree,form',
                    'name': _('Interview Summary Report'),
                    'res_model': 'kw_interview_summary_report',
                    'domain': [('id', 'in', applicant_list)],
                    'target': 'main'
                }


class kw_recruitment_interview_summary_report_new(models.TransientModel):
    _name = 'kw_recruitment_interview_summary_report_new'
    _description = 'Kw recruitment interview summery report'

    date_from = fields.Date('Date From', help="Choose a Starting date to get the applied at that date")
    date_to = fields.Date('Date To', help="Choose a Ending date to get the applied at that date")
    search_by = fields.Selection([
        ('dt', 'By Date'),
        ('job', 'Job Position'),
        ('applicant', 'By Applicant'),
    ], string="Search By", default='dt')
    applicant_id = fields.Many2many('hr.applicant', string="Applicant", domain="['|', ('active','=',True), ('active','=',False)]")
    job_id = fields.Many2many('kw_hr_job_positions', 'summary_report_job_position_rel', 'job_id', 'report_id',
                              string="Job Position")

    def view_report(self):
        self.ensure_one()
        dt1 = self.date_from
        dt2 = self.date_to
        applicant_object = self.env['hr.applicant'].sudo()
        tree_view_id = self.env.ref('kw_recruitment_meeting_schedule.applicant_summary_report_list_view').id
        id_list = []

        if self.search_by == 'dt':
            record_data = applicant_object.search([])
            for record in record_data:
                if dt1 <= record.create_date.date() <= dt2:
                    id_list.append(record.id)

        if self.search_by == 'applicant':
            id_list = [rec for rec in self.applicant_id.ids]
        if self.search_by == 'job':
            records = applicant_object.search([('job_position', '=', self.job_id.id)])
            id_list = [rec.id for rec in records]

        return {
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'tree')],
            'view_mode': 'tree,form',
            'name': _('Interview Summary Report'),
            'res_model': 'hr.applicant',
            'domain': [('id', 'in', id_list)],
            'target': 'main'
        }
