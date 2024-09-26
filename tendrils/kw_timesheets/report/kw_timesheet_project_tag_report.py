from odoo import models, fields, api, tools
from datetime import date


class TimesheetProjectTagReport(models.Model):
    _name = "kw_timesheet_project_tag_report"
    _description = "Timesheet Project taging report Summary"
    _auto = False
    
    project_name = fields.Char("Project Name")
    resource_count = fields.Integer("Resource Count")
    estimated_effort = fields.Float('Estimated Effort')
    actual_timesheet_effort = fields.Float('Actual Timesheet Effort')
    deviation_percentage = fields.Float('Deviation in (Precentage)',compute="_compute_time_format")

    @api.multi
    def _compute_time_format(self):
        for rec in self:
            time_required_effort_hour = rec.estimated_effort
            time_actual_effort_hour = rec.actual_timesheet_effort
            if time_actual_effort_hour > 0 and time_required_effort_hour > 0:
                perc = ((time_actual_effort_hour - time_required_effort_hour) / time_required_effort_hour) * 100
                rec.deviation_percentage = "{:.2f}".format(perc)
            elif time_actual_effort_hour == 0 and time_required_effort_hour > 0:
                rec.deviation_percentage = "-100"
            elif time_actual_effort_hour == 0 and time_required_effort_hour == 0:
                rec.deviation_percentage = "0"
    

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        # print("***** Called *****")
        # print(self._context)
        from_date = 'from_date' in self._context and self._context['from_date'] and self._context['from_date'] or date.today()
        to_date = 'to_date' in self._context and self._context['to_date'] and self._context['to_date'] or date.today()
        # print(from_date,to_date)
        self.env.cr.execute(f"""CREATE or REPLACE VIEW %s as (
           with project as (
                select id,name from project_project
            ),
            timesheet as (
                select id,employee_id,date as timesheet_date,unit_amount,project_id from account_analytic_line where ( date in (select attendance_recorded_date from kw_daily_employee_attendance where day_status in ('0','3')))  and date >= '{from_date.strftime('%Y-%m-%d')}' and date <= '{to_date.strftime('%Y-%m-%d')}' group by id,employee_id,project_id 
            ),
            resource as (
                select id,emp_id,project_id from kw_project_resource_tagging
            )
                        
            select p.id,
            p.name as project_name,
            (count(distinct pr.emp_id)) as resource_count,
           ((count(t.timesheet_date) * 8.5) *(count(distinct pr.emp_id))) as estimated_effort,
            sum(t.unit_amount) as actual_timesheet_effort
            from project p
            left join timesheet t on p.id = t.project_id
            left join resource pr on p.id =pr.project_id
            where t.timesheet_date >= '{from_date.strftime('%Y-%m-%d')}' and t.timesheet_date <= '{to_date.strftime('%Y-%m-%d')}'
            group by p.id,p.name
            )""" % (self._table))

    @api.multi
    def projec_tag_employee_action(self):
        # print("view_details", self._context)
        from_date = 'from_date' in self._context and self._context['from_date'] and self._context['from_date'] or date.today()
        to_date = 'to_date' in self._context and self._context['to_date'] and self._context['to_date'] or date.today()
        view_id = self.env.ref("kw_timesheets.viewkw_timesheet_report_tree").id
        action = {
            'name': 'Timesheet Report',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_timesheet_report',
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'self',
            'domain': [('project', '=',  self.project_name),('date','>=',from_date),('date','<=',to_date)],
            'context': {'group_by': 'employee_id'}

        }
        return action