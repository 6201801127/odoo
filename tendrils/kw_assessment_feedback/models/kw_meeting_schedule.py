# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

class FeedbackMeetingScheduleIn(models.Model):
    _inherit = "kw_meeting_events"

    @api.model
    def create(self, values):
        meeting = super(FeedbackMeetingScheduleIn, self).create(values)
        try:
            if 'active_model' in self._context and 'active_id' in self._context:

                feedback = []

                if 'active_model' in self._context and self._context['active_model'] == 'kw_feedback_details':
                    feedback = self.env['kw_feedback_details'].browse(self._context['active_id'])
                    
                elif 'active_model' in self._context and self._context['active_model'] == 'kw_feedback_assessment_period':
                    feedback = self.env['kw_feedback_assessment_period'].browse(self._context['active_id'])

                if feedback :
                    data = {
                        'meeting_id':meeting.id,
                        'assessment_date': meeting.kw_start_meeting_date
                    }
                    
                    feedback.write(data)
        except Exception as e:
            pass
                
        return meeting
    
    @api.multi
    def write(self, values):
        result = super(FeedbackMeetingScheduleIn, self).write(values)
        try:

            for meeting in self:
                details_feedback = self.env['kw_feedback_details'].sudo().search([('meeting_id', '=', meeting.id)])
                period_feedback = self.env['kw_feedback_assessment_period'].sudo().search([('meeting_id', '=', meeting.id)])

                data = {
                    'assessment_date': meeting.kw_start_meeting_date,
                }

                if details_feedback:
                    details_feedback.write(data)

                if period_feedback:
                    period_feedback.write(data)
        except Exception as e:
            pass
        return result
