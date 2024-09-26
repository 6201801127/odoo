from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import time, datetime,timedelta
from dateutil.relativedelta import relativedelta
from datetime import timedelta, date, datetime
import datetime
from odoo.tools import float_utils
from collections import defaultdict
from pytz import utc


class WizardLateComing(models.TransientModel):
    _name = 'file.tracker.wizard'
    _description = 'PF Ledger'
    


    @api.onchange('date_range')
    def get_dates(self):
        for rec in self:
            rec.from_date = rec.date_range.date_start
            rec.to_date = rec.date_range.date_end


    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    
    report_of = fields.Selection([('File','File'),
                                  ('Correspondence','Correspondence'),
                                  ('Both','Both'),
                                  ],string="Report On", default='Both')
    search_through = fields.Selection([('Employee','Employee'),
                                  ('Branch','Branch'),
                                  ('Job','Job'),
                                  ('Department','Department'),
                                  ('All','All'),
                                  ],string="Search Via", default='Employee')

    details = fields.Char('Number/Name')
    employee_id = fields.Many2one('hr.employee', default=_default_employee)
    date_range = fields.Many2one('date.range', string='Date Range')
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')
    branch_id = fields.Many2one('res.branch', string='Branch')
    job_id = fields.Many2one('hr.job', string='Functional Designation')
    department_id = fields.Many2one('hr.department', string='Department')
    action_taken = fields.Selection([('correspondence_created', 'Correspondence Created'),
                                     ('file_created', 'File Creates'),
                                     ('correspondence_forwarded', 'Correspondence Forwarded'),
                                     ('file_forwarded', 'File Forwarded'),
                                     ('correspondence_transferred', 'Correspondence Transferred'),
                                     ('file_transferred', 'File Transferred'),
                                     ('correspondence_pulled', 'Correspondence Pulled'),
                                     ('file_pulled', 'File Pulled'),
                                     ('assigned_to_file', 'Assigned To File'),
                                     ('file_closed', 'File Closed'),
                                     ('file_repoened', 'File Reopened'),
                                     ('all', 'All')
                                     ], string='Action Taken', default='all')


    @api.multi
    def confirm_report(self):
        for rec in self:
            views_domain = []
            if rec.report_of == 'Both':
                if rec.search_through == 'Employee':
                    if rec.action_taken == 'correspondence_created':
                        view_id = self.env.ref('smart_office.view_correspondence_created_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('created_by', '=', rec.employee_id.name),
                             ('action_taken', '=', rec.action_taken),
                             ('create_date', '>=', rec.date_range.date_start),
                             ('create_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'file_created':
                        view_id = self.env.ref('smart_office.view_file_created_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('created_by', '=', rec.employee_id.name),
                             ('action_taken', '=', rec.action_taken),
                             ('create_date', '>=', rec.date_range.date_start),
                             ('create_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'correspondence_forwarded':
                        view_id = self.env.ref('smart_office.view_correspondence_forwarded_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            ['|', ('forwarded_by', '=', rec.employee_id.name), ('forwarded_to_user', '=', rec.employee_id.name), ('action_taken', '=', rec.action_taken),
                             ('forwarded_date', '>=', rec.date_range.date_start),
                             ('forwarded_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'file_forwarded':
                        view_id = self.env.ref('smart_office.view_file_forwarded_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            ['|', ('forwarded_by', '=', rec.employee_id.name), ('forwarded_to_user', '=', rec.employee_id.name), ('action_taken', '=', rec.action_taken),
                             ('forwarded_date', '>=', rec.date_range.date_start),
                             ('forwarded_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'correspondence_pulled':
                        view_id = self.env.ref('smart_office.view_correspondence_pulled_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            ['|', ('pulled_by', '=', rec.employee_id.name), ('pulled_to_user', '=', rec.employee_id.name), ('action_taken', '=', rec.action_taken),
                             ('pulled_date', '>=', rec.date_range.date_start),
                             ('pulled_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'file_pulled':
                        view_id = self.env.ref('smart_office.view_file_pulled_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            ['|', ('pulled_by', '=', rec.employee_id.name), ('pulled_to_user', '=', rec.employee_id.name), ('action_taken', '=', rec.action_taken),
                             ('pulled_date', '>=', rec.date_range.date_start),
                             ('pulled_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'correspondence_transferred':
                        view_id = self.env.ref('smart_office.view_correspondence_transferred_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            ['|', ('transferred_by', '=', rec.employee_id.name), ('transferred_to_user', '=', rec.employee_id.name), ('action_taken', '=', rec.action_taken),
                             ('transferred_date', '>=', rec.date_range.date_start),
                             ('transferred_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'file_transferred':
                        view_id = self.env.ref('smart_office.view_file_transferred_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            ['|', ('transferred_by', '=', rec.employee_id.name), ('transferred_to_user', '=', rec.employee_id.name), ('action_taken', '=', rec.action_taken),
                             ('transferred_date', '>=', rec.date_range.date_start),
                             ('transferred_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'assigned_to_file':
                        view_id = self.env.ref('smart_office.view_assigned_to_file_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('assigned_by', '=', rec.employee_id.name),
                             ('action_taken', '=', rec.action_taken),
                             ('assigned_date', '>=', rec.date_range.date_start),
                             ('assigned_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'file_closed':
                        view_id = self.env.ref('smart_office.view_file_closed_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('closed_by', '=', rec.employee_id.name),
                             ('action_taken', '=', rec.action_taken),
                             ('close_date', '>=', rec.date_range.date_start),
                             ('close_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'file_repoened':
                        view_id = self.env.ref('smart_office.view_file_repoened_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('repoen_by', '=', rec.employee_id.name),
                             ('action_taken', '=', rec.action_taken),
                             ('repoen_date', '>=', rec.date_range.date_start),
                             ('repoen_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    else:
                        view_id = self.env.ref('smart_office.file_tracking_report_tree_view').id
                        dmn = self.env['file.tracker.report'].search([])
                        for line in dmn:
                            if line.created_by == rec.employee_id.name or line.assigned_by == rec.employee_id.name or line.closed_by == rec.employee_id.name or line.repoen_by == rec.employee_id.name or line.forwarded_by == rec.employee_id.name or line.forwarded_to_user == rec.employee_id.name:
                                if (line.create_date and rec.date_range.date_start <= line.create_date <= rec.date_range.date_end) or (line.assigned_date and rec.date_range.date_start <= line.assigned_date <= rec.date_range.date_end) or (line.close_date and rec.date_range.date_start <= line.close_date <= rec.date_range.date_end) or (line.repoen_date and rec.date_range.date_start <= line.repoen_date <= rec.date_range.date_end) or (line.forwarded_date and rec.date_range.date_start <= line.forwarded_date <= rec.date_range.date_end):
                                    views_domain.append(line.id)
                    return {
                        'name': 'File Tracking Report',
                        'view_type': 'form',
                        'view_mode': 'tree',
                        'res_model': 'file.tracker.report',
                        'type': 'ir.actions.act_window',
                        'target': 'current',
                        'view_id': view_id,
                        'domain': [('id', 'in', views_domain)],
                    }

                elif rec.search_through == 'Branch':

                    if rec.action_taken == 'correspondence_created':
                        view_id = self.env.ref('smart_office.view_correspondence_created_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('created_by_branch', '=', rec.branch_id.name),
                             ('action_taken', '=', rec.action_taken),
                             ('create_date', '>=', rec.date_range.date_start),
                             ('create_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'file_created':
                        view_id = self.env.ref('smart_office.view_file_created_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('created_by_branch', '=', rec.branch_id.name),
                             ('action_taken', '=', rec.action_taken),
                             ('create_date', '>=', rec.date_range.date_start),
                             ('create_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'correspondence_forwarded':
                        view_id = self.env.ref('smart_office.view_correspondence_forwarded_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            ['|', ('forwarded_by_branch', '=', rec.branch_id.name), ('forwarded_to_branch', '=', rec.branch_id.name), ('action_taken', '=', rec.action_taken),
                             ('forwarded_date', '>=', rec.date_range.date_start),
                             ('forwarded_date', '<=', rec.date_range.date_end)])
                    elif rec.action_taken == 'file_forwarded':
                        view_id = self.env.ref('smart_office.view_file_forwarded_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            ['|', ('forwarded_by_branch', '=', rec.branch_id.name), ('forwarded_to_branch', '=', rec.branch_id.name), ('action_taken', '=', rec.action_taken),
                             ('forwarded_date', '>=', rec.date_range.date_start),
                             ('forwarded_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'correspondence_pulled':
                        view_id = self.env.ref('smart_office.view_correspondence_pulled_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            ['|', ('pulled_by_branch', '=', rec.branch_id.name), ('pulled_to_branch', '=', rec.branch_id.name), ('action_taken', '=', rec.action_taken),
                             ('pulled_date', '>=', rec.date_range.date_start),
                             ('pulled_date', '<=', rec.date_range.date_end)])
                    elif rec.action_taken == 'file_pulled':
                        view_id = self.env.ref('smart_office.view_file_pulled_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            ['|', ('pulled_by_branch', '=', rec.branch_id.name), ('pulled_to_branch', '=', rec.branch_id.name), ('action_taken', '=', rec.action_taken),
                             ('pulled_date', '>=', rec.date_range.date_start),
                             ('pulled_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)

                    elif rec.action_taken == 'correspondence_transferred':
                        view_id = self.env.ref('smart_office.view_correspondence_transferred_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            ['|', ('transferred_by_branch', '=', rec.branch_id.name), ('transferred_to_branch', '=', rec.branch_id.name), ('action_taken', '=', rec.action_taken),
                             ('transferred_date', '>=', rec.date_range.date_start),
                             ('transferred_date', '<=', rec.date_range.date_end)])
                    elif rec.action_taken == 'file_transferred':
                        view_id = self.env.ref('smart_office.view_file_transferred_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            ['|', ('transferred_by_branch', '=', rec.branch_id.name), ('transferred_to_branch', '=', rec.branch_id.name), ('action_taken', '=', rec.action_taken),
                             ('transferred_date', '>=', rec.date_range.date_start),
                             ('transferred_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'assigned_to_file':
                        view_id = self.env.ref('smart_office.view_assigned_to_file_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('assigned_by_branch', '=', rec.branch_id.name),
                             ('action_taken', '=', rec.action_taken),
                             ('assigned_date', '>=', rec.date_range.date_start),
                             ('assigned_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'file_closed':
                        view_id = self.env.ref('smart_office.view_file_closed_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('closed_by_branch', '=', rec.branch_id.name),
                             ('action_taken', '=', rec.action_taken),
                             ('close_date', '>=', rec.date_range.date_start),
                             ('close_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'file_repoened':
                        view_id = self.env.ref('smart_office.view_file_repoened_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('repoen_by_branch', '=', rec.branch_id.name),
                             ('action_taken', '=', rec.action_taken),
                             ('repoen_date', '>=', rec.date_range.date_start),
                             ('repoen_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    else:
                        view_id = self.env.ref('smart_office.file_tracking_report_tree_view').id
                        dmn = self.env['file.tracker.report'].search([])
                        for line in dmn:
                            if line.created_by == rec.employee_id.name or line.assigned_by == rec.employee_id.name or line.closed_by == rec.employee_id.name or line.repoen_by == rec.employee_id.name or line.forwarded_by == rec.employee_id.name or line.forwarded_to_user == rec.employee_id.name:
                                if (
                                        line.create_date and rec.date_range.date_start <= line.create_date <= rec.date_range.date_end) or (
                                        line.assigned_date and rec.date_range.date_start <= line.assigned_date <= rec.date_range.date_end) or (
                                        line.close_date and rec.date_range.date_start <= line.close_date <= rec.date_range.date_end) or (
                                        line.repoen_date and rec.date_range.date_start <= line.repoen_date <= rec.date_range.date_end) or (
                                        line.forwarded_date and rec.date_range.date_start <= line.forwarded_date <= rec.date_range.date_end):
                                    views_domain.append(line.id)
                    return {
                        'name': 'File Tracking Report',
                        'view_type': 'form',
                        'view_mode': 'tree',
                        'res_model': 'file.tracker.report',
                        'type': 'ir.actions.act_window',
                        'target': 'current',
                        'view_id': view_id,
                        'domain': [('id', 'in', views_domain)],
                    }

                elif rec.search_through == 'Job':
                    if rec.action_taken == 'correspondence_created':
                        view_id = self.env.ref('smart_office.view_correspondence_created_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('created_by_jobpos', '=', rec.job_id.name),
                             ('action_taken', '=', rec.action_taken),
                             ('create_date', '>=', rec.date_range.date_start),
                             ('create_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'file_created':
                        view_id = self.env.ref('smart_office.view_file_created_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('created_by_jobpos', '=', rec.job_id.name),
                             ('action_taken', '=', rec.action_taken),
                             ('create_date', '>=', rec.date_range.date_start),
                             ('create_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'correspondence_forwarded':
                        view_id = self.env.ref('smart_office.view_correspondence_forwarded_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            ['|', ('forwarded_by_jobpos', '=', rec.job_id.name), ('job_pos', '=', rec.job_id.name), ('action_taken', '=', rec.action_taken),
                             ('forwarded_date', '>=', rec.date_range.date_start),
                             ('forwarded_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'file_forwarded':
                        view_id = self.env.ref('smart_office.view_file_forwarded_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            ['|', ('forwarded_by_jobpos', '=', rec.job_id.name), ('job_pos', '=', rec.job_id.name), ('action_taken', '=', rec.action_taken),
                             ('forwarded_date', '>=', rec.date_range.date_start),
                             ('forwarded_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'correspondence_pulled':
                        view_id = self.env.ref('smart_office.view_correspondence_pulled_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            ['|', ('pulled_by_jobpos', '=', rec.job_id.name), ('pulled_to_job_pos', '=', rec.job_id.name), ('action_taken', '=', rec.action_taken),
                             ('pulled_date', '>=', rec.date_range.date_start),
                             ('pulled_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'file_pulled':
                        view_id = self.env.ref('smart_office.view_file_pulled_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            ['|', ('pulled_by_jobpos', '=', rec.job_id.name), ('pulled_to_job_pos', '=', rec.job_id.name), ('action_taken', '=', rec.action_taken),
                             ('pulled_date', '>=', rec.date_range.date_start),
                             ('pulled_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'correspondence_transferred':
                        view_id = self.env.ref('smart_office.view_correspondence_transferred_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            ['|', ('transferred_by_jobpos', '=', rec.job_id.name), ('transferred_to_job_pos', '=', rec.job_id.name), ('action_taken', '=', rec.action_taken),
                             ('transferred_date', '>=', rec.date_range.date_start),
                             ('transferred_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'file_transferred':
                        view_id = self.env.ref('smart_office.view_file_transferred_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            ['|', ('transferred_by_jobpos', '=', rec.job_id.name), ('transferred_to_job_pos', '=', rec.job_id.name), ('action_taken', '=', rec.action_taken),
                             ('transferred_date', '>=', rec.date_range.date_start),
                             ('transferred_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'assigned_to_file':
                        view_id = self.env.ref('smart_office.view_assigned_to_file_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('assigned_by_jobpos', '=', rec.job_id.name),
                             ('action_taken', '=', rec.action_taken),
                             ('assigned_date', '>=', rec.date_range.date_start),
                             ('assigned_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'file_closed':
                        view_id = self.env.ref('smart_office.view_file_closed_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('closed_by_jobpos', '=', rec.job_id.name),
                             ('action_taken', '=', rec.action_taken),
                             ('close_date', '>=', rec.date_range.date_start),
                             ('close_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'file_repoened':
                        view_id = self.env.ref('smart_office.view_file_repoened_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('repoen_by_jobpos', '=', rec.job_id.name),
                             ('action_taken', '=', rec.action_taken),
                             ('repoen_date', '>=', rec.date_range.date_start),
                             ('repoen_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    else:
                        view_id = self.env.ref('smart_office.file_tracking_report_tree_view').id
                        dmn = self.env['file.tracker.report'].search([])
                        for line in dmn:
                            if line.created_by == rec.employee_id.name or line.assigned_by == rec.employee_id.name or line.closed_by == rec.employee_id.name or line.repoen_by == rec.employee_id.name or line.forwarded_by == rec.employee_id.name or line.forwarded_to_user == rec.employee_id.name:
                                if (
                                        line.create_date and rec.date_range.date_start <= line.create_date <= rec.date_range.date_end) or (
                                        line.assigned_date and rec.date_range.date_start <= line.assigned_date <= rec.date_range.date_end) or (
                                        line.close_date and rec.date_range.date_start <= line.close_date <= rec.date_range.date_end) or (
                                        line.repoen_date and rec.date_range.date_start <= line.repoen_date <= rec.date_range.date_end) or (
                                        line.forwarded_date and rec.date_range.date_start <= line.forwarded_date <= rec.date_range.date_end):
                                    views_domain.append(line.id)
                    return {
                        'name': 'File Tracking Report',
                        'view_type': 'form',
                        'view_mode': 'tree',
                        'res_model': 'file.tracker.report',
                        'type': 'ir.actions.act_window',
                        'target': 'current',
                        'view_id': view_id,
                        'domain': [('id', 'in', views_domain)],
                    }

                elif rec.search_through == 'Department':
                    if rec.action_taken == 'correspondence_created':
                        view_id = self.env.ref('smart_office.view_correspondence_created_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('created_by_dept', '=', rec.department_id.name),
                             ('action_taken', '=', rec.action_taken),
                             ('create_date', '>=', rec.date_range.date_start),
                             ('create_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'file_created':
                        view_id = self.env.ref('smart_office.view_file_created_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('created_by_dept', '=', rec.department_id.name),
                             ('action_taken', '=', rec.action_taken),
                             ('create_date', '>=', rec.date_range.date_start),
                             ('create_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'correspondence_forwarded':
                        view_id = self.env.ref('smart_office.view_correspondence_forwarded_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            ['|', ('forwarded_by_dept', '=', rec.department_id.name), ('forwarded_to_dept', '=', rec.department_id.name), ('action_taken', '=', rec.action_taken),
                             ('forwarded_date', '>=', rec.date_range.date_start),
                             ('forwarded_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'file_forwarded':
                        view_id = self.env.ref('smart_office.view_file_forwarded_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            ['|', ('forwarded_by_dept', '=', rec.department_id.name), ('forwarded_to_dept', '=', rec.department_id.name), ('action_taken', '=', rec.action_taken),
                             ('forwarded_date', '>=', rec.date_range.date_start),
                             ('forwarded_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'correspondence_pulled':
                        view_id = self.env.ref('smart_office.view_correspondence_pulled_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            ['|', ('pulled_by_dept', '=', rec.department_id.name), ('pulled_to_dept', '=', rec.department_id.name), ('action_taken', '=', rec.action_taken),
                             ('pulled_date', '>=', rec.date_range.date_start),
                             ('pulled_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'file_pulled':
                        view_id = self.env.ref('smart_office.view_file_pulled_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            ['|', ('pulled_by_dept', '=', rec.department_id.name), ('pulled_to_dept', '=', rec.department_id.name), ('action_taken', '=', rec.action_taken),
                             ('pulled_date', '>=', rec.date_range.date_start),
                             ('pulled_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'correspondence_transferred':
                        view_id = self.env.ref('smart_office.view_correspondence_transferred_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            ['|', ('transferred_by_dept', '=', rec.department_id.name), ('transferred_to_dept', '=', rec.department_id.name), ('action_taken', '=', rec.action_taken),
                             ('transferred_date', '>=', rec.date_range.date_start),
                             ('transferred_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'file_transferred':
                        view_id = self.env.ref('smart_office.view_file_transferred_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            ['|', ('transferred_by_dept', '=', rec.department_id.name), ('transferred_to_dept', '=', rec.department_id.name), ('action_taken', '=', rec.action_taken),
                             ('transferred_date', '>=', rec.date_range.date_start),
                             ('transferred_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'assigned_to_file':
                        view_id = self.env.ref('smart_office.view_assigned_to_file_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('assigned_by_dept', '=', rec.department_id.name),
                             ('action_taken', '=', rec.action_taken),
                             ('assigned_date', '>=', rec.date_range.date_start),
                             ('assigned_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'file_closed':
                        view_id = self.env.ref('smart_office.view_file_closed_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('closed_by_dept', '=', rec.department_id.name),
                             ('action_taken', '=', rec.action_taken),
                             ('close_date', '>=', rec.date_range.date_start),
                             ('close_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'file_repoened':
                        view_id = self.env.ref('smart_office.view_file_repoened_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('repoen_by_dept', '=', rec.department_id.name),
                             ('action_taken', '=', rec.action_taken),
                             ('repoen_date', '>=', rec.date_range.date_start),
                             ('repoen_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    else:
                        view_id = self.env.ref('smart_office.file_tracking_report_tree_view').id
                        dmn = self.env['file.tracker.report'].search([])
                        for line in dmn:
                            if line.created_by == rec.employee_id.name or line.assigned_by == rec.employee_id.name or line.closed_by == rec.employee_id.name or line.repoen_by == rec.employee_id.name or line.forwarded_by == rec.employee_id.name or line.forwarded_to_user == rec.employee_id.name:
                                if (
                                        line.create_date and rec.date_range.date_start <= line.create_date <= rec.date_range.date_end) or (
                                        line.assigned_date and rec.date_range.date_start <= line.assigned_date <= rec.date_range.date_end) or (
                                        line.close_date and rec.date_range.date_start <= line.close_date <= rec.date_range.date_end) or (
                                        line.repoen_date and rec.date_range.date_start <= line.repoen_date <= rec.date_range.date_end) or (
                                        line.forwarded_date and rec.date_range.date_start <= line.forwarded_date <= rec.date_range.date_end):
                                    views_domain.append(line.id)
                    return {
                        'name': 'File Tracking Report',
                        'view_type': 'form',
                        'view_mode': 'tree',
                        'res_model': 'file.tracker.report',
                        'type': 'ir.actions.act_window',
                        'target': 'current',
                        'view_id': view_id,
                        'domain': [('id', 'in', views_domain)],
                    }

                else:
                    if rec.action_taken == 'correspondence_created':
                        view_id = self.env.ref('smart_office.view_correspondence_created_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('action_taken', '=', rec.action_taken),
                             ('create_date', '>=', rec.date_range.date_start),
                             ('create_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'file_created':
                        view_id = self.env.ref('smart_office.view_file_created_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('action_taken', '=', rec.action_taken),
                             ('create_date', '>=', rec.date_range.date_start),
                             ('create_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'correspondence_forwarded':
                        view_id = self.env.ref('smart_office.view_correspondence_forwarded_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('forwarded_date', '>=', rec.date_range.date_start),
                             ('forwarded_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'file_forwarded':
                        view_id = self.env.ref('smart_office.view_file_forwarded_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('forwarded_date', '>=', rec.date_range.date_start),
                             ('forwarded_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'correspondence_pulled':
                        view_id = self.env.ref('smart_office.view_correspondence_pulled_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('pulled_date', '>=', rec.date_range.date_start),
                             ('pulled_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'file_pulled':
                        view_id = self.env.ref('smart_office.view_file_pulled_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('pulled_date', '>=', rec.date_range.date_start),
                             ('pulled_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'correspondence_transferred':
                        view_id = self.env.ref('smart_office.view_correspondence_transferred_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('transferred_date', '>=', rec.date_range.date_start),
                             ('transferred_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'file_transferred':
                        view_id = self.env.ref('smart_office.view_file_transferred_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('transferred_date', '>=', rec.date_range.date_start),
                             ('transferred_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'assigned_to_file':
                        view_id = self.env.ref('smart_office.view_assigned_to_file_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('action_taken', '=', rec.action_taken),
                             ('assigned_date', '>=', rec.date_range.date_start),
                             ('assigned_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'file_closed':
                        view_id = self.env.ref('smart_office.view_file_closed_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('action_taken', '=', rec.action_taken),
                             ('close_date', '>=', rec.date_range.date_start),
                             ('close_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    elif rec.action_taken == 'file_repoened':
                        view_id = self.env.ref('smart_office.view_file_repoened_tree').id
                        dmn = self.env['file.tracker.report'].search(
                            [('action_taken', '=', rec.action_taken),
                             ('repoen_date', '>=', rec.date_range.date_start),
                             ('repoen_date', '<=', rec.date_range.date_end)])
                        for id in dmn:
                            views_domain.append(id.id)
                    else:
                        view_id = self.env.ref('smart_office.file_tracking_report_tree_view').id
                        dmn = self.env['file.tracker.report'].search([])
                        for line in dmn:
                            if line.created_by == rec.employee_id.name or line.assigned_by == rec.employee_id.name or line.closed_by == rec.employee_id.name or line.repoen_by == rec.employee_id.name or line.forwarded_by == rec.employee_id.name or line.forwarded_to_user == rec.employee_id.name:
                                if (
                                        line.create_date and rec.date_range.date_start <= line.create_date <= rec.date_range.date_end) or (
                                        line.assigned_date and rec.date_range.date_start <= line.assigned_date <= rec.date_range.date_end) or (
                                        line.close_date and rec.date_range.date_start <= line.close_date <= rec.date_range.date_end) or (
                                        line.repoen_date and rec.date_range.date_start <= line.repoen_date <= rec.date_range.date_end) or (
                                        line.forwarded_date and rec.date_range.date_start <= line.forwarded_date <= rec.date_range.date_end):
                                    views_domain.append(line.id)
                    return {
                        'name': 'File Tracking Report',
                        'view_type': 'form',
                        'view_mode': 'tree',
                        'res_model': 'file.tracker.report',
                        'type': 'ir.actions.act_window',
                        'target': 'current',
                        'view_id': view_id,
                        'domain': [('id', 'in', views_domain)],
                    }
            else:
                dmn = self.env['file.tracker.report'].search(['|', ('name', '=', rec.details), ('number', '=', rec.details)])
                for id in dmn:
                    views_domain.append(id.id)
                return {
                    'name': 'File Tracking Report',
                    'view_type': 'form',
                    'view_mode': 'tree',
                    'res_model': 'file.tracker.report',
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'domain': [('id', 'in', views_domain)]
                }
