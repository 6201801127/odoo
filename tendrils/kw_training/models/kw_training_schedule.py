# -*- coding: utf-8 -*-
import pytz
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from  odoo.exceptions import ValidationError

class TrainingSchedule(models.Model):
    _name = "kw_training_schedule"
    _description = "Kwantify Training Schedule"
    _rec_name = "subject"

    @api.model
    def _get_time_list(self):
        dt = datetime.now()
        start_loop = dt.replace(hour=7, minute=45, second=0, microsecond=0)
        end_loop = dt.replace(hour=22, minute=0, second=0, microsecond=0)
        time_list = []
        while start_loop < end_loop:
            start_loop = (start_loop+relativedelta(minutes=+15))
            time_list.append((start_loop.strftime('%H:%M:%S'),
                              start_loop.strftime('%I:%M %p')))
        return time_list

    @api.model
    def default_get(self, fields):
        res = super(TrainingSchedule, self).default_get(fields)
        tr_id = self._context.get('default_training_id', False)
        if tr_id:
            training_id = self.env['kw_training'].browse(tr_id)
            if training_id and training_id.plan_ids \
                                    and not training_id.plan_ids.internal_user_ids:
                res['instructor_visibility'] = True
            if training_id and training_id.plan_ids \
                                    and  training_id.plan_ids.instructor_partner:
                res['instructor_partner'] = training_id.plan_ids.instructor_partner.id
        return res

    @api.model
    def _get_domain(self):
        tr_id = self._context.get('default_training_id',False)
        if tr_id:
            training_id = self.env['kw_training'].browse(tr_id)
            if training_id and training_id.plan_ids \
                                            and training_id.plan_ids.internal_user_ids:
                return ['|',('active','=',True),('active','=',False),('id', 'in', [r.id for r in training_id.plan_ids.internal_user_ids])]

    @api.model
    def _get_partner_domain(self):
        tr_id = self._context.get('default_training_id', False)
        if tr_id:
            training_id = self.env['kw_training'].browse(tr_id)
            if training_id and training_id.plan_ids \
                    and training_id.plan_ids.instructor_partner:
                return [('id', '=', training_id.plan_ids.instructor_partner.id)]
    
    instructor_visibility = fields.Boolean('Instructor Visibility',default=False)
    training_id = fields.Many2one("kw_training", string="Training ID",required=True,ondelete="cascade")
    instructor = fields.Many2one("hr.employee",string="Instructor",domain=_get_domain)
    instructor_partner = fields.Many2one("res.partner",string="Instructor(External)",domain=_get_partner_domain)
    subject = fields.Char(string="Session",required=True)
    session_type = fields.Selection(string="Venue",
                                    selection=[('inside', 'Indoor'),('outside','Outdoor'),('online','Online')],
                                    required=True)

    date = fields.Date("Date", default=fields.Date.context_today,required=True)
    from_time = fields.Selection(string='Start Time',selection='_get_time_list', required=True)
    to_time = fields.Selection(string='End Time',selection='_get_time_list', required=True)
    attendance_id = fields.Many2one("kw_training_attendance",string="Attendance") # to take attendance manually
    instructor_name = fields.Char(string="Instructor ",compute='_compute_instructor')
    instructor_type = fields.Selection(string="Type",selection=[('internal',"Internal"),('external','External')],compute="_compute_instructor_type")
    is_attended = fields.Boolean("Attended ?",compute="_compute_is_attended",default=False)
    attendance_present = fields.Char("Partcipant", compute="_compute_is_attended", default="Not Attended")
    meeting_time_over = fields.Boolean(string="Meeting Time Over",compute="_compute_meeting_time_over",default=False)
    session_started = fields.Boolean(string="Session Started")
    

    @api.constrains('date','from_time', 'to_time')
    def validate_schedule_date(self):
        for record in self:
            if record.from_time > record.to_time:
                raise ValidationError(f'Start time should not greater than End time : \
                    {datetime.strptime(record.from_time, "%H:%M:%S").strftime("%I:%M %p")} > {datetime.strptime(record.to_time, "%H:%M:%S").strftime("%I:%M %p")}.')

            existing_session = self.env['kw_training_schedule'].search(
                ['&',('training_id', '=', record.training_id.id),'&',('date','=',record.date),
                '|','&',('from_time','>=',record.from_time),('from_time', '<=', record.to_time),'&',
                 ('to_time', '>=', record.from_time), ('to_time', '<=', record.to_time)]) - record
            if existing_session:
                raise ValidationError("A session has already planned in this time.")
           
            if not (record.training_id.start_date <= record.date <= record.training_id.end_date):
                raise ValidationError(f"Session date must be between training \
                    start and end date.i.e \n From  {record.training_id.start_date} to {record.training_id.end_date}")

    @api.multi
    def _compute_meeting_time_over(self):
        for session in self:
            if session.from_time:
                user_tz = pytz.timezone(self.env.user.tz) if self.env.user.tz else pytz.utc
                curr_datetime = datetime.now(tz=user_tz).replace(tzinfo=None)
                session_date = session.date
                session_from = session.from_time
                session_time = datetime(session_date.year, session_date.month, session_date.day,
                                        int(session_from.split(':')[0]), int(session_from.split(':')[1]), 0)
                if curr_datetime > session_time:
                    session.meeting_time_over = True

    @api.multi
    def _compute_is_attended(self):
        uid = self._uid
        emp_id = self.env['hr.employee'].search([('user_id','=',uid)],limit=1)
        for record in self:
            if emp_id:
                if record.training_id and record.training_id.plan_ids and record.training_id.plan_ids[0].participant_ids:
                    emp_is_attendee = record.training_id.plan_ids[0].participant_ids.filtered(lambda r: r.id == emp_id.id)
                    if emp_is_attendee and record.attendance_id and record.attendance_id.attendance_detail_ids:
                                emp_attended = record.attendance_id.attendance_detail_ids.filtered(
                                            lambda r: r.participant_id.id == emp_id.id and r.attended == True)
                                record.is_attended = True if emp_attended else False
                                record.attendance_present = "Attended" if emp_attended else "Not Attended"
            
    @api.multi
    def _compute_instructor(self):
        for rec in self:
            rec.instructor_name = 'External' if rec.instructor_partner else rec.instructor.name

    @api.multi
    def _compute_instructor_type(self):
        for rec in self:
            rec.instructor_type ='external' if rec.instructor_partner else 'internal'

    @api.multi
    def view_attendance(self):

        attendance_form_view_id = self.env.ref("kw_training.view_kw_training_attendance_form").id
        _action =  {
            'name': 'Attendance',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_training_attendance',
            'view_type': 'form',
            'views': [(attendance_form_view_id, 'form')],
            'view_id': attendance_form_view_id,
            'flags': {'action_buttons': True, 'mode': 'edit'},
        }
        
        if self.attendance_id:
            _action['res_id'] = self.attendance_id.id

        else:
            # Return form view for attendance
            participants = self.training_id.plan_ids[0].participant_ids
            _action['context'] = {
                'default_training_id': self.training_id.id,
                'default_attendance_detail_ids': [[0, 0,{"participant_id": participant.id, "attended": False}] for participant in participants],
                'default_session_id': self.id,
                }

        return _action
    
    @api.multi
    def unlink(self):
        for session in self:
            if session.attendance_id:
                raise ValidationError(
                    f"Attendance for  {session.subject} is updated.Hence it can't be deleted.")
            
        result = super(TrainingSchedule, self).unlink()
    
        return result
    
