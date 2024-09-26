# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, datetime
from bs4 import BeautifulSoup 



class kw_emp_cv_info(models.Model):
    _name = 'kw_emp_profile_cv_info'
    _description = "CV information of the employees."
    _rec_name = 'emp_id'

    project_of = fields.Selection(string="Project Of", selection=[('csm', 'CSM'), ('others', 'Others')], default='csm')
    project_id = fields.Many2one('crm.lead', string="Project Name", )
    project_name = fields.Char(string='Project / Activity')
    location = fields.Char(string='Location')
    start_month_year = fields.Date(string='Start Month & Year')
    end_month_year = fields.Date(string='End Month & Year')
    project_feature = fields.Html(string='Main Project Feature')
    project_feature_text = fields.Char(string='Main Project Feature',compute="_compute_responsibility_activity_text")
    
    role = fields.Text(string='Roles')
    responsibility_activity = fields.Html(string='Responsibilities & Activities')
    responsibility_activity_text = fields.Text(string='Responsibilities & Activities',compute="_compute_responsibility_activity_text")
    emp_id = fields.Many2one('kw_emp_profile')
    emp_cv_id = fields.Many2one('kw_emp_cv_profile')
    emp_cv_info_id = fields.Many2one('kw_emp_cv_info')
    client_name = fields.Char(string='Client Name')
    compute_project = fields.Char(string="Project", compute='_get_project_name')
    organization_id = fields.Many2one('kwemp_work_experience', string='Organization Name')
    activity = fields.Selection(string="Project / Activity", selection=[('project', 'Project'), ('others', 'Others')],
                                default='project')
    other_activity = fields.Text(string="Other Activity")
    emp_project_id = fields.Many2one('project.project', 'Project Name')
    
    
    @api.depends('responsibility_activity')
    def _compute_responsibility_activity_text(self):
        for record in self:
            if record.responsibility_activity:
                # Strip HTML tags
                soup = BeautifulSoup(record.responsibility_activity, 'html.parser')
                record.responsibility_activity_text = soup.get_text()
            if record.project_feature:
                soup = BeautifulSoup(record.project_feature, 'html.parser')
                record.project_feature_text = soup.get_text()
            else:
                record.responsibility_activity_text = ''
                record.project_feature_text = ''

    @api.onchange('project_of')
    def onchange_values(self):
        for rec in self:
            if rec.project_of == 'csm':
                rec.client_name = False
                rec.project_name = False
                rec.organization_id = False
            else:
                rec.emp_project_id = False
                # rec.activity = False
                rec.other_activity = False

    @api.onchange('organization_id')
    def get_org(self):
        work_rec = []
        profile_data = self.env['kw_emp_profile'].sudo().search([('id', '=', int(self.env.context.get('current_id')))])
        for record in profile_data:
            if record.emp_id.work_experience_ids:
                for rec in record.emp_id.work_experience_ids:
                    work_rec.append(rec.name)
        return {'domain': {'organization_id': [('name', 'in', work_rec)]}}

    def _get_project_name(self):
        for record in self:
            if record.project_of == 'csm':
                if record.emp_project_id.name:
                    record.compute_project = record.emp_project_id.name
                else:
                    record.compute_project = record.other_activity
            else:
                record.compute_project = record.project_name

    @api.onchange('start_month_year', 'end_month_year')
    def onchange_start_month_year(self):
        current_date = str(datetime.now().date())
        work_effective_from = []
        work_effective_to = []
        for record in self:
            if record.start_month_year:
                if record.project_of == 'csm':
                    # if str(record.start_month_year) < str(record.emp_id.date_of_joining):
                    #     return {'warning': {
                    #     'title': ('Validation Error'),
                    #     'message': (
                    #         'The start month & year of CV info should be greater than date of joining.')
                    #     }}
                    if str(record.start_month_year) >= current_date:
                        return {'warning': {
                            'title': _('Validation Error'),
                            'message': _('The start month & year of CV info should be less than current date.')
                        }}
                    if record.end_month_year:
                        if str(record.end_month_year) <= str(record.start_month_year):
                            return {'warning': {
                                'title': _('Validation Error'),
                                'message': (
                                    'The end month & year should be greater than  start month & year.')
                            }}
                        if str(record.end_month_year) > current_date:
                            return {'warning': {
                                'title': _('Validation Error'),
                                'message': _('The end month & year of CV info should not be greater than current date.')
                            }}
                else:
                    for value in record.organization_id:
                        work_effective_from.append(value.effective_from)
                        work_effective_to.append(value.effective_to)
                    for res in work_effective_from:
                        if record.start_month_year:
                            if str(res) > str(record.start_month_year):
                                return {'warning': {
                                    'title': _('Validation Error'),
                                    'message': _('The start month & year of CV info should be less than effective from date of work experience.')
                                }}
                    for result in work_effective_to:
                        if record.end_month_year:
                            if str(result) < str(record.end_month_year):
                                return {'warning': {
                                    'title': _('Validation Error'),
                                    'message': _('The end month & year of CV info should be less than effective to date of work experience.')
                                }}
                            if record.start_month_year:
                                if str(record.end_month_year) <= str(record.start_month_year):
                                    return {'warning': {
                                        'title': _('Validation Error'),
                                        'message': _('The end month & year should be greater than  start month & year.')
                                    }}



