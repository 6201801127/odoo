from odoo import models, fields, api
from odoo import tools


class SbuProjectWiseHeadCount(models.Model):
    _name = "sbu_project_wise_head_count"
    _description = "SBU & Project wise Head count report"
    _auto = False
    
   
    sbu_name = fields.Char(string="SBU")
    project_id = fields.Many2one('project.project')
    designation_id = fields.Many2one('hr.job', string='Designation')
    head_count = fields.Char(string = "Head Count")
    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
             select
                row_number() OVER () as id,
            --     (select sbu_master from kw_sbu_master where id = a.sbu_id and type = 'sbu') as sbu_name,
                (select name from kw_sbu_master where id = hr.sbu_master_id and type = 'sbu') as sbu_name,
                a.id as project_id,
                (select job_id from hr_employee where id = b.emp_id) as designation_id,
                count(b.emp_id) as head_count
            from
                project_project a
            left join
                kw_project_resource_tagging b on a.id = b.project_id	
            left join
                hr_employee hr on hr.id = a.emp_id 
            where
                a.active = true
                and b.active = true
                and hr.sbu_master_id in (select id from kw_sbu_master where type = 'sbu')
            group by
                sbu_name, (select job_id from hr_employee where id = b.emp_id), a.name ,a.id
        )"""
        self.env.cr.execute(query)
        
        
    def get_project_emp_details(self):
        view_id = self.env.ref("kw_resource_management.sbu_project_wise_head_count_emp_details_tree").id
        action = {
            'name': 'Employee Details',
            'type': 'ir.actions.act_window',
            'res_model': 'sbu_project_wise_get_emp_details',
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'self',
            'domain': [('project_id', '=',self.project_id.id ),('designation_id','=',self.designation_id.id)]
        }
        return action
        