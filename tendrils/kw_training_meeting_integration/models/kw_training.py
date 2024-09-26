# -*- coding: utf-8 -*-
from odoo import models,fields,api
from odoo.exceptions import ValidationError

class TrainingIn(models.Model):
    _inherit = "kw_training"

    online_training_available = fields.Boolean(string="Online Meeting Available",compute="_compute_online_meeting_available")
    
    @api.multi
    def _compute_online_meeting_available(self):
        for training in self:
            if training.session_ids.filtered('disable_meeting'):
                training.online_training_available = True
    
    @api.multi
    def join_online_meeting(self):
        available_session = self.session_ids.filtered('disable_meeting')
        if not available_session:
            raise ValidationError("No online training available right now.\nPlease refresh current page.")
        else:
            return available_session[-1].action_join_online_meeting()

    @api.multi
    def unlink(self):
        '''
        cases when a training can't be deleted.
            1-assessment having assessment id from skill
            2-attendance updated for a session
            3-meeting is booked for a session i.e meeting id from meeting schedule
         '''
        for training in self:
            if training.session_ids:
                session_having_attendance_id = training.session_ids.filtered(
                    lambda r: r.attendance_id.id >0)
                if session_having_attendance_id:
                    raise ValidationError(f"Training {training.name} can't be deleted due to \
                        attendance is updated for session {session_having_attendance_id[0].subject}")
                session_having_meeting_id = training.session_ids.filtered(
                    lambda r: r.meeting_id.id >0)
                if session_having_meeting_id:
                    raise ValidationError(f"Training {training.name} can't be deleted due to \
                        meeting is booked for session {session_having_meeting_id[0].subject}")
            if training.assessment_ids:
                assessment_having_assessment_id = training.assessment_ids.filtered(
                    lambda r: r.assessment_id.id >0)
                if assessment_having_assessment_id:
                    raise ValidationError(f"Training {training.name} can't be deleted due to \
                        test is configured for assessment {assessment_having_assessment_id[0].name}")
        result = super(TrainingIn, self).unlink()
        return result