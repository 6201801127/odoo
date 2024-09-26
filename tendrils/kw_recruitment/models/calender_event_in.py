# -*- coding: utf-8 -*-
import datetime
import dateutil.parser
from werkzeug import urls
import time
from datetime import timedelta
from odoo import models, fields, api
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import ValidationError

class Calender_recruitment(models.Model):
    _inherit = "calendar.event"

    @api.model
    def _default_partners(self):
        """ When active_model is res.partner, the current partners should be attendees """
        partners = self.env.user.partner_id
        active_id = self._context.get('active_id')
        if self._context.get('active_model') == 'res.partner' and active_id:
            if active_id not in partners.ids:
                partners |= self.env['res.partner'].browse(active_id)
        return partners

    # --------Additional Fields----------#
    survey_id = fields.Many2one('survey.survey', string="Survey", readonly=False,
                                domain="[('survey_type.code', '=', 'recr')]")
    # response_id = fields.Many2one(
    #     'survey.user_input', "Response", ondelete="set null", oldname="response")
    # response_ids = fields.One2many('survey.user_input','meeting_id' "Response", ondelete="set null", oldname="response")

    response_ids = fields.One2many(string='Meeting Feedback', comodel_name='survey.user_input',
                                   inverse_name='meeting_id',
                                   ondelete='restrict'
                                   )
    current_uid = fields.Boolean("Current User ID", compute="_compute_uid")
    mode_of_interview = fields.Selection(string='Mode Of Interview',
                                         selection=[('Face to Face', 'Face to Face'), ('Telephonic', 'Telephonic'),
                                                    ('Video Conference', 'Video Conference'), ], required=False)
    get_date = fields.Char(string='Get Date', store=True)
    get_time = fields.Char(string='Get time', store=True)

    # --------Additional Fields----------#
    # ---------Modified fields-----------#
    partner_ids = fields.Many2many('res.partner', 'calendar_event_res_partner_rel', string='Attendees', states={
        'done': [('readonly', True)]},
                                   domain=[["user_ids", "!=", False]],
                                   default=_default_partners)

    # ---------Modified fields-----------#

    @api.multi
    def start_meeting_survey(self):
        self.ensure_one()
        if self.survey_id and not self.response_id:
            response = self.env['survey.user_input'].create(
                {'survey_id': self.survey_id.id, 'type': 'manually', 'applicant_id': self.applicant_id.id})
            self.response_id = response.id
            return self.survey_id.with_context(survey_token=response.token).action_start_kw_recruitment_survey()
        elif self.survey_id and self.response_id:
            response = self.response_id
            return self.survey_id.with_context(survey_token=response.token).action_start_kw_recruitment_survey()

    # @api.multi
    # def view_meeting_survey(self):
    #     """ If response is available then print this response otherwise print survey form (print template of the survey) """
    #     self.ensure_one()
    #     if not self.response_id:
    #         return self.survey_id.action_print_survey()
    #     else:
    #         response = self.response_id
    #         return self.survey_id.with_context(survey_token=response.token).action_start_kw_recruitment_survey()

    @api.multi
    def view_meeting_survey(self):
        """ If response is available then print this response otherwise print survey form (print template of the
        survey) """
        self.ensure_one()
        if not self.response_id:
            return self.survey_id.action_print_recruitment_survey()
        else:
            response = self.response_id
            return self.survey_id.with_context(survey_token=response.token).action_print_recruitment_survey()

    @api.multi
    def _compute_uid(self):
        for record in self:
            if self.env.user.has_group('hr_recruitment.group_hr_recruitment_manager'):
                record.current_uid = True
            else:
                if record.create_uid.id == self.env.user.id:
                    record.current_uid = True
                else:
                    record.current_uid = False

    @api.model
    def create(self, vals):
        if vals.get('start_datetime'):
            str_datetime = vals.get('start_datetime').split(" ")
            vals['get_date'] = str_datetime[0]
            vals['get_time'] = str_datetime[1]
        record = super(Calender_recruitment, self).create(vals)
        email = self.env.user.email
        current_user = self.env.user
        if email:
            for meeting in record:
                # template=self.env.ref('kw_recruitment.calendar_template_meeting_invitation')
                # for attendee in meeting.attendee_ids:
                #     template.send_mail(attendee.id,force_send=False)
                attendees = [attendee.name for attendee in meeting.partner_ids]

                for attendee in meeting.partner_ids:
                    tagged_user = self.env['res.users'].sudo().search([('partner_id', '=', attendee.id)])
                    if len(tagged_user) > 0:
                        ch_obj = self.env['mail.channel']
                        channel1 = tagged_user.name + ', ' + self.env.user.name
                        channel2 = self.env.user.name + ', ' + tagged_user.name
                        channel = ch_obj.sudo().search(["|",
                                                        ('name', 'ilike', str(channel1)),
                                                        ('name', 'ilike', str(channel2))
                                                        ])
                        if not channel:
                            channel_id = ch_obj.channel_get([tagged_user.partner_id.id])
                            channel = ch_obj.browse([channel_id['id']])
                        channel[0].message_post(
                            body=f"Meeting scheduled with <br>{'<br>'.join(attendees)} <br> Time:  {record.start_datetime + timedelta(hours=5, minutes=30)}",
                            message_type='comment', subtype='mail.mt_comment',
                            author_id=self.env.user.partner_id.id,
                            notif_layout='mail.mail_notification_light')
                    if meeting.survey_id and meeting.applicant_id:
                        self.env['survey.user_input'].create({
                            'meeting_id': meeting.id,
                            'survey_id': meeting.survey_id.id,
                            'partner_id': attendee.id,
                            'type': 'link',
                            'applicant_id': meeting.applicant_id.id
                        })

                if meeting.applicant_id:
                    template = self.env.ref('kw_recruitment.kw_applicant_intimatation_email_template')
                    if template:
                        template.send_mail(meeting.id, force_send=True)

                # send email to attendee Meeting Invitation
                self.notify_attendees(record.id)

        self.env.user.notify_success("Meeting created successfully.")
        return record

    @api.multi
    def write(self, values):
        for record in self:
            if values.get('start_datetime'):
                str_datetime = values.get('start_datetime').split(" ")
                values['get_date'] = str_datetime[0]
                values['get_time'] = str_datetime[1]
            if record.applicant_id:
                if 'partner_ids' in values and 'survey_id' not in values:
                    if record.response_ids:
                        if len(values['partner_ids'][0][2]) == 0:
                            given_partner = record.response_ids.filtered(lambda r: r.state != "new")
                            if given_partner:
                                raise ValidationError(f"{record.response_ids[0].partner_id.name} is given feedback .Can't be removed.")
                            else:
                                record.response_ids = False
                        else:
                            new_partners = self.env['res.partner'].sudo().browse(values['partner_ids'][0][2]) - record.partner_ids
                            old_partners = record.partner_ids - self.env['res.partner'].sudo().browse(values['partner_ids'][0][2])
                            given_feedback = record.response_ids.filtered(lambda r: r.partner_id.id in old_partners.ids and r.state != "new")
                            if given_feedback:
                                raise ValidationError(f"The user {given_feedback[0].partner_id.name} has given feedback so cant be removed.")
                            else:
                                new_user_input = []
                                for partner_old in old_partners:
                                    partner_response = record.response_ids.filtered(lambda r: r.partner_id.id == partner_old.id)
                                    if partner_response:
                                        # new_user_input.append(
                                        #     (2, partner_response.id))
                                        partner_response.unlink()
                                for ptnr in new_partners:
                                    new_user_input.append(
                                        (0, 0, {'meeting_id': record.id, 'survey_id': record.survey_id.id,
                                                'partner_id': ptnr.id, 'type': 'link',
                                                'applicant_id': record.applicant_id.id}))
                                record.response_ids = new_user_input
                    elif len(values['partner_ids'][0][2]) > 0 and record.survey_id:
                        added_partners = self.env['res.partner'].sudo().browse(values['partner_ids'][0][2])
                        survey_id = record.survey_id.id
                        new_user_input = []
                        for partner in added_partners:
                            new_user_input.append(
                                (0, 0, {'meeting_id': record.id, 'survey_id': survey_id, 'partner_id': partner.id,
                                        'type': 'link', 'applicant_id': record.applicant_id.id}))
                        record.response_ids = new_user_input

                elif 'survey_id' in values and 'partner_ids' not in values:
                    if record.response_ids:
                        given_feedback = record.response_ids.filtered(lambda r: r.state != 'new')
                        if given_feedback:
                            raise ValidationError(f"{given_feedback[0].partner_id.name} already given feedback so feedback form can't be changed.")
                        else:
                            if not values['survey_id']:
                                record.response_ids = False
                            else:
                                record.response_ids.write({'survey_id': values['survey_id']})
                elif 'survey_id' and 'partner_ids' in values:
                    if record.response_ids:
                        given_feedback = record.response_ids.filtered(lambda r: r.state != 'new')
                        if given_feedback:
                            if not values['survey_id']:
                                raise ValidationError(f"feedback form can't be removed due to{given_feedback[0].partner_id.name} is given feedback")
                            elif values['survey_id'] != given_feedback[0].survey_id.id:
                                raise ValidationError(f"feedback form can't be modified because {given_feedback[0].partner_id.name} is given feedback")
                            partner_given_feedback = given_feedback.mapped('partner_id') - self.env['res.partner'].sudo().browse(values['partner_ids'][0][2])
                            if partner_given_feedback:
                                raise ValidationError(f"user {partner_given_feedback[0].name} can't be removed due to he is given feedback")
                        else:
                            if not values['survey_id']:
                                record.response_ids = False
                            elif len(values['partner_ids'][0][2]) == 0:
                                record.response_ids = False
                            else:
                                survey_id = values['survey_id']
                                new_partners = self.env['res.partner'].sudo().browse(values['partner_ids'][0][2]) - record.partner_ids
                                old_partners = record.partner_ids - self.env['res.partner'].sudo().browse(values['partner_ids'][0][2])
                                new_user_input = []
                                for partner_old in old_partners:
                                    partner_response = record.response_ids.filtered(lambda r: r.partner_id.id == partner_old.id)
                                    if partner_response:
                                        # new_user_input.append(
                                        #     (2, partner_response.id))
                                        partner_response.unlink()
                                for ptnr in new_partners:
                                    new_user_input.append(
                                        (0, 0, {'meeting_id': record.id, 'survey_id': survey_id, 'partner_id': ptnr.id,
                                                'type': 'link', 'applicant_id': record.applicant_id.id}))
                                record.response_ids = new_user_input
                                record.response_ids.write({'survey_id': survey_id})
                    elif values['survey_id'] and len(values['partner_ids'][0][2]) > 0:
                        added_partners = self.env['res.partner'].sudo().browse(values['partner_ids'][0][2])
                        survey_id = values['survey_id']
                        new_user_input = []
                        for partner in added_partners:
                            new_user_input.append(
                                (0, 0, {'meeting_id': record.id, 'survey_id': survey_id, 'partner_id': partner.id,
                                        'type': 'link', 'applicant_id': record.applicant_id.id}))
                        record.response_ids = new_user_input

            partners = record.partner_ids.ids
            if 'partner_ids' in values and len(values['partner_ids'][0][2]) > 0:
                for p_id in values['partner_ids'][0][2]:
                    if p_id not in partners:
                        tagged_user = self.env['res.users'].sudo().search([('partner_id', '=', p_id)])
                        attendees = [attendee.name for attendee in record.partner_ids]
                        if tagged_user:
                            attendees.append(tagged_user.name)
                            ch_obj = self.env['mail.channel']
                            channel1 = tagged_user.name + ', ' + self.env.user.name
                            channel2 = self.env.user.name + ', ' + tagged_user.name
                            channel = ch_obj.sudo().search(["|",
                                                            ('name', 'ilike',
                                                             str(channel1)),
                                                            ('name', 'ilike', str(channel2))])
                            if not channel:
                                channel_id = ch_obj.channel_get([tagged_user.partner_id.id])
                                channel = ch_obj.browse([channel_id['id']])
                            channel.message_post(
                                body=f"Meeting scheduled with <br>{'<br>'.join(attendees)} <br> Time:  {record.start_datetime + timedelta(hours=5, minutes=30)}",
                                message_type='comment', subtype='mail.mt_comment',
                                author_id=self.env.user.partner_id.id,
                                notif_layout='mail.mail_notification_light')
                        # template = self.env.ref(
                        #     'kw_recruitment.calendar_template_meeting_invitation')
                        # attendee = self.env['calendar.attendee'].sudo().search(
                        #     ['&', ('id', '=', record.id), ('partner_id', '=', p_id)])
                        # template.send_mail(attendee.id,force_send=False)
        result = super(Calender_recruitment, self).write(values)

        return result

    @api.multi
    def view_redirect(self):
        applicant = self.env['hr.applicant'].sudo().search([('id', '=', self.applicant_id.id)]).id
        tree_view_id = self.env.ref('kw_recruitment.kw_recruitment_view_attachment_tree').id
        return {
            'name': 'Attachments',
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': tree_view_id,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'domain': [('res_model', '=', 'hr.applicant'), ('res_id', '=', applicant)],
            'target': 'current',
        }

    @api.multi
    def done_meeting(self):
        if self.activity_ids:
            self.activity_ids.action_feedback()
            self.env.user.notify_success("Meeting Done Successfully.")

    @api.multi
    def create_attendees(self):
        current_user = self.env.user
        result = {}
        for meeting in self:
            alreay_meeting_partners = meeting.attendee_ids.mapped('partner_id')
            meeting_attendees = self.env['calendar.attendee']
            meeting_partners = self.env['res.partner']
            for partner in meeting.partner_ids.filtered(lambda partner: partner not in alreay_meeting_partners):
                values = {
                    'partner_id': partner.id,
                    'email': partner.email,
                    'event_id': meeting.id,
                }

                if self._context.get('google_internal_event_id', False):
                    values['google_internal_event_id'] = self._context.get('google_internal_event_id')

                # current user don't have to accept his own meeting
                if partner == self.env.user.partner_id:
                    values['state'] = 'accepted'

                attendee = self.env['calendar.attendee'].create(values)

                meeting_attendees |= attendee
                meeting_partners |= partner

            if meeting_attendees:
                meeting.write({'attendee_ids': [(4, meeting_attendee.id) for meeting_attendee in meeting_attendees]})

            # # send email to attendee Meeting Invitation
            # if meeting_attendees and not self._context.get('detaching'):
            #     to_notify = meeting_attendees.filtered(lambda a: a.email != current_user.email)
            #     to_notify._send_mail_to_attendees('kw_recruitment.calendar_template_meeting_invitation_recruitment')

            if meeting_partners:
                meeting.message_subscribe(partner_ids=meeting_partners.ids)

            # We remove old attendees who are not in partner_ids now.
            all_partners = meeting.partner_ids
            all_partner_attendees = meeting.attendee_ids.mapped('partner_id')
            old_attendees = meeting.attendee_ids
            partners_to_remove = all_partner_attendees + meeting_partners - all_partners

            attendees_to_remove = self.env["calendar.attendee"]
            if partners_to_remove:
                attendees_to_remove = self.env["calendar.attendee"].search(
                    [('partner_id', 'in', partners_to_remove.ids), ('event_id', '=', meeting.id)])
                attendees_to_remove.unlink()

            result[meeting.id] = {
                'new_attendees': meeting_attendees,
                'old_attendees': old_attendees,
                'removed_attendees': attendees_to_remove,
                'removed_partners': partners_to_remove
            }
        return result

    @api.model
    def notify_attendees(self, event_id):
        current_user = self.env.user
        attendees = self.env['calendar.attendee'].search([('event_id', '=', event_id)])
        if attendees and not self._context.get('detaching'):
            to_notify = attendees.filtered(lambda a: a.email != current_user.email)
            to_notify._send_mail_to_attendees('kw_recruitment.calendar_template_meeting_invitation_recruitment')
