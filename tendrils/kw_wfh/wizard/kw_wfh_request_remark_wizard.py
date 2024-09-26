from odoo import models, fields, api
import datetime
from datetime import date, datetime, timedelta


class kw_wfh_cancel_remark_wizard(models.TransientModel):
    _name = 'kw_wfh_cancel_remark_wizard'
    _description = 'kw WFH Cancel Wizard'

    request_record_id = fields.Many2one('kw_wfh', string='Request ID')
    remark = fields.Text('Comment', size=40, required=True)

    """ Cancel WFH request """
    @api.multi
    def cancel_request(self):
        self.request_record_id.sudo().write({'state': 'cancel', 'remark': self.remark})  # 'form_status': 'cancel',
        self.env.user.notify_success("Request has been cancelled.")


class kw_wfh_grant_remark_wizard(models.TransientModel):
    _name = 'kw_wfh_grant_remark_wizard'
    _description = 'kw WFH Grant Wizard'

    request_record_id = fields.Many2one('kw_wfh', string='Request ID')
    remark = fields.Text('Comment', size=40, required=True)

    """ Grant WFH request,
        :Enable Attendance mode ids to 'portal' only when From date <= current day,
        :Send a mail to the User,HR,HOD,IT,Admin
         """
    @api.multi
    def grant_request(self):
        attn_mode = self.env['kw_attendance_mode_master'].sudo().search([('alias', '=', 'portal')])
        today_date = date.today()

        if self.request_record_id.request_from_date <= today_date <= self.request_record_id.request_to_date:
            wfh_rec = self.request_record_id
            """ Enable WFH for user """
            # self.request_record_id._enable_mode_id(rec, attn_mode)
            """ For extended WFH Request else non-extended Request """
            if wfh_rec.request_to_date and wfh_rec.revised_to_date:
                previous_mode_ids = wfh_rec.parent_ref_id.previous_attendance_mode_ids
            else:
                previous_mode_ids = wfh_rec.employee_id.attendance_mode_ids

            """if employee has not portal enabled, then it will enable portal through insert query"""
            emp_id = wfh_rec.employee_id
            wfh_rec.enable_portal_mode(emp_id, attn_mode)
            # wfh_rec.employee_id.sudo().write({'attendance_mode_ids': [(4, attn_mode.id)]})  # , 'is_wfh': True

            """keeping backup of employee's old attendance mode"""
            if previous_mode_ids:
                wfh_rec.sudo().write({'previous_attendance_mode_ids': [(6, 0, previous_mode_ids.ids)]})

        """# ===== for attendance work mode update ==== 
        # ===== ADDED BY :- ASISH====="""
        if  self.request_record_id.request_from_date == today_date:
            attendance_report = self.env['kw_daily_employee_attendance'].sudo().search(
                [('employee_id', '=',  self.request_record_id.employee_id.id), ('work_mode', '!=', '0'),
                 ('attendance_recorded_date', '=',  self.request_record_id.request_from_date)])
            if attendance_report:
                # attendance_report.sudo().write({'work_mode': '0'})
                """ updating working mode through update query """
                query = f"UPDATE kw_daily_employee_attendance SET work_mode=0 WHERE id = {attendance_report.id}"
                self._cr.execute(query)

        """mark extended for parent record if it is a WFH extend request"""
        if self.request_record_id.parent_ref_id:
            self.request_record_id.parent_ref_id.sudo().write({'is_extended': True, 'hide_extension_record': True, })

        """WFH Grant action"""
        self.request_record_id.sudo().write({'state': 'grant',
                                             'approved_on': date.today(),
                                             'approved_by': self.env.user.employee_ids.name,
                                             'action_remark': self.remark,
                                             'ra_remark': self.remark,
                                             'action_taken_by': self.env.user.employee_ids.id,
                                             'wfh_active_link': True})
        # 'form_status': 'grant',

        """Send email to user"""
        mail_context = {'state': 'Granted'}
        rec_id = self.request_record_id.id
        token = self.env['kw_wfh_action'].sudo().search([('wfh_id', '=', self.request_record_id.id)])
        act_id = self.env.ref('kw_wfh.kw_wfh_requset_takeaction_window').id
        user_template_id = self.env.ref('kw_wfh.kw_wfh_emp_request_status_email_template')
        user_template_id.with_context(mail_context, rec_id=rec_id, act_id=act_id, db_name=self._cr.dbname,
                                      token=token.access_token).send_mail(self.request_record_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        self.env.user.notify_success("Request has been approved.")


class kw_wfh_emp_extension_remark_wizard(models.TransientModel):
    _name = 'kw_wfh_emp_extension_remark_wizard'
    _description = 'kw WFH Employee Extension Wizard'

    extension_record_id = fields.Many2one('kw_wfh', string='Extension ID')
    remark = fields.Text('Comment', size=40, required=True)

    @api.multi
    def grant_extension(self):
        """ Extend WFH request
        :Send a mail to the User,HR,HOD,IT,Admin
        """
        # self.extension_record_id.parent_ref_id.hide_extension_record = True

        # self.extension_record_id.sudo().write({'state': 'grant',
        #                                        'form_status': 'grant',
        #                                        'approved_on': date.today(),
        #                                        'approved_by': self.env.user.employee_ids.name,
        #                                        'action_remark': self.remark,
        #                                        'action_taken_by': self.env.user.employee_ids.id,
        #                                        'wfh_active_link': True,
        #                                        'ra_remark': self.remark, })
        # mail_context = {'state': 'Granted'}
        # """ User mail """
        # db_name = self._cr.dbname
        # token = self.env['kw_wfh_action'].sudo().search([('wfh_id', '=', self.request_record_id.id)])
        # act_id = self.env.ref('kw_wfh.kw_wfh_requset_takeaction_window').id
        # template_id = self.env.ref('kw_wfh.kw_wfh_emp_extension_request_status_email_template')
        # template_id.with_context(mail_context, rec_id=self.request_record_id.id, act_id=act_id, db_name=db_name,
        #                          token=token.access_token).send_mail(self.extension_record_id.id,
        #                                                              notif_layout="kwantify_theme.csm_mail_notification_light")
        # self.env.user.notify_success("Extension has been approved.")
        return


# class kw_wfh_hold_remark_wizard(models.TransientModel):
#     _name = 'kw_wfh_hold_remark_wizard'
#     _description = 'kw WFH Onhold Wizard'

#     request_record_id = fields.Many2one('kw_wfh', string='Request ID')
#     remark = fields.Text('Comment', size=40, required=True)

#     @api.multi
#     def hold_request(self):
#         """ Hold WFH request of the employee """
#         self.request_record_id.sudo().write({'state': 'hold',
#                                              'form_status': 'hold',
#                                              'approved_on': date.today(),
#                                              'approved_by': self.env.user.employee_ids.name,
#                                              'action_remark': self.remark,
#                                              'action_taken_by': self.env.user.employee_ids.id,
#                                              'ra_remark': self.remark})
#         mail_context = {'state': 'On Hold'}
#         db_name = self._cr.dbname
#         token = self.env['kw_wfh_action'].sudo().search([('wfh_id', '=', self.request_record_id.id)])
#         act_id = self.env.ref('kw_wfh.kw_wfh_requset_action').id
#         template_id = self.env.ref('kw_wfh.kw_wfh_emp_request_hold_email_template')
#         template_id.with_context(mail_context, rec_id=self.request_record_id.id, act_id=act_id, db_name=db_name,
#                                  token=token.access_token).send_mail(self.request_record_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
#         self.env.user.notify_success("Request is on Hold.")


class kw_wfh_reject_remark_wizard(models.TransientModel):
    _name = 'kw_wfh_reject_remark_wizard'
    _description = 'kw WFH Reject Wizard'

    request_record_id = fields.Many2one('kw_wfh', string='Request ID')
    remark = fields.Text('Comment', size=40, required=True)

    """ Reject WFH request of the employee """
    @api.multi
    def reject_request(self):
        self.request_record_id.sudo().write({'state': 'reject',

                                             'approved_on': date.today(),
                                             'approved_by': self.env.user.employee_ids.name,
                                             'action_remark': self.remark,
                                             'action_taken_by': self.env.user.employee_ids.id,
                                             'ra_remark': self.remark})
        # 'form_status': 'reject',
        mail_context = {'state': 'Rejected'}
        db_name = self._cr.dbname
        token = self.env['kw_wfh_action'].sudo().search([('wfh_id', '=', self.request_record_id.id)])
        act_id = self.env.ref('kw_wfh.kw_wfh_requset_takeaction_window').id
        template_id = self.env.ref('kw_wfh.kw_wfh_emp_request_status_email_template')
        template_id.with_context(mail_context, rec_id=self.request_record_id.id, act_id=act_id, db_name=db_name,
                                 token=token.access_token).send_mail(self.request_record_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        self.env.user.notify_success("Request has been rejected.")


class kw_wfh_hr_grant_remark_wizard(models.TransientModel):
    _name = 'kw_wfh_hr_grant_remark_wizard'
    _description = 'kw WFH Grant Wizard'

    record_id = fields.Many2one('kw_wfh', string='Request ID')
    remark = fields.Text('Comment', size=40, required=True)

    """ On calling the method,
        :Initiates WFH of the employee,
        :WFH record is created for the selected employee by HR,
        :Enable Attendance mode ids to 'portal' only when From date <= current day,
        :Send a mail to the User,HR,HOD,IT,Admin
        """
    @api.multi
    def hr_grant_wfh_link(self):
        today_date = date.today()
        wfh_rec = self.record_id
        self.record_id.sudo().write({'state': 'grant', 'approved_on': today_date,
                                     'approved_by': self.env.user.employee_ids.name,
                                     'action_remark': self.remark,
                                     'hide_csm_wfh_extended_record': True,
                                     'hide_csm_initiated_record': True,
                                     'is_record_created': True,
                                     'hr_wfh_active_link': True,
                                     'remark': self.remark})

        """ mail to  IT and Admin """
        attn_mode = self.env['kw_attendance_mode_master'].sudo().search([('alias', '=', 'portal')])
        mail_context = {'action': 'Initiated'}

        if wfh_rec.search_by == 'user' and (wfh_rec.location_type == 'all' or wfh_rec.location_type == 'location'):
            """ Enable WFH to Employee of selected domain """
            employee_name_list = []
            location_ids_list = []
            employees_ids = wfh_rec.searched_user

            if employees_ids:
                employees_ids.sudo().write({'attendance_mode_ids': [(4, attn_mode.id)], 'is_wfh': True})
                for emp_rec in employees_ids:
                    previous_mode_ids = []
                    employee_name_list.append(emp_rec)
                    location_ids_list.append(emp_rec.job_branch_id.alias)
                    name = emp_rec.name
                    mail = emp_rec.work_email
                    if wfh_rec.request_from_date <= today_date <= wfh_rec.request_to_date:
                        if emp_rec.attendance_mode_ids:
                            wfh_rec.sudo().write({'previous_attendance_mode_ids': [(6, 0, emp_rec.attendance_mode_ids.ids)]})
                        # emp_rec.sudo().write({'attendance_mode_ids': [(4, attn_mode.id)], 'is_wfh': True})
                    record = self.env['kw_wfh'].sudo().create({
                        'req_department_id': emp_rec.department_id,
                        'req_division_id': emp_rec.division,
                        'req_section_id': emp_rec.section,
                        'req_practise_id': emp_rec.practise,
                        'department_id': [(6, 0, [emp_rec.department_id.id])] if emp_rec.department_id.id else '',
                        'division': [(6, 0, [emp_rec.division.id])] if emp_rec.division.id else '',
                        'section': [(6, 0, [emp_rec.section.id])] if emp_rec.section.id else '',
                        'practise': [(6, 0, [emp_rec.practise.id])] if emp_rec.practise.id else '',
                        'employee_id': emp_rec.id,
                        'emp_id': emp_rec.id,
                        'searched_user': [(6, 0, [emp_rec.id])] if emp_rec.id else '',
                        'job_id': emp_rec.job_id,
                        'location_id': [(6, 0, [emp_rec.job_branch_id.id])] if emp_rec.job_branch_id.id else '',
                        'reason_id': self.record_id.reason_id.id,
                        'remark': self.record_id.remark,
                        'request_from_date': self.record_id.request_from_date,
                        'request_to_date': self.record_id.request_to_date,
                        'action_taken_by': self.env.user.employee_ids.id,
                        'state': self.record_id.state,
                        'wfh_type': 'others',
                        'hide_extension_record': False,
                        'hide_csm_initiated_record': False,
                        'show_wfh_record': True,
                        'wfh_active_link': True,
                        'hide_csm_wfh_extended_record': True,
                        'hr_created_wfh_active_link': True,
                        'manager_created_record_id': self.record_id.id,
                        'filter_hr_record': True,
                        'previous_attendance_mode_ids': [(6, 0, previous_mode_ids)],
                    })
                    # 'form_status': 'grant',
                    """ mail to user """
                    mail_from = self.env.user.employee_ids.work_email
                    template_id = self.env.ref('kw_wfh.kw_wfh_csm_initiative_employee_notification_email_template')
                    template_id.with_context(mail_context, work_mail=mail, mail_from=mail_from, name=name).send_mail(
                        self.record_id.id, notif_layout='kwantify_theme.csm_mail_notification_light')
            unique_location_ids_list = []
            for rec in location_ids_list:
                if rec not in unique_location_ids_list:
                    unique_location_ids_list.append(rec)
            filtered_unique_loc_ids = []
            for record in unique_location_ids_list:
                if record != False:
                    filtered_unique_loc_ids.append(record)
            joined_location_ids = ','.join(filtered_unique_loc_ids)
            location_all = []
            if self.record_id.location_type == 'all':
                location_all.append("all")
            it_admin_users = self.record_id.get_IT_Admin_users_mail()
            if it_admin_users is not None:
                mail_from = self.env.user.employee_ids.work_email
                template_id = self.env.ref('kw_wfh.kw_wfh_csm_initiative_authorities_status_email_template')
                template_id.with_context(mail_context, mail_from=mail_from,
                                         emp_name=employee_name_list,
                                         joined_location_ids=joined_location_ids,
                                         location_type=location_all).send_mail(self.record_id.id,
                                                                               notif_layout='kwantify_theme.csm_mail_notification_light')
            hrd_template_id = self.env.ref('kw_wfh.kw_wfh_csm_initiative_hrd_status_email_template')
            hrd_template_id.with_context(mail_context, mail_from=mail_from,
                                         emp_name=employee_name_list,
                                         joined_location_ids=joined_location_ids,
                                         location_type=location_all).send_mail(self.record_id.id,
                                                                               notif_layout='kwantify_theme.csm_mail_notification_light')
            """ mail to HOD """

            hod_email_list = []
            unique_hod_list = []
            if self.record_id.searched_user:
                for rec in self.record_id.searched_user:
                    if rec.department_id.manager_id.work_email not in hod_email_list:
                        hod_email_list.append(rec.department_id.manager_id.work_email)
                for record in hod_email_list:
                    if record not in unique_hod_list:
                        unique_hod_list.append(record)
                for unique_hod in unique_hod_list:
                    hod_name_list = []
                    hod_dept_list = []
                    hod_subordinate = []
                    for rec in self.record_id.searched_user:
                        if rec.department_id.manager_id.work_email == unique_hod:
                            hod_subordinate.append(rec)
                            hod_name_list = rec.department_id.manager_id.name
                            hod_dept_list = rec.department_id.name

                    mail_from = self.env.user.employee_ids.work_email
                    hod_template_id = self.env.ref('kw_wfh.kw_wfh_csm_initiative_hod_notification_email_template')
                    hod_template_id.with_context(mail_context, mail_from=mail_from,
                                                 emp_name=hod_subordinate,
                                                 hod_name=hod_name_list,
                                                 hod_dep=hod_dept_list,
                                                 mail_to=unique_hod,
                                                 joined_location_ids=joined_location_ids,
                                                 location_type=location_all).send_mail(self.record_id.id,
                                                                                       notif_layout='kwantify_theme.csm_mail_notification_light')

            """mail to RA"""
            ra_email_list = []
            unique_ra_list = []
            if self.record_id.searched_user:
                for rec in self.record_id.searched_user:
                    if rec.parent_id.work_email not in ra_email_list:
                        ra_email_list.append(rec.parent_id.work_email)
                for record in ra_email_list:
                    if record not in unique_ra_list:
                        unique_ra_list.append(record)
                for unique_ra in unique_ra_list:
                    ra_name_list = []
                    ra_subordinate = []
                    ra_dept = []
                    for rec in self.record_id.searched_user:
                        if rec.parent_id.work_email == unique_ra:
                            ra_subordinate.append(rec)
                            ra_name_list = rec.parent_id.name
                            ra_dept = rec.parent_id.department_id.name
                    mail_from = self.env.user.employee_ids.work_email
                    hod_template_id = self.env.ref('kw_wfh.kw_wfh_csm_initiative_ra_notification_email_template')
                    hod_template_id.with_context(mail_context, mail_from=mail_from,
                                                 emp_name=ra_subordinate,
                                                 ra_name=ra_name_list,
                                                 ra_dept=ra_dept,
                                                 mail_to=unique_ra,
                                                 joined_location_ids=joined_location_ids,
                                                 location_type=location_all).send_mail(self.record_id.id,
                                                                                       notif_layout='kwantify_theme.csm_mail_notification_light')

        """ Enable WFH to Employee of selected domain """
        if self.record_id.search_by == 'hierarchy' and self.record_id.location_type == 'all':
            employees_ids = []
            filtered_ids = []
            if self.record_id.department_id != False and not self.record_id.division and not self.record_id.section and not self.record_id.practise:
                for record in self.record_id.department_id:
                    filtered_ids.append(record.name)
                    department = record.id
                    emp_ids = self.env['hr.employee'].sudo().search([('department_id', '=', department)])
                    for employee in emp_ids:
                        employees_ids.append(employee)
            if self.record_id.department_id != False and self.record_id.division != False and not self.record_id.section and not self.record_id.practise:
                for record in self.record_id.division:
                    filtered_ids.append(record.name)
                    division = record.id
                    emp_ids = self.env['hr.employee'].sudo().search([('division', '=', division)])
                    for employee in emp_ids:
                        employees_ids.append(employee)
            if self.record_id.department_id != False and self.record_id.division != False and self.record_id.section != False and not self.record_id.practise:
                for record in self.record_id.section:
                    filtered_ids.append(record.name)
                    section = record.id
                    emp_ids = self.env['hr.employee'].sudo().search([('section', '=', section)])
                    for employee in emp_ids:
                        employees_ids.append(employee)
            if self.record_id.department_id != False and self.record_id.division != False and self.record_id.section != False and self.record_id.practise != False:
                for record in self.record_id.practise:
                    filtered_ids.append(record.name)
                    practise = record.id
                    emp_ids = self.env['hr.employee'].sudo().search([('practise', '=', practise)])
                    for employee in emp_ids:
                        employees_ids.append(employee)
            if self.record_id.searched_user:
                employees_ids = self.record_id.searched_user
            employee_name_list = []
            if employees_ids:
                for rec in employees_ids:
                    previous_mode_ids = []
                    employee_name_list.append(rec)
                    name = rec.name
                    mail = rec.work_email
                    if self.record_id.request_from_date <= today_date <= self.record_id.request_to_date:
                        # rec.sudo().is_wfh = True
                        if attn_mode and attn_mode.id not in rec.attendance_mode_ids.ids:
                            for ids in rec.attendance_mode_ids:
                                previous_mode_ids.append(ids.id)
                            if rec.attendance_mode_ids:
                                self.record_id.sudo().write({'previous_attendance_mode_ids': [(6, 0, previous_mode_ids)]})
                            rec.sudo().write({'attendance_mode_ids': [(4, attn_mode.id)], 'is_wfh': True})
                        else:
                            rec.sudo().is_wfh = True
                    record = self.env['kw_wfh'].sudo().create({
                        'req_department_id': rec.department_id,
                        'req_division_id': rec.division,
                        'req_section_id': rec.section,
                        'req_practise_id': rec.practise,
                        'department_id': [(6, 0, [rec.department_id.id])] if rec.department_id.id else '',
                        'division': [(6, 0, [rec.division.id])] if rec.division.id else '',
                        'section': [(6, 0, [rec.section.id])] if rec.section.id else '',
                        'practise': [(6, 0, [rec.practise.id])] if rec.practise.id else '',
                        'employee_id': rec.id,
                        'searched_user': [(6, 0, [rec.id])] if rec.id else '',
                        'emp_id': rec.id,
                        'job_id': rec.job_id,
                        'location_id': [(6, 0, [rec.job_branch_id.id])] if rec.job_branch_id.id else '',
                        'reason_id': self.record_id.reason_id.id,
                        'remark': self.record_id.remark,
                        'request_from_date': self.record_id.request_from_date,
                        'request_to_date': self.record_id.request_to_date,
                        'action_taken_by': self.env.user.employee_ids.id,
                        'state': self.record_id.state,
                        'wfh_type': 'others',
                        'hide_extension_record': False,
                        'hide_csm_initiated_record': False,
                        'show_wfh_record': True,
                        'wfh_active_link': True,
                        'hide_csm_wfh_extended_record': True,
                        'hr_created_wfh_active_link': True,
                        'manager_created_record_id': self.record_id.id,
                        'filter_hr_record': True,
                        'previous_attendance_mode_ids': [(6, 0, previous_mode_ids)],
                    })
                    # 'form_status': 'grant',
                    mail_from = self.env.user.employee_ids.work_email
                    template_id = self.env.ref('kw_wfh.kw_wfh_csm_initiative_employee_notification_email_template')
                    template_id.with_context(mail_context, work_mail=mail,
                                             mail_from=mail_from,
                                             name=name).send_mail(self.record_id.id, notif_layout='kwantify_theme.csm_mail_notification_light')

            joined_ids = ','.join(filtered_ids)
            it_admin_users = self.record_id.get_IT_Admin_users_mail()
            if it_admin_users is not None:
                mail_from = self.env.user.employee_ids.work_email
                template_id = self.env.ref('kw_wfh.kw_wfh_csm_initiative_authorities_status_email_template')
                template_id.with_context(mail_context, mail_from=mail_from,
                                         emp_name=employee_name_list, ).send_mail(self.record_id.id,
                                                                                  notif_layout='kwantify_theme.csm_mail_notification_light')
            hrd_template_id = self.env.ref('kw_wfh.kw_wfh_csm_initiative_hrd_status_email_template')
            hrd_template_id.with_context(mail_context, mail_from=mail_from,
                                         emp_name=employee_name_list,
                                         joined_ids=joined_ids).send_mail(self.record_id.id,
                                                                          notif_layout='kwantify_theme.csm_mail_notification_light')

            """ mail to HOD """
            hod_email_list = []
            unique_hod_list = []
            if employees_ids:
                for rec in employees_ids:
                    if rec.department_id.manager_id.work_email not in hod_email_list:
                        hod_email_list.append(rec.department_id.manager_id.work_email)
                for record in hod_email_list:
                    if record not in unique_hod_list:
                        unique_hod_list.append(record)
                for unique_hod in unique_hod_list:
                    hod_name_list = []
                    hod_subordinate = []
                    hod_dept_list = []
                    for rec in employees_ids:
                        if rec.department_id.manager_id.work_email == unique_hod:
                            hod_subordinate.append(rec)
                            hod_name_list = rec.department_id.manager_id.name
                            hod_dept_list = rec.department_id.name

                    mail_from = self.env.user.employee_ids.work_email
                    hod_template_id = self.env.ref('kw_wfh.kw_wfh_csm_initiative_hod_notification_email_template')
                    hod_template_id.with_context(mail_context, mail_from=mail_from,
                                                 emp_name=hod_subordinate,
                                                 hod_name=hod_name_list,
                                                 hod_dep=hod_dept_list,
                                                 mail_to=unique_hod).send_mail(self.record_id.id,
                                                                               notif_layout='kwantify_theme.csm_mail_notification_light')

            """mail to RA"""
            ra_email_list = []
            unique_ra_list = []
            if employees_ids:
                for rec in employees_ids:
                    if rec.parent_id.work_email not in ra_email_list:
                        ra_email_list.append(rec.parent_id.work_email)
                for record in ra_email_list:
                    if record not in unique_ra_list:
                        unique_ra_list.append(record)
                for unique_ra in unique_ra_list:
                    ra_name_list = []
                    ra_subordinate = []
                    ra_dept = []
                    for rec in employees_ids:
                        if rec.parent_id.work_email == unique_ra:
                            ra_subordinate.append(rec)
                            ra_name_list = rec.parent_id.name
                            ra_dept = rec.parent_id.department_id.name
                    mail_from = self.env.user.employee_ids.work_email
                    hod_template_id = self.env.ref('kw_wfh.kw_wfh_csm_initiative_ra_notification_email_template')
                    hod_template_id.with_context(mail_context, mail_from=mail_from,
                                                 emp_name=ra_subordinate,
                                                 ra_name=ra_name_list,
                                                 ra_dept=ra_dept,
                                                 mail_to=unique_ra).send_mail(self.record_id.id,
                                                                              notif_layout='kwantify_theme.csm_mail_notification_light')

        """ Enable WFH to Employee of selected domain """
        if self.record_id.search_by == 'hierarchy' and self.record_id.location_type == 'location':
            employees_ids = []
            filtered_ids = []
            location_ids_list = []
            if self.record_id.department_id != False and not self.record_id.division and not self.record_id.section and not self.record_id.practise:
                for record in self.record_id.department_id:
                    filtered_ids.append(record.name)
                    department = record.id
                    location_id = self.record_id.location_id
                    for rec in location_id:
                        work_location = rec.id
                        location_ids_list.append(rec.alias)
                        emp_ids = self.env['hr.employee'].sudo().search(
                            [('job_branch_id', '=', work_location), ('department_id', '=', department)])
                        for employee in emp_ids:
                            employees_ids.append(employee)
            if self.record_id.department_id != False and self.record_id.division != False and not self.record_id.section and not self.record_id.practise:
                for record in self.record_id.division:
                    filtered_ids.append(record.name)
                    division_id = record.id
                    location_id = self.record_id.location_id
                    for rec in location_id:
                        work_location = rec.id
                        location_ids_list.append(rec.alias)
                        emp_ids = self.env['hr.employee'].sudo().search(
                            [('job_branch_id', '=', work_location), ('division', '=', division_id)])
                        for employee in emp_ids:
                            employees_ids.append(employee)
            if self.record_id.department_id != False and self.record_id.division != False \
                    and self.record_id.section != False and not self.record_id.practise:
                for record in self.record_id.section:
                    filtered_ids.append(record.name)
                    section_id = record.id
                    location_id = self.record_id.location_id
                    for rec in location_id:
                        work_location = rec.id
                        location_ids_list.append(rec.alias)
                        emp_ids = self.env['hr.employee'].sudo().search([('job_branch_id', '=', work_location), ('section', '=', section_id)])
                        for employee in emp_ids:
                            employees_ids.append(employee)
            if self.record_id.department_id != False and self.record_id.division != False \
                    and self.record_id.section != False and self.record_id.practise != False:
                for record in self.record_id.practise:
                    filtered_ids.append(record.name)
                    practise_id = record.id
                    location_id = self.record_id.location_id
                    for rec in location_id:
                        work_location = rec.id
                        location_ids_list.append(rec.alias)
                        emp_ids = self.env['hr.employee'].sudo().search([('practise', '=', practise_id), ('job_branch_id', '=', work_location)])
                        for employee in emp_ids:
                            employees_ids.append(employee)
            if self.record_id.searched_user:
                employees_ids = self.record_id.searched_user
            employee_name_list = []
            if employees_ids:
                for rec in employees_ids:
                    previous_mode_ids = []
                    employee_name_list.append(rec)
                    name = rec.name
                    mail = rec.work_email
                    if self.record_id.request_from_date <= today_date <= self.record_id.request_to_date:
                        # rec.sudo().is_wfh = True
                        if attn_mode and attn_mode.id not in rec.attendance_mode_ids.ids:
                            for ids in rec.attendance_mode_ids:
                                previous_mode_ids.append(ids.id)
                            if rec.attendance_mode_ids:
                                self.record_id.sudo().write({'previous_attendance_mode_ids': [(6, 0, previous_mode_ids)]})
                            rec.sudo().write({'attendance_mode_ids': [(4, attn_mode.id)], 'is_wfh': True})
                        else:
                            rec.sudo().is_wfh = True
                    record = self.env['kw_wfh'].sudo().create({
                        'req_department_id': rec.department_id,
                        'req_division_id': rec.division,
                        'req_section_id': rec.section,
                        'req_practise_id': rec.practise,
                        'department_id': [(6, 0, [rec.department_id.id])] if rec.department_id.id else '',
                        'division': [(6, 0, [rec.division.id])] if rec.division.id else '',
                        'section': [(6, 0, [rec.section.id])] if rec.section.id else '',
                        'practise': [(6, 0, [rec.practise.id])] if rec.practise.id else '',
                        'employee_id': rec.id,
                        'searched_user': [(6, 0, [rec.id])] if rec.id else '',
                        'emp_id': rec.id,
                        'job_id': rec.job_id,
                        'location_id': [(6, 0, [rec.job_branch_id.id])] if rec.job_branch_id.id else '',
                        'reason_id': self.record_id.reason_id.id,
                        'remark': self.record_id.remark,
                        'request_from_date': self.record_id.request_from_date,
                        'request_to_date': self.record_id.request_to_date,
                        'action_taken_by': self.env.user.employee_ids.id,
                        'state': self.record_id.state,
                        'wfh_type': 'others',
                        'hide_extension_record': False,
                        'hide_csm_initiated_record': False,
                        'show_wfh_record': True,
                        'wfh_active_link': True,
                        'hide_csm_wfh_extended_record': True,
                        'hr_created_wfh_active_link': True,
                        'manager_created_record_id': self.record_id.id,
                        'filter_hr_record': True,
                        'previous_attendance_mode_ids': [(6, 0, previous_mode_ids)],
                    })
                    # 'form_status': 'grant',
                    mail_from = self.env.user.employee_ids.work_email
                    template_id = self.env.ref('kw_wfh.kw_wfh_csm_initiative_employee_notification_email_template')
                    template_id.with_context(mail_context, work_mail=mail, mail_from=mail_from,
                                             name=name).send_mail(self.record_id.id, notif_layout='kwantify_theme.csm_mail_notification_light')
            unique_location_ids_list = []
            for rec in location_ids_list:
                if rec not in unique_location_ids_list:
                    unique_location_ids_list.append(rec)
            joined_ids = ','.join(filtered_ids)
            filtered_unique_loc_ids = []
            for record in unique_location_ids_list:
                if record != False:
                    filtered_unique_loc_ids.append(record)
            joined_location_ids = ','.join(filtered_unique_loc_ids)
            it_admin_users = self.record_id.get_IT_Admin_users_mail()
            if it_admin_users is not None:
                mail_from = self.env.user.employee_ids.work_email
                template_id = self.env.ref('kw_wfh.kw_wfh_csm_initiative_authorities_status_email_template')
                template_id.with_context(mail_context, mail_from=mail_from,
                                         emp_name=employee_name_list,
                                         joined_ids=joined_ids,
                                         joined_location_ids=joined_location_ids).send_mail(self.record_id.id,
                                                                                            notif_layout='kwantify_theme.csm_mail_notification_light')
            hrd_template_id = self.env.ref('kw_wfh.kw_wfh_csm_initiative_hrd_status_email_template')
            hrd_template_id.with_context(mail_context, mail_from=mail_from,
                                         emp_name=employee_name_list,
                                         joined_ids=joined_ids,
                                         joined_location_ids=joined_location_ids).send_mail(self.record_id.id,
                                                                                            notif_layout='kwantify_theme.csm_mail_notification_light')

            """ mail to HOD """
            hod_email_list = []
            unique_hod_list = []
            dept_list = []
            if employees_ids:
                for rec in employees_ids:
                    if rec.department_id.manager_id.work_email not in hod_email_list:
                        hod_email_list.append(rec.department_id.manager_id.work_email)
                for record in hod_email_list:
                    if record not in unique_hod_list:
                        unique_hod_list.append(record)
                for unique_hod in unique_hod_list:
                    hod_name_list = []
                    hod_subordinate = []
                    hod_dept_list = []
                    for rec in employees_ids:
                        if rec.department_id.manager_id.work_email == unique_hod:
                            hod_subordinate.append(rec)
                            dept_list += [rec.department_id.name if rec.department_id else '']
                            hod_name_list = rec.department_id.manager_id.name
                            hod_dept_list = rec.department_id.name
                    joined_ids = ','.join(set(dept_list))
                    mail_from = self.env.user.employee_ids.work_email
                    self.env.ref('kw_wfh.kw_wfh_csm_initiative_hod_notification_email_template').with_context(mail_context,
                                                                                                              mail_from=mail_from,
                                                                                                              emp_name=hod_subordinate,
                                                                                                              hod_name=hod_name_list,
                                                                                                              hod_dep=hod_dept_list,
                                                                                                              mail_to=unique_hod,
                                                                                                              joined_ids=joined_ids,
                                                                                                              joined_location_ids=joined_location_ids).send_mail(self.record_id.id,
                                                                                                                                                                 notif_layout='kwantify_theme.csm_mail_notification_light')

            """mail to RA"""
            ra_email_list = []
            unique_ra_list = []
            dept_list = []
            if employees_ids:
                for rec in employees_ids:
                    if rec.parent_id.work_email not in ra_email_list:
                        ra_email_list.append(rec.parent_id.work_email)
                for record in ra_email_list:
                    if record not in unique_ra_list:
                        unique_ra_list.append(record)
                for unique_ra in unique_ra_list:
                    ra_name_list = []
                    ra_subordinate = []
                    ra_dept = []
                    for rec in employees_ids:
                        if rec.parent_id.work_email == unique_ra:
                            ra_subordinate.append(rec)
                            dept_list += [rec.department_id.name if rec.department_id else '']
                            ra_name_list = rec.parent_id.name
                            ra_dept = rec.parent_id.department_id.name
                    joined_ids = ','.join(set(dept_list))
                    mail_from = self.env.user.employee_ids.work_email
                    hod_template_id = self.env.ref('kw_wfh.kw_wfh_csm_initiative_ra_notification_email_template')
                    hod_template_id.with_context(mail_context, mail_from=mail_from,
                                                 emp_name=ra_subordinate,
                                                 ra_name=ra_name_list,
                                                 ra_dept=ra_dept,
                                                 mail_to=unique_ra,
                                                 joined_ids=joined_ids,
                                                 joined_location_ids=joined_location_ids).send_mail(self.record_id.id,
                                                                                                    notif_layout='kwantify_theme.csm_mail_notification_light')

        self.env.user.notify_success("Work from home link created successfully.")


class kw_wfh_hr_extension_remark_wizard(models.TransientModel):
    _name = 'kw_wfh_hr_extension_remark_wizard'
    _description = 'kw WFH Extension Wizard'

    extension_record_id = fields.Many2one('kw_wfh', string='Request ID')
    remark = fields.Text('Comment', size=40, required=True)

    """ On calling the method,
        :Extend WFH of the employee which are not expired,
        :WFH Extended record is created for the selected employee by HR,
        :From date,To date is updated,
        :Send a mail to the User,HR,HOD,IT,Admin
        """
    @api.multi
    def hr_wfh_link_extension(self):
        self.extension_record_id.parent_ref_id.write({'hide_extension_record': True, 'is_extended': True})
        extend_from_date = self.extension_record_id.to_date + timedelta(days=1)
        if extend_from_date.strftime("%A") == "Saturday":
            extend_from_date = extend_from_date + timedelta(days=1)
        if extend_from_date.strftime("%A") == "Sunday":
            extend_from_date = extend_from_date + timedelta(days=1)
        self.extension_record_id.sudo().write({'state': 'grant',
                                               'approved_on': date.today(),
                                               'approved_by': self.env.user.employee_ids.name,
                                               'action_remark': self.remark,
                                               'hide_csm_initiated_record': True,
                                               'request_from_date': extend_from_date,
                                               'request_to_date': self.extension_record_id.revised_to_date,
                                               'hr_wfh_active_link': True,
                                               'hide_hr_request_record': True,
                                               'hide_csm_wfh_extended_record': True,
                                               'extension_remark': self.remark,
                                               'remark': self.remark,
                                               'act_from_date': self.extension_record_id.request_from_date, })

        attn_mode = self.env['kw_attendance_mode_master'].sudo().search([('alias', '=', 'portal')])
        """ mail to  IT and Admin """
        mail_context = {'action': 'Extended'}
        if self.extension_record_id.search_by == 'user' and self.extension_record_id.location_type == 'all' \
                or self.extension_record_id.search_by == 'user' and self.extension_record_id.location_type == 'location':
            user_list = []
            current_employee_ids = self.env['kw_wfh'].sudo().search(
                ['&', '&', ('employee_id', 'in', self.extension_record_id.searched_user.ids),
                 ('manager_created_record_id', '=', self.extension_record_id.parent_ref_id.id),
                 ('state', '!=', 'expired')])
            for rec in current_employee_ids:
                user_list.append(rec.employee_id)
            employee_name_list = []
            location_ids_list = []
            if user_list:
                for rec in user_list:
                    employee_name_list.append(rec)
                    location_ids_list.append(rec.job_branch_id.alias)
                    name = rec.name
                    mail = rec.work_email
                    previous_mode_ids = []
                    if attn_mode and attn_mode.id not in rec.attendance_mode_ids.ids:
                        for ids in rec.attendance_mode_ids:
                            previous_mode_ids.append(ids.id)
                        if rec.attendance_mode_ids:
                            self.extension_record_id.sudo().write({'previous_attendance_mode_ids': [(6, 0, previous_mode_ids)]})
                        rec.sudo().write({'attendance_mode_ids': [(4, attn_mode.id)], 'is_wfh': True})
                    else:
                        rec.sudo().is_wfh = True
                    record = self.env['kw_wfh'].sudo().create({
                        'req_department_id': rec.department_id,
                        'req_division_id': rec.division,
                        'req_section_id': rec.section,
                        'req_practise_id': rec.practise,
                        'department_id': [(6, 0, [rec.department_id.id])] if rec.department_id.id else '',
                        'division': [(6, 0, [rec.division.id])] if rec.division.id else '',
                        'section': [(6, 0, [rec.section.id])] if rec.section.id else '',
                        'practise': [(6, 0, [rec.practise.id])] if rec.practise.id else '',
                        'employee_id': rec.id,
                        'searched_user': [(6, 0, [rec.id])] if rec.id else '',
                        'emp_id': rec.id,
                        'job_id': rec.job_id,
                        'location_id': [(6, 0, [rec.job_branch_id.id])] if rec.job_branch_id.id else '',
                        'reason_id': self.extension_record_id.reason_id.id,
                        'remark': self.extension_record_id.remark,
                        'request_from_date': self.extension_record_id.request_from_date,
                        'request_to_date': self.extension_record_id.request_to_date,
                        'action_taken_by': self.env.user.employee_ids.id,
                        'state': self.extension_record_id.state,
                        'wfh_type': 'others',
                        'hide_extension_record': False,
                        'hide_csm_initiated_record': False,
                        'show_wfh_record': True,
                        'wfh_active_link': True,
                        'revised_to_date': self.extension_record_id.revised_to_date,
                        'extension_remark': self.extension_record_id.extension_remark,
                        'hide_csm_wfh_extended_record': True,
                        'hr_created_wfh_active_link': True,
                        'manager_created_record_id': self.extension_record_id.id,
                        'filter_hr_record': True,
                        'parent_ref_id': self.extension_record_id.parent_ref_id.id,
                    })
                    # 'form_status': 'grant',
                    mail_from = self.env.user.employee_ids.work_email
                    template_id = self.env.ref('kw_wfh.kw_wfh_csm_initiative_employee_notification_email_template')
                    template_id.with_context(mail_context, work_mail=mail, mail_from=mail_from,
                                             name=name).send_mail(self.extension_record_id.id, notif_layout='kwantify_theme.csm_mail_notification_light')
            unique_location_ids_list = []
            for rec in location_ids_list:
                if rec not in unique_location_ids_list:
                    unique_location_ids_list.append(rec)
            filtered_unique_loc_ids = []
            for record in unique_location_ids_list:
                if record != False:
                    filtered_unique_loc_ids.append(record)
            joined_location_ids = ','.join(filtered_unique_loc_ids)
            location_all = []
            if self.extension_record_id.location_type == 'all':
                location_all.append("all")
            it_admin_users = self.extension_record_id.get_IT_Admin_users_mail()
            mail_from = self.env.user.employee_ids.work_email
            if it_admin_users is not None:
                template_id = self.env.ref('kw_wfh.kw_wfh_csm_initiative_authorities_extension_status_email_template')
                template_id.with_context(mail_context, mail_from=mail_from,
                                         emp_name=employee_name_list,
                                         joined_location_ids=joined_location_ids,
                                         location_type=location_all).send_mail(self.extension_record_id.id, notif_layout='kwantify_theme.csm_mail_notification_light')
            hrd_template_id = self.env.ref('kw_wfh.kw_wfh_csm_initiative_hrd_extension_status_email_template')
            hrd_template_id.with_context(mail_context, mail_from=mail_from,
                                         emp_name=employee_name_list,
                                         joined_location_ids=joined_location_ids,
                                         location_type=location_all).send_mail(self.extension_record_id.id, notif_layout='kwantify_theme.csm_mail_notification_light')

            """ mail to HOD """
            hod_email_list = []
            unique_hod_list = []
            if user_list:
                for rec in user_list:
                    if rec.department_id.manager_id.work_email not in hod_email_list:
                        hod_email_list.append(rec.department_id.manager_id.work_email)
                for record in hod_email_list:
                    if record not in unique_hod_list:
                        unique_hod_list.append(record)
                for unique_hod in unique_hod_list:
                    hod_name_list = []
                    hod_subordinate = []
                    hod_dept_list = []
                    for rec in user_list:
                        if rec.department_id.manager_id.work_email == unique_hod:
                            hod_subordinate.append(rec)
                            hod_name_list = rec.department_id.manager_id.name
                            hod_dept_list = rec.department_id.name

                    mail_from = self.env.user.employee_ids.work_email
                    hod_template_id = self.env.ref(
                        'kw_wfh.kw_wfh_csm_initiative_hod_extension_notification_email_template')
                    hod_template_id.with_context(mail_context, mail_from=mail_from,
                                                 emp_name=hod_subordinate,
                                                 hod_name=hod_name_list,
                                                 hod_dep=hod_dept_list,
                                                 mail_to=unique_hod,
                                                 joined_location_ids=joined_location_ids,
                                                 location_type=location_all).send_mail(self.extension_record_id.id, notif_layout='kwantify_theme.csm_mail_notification_light')

            """mail to RA"""
            ra_email_list = []
            unique_ra_list = []
            if user_list:
                for rec in user_list:
                    if rec.parent_id.work_email not in ra_email_list:
                        ra_email_list.append(rec.parent_id.work_email)
                for record in ra_email_list:
                    if record not in unique_ra_list:
                        unique_ra_list.append(record)
                for unique_ra in unique_ra_list:
                    ra_name_list = []
                    ra_subordinate = []
                    ra_dept = []
                    for rec in user_list:
                        if rec.parent_id.work_email == unique_ra:
                            ra_subordinate.append(rec)
                            ra_name_list = rec.parent_id.name
                            ra_dept = rec.parent_id.department_id.name
                    mail_from = self.env.user.employee_ids.work_email
                    hod_template_id = self.env.ref('kw_wfh.kw_wfh_csm_initiative_ra_extension_notification_email_template')
                    hod_template_id.with_context(mail_context, mail_from=mail_from,
                                                 emp_name=ra_subordinate,
                                                 ra_name=ra_name_list,
                                                 ra_dept=ra_dept,
                                                 mail_to=unique_ra,
                                                 joined_location_ids=joined_location_ids,
                                                 location_type=location_all).send_mail(self.extension_record_id.id, notif_layout='kwantify_theme.csm_mail_notification_light')

        if self.extension_record_id.search_by == 'hierarchy' and self.extension_record_id.location_type == 'all':
            employees_ids = []
            filtered_ids = []
            if self.extension_record_id.department_id != False and not self.extension_record_id.division \
                    and not self.extension_record_id.section and not self.extension_record_id.practise:
                for record in self.extension_record_id.department_id:
                    filtered_ids.append(record.name)
                    department = record.id
                    emp_ids = self.env['hr.employee'].sudo().search([('department_id', '=', department)])
                    for employee in emp_ids:
                        employees_ids.append(employee)
            if self.extension_record_id.department_id != False and self.extension_record_id.division != False \
                    and not self.extension_record_id.section and not self.extension_record_id.practise:
                for record in self.extension_record_id.division:
                    filtered_ids.append(record.name)
                    division = record.id
                    emp_ids = self.env['hr.employee'].sudo().search([('division', '=', division)])
                    for employee in emp_ids:
                        employees_ids.append(employee)
            if self.extension_record_id.department_id != False and self.extension_record_id.division != False \
                    and self.extension_record_id.section != False and not self.extension_record_id.practise:
                for record in self.extension_record_id.section:
                    filtered_ids.append(record.name)
                    section = record.id
                    emp_ids = self.env['hr.employee'].sudo().search([('section', '=', section)])
                    for employee in emp_ids:
                        employees_ids.append(employee)
            if self.extension_record_id.department_id != False and self.extension_record_id.division != False \
                    and self.extension_record_id.section != False and self.extension_record_id.practise != False:
                for record in self.extension_record_id.practise:
                    filtered_ids.append(record.name)
                    practise = record.id
                    emp_ids = self.env['hr.employee'].sudo().search([('practise', '=', practise)])
                    for employee in emp_ids:
                        employees_ids.append(employee)
            if self.extension_record_id.searched_user:
                employees_ids = self.extension_record_id.searched_user
            employee_name_list = []
            user_list = []
            current_employee_ids = self.env['kw_wfh'].sudo().search(
                [('employee_id', 'in', self.extension_record_id.searched_user.ids), ('state', 'not in', ['expired']),
                 ('manager_created_record_id', '=', self.extension_record_id.parent_ref_id.id)])
            for rec in current_employee_ids:
                user_list.append(rec.employee_id)
            if user_list:
                for rec in user_list:
                    employee_name_list.append(rec)
                    name = rec.name
                    mail = rec.work_email
                    previous_mode_ids = []
                    if attn_mode and attn_mode.id not in rec.attendance_mode_ids.ids:
                        for ids in rec.attendance_mode_ids:
                            previous_mode_ids.append(ids.id)
                        if rec.attendance_mode_ids:
                            self.extension_record_id.sudo().write({'previous_attendance_mode_ids': [(6, 0, previous_mode_ids)]})
                        rec.sudo().write({'attendance_mode_ids': [(4, attn_mode.id)], 'is_wfh': True})
                        # rec.is_wfh = True
                    record = self.env['kw_wfh'].sudo().create({
                        'req_department_id': rec.department_id,
                        'req_division_id': rec.division,
                        'req_section_id': rec.section,
                        'req_practise_id': rec.practise,
                        'department_id': [(6, 0, [rec.department_id.id])] if rec.department_id.id else '',
                        'division': [(6, 0, [rec.division.id])] if rec.division.id else '',
                        'section': [(6, 0, [rec.section.id])] if rec.section.id else '',
                        'practise': [(6, 0, [rec.practise.id])] if rec.practise.id else '',
                        'employee_id': rec.id,
                        'searched_user': [(6, 0, [rec.id])] if rec.id else '',
                        'emp_id': rec.id,
                        'job_id': rec.job_id,
                        'location_id': [(6, 0, [rec.job_branch_id.id])] if rec.job_branch_id.id else '',
                        'reason_id': self.extension_record_id.reason_id.id,
                        'remark': self.extension_record_id.remark,
                        'request_from_date': self.extension_record_id.request_from_date,
                        'request_to_date': self.extension_record_id.request_to_date,
                        'action_taken_by': self.env.user.employee_ids.id,
                        'state': self.extension_record_id.state,
                        'wfh_type': 'others',
                        'hide_extension_record': False,
                        'hide_csm_initiated_record': False,
                        'show_wfh_record': True,
                        'wfh_active_link': True,
                        'revised_to_date': self.extension_record_id.revised_to_date,
                        'extension_remark': self.extension_record_id.extension_remark,
                        'hide_csm_wfh_extended_record': True,
                        'hr_created_wfh_active_link': True,
                        'manager_created_record_id': self.extension_record_id.id,
                        'filter_hr_record': True,
                        'parent_ref_id': self.extension_record_id.parent_ref_id.id,
                    })
                    # 'form_status': 'grant',
                    mail_from = self.env.user.employee_ids.work_email
                    template_id = self.env.ref('kw_wfh.kw_wfh_csm_initiative_employee_notification_email_template')
                    template_id.with_context(mail_context, work_mail=mail,
                                             mail_from=mail_from,
                                             name=name).send_mail(self.extension_record_id.id, notif_layout='kwantify_theme.csm_mail_notification_light')

            it_admin_users = self.extension_record_id.get_IT_Admin_users_mail()
            mail_from = self.env.user.employee_ids.work_email
            if it_admin_users is not None:
                template_id = self.env.ref('kw_wfh.kw_wfh_csm_initiative_authorities_extension_status_email_template')
                template_id.with_context(mail_context, mail_from=mail_from,
                                         emp_name=employee_name_list).send_mail(self.extension_record_id.id, notif_layout='kwantify_theme.csm_mail_notification_light')
            joined_ids = ','.join(filtered_ids)
            hrd_template_id = self.env.ref('kw_wfh.kw_wfh_csm_initiative_hrd_extension_status_email_template')
            hrd_template_id.with_context(mail_context, mail_from=mail_from,
                                         emp_name=employee_name_list,
                                         joined_ids=joined_ids).send_mail(self.extension_record_id.id, notif_layout='kwantify_theme.csm_mail_notification_light')

            """ mail to HOD """
            hod_email_list = []
            unique_hod_list = []
            if user_list:
                for rec in user_list:
                    if rec.department_id.manager_id.work_email not in hod_email_list:
                        hod_email_list.append(rec.department_id.manager_id.work_email)
                for record in hod_email_list:
                    if record not in unique_hod_list:
                        unique_hod_list.append(record)
                for unique_hod in unique_hod_list:
                    hod_name_list = []
                    hod_subordinate = []
                    hod_dept_list = []
                    for rec in user_list:
                        if rec.department_id.manager_id.work_email == unique_hod:
                            hod_subordinate.append(rec)
                            hod_name_list = rec.department_id.manager_id.name
                            hod_dept_list = rec.department_id.name

                    mail_from = self.env.user.employee_ids.work_email
                    hod_template_id = self.env.ref(
                        'kw_wfh.kw_wfh_csm_initiative_hod_extension_notification_email_template')
                    hod_template_id.with_context(mail_context, mail_from=mail_from,
                                                 emp_name=hod_subordinate,
                                                 hod_name=hod_name_list,
                                                 hod_dep=hod_dept_list,
                                                 mail_to=unique_hod).send_mail(self.extension_record_id.id, notif_layout='kwantify_theme.csm_mail_notification_light')

            """mail to RA"""
            ra_email_list = []
            unique_ra_list = []
            if user_list:
                for rec in user_list:
                    if rec.parent_id.work_email not in ra_email_list:
                        ra_email_list.append(rec.parent_id.work_email)
                for record in ra_email_list:
                    if record not in unique_ra_list:
                        unique_ra_list.append(record)
                for unique_ra in unique_ra_list:
                    ra_name_list = []
                    ra_subordinate = []
                    ra_dept = []
                    for rec in user_list:
                        if rec.parent_id.work_email == unique_ra:
                            ra_subordinate.append(rec)
                            ra_name_list = rec.parent_id.name
                            ra_dept = rec.parent_id.department_id.name
                    mail_from = self.env.user.employee_ids.work_email
                    hod_template_id = self.env.ref(
                        'kw_wfh.kw_wfh_csm_initiative_ra_extension_notification_email_template')
                    hod_template_id.with_context(mail_context, mail_from=mail_from,
                                                 emp_name=ra_subordinate,
                                                 ra_name=ra_name_list,
                                                 ra_dept=ra_dept,
                                                 mail_to=unique_ra).send_mail(self.extension_record_id.id,
                                                                              notif_layout='kwantify_theme.csm_mail_notification_light')

        # """ #Enable portal login to Employee of selected domain in WFH Extension """
        if self.extension_record_id.search_by == 'hierarchy' and self.extension_record_id.location_type == 'location':
            employees_ids = []
            filtered_ids = []
            location_ids_list = []
            if self.extension_record_id.department_id != False and not self.extension_record_id.division \
                    and not self.extension_record_id.section and not self.extension_record_id.practise:
                for record in self.extension_record_id.department_id:
                    filtered_ids.append(record.name)
                    department = record.id
                    location_id = self.extension_record_id.location_id
                    for rec in location_id:
                        work_location = rec.id
                        location_ids_list.append(rec.alias)
                        emp_ids = self.env['hr.employee'].sudo().search(
                            [('job_branch_id', '=', work_location), ('department_id', '=', department)])
                        for employee in emp_ids:
                            employees_ids.append(employee)
            if self.extension_record_id.department_id != False and self.extension_record_id.division != False \
                    and not self.extension_record_id.section and not self.extension_record_id.practise:
                for record in self.extension_record_id.division:
                    filtered_ids.append(record.name)
                    division_id = record.id
                    location_id = self.extension_record_id.location_id
                    for rec in location_id:
                        work_location = rec.id
                        location_ids_list.append(rec.alias)
                        emp_ids = self.env['hr.employee'].sudo().search(
                            [('job_branch_id', '=', work_location), ('division', '=', division_id)])
                        for employee in emp_ids:
                            employees_ids.append(employee)
            if self.extension_record_id.department_id != False and self.extension_record_id.division != False \
                    and self.extension_record_id.section != False and not self.extension_record_id.practise:
                for record in self.extension_record_id.section:
                    filtered_ids.append(record.name)
                    section_id = record.id
                    location_id = self.extension_record_id.location_id
                    for rec in location_id:
                        work_location = rec.id
                        location_ids_list.append(rec.alias)
                        emp_ids = self.env['hr.employee'].sudo().search(
                            [('job_branch_id', '=', work_location), ('section', '=', section_id)])
                        for employee in emp_ids:
                            employees_ids.append(employee)
            if self.extension_record_id.department_id != False and self.extension_record_id.division != False \
                    and self.extension_record_id.section != False and self.extension_record_id.practise != False:
                for record in self.extension_record_id.practise:
                    filtered_ids.append(record.name)
                    practise_id = record.id
                    location_id = self.extension_record_id.location_id
                    for rec in location_id:
                        work_location = rec.id
                        location_ids_list.append(rec.alias)
                        emp_ids = self.env['hr.employee'].sudo().search([('practise', '=', practise_id), ('job_branch_id', '=', work_location)])
                        for employee in emp_ids:
                            employees_ids.append(employee)
            if self.extension_record_id.searched_user:
                employees_ids = self.extension_record_id.searched_user

            employee_name_list = []
            user_list = []
            current_employee_ids = self.env['kw_wfh'].sudo().search(
                [('employee_id', 'in', self.extension_record_id.searched_user.ids), ('state', 'not in', ['expired']),
                 ('manager_created_record_id', '=', self.extension_record_id.parent_ref_id.id)])
            for rec in current_employee_ids:
                user_list.append(rec.employee_id)
            if user_list:
                for rec in user_list:
                    employee_name_list.append(rec)
                    name = rec.name
                    mail = rec.work_email
                    previous_mode_ids = []
                    if attn_mode and attn_mode.id not in rec.attendance_mode_ids.ids:
                        for ids in rec.attendance_mode_ids:
                            previous_mode_ids.append(ids.id)
                        if rec.attendance_mode_ids:
                            self.extension_record_id.sudo().write({'previous_attendance_mode_ids': [(6, 0, previous_mode_ids)]})
                        rec.sudo().write({'attendance_mode_ids': [(4, attn_mode.id)], 'is_wfh': True})
                        # rec.is_wfh = True
                    record = self.env['kw_wfh'].sudo().create({
                        'req_department_id': rec.department_id,
                        'req_division_id': rec.division,
                        'req_section_id': rec.section,
                        'req_practise_id': rec.practise,
                        'department_id': [(6, 0, [rec.department_id.id])] if rec.department_id.id else '',
                        'division': [(6, 0, [rec.division.id])] if rec.division.id else '',
                        'section': [(6, 0, [rec.section.id])] if rec.section.id else '',
                        'practise': [(6, 0, [rec.practise.id])] if rec.practise.id else '',
                        'employee_id': rec.id,
                        'searched_user': [(6, 0, [rec.id])] if rec.id else '',
                        'emp_id': rec.id,
                        'job_id': rec.job_id,
                        'location_id': [(6, 0, [rec.job_branch_id.id])] if rec.job_branch_id.id else '',
                        'reason_id': self.extension_record_id.reason_id.id,
                        'remark': self.extension_record_id.remark,
                        'request_from_date': self.extension_record_id.request_from_date,
                        'request_to_date': self.extension_record_id.request_to_date,
                        'action_taken_by': self.env.user.employee_ids.id,
                        'state': self.extension_record_id.state,
                        'wfh_type': 'others',
                        'hide_extension_record': False,
                        'hide_csm_initiated_record': False,
                        'show_wfh_record': True,
                        'wfh_active_link': True,
                        'revised_to_date': self.extension_record_id.revised_to_date,
                        'extension_remark': self.extension_record_id.extension_remark,
                        'hide_csm_wfh_extended_record': True,
                        'hr_created_wfh_active_link': True,
                        'manager_created_record_id': self.extension_record_id.id,
                        'filter_hr_record': True,
                        'parent_ref_id': self.extension_record_id.parent_ref_id.id,
                    })
                    # 'form_status': 'grant',
                    mail_from = self.env.user.employee_ids.work_email
                    template_id = self.env.ref('kw_wfh.kw_wfh_csm_initiative_employee_notification_email_template')
                    template_id.with_context(mail_context, work_mail=mail,
                                             mail_from=mail_from,
                                             name=name).send_mail(self.extension_record_id.id,
                                                                  notif_layout='kwantify_theme.csm_mail_notification_light')

            unique_location_ids_list = []
            for rec in location_ids_list:
                if rec not in unique_location_ids_list:
                    unique_location_ids_list.append(rec)
            joined_ids = ','.join(filtered_ids)
            filtered_unique_loc_ids = []
            for record in unique_location_ids_list:
                if record != False:
                    filtered_unique_loc_ids.append(record)
            joined_location_ids = ','.join(filtered_unique_loc_ids)
            it_admin_users = self.extension_record_id.get_IT_Admin_users_mail()
            mail_from = self.env.user.employee_ids.work_email
            if it_admin_users is not None:
                template_id = self.env.ref('kw_wfh.kw_wfh_csm_initiative_authorities_extension_status_email_template')
                template_id.with_context(mail_context, mail_from=mail_from,
                                         emp_name=employee_name_list,
                                         joined_ids=joined_ids,
                                         joined_location_ids=joined_location_ids).send_mail(self.extension_record_id.id,
                                                                                            notif_layout='kwantify_theme.csm_mail_notification_light')
            hrd_template_id = self.env.ref('kw_wfh.kw_wfh_csm_initiative_hrd_extension_status_email_template')
            hrd_template_id.with_context(mail_context, mail_from=mail_from,
                                         emp_name=employee_name_list,
                                         joined_ids=joined_ids,
                                         joined_location_ids=joined_location_ids).send_mail(self.extension_record_id.id,
                                                                                            notif_layout='kwantify_theme.csm_mail_notification_light')

            """ mail to HOD """
            hod_email_list = []
            unique_hod_list = []
            if user_list:
                for rec in user_list:
                    if rec.department_id.manager_id.work_email not in hod_email_list:
                        hod_email_list.append(rec.department_id.manager_id.work_email)
                for record in hod_email_list:
                    if record not in unique_hod_list:
                        unique_hod_list.append(record)
                for unique_hod in unique_hod_list:
                    hod_name_list = []
                    hod_subordinate = []
                    hod_dept_list = []
                    for rec in user_list:
                        if rec.department_id.manager_id.work_email == unique_hod:
                            hod_subordinate.append(rec)
                            hod_name_list = rec.department_id.manager_id.name
                            hod_dept_list = rec.department_id.name
                    mail_from = self.env.user.employee_ids.work_email
                    hod_template_id = self.env.ref('kw_wfh.kw_wfh_csm_initiative_hod_extension_notification_email_template')
                    hod_template_id.with_context(mail_context, mail_from=mail_from,
                                                 emp_name=hod_subordinate,
                                                 hod_name=hod_name_list,
                                                 hod_dep=hod_dept_list,
                                                 mail_to=unique_hod,
                                                 joined_ids=joined_ids,
                                                 joined_location_ids=joined_location_ids).send_mail(
                        self.extension_record_id.id, notif_layout='kwantify_theme.csm_mail_notification_light')

            """mail to RA"""
            ra_email_list = []
            unique_ra_list = []
            if user_list:
                for rec in user_list:
                    if rec.parent_id.work_email not in ra_email_list and rec.is_wfh:
                        ra_email_list.append(rec.parent_id.work_email)
                for record in ra_email_list:
                    if record not in unique_ra_list:
                        unique_ra_list.append(record)
                for unique_ra in unique_ra_list:
                    ra_name_list = []
                    ra_subordinate = []
                    ra_dept = []
                    for rec in user_list:
                        if rec.parent_id.work_email == unique_ra:
                            ra_subordinate.append(rec)
                            ra_name_list = rec.parent_id.name
                            ra_dept = rec.parent_id.department_id.name
                    mail_from = self.env.user.employee_ids.work_email
                    hod_template_id = self.env.ref('kw_wfh.kw_wfh_csm_initiative_ra_extension_notification_email_template')
                    hod_template_id.with_context(mail_context, mail_from=mail_from,
                                                 emp_name=ra_subordinate,
                                                 ra_name=ra_name_list,
                                                 ra_dept=ra_dept,
                                                 mail_to=unique_ra,
                                                 joined_ids=joined_ids,
                                                 joined_location_ids=joined_location_ids).send_mail(
                        self.extension_record_id.id, notif_layout='kwantify_theme.csm_mail_notification_light')
        self.env.user.notify_success("Work from home link Extended successfully.")


class kw_wfh_confirmation_wizard(models.TransientModel):
    _name = 'kw_wfh_confirmation_wizard'
    _description = 'kw WFH confirmation Wizard'

    wfh_record_id = fields.Many2one('kw_wfh', string='Request ID', default=lambda self: self.env.context.get('current_rec_id'))
    remark = fields.Text('Comment', size=40)

    """ On calling the method,
        :Extend WFH of the employee which are not expired,
        :WFH Extended record is created for the selected employee by HR,
        :From date,To date is updated,
        :Send a mail to the User,HR,HOD,IT,Admin
        """
    @api.multi
    def confirm_request(self):
        record = self.wfh_record_id
        mail_context = {'action': 'Extended'}
        record.write({'is_extended': True})
        extend_from_date = record.process_id.from_date + timedelta(days = 1)
        if extend_from_date.strftime("%A") == "Saturday":
            extend_from_date = extend_from_date + timedelta(days=1)
        if extend_from_date.strftime("%A") == "Sunday":
            extend_from_date = extend_from_date + timedelta(days=1)

        record = self.env['kw_wfh'].sudo().create({
            'req_department_id': record.department_id,
            'req_division_id': record.division,
            'req_section_id': record.section,
            'req_practise_id':record.practise,
            'employee_id':record.employee_id.id,
            'emp_id': record.emp_id.id,
            'emp_job_location_id': record.emp_job_location_id.id if record.emp_job_location_id else '',
            'reason_id': record.reason_id.id,
            'remark': record.remark,
            'request_from_date': extend_from_date,
            'request_to_date': record.process_id.to_date,
            'action_taken_by': self.env.user.employee_ids.id,
            'state': record.state,
            'wfh_type': 'others',
            'hide_extension_record': False,
            'hide_csm_initiated_record': False,
            'show_wfh_record': True,
            'wfh_active_link': True,
            'revised_to_date': record.process_id.to_date,
            'extension_remark': record.process_id.remark,
            'hide_csm_wfh_extended_record': True,
            'hr_created_wfh_active_link': True,
            'filter_hr_record': True,
            'parent_ref_id': record.id,
            'computer_info': record.computer_info.id if record.computer_info else '',
            'inter_connectivity': record.inter_connectivity if record.inter_connectivity else '',
            # 'vpn_access': record.vpn_access if record.vpn_access else '',
            'citrix_access': record.citrix_access if record.citrix_access else '',
        })
        # 'form_status': 'grant',
        """ mail to user """
        self.env.ref('kw_wfh.kw_wfh_csm_initiative_employee_notification_email_template').with_context(mail_context,
                                                                                                       work_mail=record.employee_id.work_email,
                                                                                                       mail_from=self.env.user.employee_ids.work_email,
                                                                                                       name=record.employee_id.name).send_mail(record.id, notif_layout='kwantify_theme.csm_mail_notification_light')
        if self.wfh_record_id.get_IT_Admin_users_mail() is not None:
            self.env.ref('kw_wfh.kw_wfh_csm_initiative_authorities_extension_status_email_template').with_context(mail_context, mail_from=record.employee_id.work_email,
                                                                                                                  emp_name=record.employee_id,
                                                                                                                  joined_ids=record.emp_job_location_id.alias,
                                                                                                                  joined_location_ids=record.emp_job_location_id.alias).send_mail(record.id,notif_layout='kwantify_theme.csm_mail_notification_light')
        self.env.ref('kw_wfh.kw_wfh_csm_initiative_hrd_extension_status_email_template').with_context(mail_context, mail_from=record.employee_id.work_email,
                                                                                                      emp_name=record.employee_id,
                                                                                                      joined_ids=record.emp_job_location_id.alias,
                                                                                                      joined_location_ids=record.emp_job_location_id.alias).send_mail(record.id,notif_layout='kwantify_theme.csm_mail_notification_light')
        self.env.ref('kw_wfh.kw_wfh_csm_initiative_hod_extension_notification_email_template').with_context(mail_context, mail_from=record.employee_id.work_email,
                                                                                                            emp_name=record.employee_id,
                                                                                                            hod_name=record.req_department_id.manager_id.name,
                                                                                                            hod_dep=record.req_department_id.manager_id.department_id.name,
                                                                                                            mail_to=record.req_department_id.manager_id.work_email,
                                                                                                            joined_ids=record.emp_job_location_id.alias,
                                                                                                            joined_location_ids=record.emp_job_location_id.alias).send_mail(record.id, notif_layout='kwantify_theme.csm_mail_notification_light')
        self.env.ref('kw_wfh.kw_wfh_csm_initiative_ra_extension_notification_email_template').with_context(mail_context, mail_from=record.employee_id.work_email,
                                                                                                           emp_name=record.employee_id,
                                                                                                           ra_name=record.employee_id.parent_id.name,
                                                                                                           ra_dept=record.employee_id.parent_id.department_id.name,
                                                                                                           mail_to=record.employee_id.parent_id.work_email,
                                                                                                           joined_ids=record.emp_job_location_id.alias,
                                                                                                           joined_location_ids=record.emp_job_location_id.alias).send_mail(record.id, notif_layout='kwantify_theme.csm_mail_notification_light')
        self.env.user.notify_success("Work from home link Extended successfully.")
