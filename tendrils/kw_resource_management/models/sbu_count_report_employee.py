from odoo import models, fields, api
from odoo import tools


class SbuReportEmployee(models.Model):
    _name = "hr.employee.sbu.mapping.report"
    _description = "SBU count report employees"
    _auto = False
    _order = 'sequence asc'

    sbu_id = fields.Many2one('kw_sbu_master', string="SBU")
    sbu_name = fields.Char(string="SBU")
    sequence = fields.Integer(string="Sequence")
    representative_id = fields.Many2one('hr.employee', string='Representative')
    project_count = fields.Integer(string="Total Projects")
    pm_count = fields.Integer(string="Total PMs")
    team_member_count = fields.Integer(string="Team Members")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
        
with sbu_table as(
        SELECT row_number() over() AS id,
        sb.sequence as sequence, 
        sb.type as sbu_type,
		sb.id as sbu_id,
		sb.representative_id as representative_id, 
		sb.name as sbu_name,
		cl.id as project_id,
		pp.emp_id as project_manager,
		hr.id as employee_id
		FROM kw_sbu_master AS sb
		left join hr_employee As hr on sb.id = hr.sbu_master_id
		left join crm_lead AS cl on hr.emp_project_id = cl.id
		left join project_project AS pp on cl.id = pp.crm_id
		order by sequence asc
            )
                                
            select row_number() over() AS id, sbu_id,
            sequence,
            sbu_name, 
            representative_id, 
			count(distinct project_id) as project_count, 
            count(distinct project_manager) as pm_count, 
            count(employee_id) as team_member_count
            from sbu_table
            group by sbu_id,sbu_name,sequence, representative_id
            order by sequence asc
        )"""
        # print("tracker quey",query)
        self.env.cr.execute(query)

    def action_button_view_form(self):
        tree_view_id = self.env.ref('kw_resource_management.kw_sbu_report_list_tree').id
        return {
            'name': 'SBU Report',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'hr.employee.sbu.mapped.detail.report',
            'view_id': tree_view_id,
            'target': 'self',
            'domain': [('sbu_id', '=', self.sbu_id.id)],
            'context': {'edit': False, 'create': False, 'delete': False}
        }
