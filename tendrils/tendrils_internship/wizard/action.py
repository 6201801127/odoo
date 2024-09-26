from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta ,time

class DepartmentHeadApproval(models.TransientModel):
    _name = "dept_head_approval_wiz"
    _description = "CHRO Approval"


    remark = fields.Text(string="Remark")
    

    def approve_btn(self):
        if self.env.context.get('current_id') and self._context.get('button') == 'Approve':
            intership_data = self.env['tendrils_internship'].search([('id', '=', self.env.context.get('current_id'))])
            if intership_data :
                intership_data.write({
                    'stage':'Approve',
                    'approve_reject_dept_head_bool':True,
                    'store_remark':self.remark,
                     'internship_ids': [(0, 0, {
                                'date': datetime.now(),
                                'remark': self.remark,
                                'action_taken_by': self.env.user.employee_ids.id,
                                'stage': 'Approve'
                            })]
                })

                # Fetch email details
                email_from = self.env.user.employee_ids.department_id.manager_id.work_email
                chro_group = self.env.ref('tendrils_internship.group_tendrils_internship_chro')
                email_to = ','.join([user.email for user in chro_group.users if user.email])
                name =  ','.join([user.name for user in chro_group.users if user.name])
                name_approver = self.env.user.employee_ids.name
                intern_name = intership_data.intern_name
                intern_email = intership_data.email_id
                highest_qualification = intership_data.highest_qualification
                refered_by = intership_data.refered_by.name

                

                template = self.env.ref('tendrils_internship.internship_dept_head_approve_email_template')

                if template:
                    for user in chro_group.users:
                        if user.email:
                            email_to = user.email
                            name = user.name

                            extra_params = {
                                'email_from': email_from,
                                'mail_to': email_to,
                                'name': name,
                                'name_approver': name_approver,
                                'intern_name':intern_name,
                                'intern_email':intern_email,
                                'highest_qualification':highest_qualification,
                                'refered_by':refered_by

                            }

                            # Sending the custom email
                            self.env['hr.contract'].contact_send_custom_mail(
                                res_id=self.id,
                                notif_layout='kwantify_theme.csm_mail_notification_light',
                                template_layout='tendrils_internship.internship_dept_head_approve_email_template',
                                ctx_params=extra_params,
                                description="Department Head Approval"
                            )

                            self.env.user.notify_success("Mail Sent successfully.")




        # tree_view_id = self.env.ref("tendrils_internship.internship_takeaction_list").id
            action_id =self.env.ref("tendrils_internship.take_action_server_id").id
            menu_id = self.env.context.get('menu_id') 
            return {
                    'type': 'ir.actions.act_url',
                    'url': f'/web#action={action_id}&model=tendrils_internship&view_type=list&menu_id={menu_id}',
                    'target': 'self',
                }


        elif self.env.context.get('current_id') and self._context.get('button') == 'Reject':
            intership_data = self.env['tendrils_internship'].search([('id', '=', self.env.context.get('current_id'))])
            if intership_data :
                template_id = self.env.ref('tendrils_internship.internship_dept_head_reject_email_template')
                mail_from = intership_data.employee_id.department_id.manager_id.work_email
                intern_name = intership_data.intern_name
                reject_by = self.env.user.employee_ids.name
                highest_qualification = intership_data.highest_qualification
                refered_by = intership_data.refered_by.name
                mail_to = intership_data.email_id
                 
                if template_id:
                    extra_params = {
                                'email_from': mail_from,
                                'mail_to': mail_to,
                                'name': intern_name,
                                'reject_by':reject_by,
                                'highest_qualification':highest_qualification,
                                'refered_by':refered_by
                            }

                    # Sending the custom email
                    self.env['hr.contract'].contact_send_custom_mail(
                        res_id=self.id,
                        notif_layout='kwantify_theme.csm_mail_notification_light',
                        template_layout='tendrils_internship.internship_dept_head_reject_email_template',
                        ctx_params=extra_params,
                        description="Department Head Reject"
                    )

                    self.env.user.notify_success("Mail Sent successfully.")
                # print(p)
                intership_data.write({
                    'stage':'Reject',
                    'approve_reject_dept_head_bool':True,
                    'store_remark':self.remark,
                    'internship_ids': [(0, 0, {
                                'date': datetime.now(),
                                'remark': self.remark,
                                'action_taken_by': self.env.user.employee_ids.id,
                                'stage': 'Reject'
                            })]
                })
            action_id =self.env.ref("tendrils_internship.take_action_server_id").id
            menu_id = self.env.context.get('menu_id') 
            return {
                    'type': 'ir.actions.act_url',
                    'url': f'/web#action={action_id}&model=tendrils_internship&view_type=list&menu_id={menu_id}',
                    'target': 'self',
                }
        elif self.env.context.get('current_id') and self._context.get('button') == 'Grant':
            intership_data = self.env['tendrils_internship'].search([('id', '=', self.env.context.get('current_id'))])
            if intership_data:
                 # Fetch email details
                email_from = self.env.user.employee_ids.work_email
                l_and_k_manager = self.env.ref('tendrils_internship.group_tendrils_internship_training_manager')
                email_to = ','.join([user.email for user in l_and_k_manager.users if user.email])
                name =  ','.join([user.name for user in l_and_k_manager.users if user.name])
                granted_by = self.env.user.employee_ids.name
                template = self.env.ref('tendrils_internship.internship_chro_approval_email_template')
                # intern_name = intership_data.name
                intern_email = intership_data.email_id
                intern_name = intership_data.intern_name
                highest_qualification = intership_data.highest_qualification
                refered_by = intership_data.refered_by.name
                if template:
                    for user in l_and_k_manager.users:
                        if user.email:
                            email_to = user.email
                            name = user.name
                            template.with_context(email_from=email_from, email_to=email_to,name = name,granted_by=granted_by,intern_email=intern_email,intern_name=intern_name,highest_qualification=highest_qualification,refered_by=refered_by).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")

                intership_data.write({
                    'stage':'Grant',
                    'btn_grant_bool':True,
                    'store_remark':self.remark,
                    'internship_ids': [(0, 0, {
                                'date': datetime.now(),
                                'remark': self.remark,
                                'action_taken_by': self.env.user.employee_ids.id,
                                'stage': 'Grant'})] 
                                })
            action_id =self.env.ref("tendrils_internship.take_action_server_id").id
            menu_id = self.env.context.get('menu_id') 
            return {
                    'type': 'ir.actions.act_url',
                    'url': f'/web#action={action_id}&model=tendrils_internship&view_type=list&menu_id={menu_id}',
                    'target': 'self',
                }
                

        elif self.env.context.get('current_id') and self._context.get('button') == 'chro_Reject':
            intership_data = self.env['tendrils_internship'].search([('id', '=', self.env.context.get('current_id'))])
            if intership_data:
                template_id = self.env.ref('tendrils_internship.internship_chro_reject_email_template')
                chro_group = self.env.ref('tendrils_internship.group_tendrils_internship_chro')
                email_from = self.env.user.employee_ids.work_email
                name_data = []
                
                intern_name_list = intership_data.mapped('intern_name')  # Assuming intern_name is a list field
                name_data.extend(intern_name_list)
                email_to_list = intership_data.email_id
                mail_to = intership_data.employee_id.department_id.manager_id.work_email
                department_head_name = intership_data.employee_id.department_id.manager_id.name
                cc_email = intership_data.email_id
                intern_name = intership_data.intern_name
                highest_qualification = intership_data.highest_qualification
                refered_by = intership_data.refered_by.name

                # name_data.append(department_head_name)

                if isinstance(email_to_list, str):
                    email_to_list = [email_to_list]

                # Add the manager's email to the list
                email_to_list.append(mail_to)

                reject_by = self.env.user.employee_ids.name
                if template_id:
                    # for email_to in email_to_list:
                        for intern_name in intern_name_list:
                            extra_params = {
                                'email_from': email_from,
                                'email_to': mail_to,
                                'cc_email':cc_email,
                                'name': intern_name,
                                'reject_by': reject_by,
                                'department_head_name':department_head_name,
                                'intern_name':intern_name,
                                'highest_qualification':highest_qualification,
                                'refered_by':refered_by

                            }
                            
                            # Sending the custom email
                            self.env['hr.contract'].contact_send_custom_mail(
                                res_id=self.id,
                                notif_layout='kwantify_theme.csm_mail_notification_light',
                                template_layout='tendrils_internship.internship_chro_reject_email_template',
                                ctx_params=extra_params,
                                description="CHRO Reject"
                            )


                        self.env.user.notify_success("Mail Sent successfully.")
                        # template_id.with_context(email_from=email_from, email_to=email_to,name = intern_name).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            
                intership_data.write({
                    'stage':'Reject',
                    'btn_reject_bool':True,
                    'store_remark':self.remark,
                     'internship_ids': [(0, 0, {
                                'date': datetime.now(),
                                'remark': self.remark,
                                'action_taken_by': self.env.user.employee_ids.id,
                                'stage': 'Reject'
                            })]
                })
            action_id =self.env.ref("tendrils_internship.take_action_server_id").id
            menu_id = self.env.context.get('menu_id') 
            return {
                    'type': 'ir.actions.act_url',
                    'url': f'/web#action={action_id}&model=tendrils_internship&view_type=list&menu_id={menu_id}',
                    'target': 'self',
                }
