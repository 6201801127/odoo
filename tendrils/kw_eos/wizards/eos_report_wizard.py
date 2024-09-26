# -*- coding: utf-8 -*-

import calendar
from odoo import api, fields, models, _
import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from datetime import date


def get_years():
    year_list = []
    # start_year = (date.today().year - (date.today().year - 2000))
    for i in range((date.today().year), 1997, -1):
        year_list.append((i, str(i)))
    return year_list


class eos_report_wizard(models.TransientModel):
    _name = 'eos_report_wizard'
    _description = 'EOS Report'

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    applied_by = fields.Selection([('employee', 'User'),
                                   ('dt', 'Date'),
                                   ('month', 'Month'),
                                   ('year', 'Year'),
                                   ('emptype', 'Employment Type'),
                                   ('offboard', 'Off-boarding type'),
                                   ('department', 'Department'),
                                   ('location', 'Location'),
                                   ('gender', 'Gender'), ], string="Filter", default='dt')
    employee_ids = fields.Many2many('hr.employee', string="User")
    month = fields.Selection([('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
                              ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
                              ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December'), ],
                             string="Month", default=str(date.today().month))
    year = fields.Selection(get_years(), string='Year', default=date.today().year)
    emptype = fields.Many2one('kwemp_employment_type', ondelete='cascade', string="Employment Type")
    offboarding_type = fields.Selection([('reg', 'Resignation'),
                                         ('con', 'Contract Closure'),
                                         ('ret', 'Retirement'),
                                         ('ter', 'Termination'),
                                         ('dem', 'Demise')], string="Off-boarding Type", default='reg')
    offboard = fields.Many2one('kw_offboarding_type_master')
    department = fields.Many2one('hr.department', string="Department")
    gender = fields.Selection(string="Gender", selection=[('male', 'Male'), ('female', 'Female'), ('others', 'Other')])
    location = fields.Many2one('kw_res_branch', 'Location')

    def search_report(self):
        tree_view_id = self.env.ref('kw_eos.resignation_view_report').id
        form_view_id = self.env.ref('kw_eos.report_form').id
        if self.applied_by == 'dt':
            from_date = self.date_from
            to_date = self.date_to
            record_data = self.env['kw_resignation'].sudo().search([])
            for rec in record_data:
                domain = [('last_working_date', '>=', from_date), ('last_working_date', '<=', to_date)]
                return {
                    'type': 'ir.actions.act_window',
                    'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                    'view_mode': 'tree,form',
                    'name': _('Report'),
                    'res_model': 'kw_resignation',
                    'domain': domain,
                    'target': 'main',
                }

        if self.applied_by == 'employee':
            # record_data = self.env['kw_resignation'].sudo().search([])
            # for rec in record_data:
            return {
                'type': 'ir.actions.act_window',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,form',
                'name': _('Report'),
                'res_model': 'kw_resignation',
                'domain': [('applicant_id', 'in', self.employee_ids.ids)],
                'target': 'main',
            }
        if self.applied_by == 'month':
            month = self.month
            record_data = self.env['kw_resignation'].sudo().search([])
            applicant_id = []
            for rec in record_data:
                rec_month = rec.create_date
                if str(rec_month.month) == month:
                    applicant_id.append(rec.applicant_id.id)
            domain = [('applicant_id', 'in', applicant_id)]
            return {
                'type': 'ir.actions.act_window',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,form',
                'name': _('Report'),
                'res_model': 'kw_resignation',
                'domain': domain,
                'target': 'main',
            }
        if self.applied_by == 'year':
            year = self.year
            record_data = self.env['kw_resignation'].sudo().search([])
            applicant_id = []
            for rec in record_data:
                rec_year = rec.create_date
                if rec_year.year == year:
                    applicant_id.append(rec.applicant_id.id)
            domain = [('applicant_id', 'in', applicant_id)]
            return {
                'type': 'ir.actions.act_window',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,form',
                'name': _('Report'),
                'res_model': 'kw_resignation',
                'domain': domain,
                'target': 'main',
            }
        if self.applied_by == 'emptype':
            emptype = self.emptype.id
            employee_res = self.env['hr.employee'].sudo().search([('employement_type', '=', emptype)])
            applicant_id = []
            for res in employee_res:
                record_data = self.env['kw_resignation'].sudo().search([('applicant_id', '=', res.id)])
                for rec in record_data:
                    applicant_id.append(rec.applicant_id.id)
            domain = [('applicant_id', 'in', applicant_id)]
            return {
                'type': 'ir.actions.act_window',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,form',
                'name': _('Report'),
                'res_model': 'kw_resignation',
                'domain': domain,
                'target': 'main',
            }
        if self.applied_by == 'offboard':
            offboard = self.offboard.id
            # record_data = self.env['kw_offboarding_type_master'].sudo().search([('code','=',offboard)])
            record_data = self.env['kw_resignation'].sudo().search([('offboarding_type', '=', offboard)])
            applicant_id = []
            for rec in record_data:
                applicant_id.append(rec.applicant_id.id)
            domain = [('applicant_id', 'in', applicant_id)]
            return {
                'type': 'ir.actions.act_window',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,form',
                'name': _('Report'),
                'res_model': 'kw_resignation',
                'domain': domain,
                'target': 'main',
            }
        if self.applied_by == 'department':
            department = self.department.id
            employee_res = self.env['hr.employee'].sudo().search([('department_id', '=', department)])
            applicant_id = []
            for res in employee_res:
                record_data = self.env['kw_resignation'].sudo().search([('applicant_id', '=', res.id)])
                for rec in record_data:
                    applicant_id.append(rec.applicant_id.id)
            domain = [('applicant_id', 'in', applicant_id)]
            return {
                'type': 'ir.actions.act_window',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,form',
                'name': _('Report'),
                'res_model': 'kw_resignation',
                'domain': domain,
                'target': 'main',
            }
        if self.applied_by == 'location':
            location = self.location.id
            employee_res = self.env['hr.employee'].sudo().search([('base_branch_id', '=', location)])
            applicant_id = []
            for res in employee_res:
                record_data = self.env['kw_resignation'].sudo().search([('applicant_id', '=', res.id)])
                for rec in record_data:
                    applicant_id.append(rec.applicant_id.id)
            domain = [('applicant_id', 'in', applicant_id)]
            return {
                'type': 'ir.actions.act_window',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,form',
                'name': _('Report'),
                'res_model': 'kw_resignation',
                'domain': domain,
                'target': 'main',
            }
        if self.applied_by == 'gender':
            gender = self.gender
            employee_res = self.env['hr.employee'].sudo().search([('gender', '=', gender)])
            applicant_id = []
            for res in employee_res:
                record_data = self.env['kw_resignation'].sudo().search([('applicant_id', '=', res.id)])
                for rec in record_data:
                    applicant_id.append(rec.applicant_id.id)
            domain = [('applicant_id', 'in', applicant_id)]
            return {
                'type': 'ir.actions.act_window',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,form',
                'name': _('Report'),
                'res_model': 'kw_resignation',
                'domain': domain,
                'target': 'main',
            }


class eos_feedback_wizard(models.TransientModel):
    _name = 'eos_feedback_wizard'
    _description = 'EOS Feedback Report'

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    applied_by = fields.Selection([('all', 'All'),
                                   ('dt', 'Date wise'),
                                   ('my', 'Month & Year wise'),
                                   ('employee', 'Employee'),
                                   ('exemployee', 'Ex-employee'),
                                   ], string="Applied By", default='all')
    employee_ids = fields.Many2many('hr.employee', string="Employee")
    exemployee_ids = fields.Many2many('hr.employee', 'eos_feedback_wizard_exhr_employee_rel', 'offboarding_wiz_id',
                                      'employee_id', string="Ex-employee",domain=[('active','=',False)])
    month = fields.Selection([('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
                              ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
                              ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December'), ],
                             string="Month", default=str(date.today().month))
    year = fields.Selection(get_years(), string='Year', default=date.today().year)

    @api.onchange('applied_by')
    def _get_employee(self):
        domain = []
        employee_data = False
        dm = False
        employees = self.env['hr.employee'].sudo()
        eos_employee_list = self.env['kw_eos_checklist'].sudo().search([]).mapped('applicant_id').ids
        if self.env.user.has_group('kw_employee.group_hr_ra') \
                and not self.env.user.has_group('kw_wfh.group_hr_hod') \
                and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager') \
                and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance') \
                and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_admin') \
                and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_nsa') \
                and not self.env.user.has_group('kw_eos.group_kw_eos_officer') \
                and not self.env.user.has_group('kw_eos.group_kw_eos_resource_head'):
            if self.applied_by == 'employee':
                domain = ['|', '&', '|', ('id', '=', self.env.user.employee_ids.id),
                          ('parent_id.user_id', '=', self.env.user.employee_ids.user_id.id), ('active', '=', True)]
            elif self.applied_by == 'exemployee':
                domain = ['|', '&', '|', ('id', '=', self.env.user.employee_ids.id),
                          ('parent_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                          ('active', '=', False)]
            employee_data = employees.with_context(active_test=False).search(domain).filtered(lambda x: x.id in eos_employee_list)
        elif self.env.user.has_group('kw_wfh.group_hr_hod') \
                and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager'):
            if self.applied_by == 'employee':
                domain = ['|', '&', '|', ('id', '=', self.env.user.employee_ids.id),
                          ('department_id.manager_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                          ('active', '=', True)]
            elif self.applied_by == 'exemployee':
                domain = ['|', '&', '|', ('id', '=', self.env.user.employee_ids.id),
                          ('department_id.manager_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                          ('active', '=', False)]
            employee_data = employees.with_context(active_test=False).search(domain).filtered(lambda x: x.id in eos_employee_list)
        else:
            if self.applied_by == 'employee':
                domain = [('active', '=', True)]
            elif self.applied_by == 'exemployee':
                domain = [('active', '=', False)]
            employee_data = employees.with_context(active_test=False).search(domain).filtered(lambda x: x.id in eos_employee_list)
        if employee_data and self.applied_by == 'employee':
            dm = {'domain': {'employee_ids': [('id', 'in', employee_data.ids)]}}
        elif employee_data and self.applied_by == 'exemployee':
            dm = {'domain': {'exemployee_ids': [('id', 'in', employee_data.ids)]}}
        return dm

    def search_feedback_report(self):
        tree_view_id = self.env.ref('kw_eos.view_employee_exit_interview_report_tree').id
        form_view_id = self.env.ref('kw_eos.view_employee_exit_interview_report_form').id
        if self.applied_by == 'dt':
            from_date = self.date_from
            to_date = self.date_to
            record_data = self.env['employee.exit.interview'].sudo().search([])
            for rec in record_data:
                domain = [('create_date', '>=', from_date), ('create_date', '<=', to_date)]
                return {
                    'type': 'ir.actions.act_window',
                    'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                    'view_mode': 'tree,form',
                    'name': _('Feedback Report'),
                    'res_model': 'employee.exit.interview',
                    'domain': domain,
                    'target': 'main',
                }

        if self.applied_by == 'employee' or self.applied_by == 'exemployee':
            record_data = self.env['employee.exit.interview'].sudo().search([])
            for rec in record_data:
                action_return =  {
                    'type': 'ir.actions.act_window',
                    'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                    'view_mode': 'tree,form',
                    'name': _('Feedback Report'),
                    'res_model': 'employee.exit.interview',
                    'target': 'main',
                }
                if self.applied_by == 'employee':
                    action_return['domain'] = [('employee_id', 'in', self.employee_ids.ids)]
                if self.applied_by == 'exemployee':
                    action_return['domain'] = [('employee_id', 'in', self.exemployee_ids.ids)]
                return action_return
        if self.applied_by == 'my':
            month = self.month
            year = self.year
            record_data = self.env['employee.exit.interview'].sudo().search([])
            applicant_id = []
            for rec in record_data:
                rec_month = rec_year = rec.create_date
                if str(rec_month.month) == month and rec_year.year == year:
                    applicant_id.append(rec.employee_id.id)
            domain = [('employee_id', 'in', applicant_id)]
            return {
                'type': 'ir.actions.act_window',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,form',
                'name': _('Feedback Report'),
                'res_model': 'employee.exit.interview',
                'domain': domain,
                'target': 'main',
            }
        # if self.applied_by == 'year':
        #     year = self.year
        #     record_data = self.env['employee.exit.interview'].sudo().search([])
        #     applicant_id = []
        #     for rec in record_data:
        #         rec_year = rec.create_date
        #         if rec_year.year == year:
        #             applicant_id.append(rec.employee_id.id)
        #     domain = [('employee_id', 'in', applicant_id)]
        #     return {
        #         'type': 'ir.actions.act_window',
        #         'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
        #         'view_mode': 'tree,form',
        #         'name': ('Feedback Report'),
        #         'res_model': 'employee.exit.interview',
        #         'domain': domain,
        #         'target': 'main',
        #     }
        if self.applied_by == 'all':
            action = {
                'type': 'ir.actions.act_window',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,form',
                'name': _('Feedback Report'),
                'res_model': 'employee.exit.interview',
                'target': 'main',
            }
            if self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                    or self.env.user.has_group('kw_eos.group_kw_eos_report_manager') \
                    or self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance') \
                    or self.env.user.has_group('kw_onboarding.group_kw_onboarding_admin') \
                    or self.env.user.has_group('kw_onboarding.group_kw_onboarding_nsa'):
                action['domain'] = []
            if self.env.user.has_group('kw_employee.group_hr_ra') \
                    and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                    and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager') \
                    and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance') \
                    and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_admin') \
                    and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_nsa') \
                    and not self.env.user.has_group('kw_wfh.group_hr_hod'):
                action['domain'] = [('employee_id.parent_id.user_id', '=', self.env.user.id)]
            if self.env.user.has_group('kw_wfh.group_hr_hod') \
                    and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                    and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager'):
                action['domain'] = ['|', ('employee_id.parent_id.user_id', '=', self.env.user.id), (
                    'employee_id.department_id.manager_id.user_id', '=', self.env.user.employee_ids.user_id.id)]
            return action


class eos_feedback_wizard(models.TransientModel):
    _name = 'eos_clearance_wizard'
    _description = 'EOS Clearance Report'

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')

    employee_ids = fields.Many2many('hr.employee', string="User")
    exemployee_ids = fields.Many2many('hr.employee', 'eos_clearance_wiz_exhr_employee_rel', 'offboarding_wiz_id',
                                      'employee_id', string="Ex-employee", domain=[('active', '=', False)])

    applied_by = fields.Selection([('all', 'All'),
                                   ('dt', 'Date wise'),
                                   ('my', 'Month & Year wise'),
                                   ('employee', 'Employee'),
                                   ('exemployee', 'Ex-employee')], string="Applied By", default='all')

    month = fields.Selection([('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
                              ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
                              ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December'), ],
                             string="Month", default=str(date.today().month))
    year = fields.Selection(get_years(), string='Year', default=date.today().year)

    @api.onchange('applied_by')
    def _get_employee(self):
        # import pdb
        # pdb.set_trace()
        domain = []
        employee_data = False
        employees = self.env['hr.employee'].sudo()
        dm = False
        eos_employee_list = self.env['kw_eos_checklist'].sudo().search([]).mapped('applicant_id').ids
        if self.env.user.has_group('kw_employee.group_hr_ra') \
                and not self.env.user.has_group('kw_wfh.group_hr_hod') \
                and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager') \
                and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance') \
                and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_admin') \
                and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_nsa') \
                and not self.env.user.has_group('kw_eos.group_kw_eos_officer') \
                and not self.env.user.has_group('kw_eos.group_kw_eos_resource_head'):
            if self.applied_by == 'employee':
                domain = ['|', '&', '|', ('id', '=', self.env.user.employee_ids.id),
                          ('parent_id.user_id', '=', self.env.user.employee_ids.user_id.id), ('active', '=', True)]
            elif self.applied_by == 'exemployee':
                domain = ['|', '&', '|', ('id', '=', self.env.user.employee_ids.id),
                          ('parent_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                          ('active', '=', False)]
            employee_data = employees.with_context(active_test=False).search(domain).filtered(lambda x: x.id in eos_employee_list)
        elif self.env.user.has_group('kw_wfh.group_hr_hod') \
                and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager'):
            if self.applied_by == 'employee':
                domain = ['|', '&', '|', ('id', '=', self.env.user.employee_ids.id),
                          ('department_id.manager_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                          ('active', '=', True)]
            elif self.applied_by == 'exemployee':
                domain = ['|', '&', '|', ('id', '=', self.env.user.employee_ids.id),
                          ('department_id.manager_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                          ('active', '=', False)]
            employee_data = employees.with_context(active_test=False).search(domain).filtered(lambda x: x.id in eos_employee_list)
        else:
            if self.applied_by == 'employee':
                domain = [('active', '=', True)]
            elif self.applied_by == 'exemployee':
                domain = [('active', '=', False)]
            employee_data = employees.with_context(active_test=False).search(domain).filtered(lambda x: x.id in eos_employee_list)
        if employee_data and self.applied_by == 'employee':
            dm = {'domain': {'employee_ids': [('id', 'in', employee_data.ids)]}}
        elif employee_data and self.applied_by == 'exemployee':
            dm = {'domain': {'exemployee_ids': [('id', 'in', employee_data.ids)]}}
        
        return dm

    def search_clearance_report(self):
        tree_view_id = self.env.ref('kw_eos.view_hr_employee_clearance_report_tree').id
        form_view_id = self.env.ref('kw_eos.view_hr_employee_clearance_report_form').id
        if self.applied_by == 'dt':
            from_date = self.date_from
            to_date = self.date_to
            record_data = self.env['hr.employee.clearance'].sudo().search([])
            for rec in record_data:
                domain = [('create_date', '>=', from_date), ('create_date', '<=', to_date)]
                return {
                    'type': 'ir.actions.act_window',
                    'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                    'view_mode': 'tree,form',
                    'name': _('Clearance Report'),
                    'res_model': 'hr.employee.clearance',
                    'domain': domain,
                    'target': 'main',
                }

        if self.applied_by == 'employee' or self.applied_by == 'exemployee':
            record_data = self.env['hr.employee.clearance'].sudo().search([])
            for rec in record_data:
                action_return =  {
                    'type': 'ir.actions.act_window',
                    'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                    'view_mode': 'tree,form',
                    'name': _('Clearance Report'),
                    'res_model': 'hr.employee.clearance',
                    'target': 'main',
                }
                if self.applied_by == 'employee':
                    action_return['domain'] = [('employee_id', 'in', self.employee_ids.ids)]
                if self.applied_by == 'exemployee':
                    action_return['domain'] = [('employee_id', 'in', self.exemployee_ids.ids)]
                return action_return
        if self.applied_by == 'my':
            month = self.month
            year = self.year
            record_data = self.env['hr.employee.clearance'].sudo().search([])
            applicant_id = []
            for rec in record_data:
                rec_month = rec_year = rec.create_date

                if str(rec_month.month) == month and rec_year.year == year:
                    applicant_id.append(rec.employee_id.id)
            domain = [('employee_id', 'in', applicant_id)]
            return {
                'type': 'ir.actions.act_window',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,form',
                'name': _('Clearance Report'),
                'res_model': 'hr.employee.clearance',
                'domain': domain,
                'target': 'main',
            }
        # if self.applied_by == 'year':
        #     year = self.year
        #     record_data = self.env['hr.employee.clearance'].sudo().search([])
        #     applicant_id = []
        #     for rec in record_data:
        #         rec_year = rec.create_date
        #         if rec_year.year == year:
        #             applicant_id.append(rec.employee_id.id)
        #     domain = [('employee_id', 'in', applicant_id)]
        #     return {
        #         'type': 'ir.actions.act_window',
        #         'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
        #         'view_mode': 'tree,form',
        #         'name': ('Clearance Report'),
        #         'res_model': 'hr.employee.clearance',
        #         'domain': domain,
        #         'target': 'main',
        #     }
        if self.applied_by == 'all':

            action = {
                'type': 'ir.actions.act_window',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,form',
                'name': _('Clearance Report'),
                'res_model': 'hr.employee.clearance',
                'target': 'main',
            }
            if self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                    or self.env.user.has_group('kw_eos.group_kw_eos_report_manager') \
                    or self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance') \
                    or self.env.user.has_group('kw_onboarding.group_kw_onboarding_admin') \
                    or self.env.user.has_group('kw_onboarding.group_kw_onboarding_nsa'):
                action['domain'] = []
            if self.env.user.has_group('kw_employee.group_hr_ra') \
                    and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                    and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager') \
                    and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance') \
                    and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_admin') \
                    and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_nsa') \
                    and not self.env.user.has_group('kw_wfh.group_hr_hod'):
                action['domain'] = [('employee_id.parent_id.user_id', '=', self.env.user.id)]
            if self.env.user.has_group('kw_wfh.group_hr_hod') \
                    and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                    and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager'):
                action['domain'] = ['|', ('employee_id.parent_id.user_id', '=', self.env.user.id), (
                    'employee_id.department_id.manager_id.user_id', '=', self.env.user.employee_ids.user_id.id)]
            return action
