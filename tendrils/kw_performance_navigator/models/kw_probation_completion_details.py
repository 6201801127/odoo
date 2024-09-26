from odoo import models, fields, api, tools
from odoo.exceptions import  ValidationError
from datetime import date, datetime, date, timedelta


class AssessmentCompletionDetails(models.Model):
    _name = 'assessment_completion_details'
    _description = "Assessment Completion Details"
    _rec_name = 'name'

    name = fields.Char(related='employee_id.name')
    employee_id=fields.Many2one("hr.employee",String='Employee')
    parent_id=fields.Many2one('hr.employee',string="Reporting Authority")
    department_id=fields.Many2one('hr.department',string="Department")
    division_id=fields.Many2one('hr.department',string="division")
    job_id=fields.Many2one('hr.job',string="Designation")
    emp_code=fields.Char(string="Code")
    probation_completion_date=fields.Date(string="Probation Completion Date")
    active = fields.Boolean()
    assessment_complete_boolean = fields.Boolean(string="Assessment Complete")
    mail_from_time = fields.Datetime(string="Mail From Time")
    mail_to_time = fields.Datetime(string="Mail To Time")

    
    def send_reminder_mail(self):
        # goal_set = self.env['kw_appraisal_goal'].search(['name','!=',])
        if self.employee_id and self.parent_id:
            email_cc = ''
            template = self.env.ref('kw_performance_navigator.add_goal_reminder_email_template')
            manager = self.env.ref('kw_performance_navigator.group_performance_navigator_manager').users
            email_cc = ','.join(manager.mapped("email")) if manager else ''
            self.env.user.notify_success(message='Record Send!.')
            template.with_context(cc=email_cc).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")  
            message = f"Mail sent to {self.parent_id.name if self.parent_id else ''}"
            self.assessment_complete_boolean = True
            self.mail_from_time = datetime.now()     
            self.mail_to_time = datetime.now() + timedelta(days=3)  
            return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': message,
                        'img_url':  '/web/static/src/img/smile.svg',
                        'type': 'rainbow_man',
                    }
                }
            
    @api.multi
    def milestone_creation_reminder_mail(self):
        email_cc = ''
        send_mail_records = self.env['assessment_completion_details'].search([
            ('assessment_complete_boolean', '=', True)])
        for record in send_mail_records:
            if record.mail_from_time <= datetime.now() <= record.mail_to_time and (record.mail_from_time +  timedelta(days=2))  <= datetime.now():
                goal_ids = self.env['kw_appraisal_goal'].sudo().search([('employee_id','=',record.employee_id.id)])
                if not goal_ids:
                    record.mail_from_time = datetime.now()     
                    record.mail_to_time = datetime.now() + timedelta(days=3)  
                    if record.employee_id.active == True:
                        template = self.env.ref('kw_performance_navigator.creation_goal_reminder_email_template')
                        manager = self.env.ref('kw_performance_navigator.group_performance_navigator_manager').users
                        email_cc = ','.join(manager.mapped("email")) if manager else ''
                        template.with_context(cc=email_cc,employee=record.employee_id.parent_id).send_mail(record.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        
    # did server active to add already probation completed employee who dont have goal
    def view_assessment_details(self):
        employee_list = []
        with_goal = []
        active_false = []
        
        self.env.cr.execute("""UPDATE assessment_completion_details
            SET active = false
            WHERE employee_id IN (
                SELECT id
                FROM hr_employee
                WHERE active = false
            )
        """)
        self.env.cr.execute("""UPDATE assessment_completion_details
            SET active = false
            WHERE employee_id IN (
                SELECT emp_id
                FROM hr_appraisal
            )
        """)
        # Fetch employees eligible for payroll and with completed probation using a direct SQL query
        self.env.cr.execute("""
            SELECT a.id FROM hr_employee as a
            join kw_feedback_details as f
            on f.assessee_id = a.id 
            WHERE a.enable_payroll = 'yes'  and f.feedback_status = '6'
        """)
        hr_emp_ids = [rec[0] for rec in self.env.cr.fetchall()]
        

        if hr_emp_ids:
        # Fetch employees with appraisal goals using a direct SQL query
            self.env.cr.execute("""
                SELECT DISTINCT employee_id FROM kw_appraisal_goal
                WHERE employee_id IN %s
            """, (tuple(hr_emp_ids),))
            with_goal = [rec[0] for rec in self.env.cr.fetchall()]

            # Determine employees without goals
            employee_list = list(set(hr_emp_ids) - set(with_goal))

            # Deactivate records for employees with goals in the assessment completion table
            if with_goal:
                self.env.cr.execute("""
                    UPDATE assessment_completion_details
                    SET active = false
                    WHERE employee_id IN %s
                """, (tuple(with_goal),))

            if active_false:
                self.env.cr.execute("""
                    DELETE FROM assessment_completion_details
                    WHERE employee_id IN %s
                """, (tuple(active_false),))

            # Fetch existing records from the assessment completion table
            self.env.cr.execute("SELECT employee_id FROM assessment_completion_details")
            existing_records = [rec[0] for rec in self.env.cr.fetchall()]

            # Prepare values for insertion
            values = []
            for emp in employee_list:
                if emp not in existing_records:
                    self.env.cr.execute("""
                        SELECT parent_id, department_id, division, job_id, emp_code, date_of_completed_probation
                        FROM hr_employee
                        WHERE id = %s
                    """, (emp,))
                    emp_data = self.env.cr.fetchone()
                    parent_id = emp_data[0] if emp_data[0] else 'NULL'
                    department_id = emp_data[1] if emp_data[1] else 'NULL'
                    division_id = emp_data[2] if emp_data[2] else 'NULL'
                    job_id = emp_data[3] if emp_data[3] else 'NULL'
                    emp_code = emp_data[4] if emp_data[4] else 'NULL'
                    probation_completion_date = emp_data[5] if emp_data[5] else 'NULL'

                    values.append(f"({emp}, {parent_id}, {department_id}, {division_id}, {job_id}, '{emp_code}', '{probation_completion_date}', true)")

            # Insert new records into the assessment completion table
            if values:
                query = f"""
                    INSERT INTO assessment_completion_details
                    (employee_id, parent_id, department_id, division_id, job_id, emp_code, probation_completion_date, active)
                    VALUES {', '.join(values)}
                """
                self.env.cr.execute(query)

        # Define action to return tree view
        tree_view_id = self.env.ref('kw_performance_navigator.assessment_completion_details_view_tree').id
        action = {
            'name': 'Probation Completion Details',
            'type': 'ir.actions.act_window',
            'res_model': 'assessment_completion_details',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(tree_view_id, 'tree')],
            'target': 'self',
            'context': {'create': 0, 'delete': 0, 'edit': 0}
        }
        return action

    # def view_assessment_details(self):
    #     employee_list = []
    #     with_gaol = []
    #     hr_emp = self.env['hr.employee'].search([
    #         ('enable_payroll', '=', 'yes'),
    #         ('date_of_completed_probation', '!=', False)
    #     ])

    #     for rec in hr_emp:
    #         gaol_rec = self.env['kw_appraisal_goal'].sudo().search([
    #             ('employee_id', '=', rec.id)
    #         ])
    #         if not gaol_rec:
    #             employee_list.append(rec.id)
    #         else:
    #             with_gaol.append(rec.id)
        
    #     records = self.env['assessment_completion_details'].sudo().search([])
    #     for goal in with_gaol:
    #         check_goal =  records.filtered(lambda x:x.employee_id.id == goal)
    #         if check_goal:
    #             check_goal.write({'active':False})
            
    #     values = []
    #     if records:
    #         for employee in records:
    #             for emp in employee_list:
    #                 if employee.employee_id.id == emp:
    #                     pass
    #                 else:
    #                     emp_rec = self.env['hr.employee'].browse(emp)
    #                     parent_id = emp_rec.parent_id.id if emp_rec.parent_id else 'NULL'
    #                     department_id = emp_rec.department_id.id if emp_rec.department_id else 'NULL'
    #                     division_id = emp_rec.division.id if emp_rec.division else 'NULL'
    #                     job_id = emp_rec.job_id.id if emp_rec.job_id else 'NULL'
    #                     emp_code = emp_rec.emp_code if emp_rec.emp_code else 'NULL'
    #                     probation_completion_date = emp_rec.date_of_completed_probation if emp_rec.date_of_completed_probation else 'NULL'

    #                     values.append(f"({emp}, {parent_id}, {department_id}, {division_id}, {job_id}, '{emp_code}', '{probation_completion_date}',true)")
    #     else:
    #         for emp in employee_list:
    #             emp_rec = self.env['hr.employee'].browse(emp)
    #             parent_id = emp_rec.parent_id.id if emp_rec.parent_id else 'NULL'
    #             department_id = emp_rec.department_id.id if emp_rec.department_id else 'NULL'
    #             division_id = emp_rec.division.id if emp_rec.division else 'NULL'
    #             job_id = emp_rec.job_id.id if emp_rec.job_id else 'NULL'
    #             emp_code = emp_rec.emp_code if emp_rec.emp_code else 'NULL'
    #             probation_completion_date = emp_rec.date_of_completed_probation if emp_rec.date_of_completed_probation else 'NULL'

    #             values.append(f"({emp}, {parent_id}, {department_id}, {division_id}, {job_id}, '{emp_code}', '{probation_completion_date}',true)")
        
    #     if values:
    #         query = f"""
    #             INSERT INTO assessment_completion_details
    #             (employee_id, parent_id, department_id, division_id, job_id, emp_code, probation_completion_date,active)
    #             VALUES {', '.join(values)}
    #         """
    #         self.env.cr.execute(query)
    #     tree_view_id = self.env.ref('kw_performance_navigator.assessment_completion_details_view_tree').id
    #         # form_view_id = self.env.ref('kw_recruitment.view_kw_mrf_rcm_checkpoint_form').id
    #     action = {
    #         'name': 'Probation Completion Details',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'assessment_completion_details',
    #         'view_type': 'form',
    #         'view_mode': 'tree',
    #         'views': [(tree_view_id, 'tree')],
    #         'target': 'self',
    #         'context': {'create':0,'delete':0,'edit':0,},
            
    #     }
    #     return action
        
        