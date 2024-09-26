# -*- coding: utf-8 -*-
# ########################
    #Modification History :
    # 03-Aug-2020 : modified to store all the logs with open check-outs n all, By : T Ketaki Debadarshini
   
# ########################
import base64
from datetime import date, datetime, timezone, timedelta
from odoo.addons.kw_utility_tools import kw_helpers

from odoo.http import request
from odoo import models, fields, api, exceptions

from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import IN_STATUS_LE, IN_STATUS_EXTRA_LE, \
    IN_STATUS_LE_HALF_DAY, IN_STATUS_LE_FULL_DAY, ATD_MODE_BIO, ATD_MODE_PORTAL, ATD_MODE_MANUAL, ATD_MODE_ATD_REQUEST


class HrAttendance(models.Model):
    _inherit = "hr.attendance"
    _description = "Attendance"

    branch_id = fields.Many2one('kw_res_branch', string="Branch/SBU")
    # branch_location = fields.Many2one('kw_location_master', string="Location",related="branch_id.location",store=True)

    check_in_mode = fields.Integer(string='Check-in Mode', default=0)  # #0- web, 1- bio, 2- facial Recognition
    # check_out_mode  = fields.Integer(string='Log-out Mode',default=0) 

    check_in_mode_display = fields.Char(string="Check-in Mode", compute="_compute_mode_display")
    # check_out_mode_display  = fields.Char(string="Log-Out Mode",compute="_compute_mode_display")

    in_ip_address = fields.Char(string="Client IP In Mode")
    out_ip_address = fields.Char(string="Client IP Out Mode")

    mode_enabled = fields.Boolean(string="Attendance Mode Enabled", default=False, compute="_compute_mode_enabled", store=True)

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        
        """ If this is an automatic checkout the constraint is invalid
        as there may be old attendances not closed
        """       
        return True

    @api.depends('check_in', 'check_out')
    def _compute_mode_enabled(self):
        bio_attendance_mode = ATD_MODE_BIO
        portal_attendance_mode = ATD_MODE_PORTAL

        for rec in self: 
            all_attendance_modes = rec.employee_id.attendance_mode_ids.mapped('alias')
            # """is valid if no attendance is configured or portal mode enabled and check in mode is portal or bio mode enabled and check-in mode is bio
            # option added/allowed for attendance request modes
            # """
            if (rec.check_in_mode == 0 and portal_attendance_mode in all_attendance_modes) \
                    or (rec.check_in_mode == 1 and bio_attendance_mode in all_attendance_modes) \
                    or rec.employee_id.no_attendance or rec.check_in_mode == 3:
                rec.mode_enabled = True

    @api.depends('check_in_mode')
    def _compute_mode_display(self):
        modes = ['Portal', 'Bio-metric', 'Facial Recognition', 'Manual']
        for rec in self:
            rec.check_in_mode_display = modes[rec.check_in_mode] if rec.check_in and rec.check_in_mode >= 0 else ''
            # rec.check_out_mode_display = modes[rec.check_out_mode] if rec.check_out and  rec.check_out_mode>=0 else ''

    @api.model
    def create(self, values):
        """
            Create a new record for a model ModelName
            @param values: provides a data for new record
    
            @return: returns a id of new record
        """
        employee_id = values.get('employee_id', False)
        if not values.get('branch_id'):
            values.update({'branch_id': self.env['hr.employee'].browse(employee_id).user_id.branch_id.id})

        result = super(HrAttendance, self).create(values)

        # self.env['kw_daily_employee_attendance'].create_daily_attendance(result)
        for attendance_rec in result:
            if attendance_rec.mode_enabled:
                self.env['kw_daily_employee_attendance'].create_daily_attendance(attendance_rec, 'check_in')
    
        return result
       
    @api.multi
    def write(self, values):
        """
            Update all record(s) in recordset, with new value comes as {values}
            return True on success, False otherwise
    
            @param values: dict of new values to be set
    
            @return: True on success, False otherwise
        """
    
        result = super(HrAttendance, self).write(values)        
        # self.env['kw_daily_employee_attendance'].create_daily_attendance(self)

        for attendance_rec in self:
            if attendance_rec.mode_enabled:
                self.env['kw_daily_employee_attendance'].create_daily_attendance(attendance_rec, 'check_out')
    
        return result

    # #portal log-in
    @api.model
    def employee_check_in(self, employee_id, mode=0):
        """for employee attendance check-in records
        """
        self.env['hr.attendance'].create({'employee_id': employee_id,
                                          'check_in': datetime.now(),
                                          'check_in_mode': mode,
                                          'in_ip_address': request.httprequest.remote_addr if mode == 0 else ''})
    
    # #portal log-out
    @api.model
    def employee_portal_log_out(self, user_id, mode=0):
        """To record employee attendance check-out at the time of portal log-out
        """
        attendance_log = self.env['hr.attendance']
        today = datetime.now().date()
        yesterday_date = today - timedelta(days=1)

        user = self.env['res.users'].sudo().browse(user_id)
        latest_log_rec = attendance_log.sudo(user.id).search(
            [('employee_id', '=', user.employee_ids.id), ('check_out', '=', False), ('check_in_mode', '=', mode)],
            limit=1)

        if latest_log_rec and latest_log_rec.check_in and not latest_log_rec.check_out \
                and latest_log_rec.check_in.date() in [today, yesterday_date] and latest_log_rec.check_in < datetime.now():
            latest_log_rec.sudo(user.id).write({'check_out': datetime.now(),
                                                'out_ip_address': request.httprequest.remote_addr if mode == 0 else ''})
        
    @api.model
    def show_late_entry_reason(self, employee_id):
        """
            method to check if late entry status exists for the day then return the late entry url

            @params  : employee id - int
            @returns : late entry url
        """
        url = False
        check_in_utc = datetime.now()

        kw_attendance_log = self.env['kw_daily_employee_attendance'].search([('employee_id', '=', employee_id), ], limit=1)

        curr_date = kw_attendance_log.employee_id.get_employee_tz_today().date() if kw_attendance_log else check_in_utc.date()
        prev_date = curr_date - timedelta(days=1)

        if ((kw_attendance_log.is_cross_shift and kw_attendance_log.attendance_recorded_date in [curr_date, prev_date]) \
            or (not kw_attendance_log.is_cross_shift and kw_attendance_log.attendance_recorded_date == curr_date)) \
                and kw_attendance_log.check_in_status in [IN_STATUS_LE, IN_STATUS_EXTRA_LE] \
                and kw_attendance_log.le_state in ['0', False] and not kw_attendance_log.is_on_tour:
            if kw_attendance_log.late_entry_reason == False:
                url = self.generate_le_url(curr_date, kw_attendance_log)
        return url   

    def action_name(self):
        self.env['kw_daily_employee_attendance'].create_daily_attendance(self, 'check_in')

    @api.model
    def generate_le_url(self, atd_date, atd_log_rec):
        # print("Yes")
        raw_string = """{0}##{1}##{2}""".format(atd_date, atd_log_rec.id, datetime.now())
        # raw_string  = bytes(raw_string, 'utf-8') 
        # print(raw_string)
        enc_string = kw_helpers.encrypt_msg(raw_string)
        enc_uid = base64.b64encode(enc_string).decode('utf8')
        # print(enc_uid) #
        return f'/late_entry/{enc_uid}'

    @api.model
    def _user_landing_page(self):
        """returns : landing url""" 
        # try:
        #     action_id = self.env.ref('kw_hr_attendance.action_my_office_time').id
        #     menu_id   = self.env.ref('hr_attendance.menu_hr_attendance_root').id or self.env.ref('kw_hr_attendance.menu_my_office_time').id 
        #     return f"/web?#action={action_id}&menu_id={menu_id}"
        # except Exception:
        #     #values['error'] = e.args[0]
        #     pass

        return "/web"

    @api.model
    def sync_attendance_info_kwantify(self):
        """sync attendance info with kwantify server -- called by the ir action cron"""
        daily_employee_attendance = self.env['kw_daily_employee_attendance']
        start_date = datetime.strptime("2020-10-09", "%Y-%m-%d")

        un_sync_attendance = daily_employee_attendance.search(
            [('kw_sync_status', '=', False), ('attendance_recorded_date', '>=', start_date), ('check_in', '!=', False)], limit=100, order="attendance_recorded_date desc")

        # print(un_sync_attendance)
        # un_sync_attendance.share_attendance_info_with_kwantify()
        for rec in un_sync_attendance:
            rec.share_attendance_info_with_kwantify()

        return True 

    # #send custom email by changing the model description

    def attendance_send_custom_mail(self, res_id, force_send=False, raise_exception=False, email_values=None,
                                    notif_layout=False, template_layout=False, ctx_params=None, description=False):
        template = self.env.ref(template_layout)
        if template:
            # template.with_context(extra_params).send_mail(emp_rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")

            values = template.with_context(ctx_params).generate_email(res_id)
            values['recipient_ids'] = [(4, pid) for pid in values.get('partner_ids', list())]
            values.update(email_values or {})
            # print(values)                    

            # add a protection against void email_from
            if 'email_from' in values and not values.get('email_from'):
                values.pop('email_from')
            # encapsulate body
            if notif_layout and values['body_html']:
                try:
                    notif_template = self.env.ref(notif_layout, raise_if_not_found=True)
                except ValueError:
                    pass
                else:
                    record = self.env[template.model].browse(res_id)
                    template_ctx = {
                        'message': self.env['mail.message'].sudo().new(dict(body=values['body_html'], record_name=record.display_name)),
                        'model_description': description if description else self.env['ir.model']._get(record._name).display_name,
                        'company': 'company_id' in record and record['company_id'] or self.env.user.company_id,
                    }
                    body = notif_template.render(template_ctx, engine='ir.qweb', minimal_qcontext=True)
                    values['body_html'] = self.env['mail.thread']._replace_local_links(body)

            mail = self.env['mail.mail'].create(values)

            if force_send:
                mail.send(raise_exception=raise_exception)
            return mail.id  
