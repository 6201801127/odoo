# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import ValidationError


class HrApplicant(models.Model):
    _inherit = "hr.applicant"
    _rec_name = "partner_name"
    _order = "id desc"

    schedule_meeting_count = fields.Integer(compute='_compute_kwmeeting_count', help='Meeting Count')

    def _compute_interview_data(self):
        meeting_events = self.env['kw_meeting_events'].sudo()
        for rec in self:
            meetings = self.env['kw_meeting_events'].sudo().search([('applicant_ids','=',rec.id)],order='kw_start_meeting_date asc')
            for index, ele in enumerate(meetings.ids):
                if index == 0:
                    rec.first_round_date = meeting_events.browse(ele).kw_start_meeting_date
                    rec.first_round_panel = self._compute_panel_info(ele, rec.id)
                    rec.first_round_feedback = self._compute_feedback(ele, rec.id)
                if index == 1:
                    rec.second_round_date = meeting_events.browse(ele).kw_start_meeting_date
                    rec.second_round_panel = self._compute_panel_info(ele, rec.id)
                    rec.second_round_feedback = self._compute_feedback(ele, rec.id)
                if index == 2:
                    rec.third_round_date = meeting_events.browse(ele).kw_start_meeting_date
                    rec.third_round_panel = self._compute_panel_info(ele, rec.id)
                    rec.third_round_feedback = self._compute_feedback(ele, rec.id)
                if index == 3:
                    rec.forth_round_date = meeting_events.browse(ele).kw_start_meeting_date
                    rec.fouth_round_panel = self._compute_panel_info(ele, rec.id)
                    rec.forth_round_feedback = self._compute_feedback(ele, rec.id)
                if index == 4:
                    rec.fifth_round_date = meeting_events.browse(ele).kw_start_meeting_date
                    rec.fifth_round_panel = self._compute_panel_info(ele, rec.id)
                    rec.fifth_round_feedback = self._compute_feedback(ele, rec.id)

    @api.multi
    def _compute_panel_info(self, meeting, applicant):
        final_op = ''
        score_status = ''
        for feedback_input in self.env['kw_meeting_events'].sudo().browse(meeting).mapped('response_ids').filtered(lambda r: r.applicant_id.id == applicant):
            status = ''
            score = ''
            interviewer = ''
            interviewer = feedback_input.partner_id.name
            for line in feedback_input.user_input_line_ids:
                if line.question_id.question == 'Status':
                    status = line.value_suggested.value
                if line.question_id.question == 'Grand Total':
                    score = str(int(line.value_number))
            if score and status:
                score_status = "("+status+"|"+score+")"
            else:
                score_status = ''
            if final_op == '':
                final_op = interviewer + score_status
            else:
                final_op += " | " + interviewer + score_status
        return final_op

    @api.multi
    def _compute_feedback(self, meeting, applicant):
        feed_lst = []
        final_status = ''

        for feedback_input in self.env['kw_meeting_events'].sudo().browse(meeting).mapped('response_ids').filtered(lambda r: r.applicant_id.id == applicant):
            status = ''
            if not feedback_input.user_input_line_ids:
                status = 'Not Submitted'
                feed_lst.append(status)
            for line in feedback_input.user_input_line_ids:
                if line.question_id.question == 'Status':
                    status = line.value_suggested.value
                    feed_lst.append(status)

        feed_lst = list(set(feed_lst))
        # print(feed_lst)
        if 'Recommended' in feed_lst:
            final_status = 'Recommended'
        elif 'Recommended' not in feed_lst and 'Hold' in feed_lst:
            final_status = 'Hold'
        elif all(item in feed_lst for item in ['Hold', 'Recommended']) and 'Not Recommended' in feed_lst:
            final_status = 'Not Recommended'
        else:
            final_status = 'Not Submitted'
        return final_status

    first_round_date = fields.Date('1st Round Date', compute='_compute_interview_data')
    first_round_panel = fields.Char('1st Round Panel',compute='_compute_interview_data')
    first_round_feedback = fields.Char('1st Round Feedback',compute='_compute_interview_data')
    second_round_date = fields.Date('2nd Round Date', compute='_compute_interview_data')
    second_round_panel = fields.Char('2nd Round Panel',compute='_compute_interview_data')
    second_round_feedback = fields.Char('2nd Round Feedback',compute='_compute_interview_data')
    third_round_date = fields.Date('3rd Round Date', compute='_compute_interview_data')
    third_round_panel = fields.Char('3rd Round Panel',compute='_compute_interview_data')
    third_round_feedback = fields.Char('3rd Round Feedback',compute='_compute_interview_data')
    forth_round_date = fields.Date('4th Round Date', compute='_compute_interview_data')
    fouth_round_panel = fields.Char('4th Round Panel',compute='_compute_interview_data')
    forth_round_feedback = fields.Char('4th Round Feedback',compute='_compute_interview_data')
    fifth_round_date = fields.Date('5th Round Date', compute='_compute_interview_data')
    fifth_round_panel = fields.Char('5th Round Panel',compute='_compute_interview_data')
    fifth_round_feedback = fields.Char('5th Round Feedback', compute='_compute_interview_data')

    def _compute_kwmeeting_count(self):
        for applicant in self:
            # applicant.schedule_meeting_count = self.env['kw_meeting_events'].search_count([('applicant_ids', '=', applicant.id)])
            c=0
            for i in self.env['kw_meeting_events'].search([('applicant_ids', '=', applicant.id)]):
                if i.state != 'cancelled':
                    c += 1
            applicant.schedule_meeting_count = c
           
    @api.multi
    def action_makeMeeting_schedule(self):
        """ This opens Meeting's calendar view to schedule meeting on current applicant
            @return: Dictionary value for created Meeting view
        """
        # for applicant in self:
        #     applicant.schedule_meeting_count = self.env['kw_meeting_events'].search_count(
        #         [('applicant_ids', '=', applicant.id)])

        # for records in self:
        #     feedback_record = self.env['kw_meeting_events'].sudo().search([('applicant_ids','=',records.id)])
        #     # print(feedback_record[-1])
        #     if records.schedule_meeting_count > 0:
        #         for rec in feedback_record[-1]:
        #             for response in rec.response_ids.filtered(lambda r: r.applicant_id.id == records.id):
        #                 if response.state == 'new' :
        #                     raise ValidationError(f'You cant not Schedule interview for {records.partner_name} as feedback is not given for previous meeting')
        #                 else :
        #                     self.ensure_one()
        #                     res = self.env['ir.actions.act_window'].for_xml_id('kw_meeting_schedule', 'action_window_kw_meeting_schedule')
        #                     meetingtype = self.env['calendar.event.type'].search([('code', '=', 'interview')],limit=1)
        #                     res['domain'] = [('applicant_ids', 'in', [self.id])]
        #                     res['context'] = {
        #                         'visible': False,
        #                         'default_applicant_ids': [(6, 0, [self.id])],
        #                         'default_user_id': self.env.uid,
        #                         'default_name': "Interview schedule -",
        #                         'default_meeting_type_id': meetingtype.id,
        #                         'default_is_meeting_responsible': True
        #                     }
        #                     return res
        #     else:
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('kw_meeting_schedule', 'action_window_kw_meeting_schedule')
        meetingtype = self.env['calendar.event.type'].search([('code', '=', 'interview')],limit=1)
        res['domain'] = [('applicant_ids', 'in', [self.id])]
        res['context'] = {
            'visible': False,
            'default_applicant_ids': [(6, 0, [self.id])],
            'default_user_id': self.env.uid,
            'default_name': "Interview schedule -",
            'default_meeting_type_id': meetingtype.id,
            'default_is_meeting_responsible': True
        }
        return res

    @api.multi
    def action_get_meetings_tree_view(self):
        meeting_action = self.env.ref('kw_meeting_schedule.action_window_kw_meeting_schedule')
        action = meeting_action.read()[0]
        action['domain'] = [('applicant_ids', 'in', self.id)]
        action['search_view_id'] = (self.env.ref('kw_meeting_schedule.view_kw_meeting_calendar_search').id, )
        return action

    # #send whatsapp message
    @api.multi
    def send_whatsAppmessage_to_applicants(self, meeting):
        kw_whatsapp_message_log_model = self.env['kw_whatsapp_message_log']
        kw_whatsapp_message_log_data = []
        for applicant in self:
            try:
                meeting_agenda = ", ".join(meeting.agenda_ids.mapped('name'))
                # participants = ", ".join(meeting.employee_ids.mapped('name'))

                meeting_datetime = meeting.display_time
                if meeting.recurrency:
                    meeting_date = ", ".join([mix.split('at')[0] for mix in meeting.child_ids.mapped('display_time')])
                else:
                    meeting_date = meeting.kw_start_meeting_date.strftime('%d-%b-%Y')
                meeting_time = datetime.strptime(meeting.kw_start_meeting_time,'%H:%M:%S').strftime('%I:%M %p')

                message = meeting.whatsapp_message.format(name=applicant.partner_name,
                                                                    meeting_scheduler=meeting.user_id.name,
                                                                    meeting_subject=meeting.name,
                                                                    meeting_date=meeting_date,
                                                                    meeting_time=meeting_time,
                                                                    meeting_venue=meeting.meeting_room_id.name if meeting.meeting_room_id else 'NA',
                                                                    meeting_agenda=meeting_agenda,
                                                                    mom_controller='NA',
                                                                    participants='NA',
                                                                    meeting_link=meeting.online_meeting_join_url if meeting.online_meeting_join_url else 'NA' )

                mobile_no = '+91' + applicant.partner_mobile
                html_msg = message.replace('\\n', '\n')
                kw_whatsapp_message_log_data.append({'mobile_no': mobile_no, 'message': html_msg})
            except Exception as e:
                # raise Warning("Some error occurred while sending whatsApp notification: %s" % str(e))
                # print("Some error occurred while sending whatsApp notification: %s" % str(e))
                pass

        if len(kw_whatsapp_message_log_data) > 0:
            kw_whatsapp_message_log_model.create(kw_whatsapp_message_log_data)
