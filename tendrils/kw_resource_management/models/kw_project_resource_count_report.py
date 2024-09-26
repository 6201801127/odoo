from odoo import models, fields, api
from odoo import tools


class ProjectwiseresourceCount(models.Model):
    _name = "kw_project_resource_count_report"
    _description = "Project wise resource count"
    _auto = False
    
   
    order_oppurtinity = fields.Char(string="WO/OPP")
    project_name = fields.Char(string="Project Name")
    project_manager = fields.Char(string="Project Manager")
    project_manager_id = fields.Many2one('hr.employee', string="Project Manager")
    reviewer = fields.Many2one('hr.employee', string="Reviewer")
    team_lead_count = fields.Integer(string="TL")
    developer_count = fields.Integer(string="Developer")
    total_count = fields.Integer(string="Total")
    rsrc_dplmnt_count = fields.Integer(string="Resource Deployement")
    ba_count = fields.Integer(string="BA")
    pm_count = fields.Integer(string="PMG")
    sbu_name = fields.Char(string="Project SBU")
    id =  fields.Integer(string="Sl No.")
    horizontal_count = fields.Integer(string="Horizontal")
    sbu_id = fields.Many2one('hr.employee', string="SBU")
    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
select row_number() over(order by a.name) as id,(select code from crm_lead where id = a.crm_id)
			as order_oppurtinity,a.name as project_name,
            (select name from hr_employee where id = a.emp_id) as project_manager,
            (select id from hr_employee where id = a.emp_id) as project_manager_id,
            (select id from hr_employee where id = a.reviewer_id) as reviewer,
	        (select name from kw_sbu_master where id = a.sbu_id) as sbu_name,
            (select representative_id from kw_sbu_master where id = a.sbu_id) as sbu_id,
            --(select sbu_type from hr_employee where id = b.emp_id) as sbu_type,
			count(b.emp_id) as total_count,
            count(b.id)  FILTER (WHERE (select emp_category from hr_employee where id = b.emp_id) = (select id from kwmaster_category_name where code = 'TTL')) as team_lead_count,
	        count(b.emp_id) FILTER (WHERE (select emp_category from hr_employee where id = b.emp_id) = (select id from kwmaster_category_name where code = 'DEV') or (select emp_category from hr_employee where id = b.emp_id) = (select id from kwmaster_category_name where code = 'INN')) as developer_count,
            count(b.emp_id) FILTER (WHERE (select emp_category from hr_employee where id = b.emp_id) = (select id from kwmaster_category_name where code = 'BA')) as ba_count,
            count(b.emp_id) FILTER (WHERE (select emp_category from hr_employee where id = b.emp_id) = (select id from kwmaster_category_name where code = 'PM')) as pm_count,
			count(b.emp_id) FILTER (WHERE (select emp_role from hr_employee where id = b.emp_id) = (select id from kwmaster_role_name where code = 'R'))as rsrc_dplmnt_count,
            count(b.emp_id) FILTER (WHERE(select sbu_type from hr_employee where id=b.emp_id) = 'horizontal') as horizontal_count
            from project_project a 
            left join kw_project_resource_tagging b on a.id = b.project_id 
            where a.active = true and b.active=true group by a.name,a.crm_id,a.emp_id,a.reviewer_id,a.sbu_id
        )"""
        self.env.cr.execute(query)
        
    
    @api.multi
    def view_details_action_button(self):
        view_id = self.env.ref("kw_resource_management.Project_wise_resource_tree").id
        return {
            'name': 'Project Report',
            'type': 'ir.actions.act_window',
            'res_model': 'project_wise_resource',
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'tree',
            'target': 'self',
            'domain': [('project_name', '=', self.project_name)]
        }