# -*- coding: utf-8 -*-
import re
import uuid
import base64
from odoo import models, fields, api, tools
from odoo.exceptions import ValidationError, UserError
from kw_utility_tools import kw_validations
from odoo.tools.translate import _
from datetime import datetime


class Kw_Meeting_External_Participants(models.Model):
    _name = 'kw_meeting_external_participants'
    _description = 'Meeting Information'
    _rec_name = 'name'
    _order = 'name ASC'

    name = fields.Char(string='Name', compute='_compute_name', store=True)
    designation = fields.Char(string='Designation', )
    email = fields.Char(string='Email', store=True)
    is_saved_attendee = fields.Boolean(default=False)
    mobile_no = fields.Char(string='Mobile No')
    phone = fields.Char(string='Phone')
    partner_id = fields.Many2one(string='Partner', comodel_name='res.partner')
    meeting_id = fields.Many2one(string='meeting', comodel_name='kw_meeting_events', ondelete='restrict')
    # announcement_id = fields.Many2one(string='Announcement',comodel_name='kw_announcement',ondelete='restrict')
    attendance_status = fields.Boolean(string='Attended Meeting', )

    _sql_constraints = [
        ('partner_unique', 'unique (meeting_id,partner_id)', 'Please remove duplicate participant from list !'),
    ]

    @api.constrains('phone')
    def check_phone(self):
        for record in self:
            if record.phone:
                if not re.match("^[0-9+/-]*$", str(record.phone)) is not None:
                    raise ValidationError("Phone number is invalid for: %s" % record.phone)

    @api.constrains('email')
    def check_email_from(self):
        for record in self:
            kw_validations.validate_email(record.email)

    @api.depends('partner_id')
    def _compute_name(self):
        for attendee in self:
            attendee.name = attendee.partner_id.name or attendee.email

    @api.onchange('email')
    def _onchange_partner_id(self):
        kw_validations.validate_email(self.email)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """ Make entry on email and availability on change of partner_id field. """
        self.email = self.partner_id.email
        self.name = self.partner_id.name
        self.phone = self.partner_id.phone

    @api.model
    def create(self, values):
        if values.get('partner_id') and values.get('phone') or values.get('email'):
            partner = self.env['res.partner'].search([('id', '=', values.get('partner_id'))])
            if partner:
                partner.write({'phone': values.get('phone'), 'email': values.get('email')})
        return super(Kw_Meeting_External_Participants, self).create(values)

    @api.multi
    def write(self, values):
        vals = {}
        if values.get('phone'):
            vals['phone'] = values.get('phone')
        elif values.get('email'):
            vals['email'] = values.get('email')
        self.partner_id.write(vals)
        return super(Kw_Meeting_External_Participants, self).write(values)

    @api.multi
    def _send_mail_to_external_attendees(self, template_xmlid, force_send=False):
        """ Send mail for event invitation to event External attendees.
            :param template_xmlid: xml id of the email template to use to send the invitation
            :param force_send: if set to True, the mail(s) will be sent immediately (instead of the next queue processing)
        """
        res = False
        mails_to_send = self.env['mail.mail']

        if self.env['ir.config_parameter'].sudo().get_param('calendar.block_mail') or self._context.get("no_mail_to_attendees"):
            return res

        calendar_view = self.env.ref('kw_meeting_schedule.view_kw_meeting_schedule_calendar_event_calendar')
        invitation_template = self.env.ref(template_xmlid)

        # #attachment id if any
        if self.mapped('meeting_id'):
            event_id = self.mapped('meeting_id')[0]
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
                    meeting_attachment_id = int(val[0])

                if meeting_attachment_id:
                    attachment_data = self.env['ir.attachment'].browse([meeting_attachment_id])
                    attachment_data.generate_access_token()

            # get ics file for all meetings
            ics_files = self.mapped('meeting_id')._get_ics_file()

            # prepare rendering context for mail template
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
                'base_url': self.env['ir.config_parameter'].sudo().get_param('web.base.url',
                                                                             default='http://localhost:8069'),

            })
            invitation_template = invitation_template.with_context(rendering_context)

            """# send email with attachments"""

            for attendee in self:
                if attendee.partner_id.email:
                    # FIXME: is ics_file text or bytes?
                    ics_file = ics_files.get(attendee.meeting_id.id)
                    mail_id = invitation_template.send_mail(attendee.id, notif_layout='kwantify_theme.csm_mail_notification_light')
                    # mail_id = invitation_template.send_mail(attendee.id, notif_layout='mail.mail_notification_light')

                    vals = {}
                    if ics_file:
                        vals['attachment_ids'] = [(0, 0, {'name': 'invitation.ics',
                                                          'mimetype': 'text/calendar',
                                                          'datas_fname': 'invitation.ics',
                                                          'datas': base64.b64encode(ics_file)})]
                    # #if attachment is there then send it in email
                    if attendee.meeting_id.reference_document and meeting_attachment_id:
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

    # #send whatsapp message
    @api.multi
    def send_whatsAppmessage_to_participants(self):
        kw_whatsapp_message_log_model = self.env['kw_whatsapp_message_log']
        kw_whatsapp_message_log_data = []
        for attendee in self:
            if attendee.phone:
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


    # #send sms to attendees
    @api.multi
    def send_sms_to_attendees(self, message, category):

        sms_log_model = self.env['sms_log']
        sms_log_data = []
        for attendee in self:
            if attendee.employee_id.mobile_phone:
                # """Meeting scheduled by {meeting_scheduler},TIME: {meeting_date} for {meeting_subject},Venue: {meeting_venue}"""
                try:
                    sms_log_data.append(
                        {'mobile_no': attendee.employee_id.mobile_phone, 'message_id': message, 'category': category})

                except Exception as e:
                    # raise Warning("Some error occurred while sending sms: %s" % str(e))
                    # print("Some error occurred while sending sms: %s" % str(e))
                    pass

        if len(sms_log_data) > 0:
            sms_log_model.create(sms_log_data)
