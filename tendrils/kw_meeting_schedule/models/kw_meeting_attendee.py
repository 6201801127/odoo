import uuid
from datetime import datetime
import base64
from odoo import api, fields, models, tools

from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _


class MeetingAttendee(models.Model):
    """ Calendar Attendee Information """

    _name = 'kw_meeting_attendee'
    _rec_name = 'common_name'
    _description = 'Meeting Information'

    def _default_access_token(self):
        return uuid.uuid4().hex

    STATE_SELECTION = [
        ('needsAction', 'Needs Action'),
        ('tentative', 'Uncertain'),
        ('declined', 'Declined'),
        ('accepted', 'Accepted'),
    ]

    state = fields.Selection(STATE_SELECTION, string='Status', readonly=True, default='needsAction', help="Status of the attendee's participation")
    common_name = fields.Char('Common name', compute='_compute_common_name', store=True)
    partner_id = fields.Many2one('res.partner', 'Contact', readonly="True")
    employee_id = fields.Many2one('hr.employee', 'Employee', domain=[('user_id', '!=', False)])
    image_small = fields.Binary("Small-sized photo", related='employee_id.image_small',attachment=True)
    job_id = fields.Many2one('hr.job', related='employee_id.job_id', string='Job Position')
    whatsapp_no = fields.Char('Whatsapp No', related='employee_id.whatsapp_no', readonly=True, store=False)

    email = fields.Char('Email', help="Email of Invited Person")
    availability = fields.Selection([('free', 'Free'), ('busy', 'Busy')], 'Free/Busy', readonly="True")
    access_token = fields.Char('Invitation Token', default=_default_access_token)
    event_id = fields.Many2one('kw_meeting_events', 'Meeting linked', ondelete='cascade')

    event_recurrency = fields.Boolean('Event Recurrency', related='event_id.recurrency', readonly=True, store=False)
    event_state = fields.Selection('Event State', related='event_id.state', readonly=True, store=False)

    attendance_status = fields.Boolean(string='Attended Meeting',)
    is_external = fields.Boolean(default=False)
    is_saved_attendee = fields.Boolean(default=False)

    _sql_constraints = [
        ('employee_unique', 'unique (event_id,employee_id)', 'Please remove duplicate participant from list !'),
    ]

    @api.depends('employee_id', 'employee_id.name', 'email')
    def _compute_common_name(self):
        for attendee in self:
            attendee.common_name = attendee.employee_id.name if attendee.employee_id else attendee.partner_id.name

    @api.onchange('employee_id')
    def _onchange_partner_id(self):
        """ Make entry on email and availability on change of partner_id field. """
        self.email = self.employee_id.work_email

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if not values.get("email") and values.get("common_name"):
                common_nameval = values.get("common_name").split(':')
                email = [x for x in common_nameval if '@' in x]  # TODO JEM : should be refactored
                values['email'] = email and email[0] or ''
                values['common_name'] = values.get("common_name")
        return super(MeetingAttendee, self).create(vals_list)

    @api.multi
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        raise UserError(_('You cannot duplicate a calendar attendee.'))

    @api.multi
    def _send_mail_to_attendees(self, template_xmlid, force_send=False):
        """ Send mail for event invitation to event attendees.
            :param template_xmlid: xml id of the email template to use to send the invitation
            :param force_send: if set to True, the mail(s) will be sent immediately (instead of the next queue processing)
        """

        # print(self)
        res = False
        mails_to_send = self.env['mail.mail']

        if self.env['ir.config_parameter'].sudo().get_param('calendar.block_mail') or self._context.get("no_mail_to_attendees"):
            return res

        calendar_view = self.env.ref('kw_meeting_schedule.view_kw_meeting_schedule_calendar_event_calendar')
        invitation_template = self.env.ref(template_xmlid)

        """# #attachment id if any"""
        if self.mapped('event_id'):
            event_id = self.mapped('event_id')[0]
        else:
            event_id = False
        meeting_attachment_id = False
        if event_id:
            if event_id.reference_document:
                sql_query = '''
                        SELECT id  FROM ir_attachment
                        WHERE res_model ='{res_model}' and res_id ={res_id} and name ='{name}' ;
                    '''.format(
                    res_model='kw_meeting_events', res_id=event_id.id, name='reference_document'
                )
                self.env.cr.execute(sql_query, [])
                for val in self.env.cr.fetchall():
                    meeting_attachment_id = val[0]

                if meeting_attachment_id:
                    attachment_data = self.env['ir.attachment'].browse([meeting_attachment_id])
                    attachment_data.generate_access_token()

            """# get ics file for all meetings"""
            ics_files = self.mapped('event_id')._get_ics_file()

            """# prepare rendering context for mail template"""
            colors = {
                'needsAction': 'grey',
                'accepted': 'green',
                'tentative': '#FFFF00',
                'declined': 'red'
            }
            rendering_context = dict(self._context)
            rendering_context.update({
                'color': colors,
                'action_id': self.env['ir.actions.act_window'].search([('view_id', '=', calendar_view.id)], limit=1).id,
                'dbname': self._cr.dbname,
                'base_url': self.env['ir.config_parameter'].sudo().get_param('web.base.url', default='http://localhost:8069'),
            })
            invitation_template = invitation_template.with_context(rendering_context)

            """# send email with attachments"""

            for attendee in self:
                if attendee.employee_id.work_email or attendee.partner_id.email:
                    # print('attendee >>> ', attendee)
                    """# FIXME: is ics_file text or bytes?"""
                    ics_file = ics_files.get(attendee.event_id.id)
                    mail_id = invitation_template.send_mail(attendee.id, notif_layout='kwantify_theme.csm_mail_notification_light')
                    # mail_id = invitation_template.send_mail(attendee.id, notif_layout='mail.mail_notification_light')

                    vals = {}
                    if ics_file:
                        vals['attachment_ids'] = [(0, 0, {'name': 'invitation.ics',
                                                          'mimetype': 'text/calendar',
                                                          'datas_fname': 'invitation.ics',
                                                          'datas': base64.b64encode(ics_file)})]
                    """# #if attachment is there then send it in email"""
                    if attendee.event_id.reference_document and meeting_attachment_id:
                        if 'attachment_ids' in vals:
                            vals['attachment_ids'].append((4, meeting_attachment_id, ''))
                        else:
                            vals['attachment_ids'] = [(6, 0, [meeting_attachment_id])]

                    vals['model'] = None  # We don't want to have the mail in the tchatter while in queue!
                    vals['res_id'] = False
                    current_mail = self.env['mail.mail'].browse(mail_id)
                    current_mail.mail_message_id.write(vals)
                    mails_to_send |= current_mail

        if force_send and mails_to_send:
            res = mails_to_send.send()

        return res

    """
    send whatsapp message
    """
    @api.multi
    def send_whatsAppmessage_to_attendees(self):
        kw_whatsapp_message_log_model = self.env['kw_whatsapp_message_log']
        kw_whatsapp_message_log_data = []
        for attendee in self:
            if attendee.whatsapp_no:
                # print(whatsapp_message) whatsapp_message
                # Hi {name}, meeting has been scheduled by {meeting_scheduler} for {meeting_subject} on {meeting_date} in {meeting_venue}. Agenda : *{meeting_agenda}*. MoM  Controller: {mom_controller} . Kindly make yourself available
                try:
                    meeting_agenda = ", ".join(attendee.event_id.agenda_ids.mapped('name'))
                    participants = ", ".join(attendee.event_id.employee_ids.mapped('name'))

                    meeting_datetime = attendee.event_id.display_time
                    if attendee.event_id.recurrency:
                        meeting_date = ", ".join([mix.split('at')[0] for mix in attendee.event_id.child_ids.mapped('display_time')])
                    else:
                        meeting_date = attendee.event_id.kw_start_meeting_date.strftime('%d-%b-%Y')
                    meeting_time = datetime.strptime(attendee.event_id.kw_start_meeting_time,'%H:%M:%S').strftime('%I:%M %p')

                    message = attendee.event_id.whatsapp_message.format(name=attendee.employee_id.name,
                                                                        meeting_scheduler=attendee.event_id.user_id.name,
                                                                        meeting_subject=attendee.event_id.name,
                                                                        meeting_date=meeting_date,
                                                                        meeting_time=meeting_time,
                                                                        meeting_venue=attendee.event_id.meeting_room_id.name if attendee.event_id.meeting_room_id else 'NA',
                                                                        meeting_agenda=meeting_agenda,
                                                                        mom_controller=attendee.event_id.mom_controller_id.name if attendee.event_id.mom_controller_id else 'NA',
                                                                        participants=participants,
                                                                        meeting_link=attendee.event_id.online_meeting_join_url if attendee.event_id.online_meeting_join_url else 'NA' )

                    mobile_no = '+91' + attendee.whatsapp_no
                    html_msg = message.replace('\\n', '\n')
                    kw_whatsapp_message_log_data.append({'mobile_no': mobile_no, 'message': html_msg})
                except Exception as e:
                    # raise Warning("Some error occurred while sending whatsApp notification: %s" % str(e))
                    # print("Some error occurred while sending whatsApp notification: %s" % str(e))
                    pass

        if len(kw_whatsapp_message_log_data) > 0:
            kw_whatsapp_message_log_model.create(kw_whatsapp_message_log_data)

    """
    send sms to attendees
    """
    @api.multi
    def send_sms_to_attendees(self, message, category):
        sms_log_model = self.env['sms_log']
        sms_log_data = []
        for attendee in self:
            if attendee.employee_id.mobile_phone:
                """Meeting scheduled by {meeting_scheduler},TIME: {meeting_date} for {meeting_subject},Venue: {meeting_venue}"""
                try:
                    sms_log_data.append({'mobile_no': attendee.employee_id.mobile_phone, 'message_id': message, 'category': category})

                except Exception as e:
                    # raise Warning("Some error occurred while sending sms: %s" % str(e))
                    # print("Some error occurred while sending sms: %s" % str(e))
                    pass

        if len(sms_log_data) > 0:
            sms_log_model.create(sms_log_data)

    @api.multi
    def do_tentative(self):
        """ Makes event invitation as Tentative. """
        return self.write({'state': 'tentative'})

    @api.multi
    def do_accept(self):
        """ Marks event invitation as Accepted. """
        result = self.write({'state': 'accepted'})
        for attendee in self:
            attendee.event_id.message_post(body=_("%s has accepted invitation") % (attendee.common_name),
                                           subtype="calendar.subtype_invitation")
        return result

    @api.multi
    def do_decline(self):
        """ Marks event invitation as Declined. """
        res = self.write({'state': 'declined'})
        for attendee in self:
            attendee.event_id.message_post(body=_("%s has declined invitation") % (attendee.common_name),
                                           subtype="calendar.subtype_invitation")
        return res

    @api.model
    def find_or_create(self, vals):
        """ Find a partner with the given ``email`` or use :py:method:`~.name_create`
            to create one

            :param str email: email-like string, which should contain at least one email,
                e.g. ``"Raoul Grosbedon <r.g@grosbedon.fr>"``"""
        # assert email, 'an email is required for find_or_create to work'
        # emails = tools.email_split(email)
        # name_emails = tools.email_split_and_format(email)
        if vals.get('partner_id'):
            partner = vals.get('partner_id')
        else:
            partner = False
        record = self.search([('partner_id', '=', partner), ('event_id', '=', vals.get('event_id'))], limit=1)
        return record or self.create(vals)
