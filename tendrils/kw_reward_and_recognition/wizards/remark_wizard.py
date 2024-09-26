from traceback import print_tb
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
from ast import literal_eval
from datetime import date, datetime, time
import datetime, calendar

class RnrRemarkWizard(models.TransientModel):
    _name = 'rnr_remark_wizard'
    _description = "Starlight"


    def get_employee(self):
        send_to_data = self.env['reward_and_recognition'].browse(self._context.get('remark_id'))
        domain = []
        if send_to_data:
            sbu_users = False
            if send_to_data.rnr_division_id and send_to_data.rnr_division_id.reviewer_id:
                sbu_users = send_to_data.rnr_division_id.reviewer_id.ids
            domain = [('id', 'in', sbu_users)]
        return domain
    
    def _hide_note(self):
        if  self._context.get('finalise') or self._context.get('sbu'):
            return True
        else:
            return False

    def _hide_remark(self):
        if  self._context.get('sbu'):
            return True
        else:
            return False

    def _hide_button_access(self):
        if self._context.get('award') or self._context.get('scrutinize') or self._context.get('reject'):
            return True
        else:
            return False
    
    def get_final_reviewers(self):
        users = self.env['res.users'].sudo().search([])
        
        finalreviewer_users = users.filtered(lambda user: user.has_group('kw_reward_and_recognition.rnr_final_reviewer')==True).mapped('employee_ids').ids
        domain = [('id', 'in', finalreviewer_users)]
        return domain


    remark = fields.Text(string="Remark")
    rnr_id=fields.Many2one("reward_and_recognition", default=lambda self: self.env.context.get('remark_id'))
    send_to_emp = fields.Many2one('hr.employee',string="Send To",domain=get_employee)
    send_to_emps = fields.Many2many('hr.employee',string="Send To",domain=get_final_reviewers)
    hide_button = fields.Boolean(string="Hide Button", default=_hide_button_access)
    hide_note = fields.Boolean(string="Hide Note", default=_hide_note)
    hide_remark = fields.Boolean(string="Hide Note", default=_hide_remark)
    
    @api.constrains('rnr_id')
    def _check_duplicate(self):
        if self.rnr_id:
            award_datas,award_count_data = self.rnr_id.call_award_validation(self.rnr_id.id)
            if award_datas and award_count_data and self._context.get('award'):
                if len(award_datas) >= int(award_count_data[0][0]):
                    raise ValidationError(f"Maximum award limit({award_count_data[0][0]}) has reached.You cannot award more.")
     

    @api.multi
    def button_confirm(self):
        log = self.env['reward_recognition_action_log'].create({
                    'state':self.rnr_id.state,
                    'action_remark':self.remark,
                    'action_taken_by': self.env.user.employee_ids.name,
                    'action_taken_on': date.today(),
                    'rnr_id':self.rnr_id.id,
                    })
        if self._context.get('remark_id'):
            params = self.env['kw_starlight_general_configuration'].sudo().search([],order='id desc',limit=1)
            cc_group = params.cc_notify.ids
            cc_emails = ""
            if cc_group:
                empls = self.env['hr.employee'].search([('id', 'in', cc_group), ('active', '=', True)]).mapped('work_email')
                cc_emails = ','.join(empls)
            if self._context.get('sbu'):
                nominated_by = False
                if self.rnr_id.nominated_by:
                    nominated_by = self.rnr_id.nominated_by
                else:
                    nominated_by = self.env.user.employee_ids
                create_date_today = date.today().strftime("%Y-%m-%d 00:00:00")
                current_month = date.today().month
                compute_month =  datetime.datetime.today().strftime("%B")
                migrating_starlight_query = f"""update reward_and_recognition set  create_date = '{create_date_today}', month = '{current_month}',compute_month='{compute_month}' where id = { self.rnr_id.id}"""
                self._cr.execute(migrating_starlight_query)
                
                self.rnr_id.sudo().write({
                    'state':'nominate',
                    'sbu_feedback':self.remark,
                    'action_taken_by': self.env.user.employee_ids.id,
                    'action_taken_on': date.today(),
                    'pending_at':  self.send_to_emp.id,
                    'nominated_by': nominated_by.id,
                    })
                    
                if self.rnr_id.rnr_division_id.reviewer_id:
                    email_to = self.rnr_id.rnr_division_id.reviewer_id.work_email
                    view_id = self.env.ref('kw_reward_and_recognition.rnr_take_action').id
                    template = self.env.ref('kw_reward_and_recognition.kw_rnr_scrutinize_notification_email_template')
                    review_date = datetime.datetime.strptime(str(params.review_end_Date), "%Y-%m-%d").date()
                    template.with_context(emails=email_to,
                                        name=self.rnr_id.rnr_division_id.reviewer_id.name,
                                        nominated_by =nominated_by.name,
                                        nominated_by_designation = nominated_by.job_id.name,
                                        view_id=view_id,
                                        emp_name=self.rnr_id.employee_id.name,
                                        emp_code=self.rnr_id.employee_id.emp_code,
                                        location=self.rnr_id.employee_id.job_branch_id.alias,
                                        department=self.rnr_id.employee_id.department_id.name,
                                        division=self.rnr_id.employee_id.division.name,
                                        section=self.rnr_id.employee_id.section.name,
                                        practise=self.rnr_id.employee_id.practise.name,
                                        designation=self.rnr_id.employee_id.job_id.name,
                                        cc=cc_emails,
                                        review_date=review_date.strftime('%B %d, %Y'),
                                        signature=self.env.user.signature,
                                        image_id=self.rnr_id.employee_id.id,
                                        ).send_mail(log.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                else:
                    """ If RNR reviewer is not set then mail sent to HOD of the employee """
                    if self.rnr_id.employee_id.department_id.manager_id.work_email:
                        review_date = datetime.datetime.strptime(str(params.review_end_Date), "%Y-%m-%d").date()
                        email_to = self.rnr_id.employee_id.department_id.manager_id.work_email
                        view_id = self.env.ref('kw_reward_and_recognition.rnr_take_action').id
                        template = self.env.ref('kw_reward_and_recognition.kw_rnr_scrutinize_notification_email_template')
                        template.with_context(emails=email_to,
                                        view_id=view_id,
                                        name=self.rnr_id.employee_id.department_id.manager_id.name,
                                        nominated_by =self.rnr_id.nominated_by.name,
                                        nominated_by_designation = self.rnr_id.nominated_by.job_id.name,
                                        emp_name=self.rnr_id.employee_id.name,
                                        emp_code=self.rnr_id.employee_id.emp_code,
                                        location=self.rnr_id.employee_id.job_branch_id.alias,
                                        department=self.rnr_id.employee_id.department_id.name,
                                        division=self.rnr_id.employee_id.division.name,
                                        section=self.rnr_id.employee_id.section.name,
                                        practise=self.rnr_id.employee_id.practise.name,
                                        designation=self.rnr_id.employee_id.job_id.name,
                                        cc=cc_emails,
                                        review_date=review_date.strftime('%B %d, %Y'),
                                        signature=self.env.user.signature).send_mail(log.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                    else:
                        raise ValidationError('Please Add HOD')
            
            # if self._context.get('scrutinize'):
            #     action_id = self.env.ref('kw_reward_and_recognition.rnr_take_action').id
            #     self.rnr_id.sudo().write({
            #         'state':'review',
            #         'reviewer_feedback':self.remark,
            #         'action_taken_by': self.env.user.employee_ids.id,
            #         'action_taken_on': date.today(),
            #         'reviewed_by': self.env.user.employee_ids.id
            #         })
               
            if self._context.get('finalise'):
                self.rnr_id.sudo().write({
                    'state':'finalise',
                    'final_reviewer_feedback':self.remark,
                    'action_taken_by': self.env.user.employee_ids.id,
                    'action_taken_on': date.today(),
                    'publish_on': date.today(),
                    'pending_at':  False,
                    }) 
                
                view_id = self.env.ref('kw_reward_and_recognition.rnr_take_action').id
                template = self.env.ref('kw_reward_and_recognition.kw_rnr_awrad_publish_notification_email_template')
                email_to = self.rnr_id.employee_id.work_email
                employee_ra = self.rnr_id.employee_id.parent_id.work_email
                employee_hod = self.rnr_id.employee_id.department_id.manager_id.work_email
                template.with_context(emails=email_to,
                                        employee_hod=employee_hod,
                                        employee_ra = employee_ra,
                                        view_id=view_id,
                                        reviewer = self.rnr_id.reviewed_by.name,
                                        emp_name=self.rnr_id.employee_id.name,
                                        emp_code=self.rnr_id.employee_id.emp_code,
                                        location=self.rnr_id.employee_id.job_branch_id.alias,
                                        department=self.rnr_id.employee_id.department_id.name,
                                        division=self.rnr_id.employee_id.division.name,
                                        section=self.rnr_id.employee_id.section.name,
                                        practise=self.rnr_id.employee_id.practise.name,
                                        designation=self.rnr_id.employee_id.job_id.name,
                                        cc=cc_emails,
                                        signature=self.env.user.signature).send_mail(log.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                
            if self._context.get('award'):
                view_id = self.env.ref('kw_reward_and_recognition.rnr_take_action').id
                template = self.env.ref('kw_reward_and_recognition.kw_rnr_publish_reminder_email_template')
                email_to = ','.join(self.send_to_emps.mapped('work_email'))
                template.with_context(emails=email_to,
                                        reviewer = self.env.user.employee_ids.name,
                                        reviewer_designation =self.env.user.employee_ids.job_id.name,
                                        view_id=view_id,
                                        emp_name=self.rnr_id.employee_id.name,
                                        emp_code=self.rnr_id.employee_id.emp_code,
                                        location=self.rnr_id.employee_id.job_branch_id.alias,
                                        department=self.rnr_id.employee_id.department_id.name,
                                        division=self.rnr_id.employee_id.division.name,
                                        section=self.rnr_id.employee_id.section.name,
                                        practise=self.rnr_id.employee_id.practise.name,
                                        designation=self.rnr_id.employee_id.job_id.name,
                                        cc=cc_emails,
                                        signature=self.env.user.signature).send_mail(log.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                self.rnr_id.sudo().write({
                    'state':'award',
                    'reviewer_feedback':self.remark,
                    'action_taken_by': self.env.user.employee_ids.id,
                    'action_taken_on': date.today(),
                    'pending_at':  False,
                    'reviewed_by': self.env.user.employee_ids.id
                    })
                self.env.user.notify_info(message='Application is forwarded sucessfully For Publication')
                
            # if self._context.get('reject'):
            #     view_id = self.env.ref('kw_reward_and_recognition.rnr_take_action').id
            #     template = self.env.ref('kw_reward_and_recognition.kw_rnr_reject_notification_email_template')
            #     email_to = self.rnr_id.create_uid.email
            #     template.with_context(emails=email_to,
            #                             view_id=view_id,
            #                             name=self.rnr_id.create_uid.name,
            #                             emp_name=self.rnr_id.employee_id.name,
            #                             emp_code=self.rnr_id.employee_id.emp_code,
            #                             reviewer = self.env.user.employee_ids.name,
            #                             location=self.rnr_id.employee_id.job_branch_id.alias,
            #                             reviewer_designation = self.env.user.employee_ids.job_id.name,
            #                             department=self.rnr_id.employee_id.department_id.name,
            #                             division=self.rnr_id.employee_id.division.name,
            #                             section=self.rnr_id.employee_id.section.name,
            #                             practise=self.rnr_id.employee_id.practise.name,
            #                             designation=self.rnr_id.employee_id.job_id.name,
            #                             cc=cc_emails,
            #                             signature=self.env.user.signature).send_mail(log.id,notif_layout="kwantify_theme.csm_mail_notification_light")
            #     self.rnr_id.write({
            #         'state':'reject',
            #         'reviewer_feedback':self.remark,
            #         'action_taken_by': self.env.user.employee_ids.id,
            #         'action_taken_on': date.today(),
            #         'pending_at':  False,
            #         'reviewed_by': self.env.user.employee_ids.id
            #         })
        action_id = False
        type_view = False        
        if self._context.get('sbu'):
            action_id = self.env.ref('kw_reward_and_recognition.reward_and_recognition_action').id
            type_view = 'kanban'
        if self._context.get('award') or self._context.get('reject') or self._context.get('finalise'):
            action_id = self.env.ref('kw_reward_and_recognition.rnr_take_action').id
            type_view = 'list' 
        if action_id and type_view:
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web#action={action_id}&model=reward_and_recognition&view_type={type_view}',
                'target': 'self',
            }                       
        
        if self._context.get('scrutinize'):
            form_view_id = self.env.ref('kw_reward_and_recognition.reward_andrecognition_view_form').id
            return {
                'name': 'Take Action',
                'type': 'ir.actions.act_window',
                'res_model': 'reward_and_recognition',
                'view_mode': 'form',
                'view_id': form_view_id,
                'target': 'main',
                'res_id':self.rnr_id.id,
                'context': {'create': False,'edit': False},
                'flags'     : {'create': False, },
            }

        
        
       