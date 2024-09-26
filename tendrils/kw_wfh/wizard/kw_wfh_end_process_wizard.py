from odoo import models, fields, api
from datetime import date


class kw_wfh_end_process_wizard(models.TransientModel):
    _name = 'kw_wfh_end_process_wizard'
    _description = 'WFH End process wizard'

    record_id = fields.Many2one('kw_wfh', string="Record Id",
                                default=lambda self: self.env.context.get('current_rec_id'))
    remark = fields.Text('Comment', size=40, required=True)

    @api.multi
    def call_end_process(self):
        """ On calling this method 
        :WFH active record of the employees get expired,
        :Mail notification is send to the User,HR,HOD,IT,Admin,
        :Attendance mode ids changed back to the existing mode.
        """
        self.record_id.sudo().write({'action_remark': self.remark,
                                     'wfh_end_process':True,
                                     'hide_expired_record':True,
                                     'hr_wfh_active_link':False,
                                     'state':'expired',
                                     'remark':self.remark,
                                     'act_to_date':date.today(),
                                     })
        """ mail to IT and Admin """
        dept_list = {}
        ra_list = {}
        department_list = []
        mail_context = {'action': 'Closed'}
        it_admin_users_mail = self.record_id.get_IT_Admin_users_mail()
        mail_from = 'tendrils@csm.tech'
        signature = self.env.user.signature
        location_ids_list = []
        employee_name_list = []
        rec_dept_list = []
        counter = 0
        attn_mode = self.env['kw_attendance_mode_master'].sudo().search([('alias', '=', 'portal')])
        child_ids = self.env['kw_wfh'].sudo().search([('manager_created_record_id', '=', self.record_id.id),('state','=','grant')])
        """ counter is used for fetching departments """
        if self.record_id.department_id and not self.record_id.division and not self.record_id.section and not self.record_id.practise:
            department_list = self.record_id.department_id.mapped('name')
            counter = 1
        elif self.record_id.department_id and self.record_id.division and not self.record_id.section and not self.record_id.practise:
            department_list = self.record_id.division.mapped('name')
            counter = 2
        elif self.record_id.department_id and self.record_id.division and self.record_id.section and not self.record_id.practise:
            department_list = self.record_id.section.mapped('name')
            counter = 3
        else:
            department_list = self.record_id.practise.mapped('name')
            counter = 4
        for child in child_ids:
            name = child.employee_id.name
            mail = child.employee_id.work_email
            emp_code = child.employee_id.emp_code
            location_ids_list.append(child.employee_id.job_branch_id.alias)
            employee_name_list.append(child.employee_id)
            """ fetching departments using counter """
            rec_dept_list += [child.department_id.name] if counter == 1 else [child.division.name] if counter == 2 else [child.section.name] if counter == 3 else [child.practise.name]
            """ close WFH child record """
            self.record_id._close_record(child)
            """ mail to user """
            self.env.ref('kw_wfh.kw_wfh_employees_end_process_email_template').with_context(mail_context, 
                                                                                            signature=signature, 
                                                                                            mail_from=mail_from, 
                                                                                            emp_name=name,
                                                                                            mail_to=mail, 
                                                                                            emp_code=emp_code).send_mail(self.record_id.id,notif_layout='kwantify_theme.csm_mail_notification_light')
            dept = child.employee_id.department_id
            ra = child.employee_id.parent_id
            if not dept_list.get(dept.id) and dept.manager_id.name and dept.manager_id.work_email:
                dept_list.update({dept.id:{'to_name':dept.manager_id.name, 'to_email':dept.manager_id.work_email, 'dept_name':dept.name, 'rec_dept':set(rec_dept_list) if rec_dept_list else ''}})
            if ra.id not in ra_list.keys() and ra.name and ra.work_email:
                ra_list.update({ra.id:{'to_name':ra.name, 'to_email':ra.work_email, 'dept_name':ra.department_id.name, 'rec_dept':set(rec_dept_list) if rec_dept_list else ''}})
            """ Remove attendance mode ids """
            self.record_id._remove_mode_id(child, attn_mode)
        """ mail to IT , ADMIN """
        unique_location_ids_list = []
        unique_location_ids_list += [rec for rec in location_ids_list if rec not in unique_location_ids_list and rec != False]
        joined_location_ids = False
        if unique_location_ids_list != []:
            joined_location_ids = ','.join(set(unique_location_ids_list))
        if employee_name_list and it_admin_users_mail is not None:
            self.env.ref('kw_wfh.kw_wfh_It_admin_end_process_email_template').with_context(mail_context, mail_from=mail_from,
                                                                                                        emp_name=employee_name_list,
                                                                                                        joined_location_ids=joined_location_ids,
                                                                                                        dept_ids=','.join(set(department_list)), 
                                                                                                        signature=signature, ).send_mail(self.record_id.id,notif_layout='kwantify_theme.csm_mail_notification_light')
        if employee_name_list:
            """ mail to  HRD """
            self.env.ref('kw_wfh.kw_wfh_employees_hr_end_process_email_template').with_context(mail_context, mail_from=mail_from,
                                                                                                        emp_name=employee_name_list,
                                                                                                        joined_location_ids=joined_location_ids,
                                                                                                        dept_ids=','.join(set(department_list)), 
                                                                                                        signature=signature).send_mail(self.record_id.id,notif_layout='kwantify_theme.csm_mail_notification_light')
        """ Compute HOD and RA Mail Data """
        for emp in employee_name_list:
            dept_id = emp.department_id.id
            if dept_list.get(dept_id):
                if 'child' in dept_list[dept_id].keys():
                    dept_list[dept_id]['child']+=emp
                    if 'location_name' in dept_list[dept_id].keys() and emp.job_branch_id.alias:
                        dept_list[dept_id]['location_name']+=emp.job_branch_id.alias + ', ' if emp.job_branch_id.alias not in dept_list[dept_id]['location_name'] else ''
                else:
                    dept_list[dept_id]['child'] = emp
                    if emp.job_branch_id.alias:
                        dept_list[dept_id]['location_name'] = emp.job_branch_id.alias + ', '
            
            if ra_list.get(emp.parent_id.id):
                if 'child' in ra_list[emp.parent_id.id].keys():
                    ra_list[emp.parent_id.id]['child']+=emp
                    if 'location_name' in ra_list[emp.parent_id.id].keys() and emp.job_branch_id.alias:
                        ra_list[emp.parent_id.id]['location_name']+=emp.job_branch_id.alias + ', ' if emp.job_branch_id.alias not in ra_list[emp.parent_id.id]['location_name'] else ''
                else:
                    ra_list[emp.parent_id.id]['child'] = emp
                    if emp.job_branch_id.alias:
                        ra_list[emp.parent_id.id]['location_name'] = emp.job_branch_id.alias + ', '
        
        if dept_list:
            for val in dept_list.values():
                self.env.ref('kw_wfh.kw_wfh_employees_hod_end_process_email_template').with_context(mail_context, 
                                                                                                    mail_from=mail_from,
                                                                                                    emp_name=val.get('child'),
                                                                                                    hod_name=val.get('to_name'),
                                                                                                    hod_dep=val.get('dept_name'),
                                                                                                    mail_to=val.get('to_email'),
                                                                                                    rec_dept=','.join(val.get('rec_dept')),
                                                                                                    joined_location_ids=val.get('location_name'),
                                                                                                    signature=signature).send_mail(self.record_id.id,notif_layout='kwantify_theme.csm_mail_notification_light')
        if ra_list:
            for val in ra_list.values():
                self.env.ref('kw_wfh.kw_wfh_employees_ra_end_process_email_template').with_context(mail_context, 
                                                                                                        mail_from=mail_from,
                                                                                                        emp_name=val.get('child'),
                                                                                                        ra_name=val.get('to_name'),
                                                                                                        ra_dept=val.get('dept_name'),
                                                                                                        mail_to=val.get('to_email'),
                                                                                                        rec_dept=','.join(val.get('rec_dept')),
                                                                                                        joined_location_ids=val.get('location_name'),
                                                                                                        signature=signature).send_mail(self.record_id.id, notif_layout='kwantify_theme.csm_mail_notification_light')


