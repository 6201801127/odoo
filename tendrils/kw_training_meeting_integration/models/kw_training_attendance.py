# -*- coding: utf-8 -*-
from odoo import models, fields, api

class TrainingAttendanceMeetingIntegration(models.Model):
    _inherit = 'kw_training_attendance'

    @api.model
    def create(self, values):
        # print("meeting attendance create method called")
        result = super(TrainingAttendanceMeetingIntegration, self).create(values)
        # if 'active_model' and 'active_id' in self._context:
        #     if self._context['active_model'] == 'kw_training_schedule':
        #         schedule_rec = self.env['kw_training_schedule'].browse(self._context['active_id'])
        #         if schedule_rec and not schedule_rec.attendance_id:
        #             schedule_rec.attendance_id = result.id
        # session = self.env['kw_training_schedule'].browse(self._context['active_id'])
        # print("Session is ",session , "and attendance id is",session.attendance_id)
        plan = result.training_id.plan_ids[-1] if result.training_id.plan_ids else False
        if plan:
            new_participants = result.attendance_detail_ids.mapped('participant_id') # employees of attendance
            meeting_user_group = self.env.ref('kw_meeting_schedule.group_kw_meeting_schedule_user')

            for participant_emp in new_participants:
                # print("Name is ",participant_emp.name)
                plan.write({'participant_ids': [(4, participant_emp.id)]})

                if participant_emp.user_id:
                    p_user = participant_emp.user_id
                    if not p_user.has_group('kw_meeting_schedule.group_kw_meeting_schedule_user'):
                        meeting_user_group.sudo().write({'users': [(4, p_user.id)]})
            if result.session_id and result.session_id.meeting_id:
                ''' Update attendees of meeting by training '''
                meeting = result.session_id.meeting_id
                new_participants |= meeting.employee_ids
                new_participants |= result.session_id.instructor
                try:
                    # inside try catch to overcome the validationerror in meeting integration and update attendance smoothly
                    # to_update_attendees = new_participants - meeting.employee_ids
                    # for emp in to_update_attendees:
                    #     meeting.employee_ids = [[4,emp.id]]
                        
                    meeting.write({'employee_ids': [[6, 0, new_participants.ids]]})
                except Exception as e:
                    # print("Attendance Update to Meeting Error : ",e)
                    pass

                attended_participant = result.attendance_detail_ids.filtered(lambda r: r.attended == True).mapped('participant_id')
                attended_participant |= result.session_id.instructor

                not_attended_participant = new_participants - attended_participant

                meeting_attended = meeting.attendee_ids.filtered(lambda r: r.employee_id in attended_participant)
                meeting_attended.write({'attendance_status':True})

                meeting_not_attended = meeting.attendee_ids.filtered(lambda r: r.employee_id in not_attended_participant)
                meeting_not_attended.write({'attendance_status': False})
        return result

    @api.multi
    def write(self, values):
        result = super(TrainingAttendanceMeetingIntegration, self).write(values)
        for record in self:
            plan = record.training_id.plan_ids[-1] if record.training_id.plan_ids else False
            if plan:
                new_participants = record.attendance_detail_ids.mapped('participant_id')

                meeting_user_group = self.env.ref('kw_meeting_schedule.group_kw_meeting_schedule_user')
                for participant_emp in new_participants:
                    plan.write({'participant_ids': [(4, participant_emp.id)]})
                    if participant_emp.user_id:
                        p_user = participant_emp.user_id
                        if not p_user.has_group('kw_meeting_schedule.group_kw_meeting_schedule_user'):
                            meeting_user_group.sudo().write({'users': [(4, p_user.id)]})
                if record.session_id and record.session_id.meeting_id:
                    ''' Update attendees of meeting by training '''
                    meeting = record.session_id.meeting_id
                    new_participants |= meeting.employee_ids
                    new_participants |= record.session_id.instructor
                    try:
                        # inside try catch to overcome the validationerror in meeting integration and update attendance smoothly
                        # to_update_attendees = new_participants - meeting.employee_ids
                        # for emp in to_update_attendees:
                        #     meeting.employee_ids = [[4,emp.id]]
                            
                        meeting.write({'employee_ids': [[6, 0, new_participants.ids]]})
                    except Exception as e:
                        # print("Attendance Update to Meeting Error : ",e)
                        pass

                    attended_participant = record.attendance_detail_ids.filtered(lambda r: r.attended == True).mapped('participant_id')
                    attended_participant |= record.session_id.instructor

                    not_attended_participant = new_participants - attended_participant

                    meeting_attended = meeting.attendee_ids.filtered(lambda r: r.employee_id in attended_participant)
                    meeting_attended.write({'attendance_status':True})

                    meeting_not_attended = meeting.attendee_ids.filtered(lambda r: r.employee_id in not_attended_participant)
                    meeting_not_attended.write({'attendance_status': False})

        return result
