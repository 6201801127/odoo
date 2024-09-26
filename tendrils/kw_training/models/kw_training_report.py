# -*- coding: utf-8 -*-
from odoo import tools
from odoo import models, fields, api

class kw_training_report(models.Model):
    _name           = "kw_training_report"
    _description    = "Training Report"
    _auto           = False

    fiscal_year = fields.Char(string='Fiscal Year',) 
    course = fields.Char(string='Course')
    name = fields.Char(string='Training Name')
    instructor_type = fields.Char(string='Instructor Type')
    totalattendee = fields.Integer(string="Total Attendee")
    totalpaticipatedper = fields.Float(string='Total Participated')
    feedbackpercentage = fields.Float(string='Feedback Percentage')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(""" CREATE or REPLACE VIEW %s as (		
			with training as 
			(
				select t.id, y.name as fiscalyear, s.name as course, t.name, instructor_type
				from kw_training t 
				join account_fiscalyear y on y.id=t.financial_year
				join kw_skill_master s on s.id=t.course_id
			), attendee as
			(
				select p.training_id, count(hr_employee_id) as totalattendee
				from kw_training_plan p 
				join hr_employee_kw_training_plan_rel pr on pr.kw_training_plan_id=p.id
				group by p.training_id
			)
			, attendance as
			(
				select training_id, sum(case when attendance_status=1 then 1 else 0 end) as totalpaticipated from 
				(
					select training_id, participant_id, max(case when attended='true' then 1 else 0 end) as attendance_status from 
					(
						select s.training_id, a.participant_id, attended
						from kw_training_schedule s
						join kw_training_attendance_details a on a.attendance_id=s.attendance_id
					) training_attendance
					group by training_id, participant_id
				) attendance_count
				group by training_id
			), feedback as
			(
				select training_id, sum(case when feedbackpercentage>=60 then 1 else 0 end) as Totfeedback from 
				(
					select training_id, emp_id, sum(quizz_mark)*100.00/sum(fullmark) feedbackpercentage
					from kw_training_feedback tf
					join survey_user_input_line sl on sl.user_input_id=tf.response_id
					join (select question_id, max(quizz_mark) as Fullmark from survey_label group by question_id) l on l.question_id=sl.question_id
					where answer_type='suggestion'
					group by training_id, emp_id
				) user_input
				group by training_id
			)
			select t.id as id,fiscalyear as fiscal_year, course as course, name as name, INITCAP(instructor_type) as instructor_type, totalattendee as totalattendee
			, TRUNC(coalesce(totalpaticipated*100.00/totalattendee, 0), 2) as totalpaticipatedper
			, TRUNC(coalesce(Totfeedback*100.00/totalattendee, 0),2) as feedbackpercentage
			from training t 
			join attendee p on p.training_id=t.id
			join attendance a on a.training_id=t.id
			left join feedback f on f.training_id=t.id

        )""" % (self._table))


   