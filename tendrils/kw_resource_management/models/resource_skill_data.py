# -*- coding: utf-8 -*-
from odoo import fields, models,api


class ResourceSkillData(models.Model):
    _name = 'resource_skill_data'
    _description = 'Resource Wise Skill'
    
    
    def get_emp_code(self):
        for rec in self:
            rec.emp_code = rec.employee_id.emp_code
            rec.emp_designation = rec.employee_id.job_id.name
            rec.emp_location = rec.employee_id.job_branch_id.alias
            rec.active = rec.employee_id.active
                


    employee_id = fields.Many2one('hr.employee',string='Resource')
    emp_code = fields.Char(string='Employee Code',compute = 'get_emp_code')
    emp_designation = fields.Char(string="Designation",compute = 'get_emp_data')
    emp_location = fields.Char(string='Location',compute = 'get_emp_data')
    primary_skill_id = fields.Many2one('kw_skill_master', string='Primary Skill')
    secondary_skill_id = fields.Many2one('kw_skill_master',string='Secondary Skill' )
    tertial_skill_id = fields.Many2one('kw_skill_master',string='Tertiarry Skill')
    active=fields.Boolean(string="Active",compute = 'get_emp_data')
    
            
    def update_emp_skill_on_resource_skill(self):
        resource_skill_data = self.env['resource_skill_data'].sudo().search([])
        temp_query = "select hr.id,hr.primary_skill_id from hr_employee hr join hr_department  \
                                         hrd on hrd.id= hr.department_id where hr.active=true and hrd.code='BSS' \
                                         and hr.primary_skill_id is not null AND hr.employement_type not in (SELECT id FROM kwemp_employment_type where code = 'O')"
        self._cr.execute(temp_query)
        employees = self._cr.dictfetchall()
        query=''
        for emp in employees:
            employee_id = emp['id']
            primary_skill_id= emp['primary_skill_id'] if emp['primary_skill_id'] != None else 0
            filter_resource = resource_skill_data.filtered(lambda x : x.employee_id.id == employee_id)
            if not filter_resource:
                query += f"insert into resource_skill_data (employee_id,primary_skill_id) values({employee_id},{primary_skill_id});"
                
        self.env.cr.execute(query)
            