class KwEmpCVInfoQuery(models.Model):
    _name = 'kw_emp_cv_info_report'
    _description = "Query Model for Employee CV Information"
    _auto = False 

    employee_id = fields.Many2one('hr.employee')
    cv_count = fields.Integer('CV Info' )
    department_id = fields.Many2one('hr.department')
    division = fields.Many2one('hr.department')
    name = fields.Char('Name')
    emp_code = fields.Char('Code')
    sbu_master_id = fields.Many2one('kw_sbu_master')
    parent_id = fields.Many2one('hr.employee')
    pending_at = fields.Char(compute='_compute_pending_at')
    cv_info = fields.Char(compute='_compute_cv_count')
    
    job_id = fields.Many2one('hr.job')
    
    @api.depends('cv_count')
    def _compute_cv_count(self):
        for rec in self:
            if rec.cv_count == 1:
                rec.cv_info = f'{rec.cv_count} record present.'
            elif rec.cv_count == 0:
                rec.cv_info = f'-NA-'
            else:
                rec.cv_info = f'{rec.cv_count} records present.'

    @api.depends('employee_id')
    def _compute_pending_at(self):
        above_m8_grade = {'M8', 'M9', 'M10', 'E1', 'E2', 'E3', 'E4', 'E5'}
        profile_ids = self.env['kw_emp_profile'].sudo().search([('cv_sts', '=', True)]).mapped('emp_id.id')
        
        for rec in self:
            if rec.employee_id.id in profile_ids:
                new_data = self.env['kw_emp_cv_profile'].sudo().search([
                    ('emp_cv_prfl_id.emp_id', '=', rec.employee_id.id),
                    ('cv_info_boolean', '=', True),
                    ('state', '=', 'pending')
                ])
                if new_data:
                    if rec.employee_id.grade.name in above_m8_grade:
                        rec.pending_at = rec.employee_id.parent_id.name
                    else:
                        rec.pending_at = self.check_higher_authority(rec.employee_id, above_m8_grade)


    def check_higher_authority(self, employee_id, above_m8_grade):
        current_employee = employee_id.parent_id
        while current_employee:
            if current_employee.grade.name in above_m8_grade:
                if current_employee.user_id.id == self.env.uid:
                    return current_employee.name
                return current_employee.name
            current_employee = current_employee.parent_id
        return employee_id.parent_id.name

        
    def action_show_cv(self):
        tree_view_id = self.env.ref('kw_emp_profile.kw_emp_profile_cv_info_view_tree').id
        form_view_id = self.env.ref('kw_emp_profile.kw_emp_profile_cv_info_view_form').id
        profile = self.env['kw_emp_profile'].sudo().search([('emp_id','=',self.employee_id.id)],limit=1)
        cv_profile = self.env['kw_emp_profile_cv_info'].sudo().search([('emp_id','=',profile.id)])
        action = {
            'name':f'{self.employee_id.name}',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'res_model': 'kw_emp_profile_cv_info',
            'context': {'create':False,'edit': False,'delete':False},
            'domain': [('id','in',cv_profile.ids)],
            'target': 'self',
        }
        return action
        
        

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        employee = self.env.user.employee_ids
        employee_id = employee.id
        inc = set()

        # Own records access (for regular employees)
        if employee_id:
            inc.add(employee_id)

        above_m8_grade = ('M8', 'M9', 'M10', 'E1', 'E2', 'E3', 'E4', 'E5')
        
        # Create a parameterized query for the higher grades
        query_higher_grade = """
            SELECT e.id 
            FROM hr_employee e
            JOIN kwemp_grade_master g ON g.id = e.grade
            WHERE e.active = true AND g.name IN %s
            AND e.parent_id = %s 
        """
        # Convert the list to a tuple and use it in the query
        self._cr.execute(query_higher_grade, (above_m8_grade, employee_id))
        inc.update(rec[0] for rec in self._cr.fetchall())
        
        
       
        if self.env.user.employee_ids.grade.name in above_m8_grade:
            emps = self.env['hr.employee'].sudo().search([('id','child_of',self.env.user.employee_ids.ids)])
            if emps:
                if emps:
                    inc.update(emps.ids)
                
        # Update search arguments
        if inc:
            args.append(('id', 'in', list(inc)))
        return super()._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)


    
    
    @api.model_cr
    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW kw_emp_cv_info_report AS (
            SELECT  e.id AS id,
                COUNT(c.id) AS cv_count,
                e.id AS employee_id,
                e.department_id,
				e.division,
				e.name,
				e.emp_code,
                e.sbu_master_id,
                e.parent_id,
                e.job_id
            FROM
            hr_employee e 
            LEFT JOIN kw_emp_profile p ON p.emp_id = e.id
            LEFT JOIN kw_emp_profile_cv_info c ON p.id = c.emp_id
            WHERE
                e.active = TRUE
            GROUP BY
                e.id
            )
        """)

