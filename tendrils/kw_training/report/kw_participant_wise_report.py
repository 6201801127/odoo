from odoo import models, fields, api
from odoo import tools

class SkillEnhancementReport(models.Model):
    _name = 'kw_participant_wise_report'
    _description = 'Participant wise report'

    _auto = False
    _rec_name = 'employee_name'

    financial_year = fields.Char("Financial Year")
    topic = fields.Char("Topic")
    employee_name = fields.Char("Employee Name")
    attendance_status = fields.Char("Attendance Status")
    session_attended = fields.Integer("Session Attended")
    pretest_status = fields.Char("Pre-Test Status")
    pretest_score = fields.Integer("Pre-Test Score")
    posttest_status = fields.Char("Post-Test Status")
    posttest_score = fields.Integer("Post-Test Score") 
    improvements = fields.Integer("Skill Enhancement")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(""" CREATE or REPLACE VIEW %s as (	
            with nominated_participants as
            (
                select af.name as financial_year, ktp.training_id as training_id,
                kt.name as topic, emp.hr_employee_id as emp_id,
                hr.name as employee_name
                from hr_employee_kw_training_plan_rel emp 
                join kw_training_plan ktp on ktp.id = emp.kw_training_plan_id and ktp.state = 'approved'
                join hr_employee hr on hr.id = emp.hr_employee_id
                join kw_training kt on kt.id = ktp.training_id
                join account_fiscalyear af on af.id = kt.financial_year
            ), pretest_score as
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
                select training_id, emp_id, score
                from pre
                where id in (select id from (select row_number() over(partition by training_id order by id desc) as slno, id from kw_training_assessment where test_type = 'pre')  pr where slno=1)
            ), posttest_score as
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
                select training_id, emp_id, score from post
                where id in 
                (select id from (select row_number() over(partition by training_id order by id desc) as slno, id from kw_training_assessment where test_type = 'post')  pr where slno=1)
            ),actual_attendee as
            (
                select training_id ,participant_id, session_count,
                case
                    when total_attended >= 75.00 then 'Attended' else 'Not Attended' end
                as attendance_status
                from 
                (
                select kta.training_id, ktad.participant_id,
                sum(
                case
                    when ktad.attended = 't' then 1 else 0 end
                )*100.00/count(kta.session_id) as total_attended,
                sum(case when ktad.attended = 't' then 1 else 0 end) as session_count
                from kw_training_attendance kta
                join kw_training_attendance_details ktad on ktad.attendance_id = kta.id 
                group by kta.training_id, ktad.participant_id
                ) b group by training_id,participant_id,total_attended, session_count
            )

            select ROW_NUMBER () OVER (ORDER BY np.training_id) as id,
            np.financial_year as financial_year,np.training_id as training_id, np.topic, 
            np.emp_id as employee_id, np.employee_name as employee_name,
            coalesce(aa.attendance_status,'Not Attended') as attendance_status, 
            coalesce(aa.session_count,0) as session_attended,
            case when pre.score is not null then 'Given' else 'Not Given' end as pretest_status,
            coalesce(pre.score,0) as pretest_score, 
            case when post.score is not null then 'Given' else 'Not Given' end as posttest_status,
            coalesce(post.score,0) as posttest_score,
            coalesce(post.score,0) - coalesce(pre.score,0) as improvements
            from nominated_participants np
            left join pretest_score pre on pre.training_id = np.training_id and pre.emp_id = np.emp_id
            left join posttest_score post on post.training_id = np.training_id and post.emp_id = np.emp_id
            left join actual_attendee aa on aa.training_id = np.training_id and aa.participant_id = np.emp_id
            order by improvements desc
        )""" % (self._table))	