from odoo import models, fields, api, tools
from datetime import datetime, time, timedelta


class TaskManagementReport(models.Model):
    _name = "task_management_report"
    _description = "Task Management Report"
    _rec_name = "ticket_no"
    _order = "id desc"
    _auto = False

    assign_task_date = fields.Datetime(string="Assigned Date")
    assigned_to = fields.Many2one('hr.employee', string="Assigned To")
    assigned_to_code = fields.Char(related='assigned_to.emp_code', string='Employee Code')
    assigned_by = fields.Many2one('hr.employee', string="Assigned By")
    ticket_no = fields.Char(string='Ticket No')
    actual_time_to_resolve = fields.Datetime(string="Resolved Date")
    description_of_task = fields.Text(string="Description of Activity")
    working_time_spent = fields.Float(string='Time Spent')
    target_time = fields.Float(string='Assigned Time')
    deviation_time = fields.Char(string='Deviation Time', compute='_compute_deviation')
    details_of_acceptance = fields.Char(string='Acceptance Remark')
    month_index = fields.Integer(string="Task Month Index")
    task_assign_year = fields.Integer(string="Task Assign Year")
    month_number = fields.Date(string="Task Assign Month")
    create_uid = fields.Many2one("res.users", string="User")
    reported_start_bool = fields.Boolean(string='Start Bool')
    



    # def _compute_working_time_spent(self):
    #     for record in self:
    #         task_log_data = self.env['kw_task_management_log'].search([
    #             ('task_sr_management_id', '=', record.id),
    #             ('action', 'in', ['Started'])
    #         ])
    #         print(task_log_data,"")
    #         total_duration_seconds = 0
    #         for rec in task_log_data:
    #             duration_str = rec.duration_of_task
    #             print(duration_str,"duration_str=========================")
    #             if duration_str and isinstance(duration_str, str):
    #                 hours, minutes, seconds = map(int, duration_str.split(':'))
    #                 # print(hours,minutes,seconds,"seconds======================")
    #                 task_duration_seconds = hours * 3600 + minutes * 60 + seconds
    #                 total_duration_seconds += task_duration_seconds
    #                 # print(total_duration_seconds,"total_duration_seconds==============")

    #         total_hours = total_duration_seconds // 3600
    #         # print(total_hours,"total_hours===========")
    #         minutes = (total_duration_seconds % 3600) // 60
    #         # print(minutes,"minutes======================")
    #         # working_time_spent = total_hours + minutes
    #         formatted_time = "{:02}:{:02}".format(total_hours, minutes)
    #         formatted_time = formatted_time.replace(':', '.')
    #         record.working_time_spent = float(formatted_time)
            # print(record.working_time_spent,"=====================working_time_spent=")

    def _compute_deviation(self):
        for rec in self:
            deviation_in_hours = rec.target_time - rec.working_time_spent
            rec.deviation_time = deviation_in_hours

    @api.model
    def report_task_management(self):
        tree_view_id = self.env.ref('task_management.task_management_report_tree').id
        search_view_id = self.env.ref('task_management.task_management_report_search_view').id
        form_view_id = self.env.ref('task_management.task_management_report_form').id

        action = {
            'type': 'ir.actions.act_window',
            'name':'Task Management Report',
            'views': [(tree_view_id, 'tree'), (search_view_id, 'search'), (form_view_id, 'form')],
            'view_mode': 'tree,search,form',
            'view_type': 'form',
            'res_model': 'task_management_report',
            'target': 'main',
        }
        
        if self.env.user.has_group('task_management.group_task_management_manager'):
            action['domain'] = []
        elif self.env.user.has_group('task_management.group_task_management_user'):
            action['domain'] = ['|', ('assigned_to.id', 'child_of', self.env.user.employee_ids.ids), ('assigned_by.id', '=', self.env.user.employee_ids.id)]

        
        return action


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
            SELECT
                tm.id,  
                tm.assigned_to AS assigned_to,
                tm.task_raised_by as assigned_by,
                tm.reference_no_txt AS ticket_no,
                tm.description AS description_of_task,
                tm.assign_task_date AS assign_task_date,
                tl.end_datetime AS actual_time_to_resolve,
                tm.estimated_hour AS target_time,
				tm.reported_start_bool as reported_start_bool,
                --null AS deviation_time,
                tm.task_duration as working_time_spent,
                tm.create_uid as create_uid,
                EXTRACT(YEAR FROM tm.assign_task_date) AS task_assign_year,   
                DATE_TRUNC('month', tm.assign_task_date)::DATE AS month_number, 
                CAST(TO_CHAR(DATE_TRUNC('month', tm.assign_task_date), 'MM') AS INT) AS month_index, 
                CASE
                    WHEN tm.stage='Complete' and tm.task_duration <= tm.estimated_hour THEN 'Gracefully Complete'
                    ELSE tm.stage
                END as details_of_acceptance
            FROM
                kw_task_management AS tm
            LEFT JOIN (
                SELECT
                    task_sr_management_id,
                    MAX(end_datetime) AS end_datetime
                FROM
                    kw_task_management_log
                GROUP BY
                    task_sr_management_id
            ) AS latest_tl ON latest_tl.task_sr_management_id = tm.id
            LEFT JOIN
                kw_task_management_log AS tl ON tl.task_sr_management_id = tm.id AND tl.end_datetime = latest_tl.end_datetime
            GROUP BY
                tm.id,  
                tm.assigned_to,
                tm.reference_no_txt,
                tm.description,
                tm.assign_task_date,
                tl.end_datetime,
                tm.estimated_hour,
                tm.stage


        )"""
        self.env.cr.execute(query)
