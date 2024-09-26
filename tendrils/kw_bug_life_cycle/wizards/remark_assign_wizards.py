from odoo import fields, models, api,_
import datetime
from odoo.exceptions import ValidationError


class AllRemarkWizards(models.TransientModel):
    _name = 'kw_bug_remark_wizards'
    _description = 'Kwantify Bug Remarks Wizards'

    def get_module_lead_id(self):
        record = self.env.context.get('current_record')
        data = self.env['kw_raise_defect'].sudo().search([('id', '=', record)])
        emp_list = []
        if data.project_id:
            for recc in data.bug_con_id.user_ids:
                if recc.user_type in ['Module Lead', 'Developer']:
                    emp_list.append(recc.employee_id.id)
            emp_li = [('id', 'in', emp_list)]
            return emp_li

    remark = fields.Text(string='Remark')
    given_time = fields.Float(string ='Required Resolution Time(In Hours):')
    invisible_boolean = fields.Boolean()
    root_cause_and_solution = fields.Text(string='Root Cause And Solution')
    time_taken =fields.Float(string='Time Taken(In Hours)')
    snap_shot = fields.Binary("Upload Snap", attachment=True)
    done_button_boolean = fields.Boolean()
    close_button_boolean = fields.Boolean()
    project_id = fields.Many2one('project.project', string='Project')
    assigned_to_id = fields.Many2one('hr.employee', domain=get_module_lead_id)
    assigned_boolean = fields.Boolean()
    bug_id = fields.Many2one('kw_raise_defect')

    def remark_reason(self):
        context = dict(self._context)
        int_details = self.env["kw_raise_defect"].browse(context.get("active_id"))
        if context['button_name'] == 'Accept Ticket':
            self.bug_id.state = 'Progressive'
            self.bug_id.accept_bug_date = datetime.datetime.now()
            self.bug_id.required_resolation_time = self.given_time
            self.bug_id.required_resolation_time_given_on  = datetime.datetime.now()
            self.bug_id.assigned_by = self.env.user.employee_ids.id
            user_designation = self.env['kw_bug_life_cycle_conf_user_field'].sudo().search([('employee_id', '=', self.env.user.employee_ids.id), ('cycle_bug_conf_id', '=', self.bug_id.bug_con_id.id)])
            self.bug_id.write({'action_log_table_ids':[[0, 0, {'state':'Acknowledged',
                                                               'action_taken_by': self.env.user.employee_ids.name,
                                                               'designation':user_designation.user_type,
                                                               'remark':self.remark
                                                               }]]})

        if context['button_name'] == 'Hold':
            self.bug_id.state = 'Hold'
            self.bug_id.hold_bug_date = datetime.datetime.now()
            self.bug_id.assigned_by = self.env.user.employee_ids.id
            user_designation = self.env['kw_bug_life_cycle_conf_user_field'].sudo().search([('employee_id', '=', self.env.user.employee_ids.id), ('cycle_bug_conf_id', '=', self.bug_id.bug_con_id.id)])
            self.bug_id.write({'action_log_table_ids':[[0, 0, {'state':'Hold',
                                                               'action_taken_by': self.env.user.employee_ids.name,
                                                               'designation':user_designation.user_type,
                                                               'remark':self.remark
                                                               }]]})
        if context['button_name'] == 'Done':
            test_module_id = []
            template1 = self.env.ref('kw_bug_life_cycle.email_template_for_tester')
            data = self.env['kw_bug_life_cycle_conf'].sudo().search([('project_id', '=', int_details.project_id.id)])
            for recc in data.user_ids:
                if recc.user_type in ['Module Lead']:
                    test_module_id.append(recc.employee_id.work_email)
            if template1:
                email_to = int_details.employee_id.work_email
                dev_name= int_details.employee_id.name
                email_cc = ','.join(set(test_module_id))
                remark = self.remark
                defect_id = int_details.number
                subject = f"Bug Repository || {int_details.project_id.name} || Ticket Fixed"
                template1.with_context(mail_for='Done',defect_id=defect_id,email_to = email_to,subject=subject,mail_cc=email_cc, remark = remark,developer_name = int_details.developer_id.name, name = dev_name). \
                    send_mail(int_details.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                 
            self.bug_id.state = 'Done'
            self.bug_id.assigned_by = self.env.user.employee_ids.id
            self.bug_id.developer_id = False
            self.bug_id.pending_at = False
            self.bug_id.fixed_bug_date = datetime.datetime.now()
            self.bug_id.pending_at = [(4, self.bug_id.employee_id.id, False)]
            self.bug_id.developer_id = self.bug_id.employee_id.id
            user_designation = self.env['kw_bug_life_cycle_conf_user_field'].sudo().search([('employee_id', '=', self.env.user.employee_ids.id), ('cycle_bug_conf_id', '=', self.bug_id.bug_con_id.id)])
            self.bug_id.write({'action_log_table_ids':[[0, 0, {'state':'Fixed & Deployed In Test Server',
                                                               'action_taken_by': self.env.user.employee_ids.name,
                                                               'designation':user_designation.user_type,
                                                               'remark':self.remark
                                                               }]]})

        if context['button_name'] == 'Close':
            self.bug_id.state = 'Closed'
            self.bug_id.closed_bug_date = datetime.datetime.now()
            self.bug_id.assigned_by = self.env.user.employee_ids.id
            self.bug_id.developer_id = False
            user_designation = self.env['kw_bug_life_cycle_conf_user_field'].sudo().search([('employee_id', '=', self.env.user.employee_ids.id), ('cycle_bug_conf_id', '=', self.bug_id.bug_con_id.id)])
            self.bug_id.write({'action_log_table_ids':[[0, 0, {'state':'Closed',
                                                               'action_taken_by': self.env.user.employee_ids.name,
                                                               'designation':user_designation.user_type,
                                                               'remark':self.remark
                                                               }]]})
            self.bug_id.write({'snap_action_log_ids': [[0, 0, {'state': 'Closed',
                                                               'snap_shot': self.snap_shot,
                                                               'snap_upload_by': self.env.user.employee_ids.name,
                                                               }]]})
            if self.bug_id.tc_id:
                # print(self.bug_id.tc_id, 'tc_iddddddddddd')
                all_bugs_closed = all(bug.state == 'Closed' for bug in self.bug_id.tc_id.bug_ids)
                # print(all_bugs_closed, '=================>>>>>>>>>>>>>>>>>')
                if all_bugs_closed:
                    self.bug_id.tc_id.result_readonly_boolean = False

        if context['button_name'] == 'Cancel':
            test_module_id = []
            int_details = self.env["kw_raise_defect"].browse(context.get("active_id"))
            self.bug_id.state = 'Rejected'
            self.bug_id.assigned_by = self.env.user.employee_ids.id
            self.bug_id.pending_at = False
            self.bug_id.fixed_bug_date = datetime.datetime.now()
            self.bug_id.pending_at = [(4, self.bug_id.employee_id.id, False)]
            self.bug_id.reject_bug_date = datetime.datetime.now()
            template1 = self.env.ref('kw_bug_life_cycle.email_template_for_tester')
            data = self.env['kw_bug_life_cycle_conf'].sudo().search([('project_id', '=', int_details.project_id.id)])
            for recc in data.user_ids:
                if recc.user_type in ['Module Lead','Test Lead']:
                    test_module_id.append(recc.employee_id.work_email)
            test_module_id.extend(int_details.developer_id.mapped('work_email'))
            if template1:
                email_to = int_details.employee_id.work_email  
                dev_name= int_details.employee_id.name
                email_cc = ','.join(set(test_module_id))
                remark = self.remark
                subject = f"Bug Repository || {int_details.project_id.name} || Ticket Rejected"
                template1.with_context(mail_for='Rejected_dev',email_to = email_to,subject=subject,mail_cc=email_cc, remark = remark,developer_name = int_details.developer_id.name, name = dev_name). \
                    send_mail(int_details.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                 
                
            user_designation = self.env['kw_bug_life_cycle_conf_user_field'].sudo().search([('employee_id', '=', self.env.user.employee_ids.id), ('cycle_bug_conf_id', '=', self.bug_id.bug_con_id.id)])
            self.bug_id.write({'action_log_table_ids':[[0, 0, {'state':'Rejected',
                                                               'action_taken_by': self.env.user.employee_ids.name,
                                                               'designation':user_designation.user_type,
                                                               'remark':self.remark
                                                               }]]})
            self.bug_id.developer_id = False
            self.bug_id.developer_id = self.bug_id.employee_id.id

        if context['button_name'] == 'Reopen':
            test_module_id =[]
            int_details = self.env["kw_raise_defect"].browse(context.get("active_id"))
            template1 = self.env.ref('kw_bug_life_cycle.email_template_for_tester')
            data = self.env['kw_bug_life_cycle_conf'].sudo().search([('project_id', '=', int_details.project_id.id)])
            self.bug_id.reopen_bug_date = datetime.datetime.now()
            if self.assigned_to_id:
                dev_list = []
                for recc in data.user_ids:
                    if recc.user_type == 'Developer':
                        dev_list.append(recc.employee_id.id)
                if self.assigned_to_id.id in dev_list:
                    self.bug_id.developer_id = self.assigned_to_id.id
                    self.bug_id.dev_filed_boolean = False
                    self.bug_id.developer_assign_boolean = True
                    self.bug_id.pending_at = False
                    self.bug_id.pending_at = [(4, self.assigned_to_id.id, False)]
                    self.bug_id.assigned_by = self.env.user.employee_ids.id
                    user_designation = self.env['kw_bug_life_cycle_conf_user_field'].sudo().search([('employee_id', '=', self.env.user.employee_ids.id), ('cycle_bug_conf_id', '=', self.bug_id.bug_con_id.id)])
                    self.bug_id.write({'action_log_table_ids': [[0, 0, {'state': 'Reopened',
                                                                        'designation': user_designation.user_type,
                                                                        'remark': self.remark,
                                                                        'action_taken_by': self.env.user.employee_ids.name,
                                                                        }]]})
                else:
                    self.bug_id.developer_id = self.assigned_to_id.id
                    self.bug_id.dev_filed_boolean = False
                    self.bug_id.assigned_by = self.env.user.employee_ids.id
                    self.bug_id.developer_assign_boolean = False
                    self.bug_id.pending_at = False
                    self.bug_id.pending_at = [(4, self.assigned_to_id.id, False)]
                    self.bug_id.forward_to = self.assigned_to_id.id
                    self.bug_id.module_lead_boolean = True
                    user_designation = self.env['kw_bug_life_cycle_conf_user_field'].sudo().search([('employee_id', '=', self.env.user.employee_ids.id), ('cycle_bug_conf_id', '=', self.bug_id.bug_con_id.id)])
                    self.bug_id.write({'action_log_table_ids': [[0, 0, {'state': 'Reopened',
                                                                        'designation': user_designation.user_type,
                                                                        'remark': self.remark,
                                                                        'action_taken_by': self.env.user.employee_ids.name,
                                                                        }]]})
                self.bug_id.current_datetime = datetime.datetime.now()
                self.bug_id.state = 'New'
                
                for recc in data.user_ids:
                    if recc.user_type in ['Module Lead','Test Lead']:
                        test_module_id.append(recc.employee_id.work_email)
                if template1:
                    email_to = int_details.developer_id.work_email  
                    dev_name= int_details.developer_id.name
                    email_cc = ','.join(set(test_module_id))
                    remark = self.remark
                    subject = f"Bug Repository || {int_details.project_id.name} || Ticket Re-Opened"
                    template1.with_context(mail_for='Reopen_dev',email_to = email_to,subject=subject,mail_cc=email_cc, remark = remark,developer_name = int_details.developer_id.name, name = dev_name). \
                        send_mail(int_details.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                    
            else:
                test_lead_id=[]
                for recc in data.user_ids:
                    if recc.user_type == 'Test Lead':
                        test_lead_id.append(recc.employee_id.id)
                self.bug_id.pending_at = False
                self.bug_id.pending_at = [(4, id, False) for id in test_lead_id]
                self.bug_id.state = 'New'
                self.bug_id.developer_assign_boolean = False
                self.bug_id.forward_to = False
                user_designation = self.env['kw_bug_life_cycle_conf_user_field'].sudo().search([('employee_id', '=', self.env.user.employee_ids.id), ('cycle_bug_conf_id', '=', self.bug_id.bug_con_id.id)])
                self.bug_id.write({'action_log_table_ids':[[0, 0, {'state':'Reopened',
                                                                'action_taken_by': self.env.user.employee_ids.name,
                                                                'designation':user_designation.user_type,
                                                                'remark':self.remark
                                                                }]]})
                for recc in data.user_ids:
                    if recc.user_type in ['Module Lead']:
                        test_module_id.append(recc.employee_id.work_email)
                if template1:
                    for test_lead in self.bug_id.pending_at:
                        email_to = test_lead.work_email  
                        dev_name= test_lead.name
                        email_cc = ','.join(set(test_module_id))
                        remark = self.remark
                        subject = f"Bug Repository || {int_details.project_id.name} || Ticket Re-Opened"
                        template1.with_context(mail_for='Reopen',email_to = email_to,subject=subject,mail_cc=email_cc, remark = remark,developer_name = int_details.developer_id.name, name = dev_name). \
                            send_mail(int_details.id, notif_layout="kwantify_theme.csm_mail_notification_light")

            self.bug_id.write({'snap_action_log_ids': [[0, 0, {'state': 'Reopened',
                                                            'snap_shot': self.snap_shot,
                                                            'snap_upload_by': self.env.user.employee_ids.name,
                                                            }]]})
        else:
            pass
    
    def submit_confirm(self):
        context = dict(self._context)
        raise_record = self.env["kw_raise_defect"].browse(context.get("active_id"))
        
        if raise_record and context['button_name'] == 'submit_confirm':
            raise_record.confirm_bool = True
       