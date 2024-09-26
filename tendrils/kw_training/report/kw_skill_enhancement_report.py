from odoo import models, fields, api
from odoo import tools

class SkillEnhancementReport(models.Model):
    _name = 'kw_training_skill_enhancement_report'
    _description = 'Traning wise skill enhancement report'

    _auto = False
    _rec_name = 'topic'

    financial_year = fields.Char("Financial Year")
    training_id = fields.Integer("Training Id")
    topic = fields.Char("Topic")
    type = fields.Char("Type")
    total_attendee = fields.Integer("Total Attendee")
    pretest_attendee = fields.Integer("Pre-Test Attendee")
    posttest_attendee = fields.Integer("Post-Test Attendee")
    skill_enhancement_no = fields.Integer("Skill Enhancement No")
    skill_enhancement_per = fields.Float("Skill Enhancement %")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(""" CREATE or REPLACE VIEW %s as (	
            with v_kw_training as
            (
                with nominated_participants as
                (
                    select ktp.training_id as training_id, emp.hr_employee_id as emp_id
                    from hr_employee_kw_training_plan_rel emp 
                    join kw_training_plan ktp on ktp.id = emp.kw_training_plan_id and ktp.state = 'approved'
                    join hr_employee hr on hr.id = emp.hr_employee_id
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
                    select training_id ,participant_id,
                    case
                        when total_attended >= 75.00 then 1 else 0 end
                    as attendance_status
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
                    ) b group by training_id,participant_id,total_attended
                )
                
                select np.training_id as training_id, np.emp_id as employee_id,
                coalesce(aa.attendance_status,0) as attendance_status, 
                case when pre.score is not null then 1 else 0 end as pretest_status,
                coalesce(pre.score,0) as pretest_score, 
                case when post.score is not null then 1 else 0 end as posttest_status,
                coalesce(post.score,0) as posttest_score
                from nominated_participants np
                left join pretest_score pre on pre.training_id = np.training_id and pre.emp_id = np.emp_id
                left join posttest_score post on post.training_id = np.training_id and post.emp_id = np.emp_id
                left join actual_attendee aa on aa.training_id = np.training_id and aa.participant_id = np.emp_id
            )

            select ROW_NUMBER () OVER (ORDER BY vkt.training_id) as id,
            af.name as financial_year,
            vkt.training_id as training_id,
            kt.name as topic, 
            initcap(kt.instructor_type) as type,
            sum (case when vkt.attendance_status = 1 then 1 else 0 end ) as total_attendee,
            sum (case when vkt.pretest_status = 1 then 1 else 0 end ) as pretest_attendee,
            sum (case when vkt.posttest_status = 1 then 1 else 0 end ) as posttest_attendee,
            sum (case when (vkt.posttest_score - vkt.pretest_score) >0 then 1 else 0 end)  as skill_enhancement_no,
            trunc(sum (case when (vkt.posttest_score - vkt.pretest_score) >0 then 1 else 0 end)*100.00/count(vkt.employee_id),2) as skill_enhancement_per
            from v_kw_training vkt
            left join kw_training kt on kt.id = vkt.training_id
            left join account_fiscalyear af on af.id = kt.financial_year
            group by training_id, kt.name, kt.instructor_type, af.name
        )""" % (self._table))	