class kw_wfh_ra_end_process_wizard(models.TransientModel):
    _name = 'kw_wfh_ra_end_process_wizard'
    _description = 'kw WFH RA End process Wizard'

    record_id = fields.Many2one('kw_wfh', string="Record Id",
                                default=lambda self: self.env.context.get('current_rec_id'))
    remark = fields.Text('Comment', size=40, required=True)

    @api.multi
    def call_ra_end_process(self):
        """ On calling this method 
        :WFH active record of the particular employee get expired, 
        :Mail notification is send to the User,HR,HOD,IT,Admin,
        :Attendance mode ids changed back to the existing mode.
        """
        self.record_id.sudo().write({
            'action_remark': self.remark,
            'hide_extension_record': True,
            'wfh_active_link': False,
            'wfh_end_process': True,
            'hide_expired_record': True,
            'state': 'expired',
            'ra_remark': self.remark,
            'act_to_date': date.today(),
        })
        """ portal login to Employee """
        user_mail = self.record_id.employee_id.work_email
        username = self.record_id.employee_id.name
        hod_user_mail = self.record_id.req_department_id.manager_id.work_email
        hod_user_name = self.record_id.req_department_id.manager_id.name
        ra_mail = self.record_id.employee_id.parent_id.work_email
        ra_name = self.record_id.employee_id.parent_id.name
        mail_context = {'action': 'Closed'}
        mail_from = self.env.user.employee_ids.work_email
        signature = self.env.user.signature
        for rec in self.record_id:
            emp_record_id = rec.id
            emp = rec.employee_id.name
            emp_code = rec.employee_id.emp_code
            """ mail to user """
            template_id = self.env.ref('kw_wfh.kw_wfh_employees_end_process_by_ra_email_template')
            template_id.with_context(mail_context, signature=signature, mail_from=mail_from, emp=emp, emp_code=emp_code,
                                     mail_to=user_mail, ra_mail=ra_mail, hod_user_mail=hod_user_mail).send_mail(rec.id,
                                                                                                                notif_layout="kwantify_theme.csm_mail_notification_light")
            # extended_record = self.env['kw_wfh'].sudo().search([()])
        rec = self.record_id 
        self.record_id._remove_mode_id(rec)
