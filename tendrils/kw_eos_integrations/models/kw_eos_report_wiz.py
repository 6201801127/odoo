# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api
from datetime import datetime, date
from odoo.exceptions import ValidationError
import json
import requests
import calendar


def get_year_data():
    year_list = []
    # start_year = (date.today().year - (date.today().year - 2000))
    for i in range((date.today().year), 1998, -1):
        year_list.append((i, str(i)))
    return year_list


class KwEOSReportWizard(models.TransientModel):
    _name = 'kw_eos_report_wizard'
    _description = 'EOS Report'

    applied_by = fields.Selection([('all', 'All'),
                                   ('dt', 'Date wise'),
                                   ('my', 'Month & Year wise'),
                                   ('employee', 'Employee'),
                                   ('exemployee', 'Ex-employee')
                                   ], string="Applied By", default='all')
    
    report_state = fields.Selection([('Draft', 'Draft'),
                              ('Applied', 'Applied'),
                              ('Approved', 'Approved'),
                              ('Granted', 'Granted'),
                              ('Rejected', 'Rejected')],string='State',default='Applied')
    
    date_from = fields.Datetime('Date From', help="Choose a Starting date to get the salary advance at that date")
    date_to = fields.Datetime('Date To', help="Choose a Ending date to get the salary advance at that date")
    year = fields.Selection(get_year_data(), string='Year', default=date.today().year)
    month = fields.Selection([('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
                              ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'),
                              ('09', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December'), ],
                             string="Month")
    employee_ids = fields.Many2many('hr.employee', 'kw_eos_wiz_hr_employee_rel', 'eos_wiz_id',
                                    'employee_id', string="Employee")
    exemployee_ids = fields.Many2many('hr.employee', 'kw_eos_wiz_exhr_employee_rel', 'offboarding_wiz_id',
                                      'employee_id', string="Ex-employee", domain=[('active', '=', False)])
    reg_id = fields.Many2one('kw_resignation')

    @api.onchange('applied_by')
    def _get_employee(self):
        domain = []
        dm=False
        employee_data = False
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
                domain = [('parent_id.user_id', '=', self.env.user.employee_ids.user_id.id),('active', '=', True)]
            elif self.applied_by == 'exemployee':
                domain = [('parent_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                          ('active', '=', False)]
            employee_data = employees.with_context(active_test=False).search(domain).filtered(lambda x: x.id in eos_employee_list)
        elif self.env.user.has_group('kw_wfh.group_hr_hod') \
                and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager'):
            if self.applied_by == 'employee':
                domain = [('department_id.manager_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                          ('active', '=', True)]
            elif self.applied_by == 'exemployee':
                domain = [('department_id.manager_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                          ('active', '=', False)]
            employee_data = employees.with_context(active_test=False).search(domain).filtered(lambda x: x.id in eos_employee_list)
            
        elif self.env.user.has_group('kw_resource_management.group_sbu_representative') \
                and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                    and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager') \
                    and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance') \
                    and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_admin') \
                    and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_nsa') \
                    and not self.env.user.has_group('kw_wfh.group_hr_hod'):
            # print('333333333333333333333333333 of eossss')
            if self.applied_by == 'employee':
                domain = ['&', '|', ('id', '=', self.env.user.employee_ids.id),
                            ('sbu_master_id.representative_id.user_id','=',self.env.user.employee_ids.user_id.id),
                            ('active', '=', True)]
            elif self.applied_by == 'exemployee':
                domain = ['&', '|', ('id', '=', self.env.user.employee_ids.id),
                          ('sbu_master_id.representative_id.user_id','=',self.env.user.employee_ids.user_id.id),
                          ('active', '=', False)]
            employee_data = employees.with_context(active_test=False).search(domain).filtered(lambda x: x.id in eos_employee_list)
        else:
            if self.applied_by == 'employee':
                domain = [('active', '=', True)]
            elif self.applied_by == 'exemployee':
                domain = [('active', '=', False)]
            employee_data = employees.with_context(active_test=False).search(domain).filtered(lambda x: x.id in eos_employee_list)
        if self.applied_by == 'employee':
            dm = {'domain': {'employee_ids': [('id', 'in', employee_data.ids)]}}
        elif self.applied_by == 'exemployee':
            dm = {'domain': {'exemployee_ids': [('id', 'in', employee_data.ids)]}}        
        return dm

    def get_eos_report_data(self):
        self.ensure_one()
        if self.applied_by == 'dt':
            dt1 = self.date_from
            dt2 = self.date_to
            eos_data = self.env['kw_eos_checklist']
            record_data = eos_data.sudo().search([('create_date', '>=', dt1), ('create_date', '<=', dt2)])
            for rec in record_data:
                tree_view_id = self.env.ref('kw_eos_integrations.eos_view_report_2').id
                action = {
                    'type': 'ir.actions.act_window',
                    'name': 'EOS Report',
                    'views': [(tree_view_id, 'tree')],
                    'view_mode': 'tree,form',
                    'view_type': 'form',
                    'res_model': 'kw_eos_checklist',
                    'target': 'main',
                }

                if self.env.user.has_group('kw_employee.group_hr_ra') \
                        and not self.env.user.has_group('kw_wfh.group_hr_hod') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager') \
                        and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance') \
                        and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_admin') \
                        and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_nsa') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_officer') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_resource_head'):
                    # print("inside if of eos==================")

                    action['domain'] = ['&','&',('id', 'in', record_data.ids),('state','=',self.report_state),
                                        '|','|',('applicant_id', '=', self.env.user.employee_ids.id),
                                        ('applicant_id.parent_id.user_id', '=', self.env.user.employee_ids.user_id.id),('applicant_id.sbu_master_id.representative_id.user_id','=',self.env.user.employee_ids.user_id.id),
                                        ('offboarding_type', '!=', False)]
                    return action
                elif self.env.user.has_group('kw_wfh.group_hr_hod') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager'):
                    # print("inside elif of eos hod========================")
                    action['domain'] = ['&','&',('id', 'in', record_data.ids),('state','=',self.report_state),
                                        '|', ('applicant_id', '=', self.env.user.employee_ids.id), (
                                            'applicant_id.department_id.manager_id.user_id', '=',
                                            self.env.user.employee_ids.user_id.id), ('offboarding_type', '!=', False)]
                    return action
                
                elif self.env.user.has_group('kw_resource_management.group_sbu_representative') \
                        and not self.env.user.has_group('kw_wfh.group_hr_hod') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager') \
                        and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance') \
                        and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_admin') \
                        and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_nsa') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_officer') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_resource_head'):
                    # print("inside datewise of  representative eos========================")
                    action['domain'] = ['&','&',('id', 'in', record_data.ids),('state','=',self.report_state),
                                        '|', ('applicant_id', '=', self.env.user.employee_ids.id),('applicant_id.sbu_master_id.representative_id.user_id','=',self.env.user.employee_ids.user_id.id),('offboarding_type', '!=', False)]
                    return action
                else:
                    # print("inside else of eos==================================")
                    action['domain'] = [('create_date', '>=', dt1), ('create_date', '<=', dt2),
                                        ('offboarding_type', '!=', False),('state','=',self.report_state)]

                return action

        elif self.applied_by == 'my':
            cuur_year = self.year
            curr_month = int(self.month)
            num_days = calendar.monthrange(cuur_year, curr_month)
            lst_day = list(num_days)[1]
            first_day = date(cuur_year, curr_month, 1)
            last_day = date(cuur_year, curr_month, lst_day)
            record_data = self.env['kw_eos_checklist'].sudo().search([])
            for rec in record_data:
                tree_view_id = self.env.ref('kw_eos_integrations.eos_view_report_2').id
                action = {
                    'type': 'ir.actions.act_window',
                    'name': 'EOS Report',
                    'views': [(tree_view_id, 'tree')],
                    'view_mode': 'tree,form',
                    'view_type': 'form',
                    'res_model': 'kw_eos_checklist',
                    'target': 'main',
                }
                if self.env.user.has_group('kw_employee.group_hr_ra') \
                        and not self.env.user.has_group('kw_wfh.group_hr_hod') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager') \
                        and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance') \
                        and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_admin') \
                        and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_nsa') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_officer') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_resource_head'):
                    # print('inside ra of eos=================================')

                    action['domain'] = ['&', '&','&',('create_date', '>=', first_day), ('create_date', '<=', last_day),('state','=',self.report_state),
                                        '|','|',('applicant_id', '=', self.env.user.employee_ids.id),
                                        ('applicant_id.parent_id.user_id', '=', self.env.user.employee_ids.user_id.id),('applicant_id.sbu_master_id.representative_id.user_id','=',self.env.user.employee_ids.user_id.id),
                                        ('offboarding_type', '!=', False)]
                    return action
                elif self.env.user.has_group('kw_wfh.group_hr_hod') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager'):

                    action['domain'] = ['&', '&','&',('create_date', '>=', first_day), ('create_date', '<=', last_day),('state','=',self.report_state),
                                        '|', ('applicant_id', '=', self.env.user.employee_ids.id), (
                                            'applicant_id.department_id.manager_id.user_id', '=',
                                            self.env.user.employee_ids.user_id.id), ('offboarding_type', '!=', False)]
                    return action
                
                elif self.env.user.has_group('kw_resource_management.group_sbu_representative') \
                        and not self.env.user.has_group('kw_wfh.group_hr_hod') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager') \
                        and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance') \
                        and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_admin') \
                        and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_nsa') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_officer') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_resource_head'):
                    # print("inside month year of  representative eos========================")
                    action['domain'] = ['&', '&','&',('create_date', '>=', first_day), ('create_date', '<=', last_day),('state','=',self.report_state),
                                        '|', ('applicant_id', '=', self.env.user.employee_ids.id), ('applicant_id.sbu_master_id.representative_id.user_id','=',self.env.user.employee_ids.user_id.id),('offboarding_type', '!=', False)]
                    return action
                
                else:
                    action['domain'] = [('create_date', '>=', first_day), ('create_date', '<=', last_day),
                                        ('offboarding_type', '!=', False),('state','=',self.report_state),]
                    return action

        elif self.applied_by == 'employee' or self.applied_by == 'exemployee':
            record_data = self.env['kw_eos_checklist'].sudo().search([])
            for rec in record_data:
                tree_view_id = self.env.ref('kw_eos_integrations.eos_view_report_2').id
                action_return = {
                    'type': 'ir.actions.act_window',
                    'views': [(tree_view_id, 'tree')],
                    'view_mode': 'tree,form',
                    'view_type': 'form',
                    'name': 'EOS Report',
                    'res_model': 'kw_eos_checklist',
                    'target': 'main',
                }
                if self.applied_by == 'employee':
                    action_return['domain'] = [('applicant_id', 'in', self.employee_ids.ids), ('offboarding_type', '!=', False),('state','=',self.report_state),]
                if self.applied_by == 'exemployee':
                    action_return['domain'] = [('applicant_id', 'in', self.exemployee_ids.ids), ('offboarding_type', '!=', False),('state','=',self.report_state),]
                return action_return

        elif self.applied_by == 'all':
            emp_id = self.employee_ids
            record_data = self.env['kw_eos_checklist'].sudo().search([])
            for rec in record_data:
                tree_view_id = self.env.ref('kw_eos_integrations.eos_view_report_2').id
                action = {
                    'type': 'ir.actions.act_window',
                    'views': [(tree_view_id, 'tree')],
                    'view_mode': 'tree,form',
                    'view_type': 'form',
                    'name': 'EOS Report',
                    'res_model': 'kw_eos_checklist',
                    'target': 'main',
                    'context': {'disable_search': True},
                }
                if self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                        or self.env.user.has_group('kw_eos.group_kw_eos_report_manager') \
                        or self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance') \
                        or self.env.user.has_group('kw_onboarding.group_kw_onboarding_admin') \
                        or self.env.user.has_group('kw_onboarding.group_kw_onboarding_nsa'):
                    action['domain'] = [('state', '!=', 'Draft')]
                if self.env.user.has_group('kw_employee.group_hr_ra') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager') \
                        and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance') \
                        and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_admin') \
                        and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_nsa') \
                        and not self.env.user.has_group('kw_wfh.group_hr_hod'):
                    action['domain'] = [('applicant_id.parent_id.user_id', '=', self.env.user.id),
                                        ('state', '!=', 'Draft')]
                if self.env.user.has_group('kw_wfh.group_hr_hod') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                        and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager'):
                    action['domain'] = ['|',
                                        ('applicant_id.parent_id.user_id', '=', self.env.user.employee_ids.user_id.id),
                                        ('applicant_id.department_id.manager_id.user_id', '=',
                                         self.env.user.employee_ids.user_id.id)]
                if self.env.user.has_group('kw_resource_management.group_sbu_representative') \
                    and not self.env.user.has_group('kw_eos.group_kw_eos_manager') \
                    and not self.env.user.has_group('kw_eos.group_kw_eos_report_manager') \
                    and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_finance') \
                    and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_admin') \
                    and not self.env.user.has_group('kw_onboarding.group_kw_onboarding_nsa') \
                    and not self.env.user.has_group('kw_wfh.group_hr_hod'):
                    # print("inside allllll of  representative eos========================")
                    
                    action['domain'] = [('applicant_id.sbu_master_id.representative_id.user_id', '=', self.env.user.id)]
                return action
