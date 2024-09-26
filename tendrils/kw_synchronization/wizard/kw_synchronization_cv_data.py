import json
import requests
import calendar
# import datetime
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api
import base64
import urllib.request


class CVData(models.TransientModel):
    _name = "cv_data_sync_data_v5"
    _description = "Fetch CV data from v5"

    employee_ids = fields.Many2many(comodel_name='hr.employee', relation='cv_sync_employee_rel', column1='rec_id',
                                    column2='emp_id', string="Employees")
    page_no = fields.Integer(string="Page No", default=1)
    page_size = fields.Integer(string="Page Size", default=1)

    @api.multi
    def button_get_cv_data(self):
        # Fetch the url
        parameter_url = self.env['ir.config_parameter'].sudo().get_param('kwantify_cv_data_url')
        if parameter_url:
            header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            for emp in self.employee_ids:
                user_id = emp.kw_id if emp and emp.kw_id else 0
                employee_id = emp.id if emp else 0
                # parameters for url
                education_data_dict = {"UserID": str(user_id),
                                       "PageNo": str(self.page_no),
                                       "PageSize": str(self.page_size)}
                resp = requests.post(parameter_url, headers=header, data=json.dumps(education_data_dict))
                json_data = resp.json()
                if json_data:
                    for cv_data in json_data:
                        # projectof
                        project_of = ''
                        if cv_data.get('INT_PROJECTOF') == '1':
                            project_of = 'others'
                        elif cv_data.get('INT_PROJECTOF') == '0':
                            project_of = 'csm'

                        # project
                        project_id = cv_data.get('IntProjectID')
                        project_obj = False
                        if project_id != '0':
                            project_obj = self.env['project.project'].search([('kw_id', '=', project_id)])

                        # start and end date
                        start_datetime_object = datetime.strptime(cv_data.get('VCH_START_MONTH'), "%B")
                        start_month_number = start_datetime_object.month
                        start_date = datetime.now().replace(day=1, month=start_month_number, year=int(cv_data.get('INT_START_YEAR'))).date()

                        end_datetime_object = datetime.strptime(cv_data.get('VCH_END_MONTH'), "%B") + relativedelta(month=1)
                        end_month_number = end_datetime_object.month
                        end_date = datetime.now().replace(day=1, month=end_month_number,
                                                          year=int(cv_data.get('INT_END_YEAR'))).date() - timedelta(days=1)

                        cv_data_dict = {}
                        if project_of == 'csm':
                            cv_record_csm = self.env['kw_emp_cv_info'].search([('emp_id', '=', emp.id),
                                                                               ('project_of', '=', project_of),
                                                                               ('emp_project_id', '=', project_obj.id),
                                                                               ('location', '=', cv_data.get('VCH_LOCATION'))], limit=1)
                            if cv_record_csm and not cv_record_csm.kw_id:
                                cv_record_csm.update({'kw_id': cv_data.get('INT_PID')})
                            elif not cv_record_csm:
                                cv_data_dict = {
                                    'emp_id': emp.id,
                                    'kw_id': cv_data.get('INT_PID'),
                                    'project_of': project_of,
                                    'activity': 'project',
                                    'emp_project_id': project_obj.id,
                                    'location': cv_data.get('VCH_LOCATION') or 'NA',
                                    'start_month_year': start_date,
                                    'end_month_year': end_date,
                                    'project_feature': cv_data.get('VCH_PROJECTDETAILS') or 'NA',
                                    'role': cv_data.get('VCH_ROLE') or 'NA',
                                    'responsibility_activity': cv_data.get('VCH_RESPONSE') or 'NA',
                                }
                        elif project_of == 'others':
                            if cv_data.get('ExpDetails')[0].get('A_Status') == "1":
                                work_exp = self.env['kwemp_work_experience'].search(
                                    [('name', '=', cv_data.get('ExpDetails')[0].get('Organisation_Name')),
                                     ('emp_id', '=', emp.id)], limit=1)

                                country = self.env['res.country'].search(
                                    [('kw_id', '=', cv_data.get('ExpDetails')[0].get('INT_COUNTRYID'))])
                                organization_type = self.env['kwemp_organization'].search(
                                    [('kw_id', '=', cv_data.get('ExpDetails')[0].get('INT_ORG_TYPE'))])
                                industry_type = self.env['kwemp_industry'].search(
                                    [('kw_id', '=', cv_data.get('ExpDetails')[0].get('INT_IND_TYPE'))])

                                if not work_exp:
                                    work_exp = self.env['kwemp_work_experience'].create({
                                        'emp_id': emp.id,
                                        'country_id': country.id or False,
                                        'name': cv_data.get('ExpDetails')[0].get('Organisation_Name'),
                                        'designation_name': cv_data.get('VCH_ROLE') or 'NA',
                                        'organization_type': organization_type.id or False,
                                        'industry_type': industry_type.id or False,
                                        'effective_from': datetime.strptime(
                                            cv_data.get('ExpDetails')[0].get('DTM_FROMDt').split()[0],
                                            '%m/%d/%Y').strftime("%d-%b-%Y"),
                                        'effective_to': datetime.strptime(
                                            cv_data.get('ExpDetails')[0].get('DTM_TODdtT').split()[0],
                                            '%m/%d/%Y').strftime("%d-%b-%Y"),
                                        'kw_id': cv_data.get('ExpDetails')[0].get('OrganisationID')
                                    })
                                cv_record_others = self.env['kw_emp_cv_info'].search([('emp_id', '=', emp.id),
                                                                                      ('project_of', '=', project_of),
                                                                                      ('project_name', '=',
                                                                                       cv_data.get('VCH_POJECTNAME_VALUE')),
                                                                                      ('location', '=',
                                                                                       cv_data.get('VCH_LOCATION'))],
                                                                                     limit=1)
                                if cv_record_others and not cv_record_others.kw_id:
                                    cv_record_others.update({'kw_id': cv_data.get('INT_PID')})
                                elif not cv_record_others:
                                    cv_data_dict = {
                                        'emp_id': emp.id,
                                        'kw_id': cv_data.get('INT_PID'),
                                        'project_of': project_of,
                                        'project_name': cv_data.get('VCH_POJECTNAME_VALUE') or '',
                                        'location': cv_data.get('VCH_LOCATION') or 'NA',
                                        'client_name': cv_data.get('VCH_CLIENTNAME') or 'NA',
                                        'organization_id': work_exp.id or False,
                                        'start_month_year': start_date,
                                        'end_month_year': end_date,
                                        'project_feature': cv_data.get('VCH_PROJECTDETAILS') or 'NA',
                                        'role': cv_data.get('VCH_ROLE') or 'NA',
                                        'responsibility_activity': cv_data.get('VCH_RESPONSE') or 'NA',
                                    }
                        if cv_data_dict:
                            record = self.env['kw_emp_cv_info'].create(cv_data_dict)
            self.env.user.notify_success("Employee data updated successfully")
