import string
from urllib3 import Retry
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
from dateutil import relativedelta
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT


class Employee(models.Model):
    _inherit = "hr.employee"

    edu_qualification = fields.Char(string='Educational Qualification', compute='_get_filtered_employees')
    certification = fields.Char(string='Training and Certification', compute='_get_filtered_employees', store=True)
    address = fields.Char(string="Present Address", compute='compute_address')
    project_name = fields.Char(string="Project Name", compute='get_project_name')
    total_experience_display_abbr = fields.Float(string="Total Exp.(yrs)")
    csm_experience_display_abbr = fields.Float(string="CSM Exp.(yrs)")
    previous_company_experience_display_abbr = fields.Float(string="Previous Exp.(yrs)")
    previous_company_display = fields.Char(string="Previous Company", compute='_get_filtered_employees')
    active_display = fields.Char(string="Employment Status", compute='_get_filtered_employees')
    budget_effective_from = fields.Date(string='Effective From')

    @api.multi
    def button_budget_settings(self):
        form_view_id = self.env.ref("kw_employee_info_system.kw_employee_budget_settings_tree_view").id
        return {
                'name': _('Budget Settings'),
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'hr_employee_resource_budget_settings',
                'view_id': form_view_id,
                'type': 'ir.actions.act_window',
                'domain': [('employee_id', '=', self.id)],
                }

    @api.depends('name')
    def _get_filtered_employees(self):
        # countries_list, language_list, membership_list, education_list = [], [], [], []
        # professional_list, tc_list, skill_list, technical_skill_list = [], [], [], []
        education_list = []
        passout_year_list = []
        emp_company_list = []

        for employee in self:
            emp_company_list.clear()
            employee.active_display = 'Active' if employee.active else 'Inactive'
            if employee.work_experience_ids:
                for record in employee.work_experience_ids:
                    # if employee.id == record.emp_id.id:
                    emp_company_list.append(record.name)
                employee.previous_company_display = ', '.join(set(emp_company_list))

            if employee.educational_details_ids:
                education_list.clear()
                passout_year_list.clear()
                for data in employee.educational_details_ids:
                    passout_year_list.append(data.passing_year)
                passout_year_list.sort()
                highest_quali = passout_year_list[-1]
                for value in employee.educational_details_ids:
                    if int(value.passing_year) == int(highest_quali) and value.course_type == '1':
                        education_list.append(value.stream_id.name)
                    if value.course_type == '2':
                        # print(data.stream_id.name)
                        education_list.append(value.stream_id.name)
                employee.edu_qualification = ','.join(education_list)
                # print('edu_qualification========',edu_qualification)

            # if employee.educational_details_ids:
            # education_list.clear()
            # tc_list.clear()
            # professional_list.clear()
            # skill_list.clear()
            # for data in  employee.educational_details_ids:
            # stream_name = data.stream_id.name.lower()
        #     if employee.id == data.emp_id.id and data.course_type == '1' and '10th' not in stream_name and '+2' not in stream_name:
        #      education_list += [data.stream_id.name]
        #     if employee.id == data.emp_id.id and data.course_type == '2':

        #         professional_list += [data.stream_id.name]
        #     if employee.id == data.emp_id.id and data.course_type == '3':
        #      education_list += [data.stream_id.name]
        #     skill_list += [data.stream_id.name]
        # print("education list^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^",education_list)

        # print('111111111')
        # tc_list += [data.stream_id.name]
        # print('education_list >> ', data.emp_id, ' >> ', tc_list)
        # employee.edu_qualification = ', '.join(education_list)
        # employee.certification = ', '.join(set(tc_list))
        # print(employee.certification)
        # employee.pro_qualification = ', '.join(set(professional_list))
        # employee.tech_skills = ', '.join(set(skill_list))
        # employee.technical_skills = ', '.join(set(technical_skill_list))

    @api.depends('present_addr_street2', 'present_addr_country_id', 'present_addr_city', 'present_addr_state_id',
                 'present_addr_zip')
    def compute_address(self):
        for rec in self:
            address = []
            if rec.present_addr_street:
                address.append(rec.present_addr_street)
            if rec.present_addr_street2:
                address.append(rec.present_addr_street2)
            if rec.present_addr_country_id.name:
                address.append(rec.present_addr_country_id.name)
            if rec.present_addr_city:
                address.append(rec.present_addr_city)
            if rec.present_addr_state_id.name:
                address.append(rec.present_addr_state_id.name)
            if rec.present_addr_zip:
                address.append(rec.present_addr_zip)
            rec.address = ', '.join(address)

    @api.depends('name')
    def get_project_name(self):
        project_resource = self.env['kw_project_resource_tagging'].sudo().search([])
        for rec in self:
            for i in project_resource:
                if rec.id == i.emp_id.id:
                    rec.project_name = i.project_id.name
    
    @api.model
    def create(self, vals):
        res = super(Employee, self).create(vals)
        if res.emp_role and res.emp_category and res.date_of_joining:
            query = f"""INSERT INTO hr_employee_resource_budget_settings (employee_id, emp_role, emp_category, 
            budget_effective_from) VALUES ({res.id},{res.emp_role.id},{res.emp_category.id},'{res.date_of_joining}');"""
            self._cr.execute(query)
        return res

    @api.multi
    def write(self, vals):
        if ('emp_role' in vals or self.emp_role) and 'emp_category' in vals and 'budget_effective_from' in vals:
            log_record = self.env['hr_employee_resource_budget_settings'].sudo().search([('employee_id', '=', self.id)])
            budget_effective_from_o = datetime.strptime(vals['budget_effective_from'], DEFAULT_SERVER_DATE_FORMAT).date()

            # if employee has no log, create 1st record and update the new budget settings
            if self.emp_role and self.emp_category and not log_record.exists():
                query = f"""INSERT INTO hr_employee_resource_budget_settings (employee_id, emp_role, emp_category, 
                budget_effective_from, effective_to) VALUES ({self.id},{self.emp_role.id},{self.emp_category.id},
                '{self.date_of_joining}', '{vals['budget_effective_from']}');"""
                self._cr.execute(query)
            elif log_record.exists():
                record_to_update = log_record.filtered(lambda x: x.effective_to is False)
                if record_to_update.budget_effective_from >= budget_effective_from_o:
                    raise ValidationError(f"Please select effective from date after {record_to_update.budget_effective_from.strftime('%d-%b-%Y')}.")
                
                if record_to_update:
                    update_record = f"""Update hr_employee_resource_budget_settings set 
                    effective_to='{vals['budget_effective_from']}' where id = '{record_to_update.id}';"""
                    self._cr.execute(update_record)

            emp_role = vals['emp_role'] if 'emp_role' in vals else self.emp_role.id
            emp_category = vals['emp_category']
            budget_effective_from = vals['budget_effective_from']

            query = f"""INSERT INTO hr_employee_resource_budget_settings (employee_id, emp_role, emp_category, 
            budget_effective_from) VALUES ({self.id},{emp_role},{emp_category},'{budget_effective_from}');"""
            self._cr.execute(query)
            
        if 'budget_effective_from' in vals:
            del vals['budget_effective_from']

        res = super(Employee, self).write(vals)
        return res

    @api.model
    def update_experience(self):
        csm_experience_sql = """update hr_employee set csm_experience_display_abbr=concat(
div((extract('years' from AGE(CURRENT_DATE, date_of_joining)) * 12 + extract('months' from AGE(CURRENT_DATE, date_of_joining)))::numeric, 12)::varchar,
'.',
lpad(mod((extract('years' from AGE(CURRENT_DATE, date_of_joining)) * 12 + extract('months' from AGE(CURRENT_DATE, date_of_joining)))::numeric, 12)::varchar, 2, '0') 
)::double precision 
where date_of_joining is not null and (csm_experience_display_abbr is null or csm_experience_display_abbr=0);
        """
        self._cr.execute(csm_experience_sql)

        previous_company_experience_sql = """update hr_employee set previous_company_experience_display_abbr=(select 
concat(
div(sum(extract('years' from AGE(effective_to, budget_effective_from)) * 12 + extract('months' from AGE(effective_to, budget_effective_from)))::numeric, 12),
'.',
lpad(mod(sum(extract('years' from AGE(effective_to, budget_effective_from)) * 12 + extract('months' from AGE(effective_to, budget_effective_from)))::numeric, 12)::varchar, 2, '0') 
)::float as total_experience
from kwemp_work_experience x 
where x.emp_id=hr_employee.id group by emp_id
) 	
where (hr_employee.previous_company_experience_display_abbr is null or hr_employee.previous_company_experience_display_abbr=0);"""
        self._cr.execute(previous_company_experience_sql)

        total_experience_sql = """update hr_employee set total_experience_display_abbr=concat(
div((floor(coalesce(csm_experience_display_abbr,0) + coalesce(previous_company_experience_display_abbr, 0))*12 + floor(((coalesce(csm_experience_display_abbr,0) + coalesce(previous_company_experience_display_abbr, 0))-floor(coalesce(csm_experience_display_abbr,0) + coalesce(previous_company_experience_display_abbr, 0)))*100))::numeric, 12)::varchar,
'.',
lpad(mod((floor(coalesce(csm_experience_display_abbr,0) + coalesce(previous_company_experience_display_abbr, 0))*12 + round(((coalesce(csm_experience_display_abbr,0) + coalesce(previous_company_experience_display_abbr, 0))-floor(coalesce(csm_experience_display_abbr,0) + coalesce(previous_company_experience_display_abbr, 0)))*100))::numeric, 12)::varchar, 2, '0')::varchar 
)::float8
where csm_experience_display_abbr is not null or previous_company_experience_display_abbr is not null;"""
        self._cr.execute(total_experience_sql)

        certification = """update hr_employee set certification = (select string_agg(s.name,', ') from kwmaster_stream_name s 
join kwemp_educational_qualification e on  s.id = e.stream_id 
join hr_employee hr on hr.id = e.emp_id 
where hr.id = hr_employee.id and e.course_type = '3') """
        self._cr.execute(certification)

#         edu_qualification = """update hr_employee set edu_qualification = (select string_agg(s.name,', ') from kwmaster_stream_name s 
# join kwemp_educational_qualification e on  s.id = e.stream_id 
# join hr_employee hr on hr.id = e.emp_id 
# where hr.id = hr_employee.id and e.course_type = '1') """
#         self._cr.execute(edu_qualification)




