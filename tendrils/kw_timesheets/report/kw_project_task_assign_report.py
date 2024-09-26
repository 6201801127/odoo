from odoo import models, fields, api, tools
from datetime import date


class ProjectTaskAssign(models.Model):
    _name = "kw_project_task_assign_report"
    _description = "Timesheet Project Task Assign Summary"
    _auto = False
    
    sbu_name = fields.Char('SBU Name')
    project_manager = fields.Char('Project Manager Name')
    project_code  = fields.Char('KyfWO')
    project_name = fields.Char('Project Name')
    project_id = fields.Many2one('project.project',string="Project Name")
    vertical_resource_tagged = fields.Integer(string="Project Resources(Vertical)")
    v_assigned = fields.Integer(string="Task Assigned")
    v_not_assigned = fields.Integer(string="Task Not Assigned",compute='_compute_not_assigned')
    horizontal_resource_tagged =  fields.Integer(string="Project Resources(Horizontal)")
    h_assigned =  fields.Integer(string="Task Assigned")
    h_not_assigned =  fields.Integer(string="Task Not Assigned",compute='_compute_not_assigned')
    actual_vertical_resource_tagged = fields.Integer(string="Actual Vertical Resource")
    actual_horizontal_resource_tagged = fields.Integer(string="Actual Horizontal Resource")
       
    @api.multi
    def _compute_not_assigned(self):
        for rec in self:
            rec.v_not_assigned,rec.h_not_assigned= rec.vertical_resource_tagged - rec.v_assigned,rec.horizontal_resource_tagged - rec.h_assigned

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        to_date = 'to_date' in self._context and self._context['to_date'] and self._context['to_date'] or date.today()
        # print("***** Called *****")
        self.env.cr.execute(f"""CREATE or REPLACE VIEW %s as (

            select row_number() over(order by p.id) as id,(select name from kw_sbu_master where id = p.sbu_id) as sbu_name,
                (select name from hr_employee where id = p.emp_id) as project_manager,(select code from crm_lead where id = p.crm_id) as project_code,
                name as project_name,p.id as project_id,
            (select COUNT(*) from kw_project_resource_tagging rt  
			 join hr_employee e on e.id = rt.emp_id where rt.project_id = p.id and rt.active=true and e.sbu_type = 'sbu') as vertical_resource_tagged,

            (select COUNT(DISTINCT emp_id) from kw_project_resource_tagging rt  
			 join hr_employee e on e.id = rt.emp_id where rt.active=true and e.sbu_type = 'sbu') as actual_vertical_resource_tagged,

            (select count(DISTINCT assigned_employee_id) from project_task where assigned_employee_id in 
            (select rt.emp_id from kw_project_resource_tagging rt  join hr_employee e on e.id = rt.emp_id where rt.project_id = p.id 
			 and rt.active=true and e.sbu_type = 'sbu') 
            and  parent_id is not null and task_status != 'completed' and  planning_start_date <= '{to_date.strftime('%Y-%m-%d')}' and planning_end_date >= '{to_date.strftime('%Y-%m-%d')}') as v_assigned,
            (select COUNT(*) from kw_project_resource_tagging rt  join hr_employee e on e.id = rt.emp_id where rt.project_id = p.id and rt.active=true 
			 and e.sbu_type = 'horizontal') as horizontal_resource_tagged,

            (select COUNT(DISTINCT emp_id) from kw_project_resource_tagging rt  join hr_employee e on e.id = rt.emp_id  where rt.active=true 
			 and e.sbu_type = 'horizontal') as actual_horizontal_resource_tagged,
             
            (select count(DISTINCT assigned_employee_id) from project_task where assigned_employee_id in 
            (select rt.emp_id from kw_project_resource_tagging rt  join hr_employee e on e.id = rt.emp_id where rt.project_id = p.id 
			 and rt.active=true and e.sbu_type = 'horizontal') 
            and  parent_id is not null and task_status != 'completed' and planning_start_date <= '{to_date.strftime('%Y-%m-%d')}' and planning_end_date >= '{to_date.strftime('%Y-%m-%d')}') as h_assigned
            from project_project p where active = true
            )""" % (self._table))

    
    @api.multi
    def get_vertical_data(self):
        # print("view_details", self._context)
        to_date = 'to_date' in self._context and self._context['to_date'] or date.today()
        self.env['kw_project_task_not_assign_report'].with_context(to_date=to_date,project_id= self.project_id,sbu_type='sbu').init()
        view_id = self.env.ref("kw_timesheets.kw_project_task_not_assign_report_tree").id
       
        return {
            'name': 'Project Report',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_project_task_not_assign_report',
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'tree',
            'target': 'self',
            # 'context': {'to_date': to_date,'project_id':self.project_id,'type': 'sbu'}              
                      
        }
    
    @api.multi
    def get_horizontal_data(self):
        # print("view_details", self._context)
        to_date = 'to_date' in self._context and self._context['to_date'] or date.today()
        self.env['kw_project_task_not_assign_report'].with_context(to_date=to_date,project_id= self.project_id,sbu_type='horizontal').init()
        view_id = self.env.ref("kw_timesheets.kw_project_task_not_assign_report_tree").id
       
        return {
            'name': 'Project Report',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_project_task_not_assign_report',
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'tree',
            'target': 'self',
                                
        }