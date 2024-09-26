from odoo import models, fields, api
from odoo import tools


class TechnologyWiseResourceCount(models.Model):
    _name = "technology_wise_resource_count_report"
    _description = "Technnology wise resource count"
    _auto = False
    
    id =  fields.Integer(string="Sl No.")
    technology_id = fields.Many2one('kw_skill_master',string="Technology")
    # sbu_name = fields.Char(string="Emp SBU")
    team_lead_count = fields.Integer(string="TL")
    developer_count = fields.Integer(string="Developer")
    
    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
       SELECT row_number() over() AS id, 
		sm.id as technology_id,
		--hr.sbu_master_id as sbu_name,
  	--(select name from kw_sbu_master where id = hr.sbu_master_id) as sbu_name,
		count(distinct case when kcn.code = 'DEV' and hr.active=true then hr.id END) as developer_count,
		count(distinct case when kcn.code = 'TTL' and hr.active=true then hr.id END) as team_lead_count
		FROM kw_skill_master sm
		left join resource_skill_data rsd on rsd.primary_skill_id = sm.id
		join hr_employee hr on hr.id = rsd.employee_id
		join kwmaster_category_name kcn on kcn.id = hr.emp_category
		join hr_department as hrd on hrd.id= hr.department_id
        where hr.active =true and hrd.code='BSS' and hr.employement_type not in (SELECT id FROM kwemp_employment_type where code = 'O')
		group by sm.id
            )"""
        self.env.cr.execute(query)
        
    
    @api.multi
    def view_details_button(self):
        view_id = self.env.ref("kw_resource_management.technology_wise_report_tree").id
        dev_tl_category = self.env['kwmaster_category_name'].search([('code','in',['TTL','DEV'])])
        return {
            'name': 'Technology Report',
            'type': 'ir.actions.act_window',
            'res_model': 'technology_wise_resource',
            'view_id': view_id,
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'tree',
            'target': 'self',
            'domain': [('primary_skill_id', '=', self.technology_id.id),('emp_category','in', dev_tl_category.ids)]
        }
        