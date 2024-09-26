# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import operator
import uuid
import re
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class MeetingEvent(models.Model):
    _inherit = "kw_meeting_events"

    applicant_ids = fields.Many2many('hr.applicant', string="Applicant",
                                     domain=['|', ('active', '=', True), ('active', '=', False)])
    # ('stage_code', '!=', 'OA'),
    survey_id = fields.Many2one('survey.survey', string="Interview Form", domain=[('survey_type.code', '=', 'recr')])

    response_ids = fields.One2many(string='Meeting Feedback', comodel_name='survey.user_input',
                                   inverse_name='kw_meeting_id', ondelete='restrict')
    mode_of_interview = fields.Selection(string='Mode Of Interview',
                                         selection=[
                                             ('face2face', 'Face to Face'),
                                             ('telephonic', 'Telephonic'),
                                             ('teamviewer', 'Team Viewer'),
                                             ('practical', 'Practical Test'),
                                             ('videoconf', 'Video Conference')])
    meetingtype_code = fields.Char('code')
    telephone = fields.Char('Phone')
    recr_online_meeting = fields.Selection(string='VC Details', selection=[('zoom', 'Zoom'), ('other', 'Others')])
    recr_other_meeting_url = fields.Char('Other Meeting URL')
    send_to_panel = fields.Boolean('Send to Panel')
    send_to_applicant = fields.Boolean('Send to Applicant')
    app_mail_check = fields.Boolean('Applicant mail check', default=False)
    pan_mail_check = fields.Boolean('Panel Member mail check', default=False)
    c_id = fields.Many2one('res.users', string="create id")
    applicant_names = fields.Char(compute='_compute_applicant', store=True)
    is_feedbacks_completed = fields.Boolean('Check Feedback Completion', compute='_compute_is_feedbacks_completed')

    @api.multi
    @api.depends("survey_id")
    def _compute_is_feedbacks_completed(self):
        # print("method called")
        for rec in self:
            feedback_records = self.env['survey.user_input'].search(
                [('partner_id', '=', rec.env.user.partner_id.id), ('state', '=', 'new'),
                 ('kw_meeting_id', '=', rec.id)])
            # print("feedbacks===",feedback_records)
            if not feedback_records:
                rec.is_feedbacks_completed = True
            else:
                rec.is_feedbacks_completed = False

    @api.depends('applicant_ids')
    def _compute_applicant(self):
        for meeting in self:
            applicant_list = []
            for rec in meeting.applicant_ids:
                applicant_list.append(rec.partner_name)
            meeting.applicant_names = ', '.join(applicant_list)

    def isValidURL(self, url):
        # Regex to check valid URL
        regex = ("((http|https)://)(www.)?" +
                 "[a-zA-Z0-9@:%._\\-+~#?&//=]" +
                 "{2,256}\\.[a-z]" +
                 "{2,6}\\b([-a-zA-Z0-9@:%" +
                 "._\\+~#?&//=]*)")

        # Compile the ReGex
        p = re.compile(regex)

        # If the string is empty
        # return false
        if (url == None):
            return False

        # Return if the string
        # matched the ReGex
        if (re.search(p, url)):
            return True
        else:
            return False

    """ action to view meeting Feedback"""
    def action_meeting_feedback(self):
        view_id = self.env.ref('kw_recruitment_meeting_schedule.view_meeting_schedule_response_popup_form').id
        target_id = self.id
        return {
            'name': 'Meeting Feedback',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_meeting_events',
            'res_id': target_id,
            'target': 'new',
            'view_type': 'form',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'context': {"create": False, "edit": False, 'meeting_feedback_ckeck': True},
            'domain': [('response_ids.partner_id', '=', self.env.user.employee_ids.id)],
            'flags': {'toolbar': False, 'action_buttons': False, 'mode': 'readonly'},
        }

    @api.constrains('recr_other_meeting_url')
    def validate_recr_other_meeting_url(self):
        if self.recr_other_meeting_url:
            if not (self.isValidURL(self.recr_other_meeting_url) == True):
                raise ValidationError("Please use a proper URL.")

    @api.constrains('agenda_ids', 'meeting_room_id', 'categ_ids', 'meeting_category')
    def validate_agenda(self):
        for record in self:
            if not record.meeting_room_id and not record.online_meeting \
                    and record.mode_of_interview not in ['telephonic', 'teamviewer', 'practical']:
                raise ValidationError("Please select meeting room/online meeting.")

            if not record.agenda_ids:
                raise ValidationError("Please enter meeting agenda details.")

            if not record.categ_ids and not self._context.get('pass_validation'):
                raise ValidationError("Please select at least one Meeting Type.")

            if not record.meeting_category:
                raise ValidationError("Please select meeting category.")

    @api.onchange('mode_of_interview')
    def _onchange_mode_of_interview(self):
        if self.mode_of_interview == 'face2face':
            self.telephone = False
        elif self.mode_of_interview == 'videoconf':
            self.telephone = False

    @api.multi
    def open_feedback_wizard(self):
        wizard_form_view = self.env.ref('kw_recruitment_meeting_schedule.kw_recruitment_meeting_applicant_feedback_wizard_form')
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'kw_applicant_feedback',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': wizard_form_view.id,
            'target': 'new',
        }

    @api.onchange('meeting_type_id')
    def set_categ_ids(self):
        for record in self:
            record.categ_ids = record.meeting_type_id
            record.meetingtype_code = record.meeting_type_id.code

    @api.onchange('recr_online_meeting')
    def onchange_recr_online_meeting(self):
        if self.recr_online_meeting == 'zoom':
            self.recr_other_meeting_url = None
            if not self.env.user.zoom_id:
                raise UserError(_("Please link your zoom account to create zoom meeting."))
            if self.env.user.zoom_id.active == False:
                raise UserError(_("Zoom account activation still pending. Please wait."))

    @api.onchange('applicant_ids')
    def onchange_applicant_ids_(self):
        applicants = self.applicant_ids
        for applicant in applicants:
            meeting_count = self.env['kw_meeting_events'].search_count([('applicant_ids', '=', applicant.id), ('state', '!=', 'cancelled')])
            meetings = self.env['kw_meeting_events'].search([('applicant_ids', '=', applicant.id), ('state', '!=', 'cancelled')])
            if meeting_count > 0:
                for rec in sorted(meetings[-1]):
                    for response in rec.response_ids.filtered(lambda r: r.applicant_id.id == applicant.id):
                        if response.state == 'new':
                            raise ValidationError(f'You cant not Schedule interview for {response.applicant_id.partner_name} as feedback is not given for previous meeting')

    @api.model
    def create(self, vals):
        if vals.get('recr_other_meeting_url'):
            vals['other_meeting_url'] = vals.get('recr_other_meeting_url')
        if vals.get('recr_online_meeting'):
            vals['online_meeting'] = vals.get('recr_online_meeting')
        record = super(MeetingEvent, self).create(vals)
        email = self.env.user.email
        whatsapp_enabled = self.env['ir.config_parameter'].sudo().get_param('kw_auth.enable_whatsapp')

        if record.applicant_ids:
            for applicant in record.applicant_ids:
                new_stage = self.env['hr.recruitment.stage']
                if applicant.stage_id.code in ['IQ', 'SL']:
                    new_stage = self.env['hr.recruitment.stage'].search([('code', '=', 'FI')])
                if applicant.stage_id.code in ['FI']:
                    new_stage = self.env['hr.recruitment.stage'].search([('code', '=', 'SI')])
                if applicant.stage_id.code in ['SI']:
                    new_stage = self.env['hr.recruitment.stage'].search([('code', '=', 'TI')])
                if new_stage:
                    applicant.write({'stage_id':new_stage.id})
        if email:
            template = self.env.ref('kw_recruitment_meeting_schedule.kw_applicant_intimatation_email_template_schedule')
            mail_template = self.env['mail.template'].browse(template.id)
            calendar_view = self.env.ref('kw_meeting_schedule.view_kw_meeting_schedule_calendar_event_calendar')
            action_id = self.env['ir.actions.act_window'].search([('view_id', '=', calendar_view.id)], limit=1).id
            db_name = self._cr.dbname
            panel_template = self.env.ref('kw_recruitment_meeting_schedule.template_meeting_invitation_attendees')
            panel_mail = self.env['mail.template'].browse(panel_template.id)

            """check if session user is a portal user"""
            email_from_cc = False
            is_portal_user = False
            if not self.env['res.users'].sudo().browse(vals.get('create_uid',self.env.user.id)).has_group('base.group_user'):
                is_portal_user = True

            for meeting in record:
                # send email while creating meeting
                if meeting.survey_id and meeting.applicant_ids:
                    """change cc and from to hr responsible user"""
                    if is_portal_user:
                        email_from_cc = meeting.applicant_ids[0].job_position.user_id.partner_id.email
                    for applicant_id in meeting.applicant_ids:
                        if whatsapp_enabled and len(applicant_id.partner_mobile) == 10:
                            applicant_id.send_whatsAppmessage_to_applicants(meeting)

                        """Applicant email  and vals.get('send_to_applicant')"""
                        if template:
                            if meeting.survey_id.title == 'Interview Feedback_HR':
                                subject = 'HR Discussion | CSM Technologies'
                            else:
                                subject = 'Interview Schedule | CSM Technologies'

                            applicant_mail = mail_template.with_context(
                                applicantname=applicant_id.partner_name,
                                jobposition=applicant_id.job_position.title,
                                emailfrom=email_from_cc,
                                emailcc=email_from_cc,
                                is_portal_user=is_portal_user,
                                candidateprofile=applicant_id.job_position.description if applicant_id.job_position.description else '-',
                                email_to=applicant_id.email_from,
                                subject=subject).send_mail(meeting.id, force_send=False)
                            vals = {}
                            vals['model'] = None  # We don't want to have the mail in the chatter while in queue!
                            vals['res_id'] = False
                            current_mail = self.env['mail.mail'].browse(applicant_mail)
                            current_mail.mail_message_id.write(vals)

                        for attendee in meeting.employee_ids:
                            """#Email to Attendees"""
                            user_input = self.env['survey.user_input'].sudo().create({
                                'kw_meeting_id': meeting.id,
                                'survey_id': meeting.survey_id.id,
                                'partner_id': attendee.user_id.partner_id.id,
                                'type': 'link',
                                'applicant_id': applicant_id.id
                            })

                    """# get ics file for all meetings"""
                    ics_files = meeting._get_ics_file()
                    ics_file = ics_files.get(meeting.id)

                    """Panel member email and vals.get('send_to_panel')"""
                    if panel_template:
                        for attendee in meeting.employee_ids:
                            surveys = meeting.response_ids.filtered(lambda panel: panel.partner_id.id == attendee.user_id.partner_id.id)
                            lst_info = []
                            for usrinput in surveys:
                                dct_info = {}
                                dct_info['survey_url'] = f"{usrinput.survey_id.recruitment_survey_url}/{usrinput.token}"
                                dct_info['partnername'] = usrinput.applicant_id.partner_name
                                dct_info['applicant_id'] = usrinput.applicant_id.id
                                lst_info.append(dct_info)
                            meeting_attendee = self.env['kw_meeting_attendee'].search([('event_id', '=', meeting.id), ('employee_id', '=', attendee.id)])
                            access_token = meeting_attendee and meeting_attendee.access_token or False
                            # if is_portal_user:
                            #     email_from_cc = applicant_id.job_position.user_id.partner_id.email
                            mail_id = panel_mail.with_context(
                                dbname=db_name,
                                access_token=access_token,
                                action_id=action_id,
                                subject="Interview Schedule",
                                jobposition=applicant_id.job_position.title,
                                mailto=attendee.user_id.partner_id.email,
                                emailfrom=email_from_cc,
                                emailcc=email_from_cc,
                                is_portal_user=is_portal_user,
                                info=lst_info).send_mail(meeting.id, notif_layout='kwantify_theme.csm_mail_notification_light', force_send=False)

                            vals = {}
                            vals['attachment_ids'] = []

                            if ics_file:
                                vals['attachment_ids'].append([0, 0, {'name': 'invitation.ics',
                                                                      'mimetype': 'text/calendar',
                                                                      'datas_fname': 'invitation.ics',
                                                                      'datas': base64.b64encode(ics_file)}])
                            if meeting.applicant_ids:
                                recruitmentDocObj = self.env['kw_recruitment_documents'].sudo().search(
                                    [('applicant_id', 'in', meeting.applicant_ids.ids)])
                                for irattachment in recruitmentDocObj:
                                    irAttachmentObj = irattachment.ir_attachment_id
                                    vals['attachment_ids'].append([0, 0, {'name': irAttachmentObj.datas_fname,
                                                                         'mimetype': irAttachmentObj.mimetype,
                                                                         'datas_fname': irAttachmentObj.datas_fname,
                                                                         'datas': irattachment.content_file}])

                            vals['model'] = None  # We don't want to have the mail in the chatter while in queue!
                            vals['res_id'] = False
                            current_mail = self.env['mail.mail'].browse(mail_id)
                            current_mail.mail_message_id.write(vals)

        """ Applicant Feedback Report"""
        self.env.user.notify_success("Meeting created successfully.")
        """ Interview Summary Report"""
        if record.meetingtype_code == 'interview':
            panelstr = ' | '.join([panel.name for panel in record.employee_ids])
            # for panel in record.employee_ids:
            #     if panelstr == '':
            #         panelstr = panel.name
            #     else:
            #         panelstr += ' | ' + panel.name
            for rec in record.applicant_ids:
                self.env['kw_interview_summary_report'].create({'applicant_id': rec.id,
                                                                'meeting_id': record.id,
                                                                'interview_date': record.kw_start_meeting_date,
                                                                'panel_member': panelstr,
                                                                'token': uuid.uuid4().hex,
                                                                'mode_of_interview': record.mode_of_interview
                                                                })
        return record

    @api.multi
    def write(self, values):
        result = super(MeetingEvent, self).write(values)
        jobposition1 = 'NA'
        responsible_email = ''
        email_from_cc = ''
        subject = ''
        """check if session user is portal user"""
        is_portal_user = False
        if not self.env['res.users'].sudo().browse(values.get('create_uid',self.env.user.id)).has_group('base.group_user'):
            is_portal_user = True
        if self.applicant_ids:
            jobposition1 = self.applicant_ids[0].job_position.title
            email_from_cc = self.applicant_ids[0].job_position.user_id.partner_id.email
        whatsapp_enabled = self.env['ir.config_parameter'].sudo().get_param('kw_auth.enable_whatsapp')

        if self.survey_id.title == 'Interview Feedback_HR':
            subject = 'HR Discussion | CSM Technologies'
        else:
            subject = 'Interview Schedule | CSM Technologies'

        survey_data = self.env['survey.user_input']
        if values.get('employee_ids'):
            for attendee in values.get('employee_ids'):
                """ Email to Attendees"""
                # self.response_ids.unlink()
                if attendee[2] != [] or False:
                    for panel in attendee[2]:
                        emp = self.env['hr.employee'].browse(panel)
                        panelexist = survey_data.sudo().search(
                            [('partner_id', '=', emp.user_id.partner_id.id), ('kw_meeting_id', '=', self.id)])
                        if not panelexist:
                            for applicant in self.applicant_ids:
                                """ Feedback Link"""
                                user_input = survey_data.sudo().create({
                                    'kw_meeting_id': self.id,
                                    'survey_id': self.survey_id.id,
                                    'partner_id': emp.user_id.partner_id.id,
                                    'type': 'link',
                                    'applicant_id': applicant.id
                                })
        if values.get('applicant_ids'):
            # if self.applicant_ids:
            #     for applicant in self.applicant_ids:
            #         new_stage = self.env['hr.recruitment.stage']
            #         if applicant.stage_id.code in ['IQ', 'SL']:
            #             new_stage = self.env['hr.recruitment.stage'].search([('code', '=', 'FI')])
            #         if applicant.stage_id.code in ['FI']:
            #             new_stage = self.env['hr.recruitment.stage'].search([('code', '=', 'SI')])
            #         if new_stage:
            #             applicant.write({'stage_id': new_stage.id})
            for applicant in values.get('applicant_ids'):
                # """#Email to Attendees"""
                if applicant[2] != [] or False:
                    for app in applicant[2]:
                        appid = self.env['hr.applicant'].browse(app)
                        for attendee in self.employee_ids:
                            applicantexist = survey_data.sudo().search(
                                [('applicant_id', '=', appid.id), ('partner_id', '=', attendee.user_id.partner_id.id),
                                 ('kw_meeting_id', '=', self.id)])
                            if not applicantexist:
                                # Feedback Link
                                user_input = survey_data.sudo().create({
                                    'kw_meeting_id': self.id,
                                    'survey_id': self.survey_id.id,
                                    'partner_id': attendee.user_id.partner_id.id,
                                    'type': 'link',
                                    'applicant_id': appid.id
                                })
                        if len(appid.partner_mobile) == 10 and whatsapp_enabled:
                            appid.send_whatsAppmessage_to_applicants(self)
                        template = self.env.ref('kw_recruitment_meeting_schedule.kw_applicant_intimatation_email_template_schedule')
                        # if template and self.send_to_applicant == True:
                        if template and "send_to_applicant" in values.keys() and values.get('send_to_applicant') == True or "applicant_ids" in values.keys() and len(values) == 1:
                            self.env['mail.template'].browse(template.id).with_context(
                                applicantname=appid.partner_name,
                                jobposition=appid.job_position.title,
                                emailfrom=email_from_cc,
                                emailcc=email_from_cc,
                                is_portal_user=is_portal_user,
                                candidateprofile=appid.job_position.description if appid.job_position.description else '-',
                                email_to=appid.email_from,
                                subject=subject).send_mail(self.id, force_send=False)
                            self.app_mail_check = True
        user_check = self.get_portal_user(self.c_id.id)
        if user_check:
            if not values.get('applicant_ids') and values.get('kw_start_meeting_date') \
                and values.get('kw_start_meeting_time') and values.get('duration') \
                    and values.get('survey_id') and values.get('mode_of_interview') \
                        and values.get('recr_online_meeting') and not self.app_mail_check:
                if values.get('send_to_applicant') == True or self.send_to_applicant == True:
                    self.fire_applicant_mail_data(email_from_cc, is_portal_user, subject)
                    self.app_mail_check = True
        else:
            if not values.get('applicant_ids') or values.get('kw_start_meeting_date') \
                    or values.get('kw_start_meeting_time') or values.get('duration') \
                    or values.get('survey_id') or values.get('mode_of_interview') \
                    or values.get('recr_online_meeting') or values.get('send_to_applicant') \
                    or values.get('employee_ids') or values.get('meeting_room_id'):
                # if values.get('send_to_applicant') == True or self.send_to_applicant == True:
                if values.get('send_to_applicant') == True and "send_to_applicant" in values.keys() \
                        or "meeting_room_id" in values.keys() and self.send_to_panel != True \
                        or values.get('employee_ids') and len(values) <= 2 and self.send_to_applicant == True \
                        or "meeting_room_id" in values.keys() and "location_id" in values.keys() \
                        and self.send_to_applicant == True \
                        or "meeting_room_id" in values.keys() and self.send_to_applicant == True \
                        and len(values) <= 2:
                    if len(values) >= 1:
                        self.fire_applicant_mail_data(email_from_cc, is_portal_user, subject)

        if user_check:
            if values.get('employee_ids') and values.get('applicant_ids') \
                    and values.get('kw_start_meeting_date') \
                    and values.get('kw_start_meeting_time') and values.get('duration') \
                    and values.get('survey_id') and values.get('mode_of_interview') \
                    and values.get('recr_online_meeting') and not self.pan_mail_check:
                if values.get('send_to_panel', False) == True:
                    self.fire_pannel_member_mail_data(email_from_cc, is_portal_user, jobposition1)
                    self.pan_mail_check = True

        else:
            if values.get('employee_ids') or values.get('applicant_ids') \
                    or values.get('kw_start_meeting_date') or values.get('kw_start_meeting_time') \
                    or values.get('duration') or values.get('survey_id') or values.get('mode_of_interview') \
                    or values.get('recr_online_meeting') or values.get('send_to_panel') \
                    or values.get('meeting_room_id'):
                if values.get('send_to_panel', False) == True or self.send_to_panel == True:
                    if len(values) <= 6:
                        self.fire_pannel_member_mail_data(email_from_cc, is_portal_user, jobposition1)

        """ PATCH: Remove records for deleted panel & applicant"""
        for feedback in self.response_ids:
            userlist = self.employee_ids.mapped('user_id').ids
            user = self.env['res.users'].search([('partner_id', '=', feedback.partner_id.id)])
            if user.id not in userlist:
                feedback.unlink()
        for feedback in self.response_ids:
            applist = self.applicant_ids.ids
            if feedback.applicant_id.id not in applist:
                feedback.unlink()
        return result
    
    def get_portal_user(self, values=False):
        is_portal_user = False
        if not self.env['res.users'].sudo().browse(self.c_id.id).has_group('base.group_user'):
            is_portal_user = True
        return is_portal_user

    def fire_applicant_mail_data(self, email_from_cc=False, is_portal_user=False, subject=False):
        template = self.env.ref('kw_recruitment_meeting_schedule.kw_applicant_intimatation_email_template_schedule')
        for appid in self.applicant_ids:
            if template:
                # if is_portal_user:
                #     email_from_cc = appid.job_position.user_id.partner_id.email
                self.env['mail.template'].browse(template.id).with_context(
                    applicantname=appid.partner_name,
                    jobposition=appid.job_position.title,
                    emailfrom=email_from_cc,
                    emailcc=email_from_cc,
                    is_portal_user=is_portal_user,
                    candidateprofile=appid.job_position.description if appid.job_position.description else '-',
                    email_to=appid.email_from,
                    subject=subject).send_mail(self.id, force_send=False)
    
    def fire_pannel_member_mail_data(self, email_from_cc=False, is_portal_user=False, jobposition1=False):
        calendar_view = self.env.ref('kw_meeting_schedule.view_kw_meeting_schedule_calendar_event_calendar')
        action_id = self.env['ir.actions.act_window'].search([('view_id', '=', calendar_view.id)], limit=1).id
        db_name = self._cr.dbname
        panel_template = self.env.ref('kw_recruitment_meeting_schedule.template_meeting_invitation_attendees')
        """# get ics file for all meetings"""
        ics_files = self._get_ics_file()
        ics_file = ics_files.get(self.id)
        if panel_template:
            # if is_portal_user:
            #     email_from_cc = self.applicant_ids[0].job_position.user_id.partner_id.email
            for attendee in self.employee_ids:
                surveys = self.response_ids.filtered(lambda panel: panel.partner_id.id == attendee.user_id.partner_id.id)
                lst_info = []
                if surveys:
                    for usrinput in surveys:
                        dct_info = {
                            'survey_url': f"{usrinput.survey_id.recruitment_survey_url}/{usrinput.token}",
                            'partnername': usrinput.applicant_id.partner_name,
                            'applicant_id': usrinput.applicant_id.id
                        }
                        lst_info.append(dct_info)
                    meeting_attendee = self.env['kw_meeting_attendee'].search([
                                            ('event_id', '=', self.id), ('employee_id', '=', attendee.id)])
                    access_token = meeting_attendee and meeting_attendee.access_token or False
                    mail_id = self.env['mail.template'].browse(panel_template.id).with_context(
                        dbname=db_name,
                        access_token=access_token,
                        action_id=action_id,
                        subject="Interview Schedule",
                        jobposition=jobposition1,
                        mailto=attendee.user_id.partner_id.email,
                        emailfrom=email_from_cc,
                        emailcc=email_from_cc,
                        is_portal_user=is_portal_user,
                        info= lst_info).send_mail(self.id, notif_layout='kwantify_theme.csm_mail_notification_light',force_send=False)
                    vals = {}
                    if ics_file:
                        vals['attachment_ids'] = [(0, 0, {'name': 'invitation.ics',
                                                        'mimetype': 'text/calendar',
                                                        'datas_fname': 'invitation.ics',
                                                        'datas': base64.b64encode(ics_file)})]

                    if self.applicant_ids:
                        applicant_ids_list = self.applicant_ids.mapped('id')
                        for applicant in applicant_ids_list:
                            recruitmentDocObj = self.env['kw_recruitment_documents'].sudo().search(
                                [('applicant_id', '=', applicant)])
                            for irattachment in recruitmentDocObj:
                                irAttachmentObj = irattachment.ir_attachment_id
                                vals['attachment_ids'].append([0, 0, {'name': irAttachmentObj.datas_fname,
                                                                    'mimetype': irAttachmentObj.mimetype,
                                                                    'datas_fname': irAttachmentObj.datas_fname,
                                                                    'datas': irattachment.content_file}])

                    vals['model'] = None  # We don't want to have the mail in the chatter while in queue!
                    vals['res_id'] = False
                    current_mail = self.env['mail.mail'].browse(mail_id)
                    current_mail.mail_message_id.write(vals)

    @api.multi
    def action_open_document(self):
        applicant_ids = self.applicant_ids.ids
        tree_view_id = self.env.ref('kw_recruitment.kw_recruitment_view_attachment_tree').id
        return {
            'name': 'Attachments',
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': tree_view_id,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'domain': [('res_model', '=', 'hr.applicant'), ('res_id', 'in', applicant_ids)],
            'target': 'current',
        }
    
    @api.multi
    def redirect_interview_feedback(self):
        tree_view_id = self.env.ref('kw_recruitment_meeting_schedule.interview_meeting_feedback_list_view').id
        return {
            'name': F"Give Feedback for {self.name}",
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': tree_view_id,
            'res_model': 'survey.user_input',
            'type': 'ir.actions.act_window',
            'domain': [('partner_id', '=', self.env.user.partner_id.id),('state','=','new'),('kw_meeting_id','=',self.id)],
            'target': 'current',
        }

    @api.multi
    def redirect_interview_view_feedback(self):
        tree_view_id = self.env.ref('kw_recruitment_meeting_schedule.interview_meeting_feedback_list_view').id
        return {
            'name': F"View Feedback for {self.name}",
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': tree_view_id,
            'res_model': 'survey.user_input',
            'type': 'ir.actions.act_window',
            'domain': [('partner_id', '=', self.env.user.partner_id.id),('kw_meeting_id','=',self.id)],
            'target': 'current',
        }

    @api.model
    def _interview_summary_report(self):
        old_record_list = []
        interview_list = []
        meeting_record = self.env['kw_meeting_events'].sudo().search([('meetingtype_code', '=', 'interview')])
        interview_record = self.env['kw_interview_summary_report'].sudo().search([])
        for interview in interview_record:
            if interview.meeting_id not in interview_list:
                interview_list.append(interview.meeting_id)
        old_record_list = list(set(meeting_record) - set(interview_list))
        for record in old_record_list:
            panelstr = ' | '.join([panel.name for panel in record.employee_ids])
            # for panel in record.employee_ids:
            #     if panelstr == '':
            #         panelstr = panel.name
            #     else:
            #         panelstr += ' | ' + panel.name
            for rec in record.applicant_ids:
                self.env['kw_interview_summary_report'].create({'applicant_id': rec.id,
                                                                'meeting_id': record.id,
                                                                'interview_date': record.kw_start_meeting_date,
                                                                'panel_member': panelstr,
                                                                'token': uuid.uuid4().hex,
                                                                'mode_of_interview': record.mode_of_interview
                                                                })


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    kw_meeting_id = fields.Many2one('kw_meeting_events', string="Meeting ID")
    score = fields.Integer(compute='_compute_score_remark', help='Total score of the applicant.')
    remark = fields.Char(compute='_compute_score_remark', help='Remarks of the applicant.')
    current_user = fields.Boolean(compute='_get_current_user')
    applicant_id = fields.Many2one('hr.applicant')


