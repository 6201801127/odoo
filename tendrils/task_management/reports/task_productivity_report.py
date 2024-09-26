from odoo import models, fields, api, tools


class TaskProductivityReport(models.Model):
    _name = "task_productivity_report"
    _description = "Task Productivity Report"
    _auto = False

    assigned_to = fields.Many2one('hr.employee', string="Employee Name")
    task_raised_by = fields.Many2one('hr.employee',string="Task Raised By")
    no_of_ticket_assigned = fields.Integer(string='Total Ticket Assigned(Started)', compute='_compute_no_of_ticket_assigned')
    no_of_ticket_closed = fields.Integer(string='Total Gracefully Ticket Closed', compute='_compute_no_of_ticket_closed')
    not_gracefull_ticket_closed = fields.Integer(string='Ticket Closed beyond approved timeline', compute='_compute_no_of_ticket_closed')
    total_tiket_closed = fields.Float(string="Productivity (%)", compute='_compute_productivity', store=False)
    task_mgmt_id = fields.Many2one('kw_task_management', string='Task Management Id')
    assign_task_date = fields.Datetime(string="Assignment Date")
    month_index = fields.Integer(string="Task Month Index")
    task_assign_year = fields.Integer(string="Task Assign Year")
    month_number = fields.Date(string="Task Assign Month")
    create_uid = fields.Many2one("res.users", string="User")




    # def _compute_no_of_ticket_assigned(self):
    #     for record in self:
    #         task_mgmt_data = self.env['kw_task_management'].search(
    #             [('assigned_to', '=', record.assigned_to.id),('assign_to_report_bool', '=', True)])
    #         print(task_mgmt_data,"task_mgmt_data================")
    #         record.no_of_ticket_assigned = len(task_mgmt_data)
    @api.model
    def _compute_no_of_ticket_assigned(self):
        for record in self:
            # domain = [
            #     '&',
            #     ('assigned_to', '=', record.assigned_to.id),
            #     '|',
            #     ('task_raised_by', '=', self.env.user.employee_ids.id),
            #     ('assigned_to', 'child_of', self.env.user.employee_ids.ids),
            #     ('reported_start_bool', '=', True)
            # ]

            if self.env.user.has_group('task_management.group_task_management_manager'):
                domain = [
                        ('assigned_to', '=', record.assigned_to.id),
                        ('reported_start_bool', '=', True)
                    ]
        
            elif self.env.user.has_group('task_management.group_task_management_user'):
                domain = [
                '&',
                ('assigned_to', '=', record.assigned_to.id),
                '|',
                ('task_raised_by', '=', self.env.user.employee_ids.id),
                ('assigned_to', 'child_of', self.env.user.employee_ids.ids),
                ('reported_start_bool', '=', True)
            ]

            task_mgmt_count = self.env['kw_task_management'].search_count(domain)

            record.no_of_ticket_assigned = task_mgmt_count







    def _compute_no_of_ticket_closed(self):
        for record in self:
            ticket_closed = 0
            not_gracefully_closed = 0
            user = self.env.user

            if user.has_group('task_management.group_task_management_manager'):
                domain = [('assigned_to', '=', record.assigned_to.id)]
            elif user.has_group('task_management.group_task_management_user'):
                domain = [
                    '&',
                    ('assigned_to', '=', record.assigned_to.id),
                    '|',
                    ('assigned_by', '=', user.employee_ids.id),
                    ('assigned_to', 'child_of', user.employee_ids.ids)
                ]

            task_mgmt_data = self.env['task_management_report'].search(domain)

            for rec in task_mgmt_data:
                if rec.details_of_acceptance == 'Gracefully Complete' and rec.working_time_spent <= rec.target_time:
                    ticket_closed += 1
                elif rec.details_of_acceptance == 'Complete':
                    not_gracefully_closed += 1

            record.no_of_ticket_closed = ticket_closed
            record.not_gracefull_ticket_closed = not_gracefully_closed
            # print(record.not_gracefull_ticket_closed,"record.not_gracefull_ticket_closed====================")

    def _compute_productivity(self):
        for rec in self:
            if rec.no_of_ticket_assigned and rec.no_of_ticket_closed:
                rec.total_tiket_closed = (rec.no_of_ticket_closed / rec.no_of_ticket_assigned) * 100

    def btn_gracefully_closed(self):
        view_id = self.env.ref("task_management.task_management_report_tree").id
        for rec in self:
            action = {
                'name': 'Gracefully Closed' if self._context.get('button') == 'Gracefully Closed' else 'Not Gracefully Closed',
                'type': 'ir.actions.act_window',
                'res_model': 'task_management_report',
                'view_mode': 'tree',
                'view_type': 'form',
                'view_id': view_id,
                'target': 'current',
            }
            if self.env.user.has_group('task_management.group_task_management_manager'):
                base_domain = [('assigned_to', '=', rec.assigned_to.id)]
            elif self.env.user.has_group('task_management.group_task_management_user'):
                base_domain = [
                    '&',
                    ('assigned_to', '=', rec.assigned_to.id),
                    '|',
                    ('assigned_by', '=', self.env.user.employee_ids.id),
                    ('assigned_to', 'child_of', self.env.user.employee_ids.ids),
                ]

            if self._context.get('button') == 'Gracefully Closed':
                action['domain'] = base_domain + [('details_of_acceptance', '=', 'Gracefully Complete')]
            elif self._context.get('button') == 'Not Gracefully Closed':
                action['domain'] = base_domain + [('details_of_acceptance', '=', 'Complete')]

            return action



    @api.model
    def report_task_productivity(self):
        tree_view_id = self.env.ref('task_management.task_productivity_report_tree').id
        search_view_id = self.env.ref('task_management.task_productivity_report_search_view').id

        action = {
            'type': 'ir.actions.act_window',
            'name':'Productivity Report',
            'views': [(tree_view_id, 'tree'), (search_view_id, 'search')],
            'view_mode': 'tree,search',
            'view_type': 'form',
            'res_model': 'task_productivity_report',
            'target': 'main',
        }
        
        if self.env.user.has_group('task_management.group_task_management_manager'):
            action['domain'] = []
        elif self.env.user.has_group('task_management.group_task_management_user'):
            action['domain'] = ['|',('assigned_to.id', 'child_of', self.env.user.employee_ids.ids), ('task_raised_by.id', '=', self.env.user.employee_ids.id)]
            
        return action

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
            SELECT
                tm.assigned_to AS id,
                tm.assigned_to AS assigned_to,
                tm.task_raised_by as task_raised_by,
                tm.assign_task_date AS assign_task_date,
                tm.create_uid as create_uid,
                EXTRACT(YEAR FROM tm.assign_task_date) AS task_assign_year,   
                DATE_TRUNC('month', tm.assign_task_date)::DATE AS month_number, 
                CAST(TO_CHAR(DATE_TRUNC('month', tm.assign_task_date), 'MM') AS INT) AS month_index, 
                tm.id AS task_mgmt_id
               
            FROM
                kw_task_management AS tm
            LEFT JOIN 
                res_users AS usr ON usr.id = tm.create_uid
            GROUP BY
                tm.assigned_to,
                tm.id
              
        )"""
        self.env.cr.execute(query)
