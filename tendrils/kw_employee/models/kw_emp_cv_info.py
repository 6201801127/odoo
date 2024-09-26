# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, datetime
from bs4 import BeautifulSoup 


class kw_emp_cv_info(models.Model):
    _name = 'kw_emp_cv_info'
    _description = "CV information of the employees."

    project_of = fields.Selection(string="Project Of", selection=[('csm', 'CSM'), ('others', 'Others')], default='csm')
    # project_id = fields.Many2one('crm.lead', string="Project Name",)
    project_name = fields.Char(string='Project / Activity')
    location = fields.Char(string='Location')
    start_month_year = fields.Date(string='Start Month & Year')
    end_month_year = fields.Date(string='End Month & Year')
    project_feature = fields.Html(string='Main Project Feature')
    role = fields.Text(string='Roles')
    responsibility_activity = fields.Html(string='Responsibilities & Activities')
    emp_id = fields.Many2one('hr.employee')
    client_name = fields.Char(string='Client Name')
    compute_project = fields.Char(compute='_get_project_name')
    organization_id = fields.Many2one('kwemp_work_experience',string='Organization Name')
    activity = fields.Selection(string="Project / Activity", selection=[('project', 'Project'), ('others', 'Others')],default='project')
    other_activity = fields.Text(string="Project Name")
    emp_project_id = fields.Many2one('project.project', 'Project Name')
    kw_id = fields.Integer('KW ID')
    project_feature_text = fields.Char(string='Main Project Feature',compute="_compute_responsibility_activity_text")

    responsibility_activity_text = fields.Text(string='Responsibilities & Activities',compute="_compute_responsibility_activity_text")
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
                # rec.project_id = False
                rec.emp_project_id = False
                rec.other_activity = False

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
                            'message': (
                                'The start month & year of CV info should be less than current date.')
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
                                'message': (
                                    'The end month & year of CV info should not be greater than current date.')
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
                                    'message': (
                                        'The start month & year of CV info should be less than effective from date of work experience.')
                                }}
                    for result in work_effective_to:
                        if record.end_month_year:
                            if str(result) < str(record.end_month_year):
                                return {'warning': {
                                        'title': _('Validation Error'),
                                        'message': (
                                            'The end month & year of CV info should be less than effective to date of work experience.')
                                        }}
                            if record.start_month_year:
                                if str(record.end_month_year) <= str(record.start_month_year):
                                    return {'warning': {
                                        'title': _('Validation Error'),
                                        'message': (
                                            'The end month & year should be greater than  start month & year.')
                                    }}

    @api.onchange('organization_id')
    def get_org(self):
        return {'domain': {'organization_id': [('emp_id', '=', int(self.env.context.get('current_id')))]}}

    def _get_project_name(self):
        for record in self:
            if record.project_of == 'csm':
                if record.emp_project_id.name:
                    record.compute_project = record.emp_project_id.name
                else:
                    record.compute_project = record.other_activity
            else:
                record.compute_project = record.project_name

    # @api.constrains('end_month_year', 'start_month_year')
    def validate_effective_date(self):
        current_date = str(datetime.now().date())
        work_effective_from = []
        work_effective_to = []
        for record in self:
            if record.project_of == "csm":
                # if str(record.start_month_year) < str(record.emp_id.date_of_joining):
                #     raise ValidationError("The start month & year of CV info should be less than date of joining.")
                if str(record.start_month_year) >= current_date:
                    raise ValidationError("The start month & year of CV info should be less than current date.")
                if str(record.end_month_year) <= str(record.start_month_year):
                    raise ValidationError("The end month & year should be greater than  start month & year.")
            else:
                for rec in record.organization_id:
                    work_effective_from.append(rec.effective_from)
                    work_effective_to.append(rec.effective_to)
                    for res in work_effective_from:
                        if str(res) > str(record.start_month_year):
                            raise ValidationError(
                                "The start month & year of CV info should be less than effective from date of work experience.")
                    for result in work_effective_to:
                        if str(result) < str(self.end_month_year):
                            raise ValidationError(
                                "The end month & year of CV info should be greater than effective to date of work experience.")
                        if str(record.end_month_year) <= str(record.start_month_year):
                            raise ValidationError("The end month & year should be greater than  start month & year.")
