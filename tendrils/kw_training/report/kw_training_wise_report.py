from odoo import models, fields, api
from odoo import tools

class TrainingWiseReport(models.Model):
    _name = 'kw_training_wise_report'
    _description = 'Traning wise report'

    _auto = False
    _rec_name = 'topic'

    financial_year = fields.Char("Financial Year")
    topic = fields.Char(string = "Topic")
    type = fields.Char(string = "Type")
    current_status = fields.Char(string = "Current Status")
    trainer = fields.Char(string = "Trainer")
    start_date = fields.Date(string = "Start Date")
    end_date = fields.Date(string = "End Date")
    nominated_participants = fields.Integer(string="Nominated Participants")
    total_attendee = fields.Integer(string="Actual Attendee")
    attendance_percentage = fields.Float(string="Attendance %")
    feedback_given = fields.Integer(string="Feedback provided")
    feedback_percentage = fields.Float(string="Feedback %")
    pretest_appeared = fields.Integer(string="Pre-Test Appeared")
    posttest_appeared = fields.Integer(string="Post-Test Appeared")
    cost = fields.Integer(string="Cost")
    duration_in_hrs = fields.Char(string="Duration in Hrs")
    score_percentage = fields.Float(string="Score %")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(""" CREATE or REPLACE VIEW %s as (	
            with trainer_name as
            (
                select plan_id,
                string_AGG(emp.name, ', ') as trainer 
                from training_plan_hremp_rel 
                join hr_employee emp on emp.id = emp_id 
                group by plan_id
            ),
            nominated_participate as
            (
                select count(hr_employee_id) as nominated_participants,
                kw_training_plan_id as p_id 
                from hr_employee_kw_training_plan_rel 
                group by kw_training_plan_id
            ),
            actual_attendee as
            (
                select training_id ,
                sum(
                case
                    when total_attended >= 75.00 then 1 else 0 end
                ) as total_attendee
                from 
                (
                select kta.training_id, ktad.participant_id,
                sum(
                case
                    when ktad.attended = 't' then 1 else 0 end
                )*100.00/count(kta.session_id) as total_attended
                from kw_training_attendance kta
                join kw_training_attendance_details ktad on ktad.attendance_id = kta.id 
                group by kta.training_id, ktad.participant_id
                ) b group by training_id
            ),
            feedback_count as
            (
                select count(training_id) as feedback, training_id from kw_training_feedback group by training_id
            ),
            pretest_count as
            (
                with pre as
                (
                    select kta.id, kta.training_id, sam.emp_rel as emp_id, sam.total_mark_obtained as score
                    from kw_training_assessment kta 
                    join kw_skill_answer_master sam on sam.set_config_id = kta.assessment_id and kta.test_type = 'pre'
                    UNION ALL
                    select kta.id, kta.training_id, ktsd.participant_id as emp_id, ktsd.score
                    from kw_training_assessment kta 
                    join kw_training_score_details ktsd on kta.score_id = ktsd.score_id and kta.test_type = 'pre'
                )
                select training_id, count(emp_id) as pretest_total
                from pre
                where id in (select id from (select row_number() over(partition by training_id order by id desc) as slno, id from kw_training_assessment where test_type = 'pre')  pr where slno=1)
                group by training_id
            ),
            posttest_count as
            (
                with post as
                (
                    select kta.id, kta.training_id, sam.emp_rel as emp_id, sam.total_mark_obtained as score
                    from kw_training_assessment kta 
                    join kw_skill_answer_master sam on sam.set_config_id = kta.assessment_id and kta.test_type = 'post'
                    union all
                    select kta.id, kta.training_id, ktsd.participant_id as emp_id, ktsd.score
                    from kw_training_assessment kta 
                    join kw_training_score_details ktsd on kta.score_id = ktsd.score_id and kta.test_type = 'post'
                )
                select training_id, count(emp_id) as posttest_total 
                from post
                where id in 
                (select id from (select row_number() over(partition by training_id order by id desc) as slno, id from kw_training_assessment where test_type = 'post')  pr where slno=1)
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
            ),
            durartion_in_hrs as
            (
                select training_id,
                coalesce(Cast(TO_CHAR((sum(to_timestamp(to_time,'HH24:MI:SS') - to_timestamp(from_time,'HH24:MI:SS')) || 'hour')::interval, 'HH24:MI') as varchar), '00:00') as duration
                from kw_training_schedule
                group by training_id
            ),
            posttest_score_percentage as 
            (
                with posttest_score_online as
                (
                    select kta.training_id, kta.test_type, sam.emp_rel as emp_id, sam.total_mark_obtained as score
                    from kw_training_assessment kta 
                    join kw_skill_answer_master sam on sam.set_config_id = kta.assessment_id and kta.test_type = 'post'
                    
                ),
                posttest_score_offline as
                (
                    select kta.training_id, kta.test_type, ktsd.participant_id as emp_id, ktsd.score
                    from kw_training_assessment kta 
                    join kw_training_score_details ktsd on kta.score_id = ktsd.score_id and kta.test_type = 'post'
                )
                select ptoff.training_id, ptoff.test_type,
                TRUNC(avg(ptoff.score + pton.score),2) as score
                from posttest_score_offline ptoff
                join posttest_score_online pton on ptoff.training_id = pton.training_id and ptoff.test_type = pton.test_type
                group by ptoff.training_id, ptoff.test_type
            ) 

            select ROW_NUMBER () OVER (ORDER BY kt.id) as id,
            af.name as financial_year,
            kt.name as topic,
            initcap(kt.instructor_type) as type,
            CASE
            WHEN NOW()::date BETWEEN kt.start_date AND kt.end_date and ktp.state = 'approved' then 'In Progress'
            when Now()::date > kt.end_date and ktp.state = 'approved' then 'Completed'
            when ktp.state = 'rejected' then 'Rejected'
            when ktp.state = 'apply' then 'Applied'
            when Now()::date < kt.start_date and ktp.state = 'approved' then 'Not Started'
            when ktp.state is NULL then 'Not Planned'
            END      as current_status,
            tn.trainer as trainer, 
            kt.start_date, kt.end_date,
            coalesce(np.nominated_participants, 0) as nominated_participants, 
            coalesce(a.total_attendee, 0) as total_attendee,
            Round(CAST(coalesce((cast(a.total_attendee as float)*100)/cast(np.nominated_participants as float), 0) as numeric), 2) as attendance_percentage,
            coalesce(fc.feedback, 0) as feedback_given,
            TRUNC(coalesce(Totfeedback*100.00/np.nominated_participants, 0),2) as feedback_percentage,
            coalesce(prec.pretest_total, 0) as pretest_appeared,
            coalesce(postc.posttest_total, 0) as posttest_appeared,
            coalesce(dh.duration,'00:00') as duration_in_hrs,
            coalesce(psp.score,00.00) as score_percentage,
            ktp.cost as cost
            from kw_training kt
            left join account_fiscalyear af on af.id = kt.financial_year
            left join kw_training_plan ktp on ktp.training_id = kt.id
            left join trainer_name tn on ktp.id = tn.plan_id
            left join nominated_participate np on np.p_id = ktp.id
            left join actual_attendee a on a.training_id = kt.id
            left join feedback_count fc on fc.training_id = kt.id
            left join pretest_count prec on prec.training_id = kt.id 
            left join posttest_count postc on postc.training_id = kt.id
            left join feedback f on f.training_id = kt.id
            left join durartion_in_hrs dh on dh.training_id = kt.id
            left join posttest_score_percentage psp on psp.training_id = kt.id

        )""" % (self._table))	
