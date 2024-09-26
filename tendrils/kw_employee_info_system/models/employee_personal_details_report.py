from odoo import fields, models, api
from odoo import tools


class EmployeePersonalDetails(models.Model):
    _name = "employee_personal_details"
    _description = "Report for Employee Personal Details"
    _auto = False
    _order = "emp_name asc"

    emp_name = fields.Char(string="Employee Name")
    department_id = fields.Many2one("hr.department", string="Department")
    job_id = fields.Many2one("hr.job", string="Designation")
    emp_code = fields.Char(string="Employee Code")
    father_name = fields.Char(string="Father")
    father_dob = fields.Date(string="Father DOB")
    mother_name = fields.Char(string="Mother")
    mother_dob = fields.Date(string="Mother DOB")
    enable_epf = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="EPF")
    esi_applicable = fields.Boolean(string='ESI APPLICABLE')
    marital_sts = fields.Many2one('kwemp_maritial_master', string='Marital Status')
    birthday = fields.Date("Date of Birth")
    date_of_joining = fields.Char(string="Joining Date")
    mobile_phone = fields.Char(string="Contact Number")
    gender = fields.Char(string="Gender")
    adhara_number = fields.Char(string="Adhara Number")
    salary_account = fields.Char(string="Salary Account")
    ifsc_code = fields.Char(string="IFSC Code")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
            with father as (select name, date_of_birth, emp_id from kwemp_family_info 
                where relationship_id =(select id from kwmaster_relationship_name where name = 'Father')),
            mother as (select name, date_of_birth, emp_id from kwemp_family_info 
                where relationship_id =(select id from kwmaster_relationship_name where name = 'Mother'))
                
            SELECT 
            a.id AS id,
            a.department_id AS department_id,
            a.job_id AS job_id,
            a.emp_code AS emp_code,
            a.name AS emp_name,
            a.birthday AS birthday,
            a.date_of_joining AS date_of_joining,
            a.mobile_phone AS mobile_phone,
            a.enable_epf AS enable_epf,
            a.esi_applicable AS esi_applicable,
            a.gender AS gender,
            a.marital_sts AS marital_sts, 
            b.doc_number  AS adhara_number,
            a.personal_bank_account AS salary_account,
			a.personal_bank_ifsc AS ifsc_code ,          
            father.name AS father_name,
            father.date_of_birth AS father_dob,
            mother.name AS mother_name,
            mother.date_of_birth AS mother_dob
            FROM hr_employee AS a
            left join father  on a.id=father.emp_id
            left join mother  on a.id=mother.emp_id
            left join kwemp_identity_docs as b
			on a.id = b.emp_id and b.name='5'
            where a.active=true            
        )"""
        self.env.cr.execute(query)
