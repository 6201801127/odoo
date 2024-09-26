"""Part of odoo. See LICENSE file for full copyright and licensing details."""

import functools
import logging
import datetime
from datetime import date, datetime, timedelta
from odoo import http
from odoo.addons.restful.common import (
    extract_arguments,
    invalid_response,
    valid_response,
)
from odoo.http import request
import pytz
from pytz import timezone

_logger = logging.getLogger(__name__)


class APIController(http.Controller):

    @http.route('/api/get_applicant_info', type="http", auth="public", methods=["GET"], csrf=False, cors='*',website=False)
    def get_applicant_info(self):
        query = request._cr.execute(f""" 
            SELECT Applicant.id as CANDIDATE_ID, Applicant.partner_name as CANDIDATE_NAME, 
CASE WHEN Source.name is NULL THEN NULL  ELSE Source.name END AS RECRUITMENT_SOURCE_NAME, 
CASE WHEN Job.title is NULL THEN NULL  ELSE Job.title END AS JOB_POSITION, 
CASE WHEN Location.name is NULL THEN NULL  ELSE Location.name END AS JOB_LOCATION, 
CASE WHEN Applicant.current_location is NULL THEN NULL  ELSE Applicant.current_location END AS CANDIDATE_LOCATION, 
CASE WHEN Applicant.create_date is NULL THEN NULL  ELSE Applicant.create_date::date::text END AS APPLIED_DATE,
(SELECT date(max(date)) as date FROM mail_message WHERE id in (SELECT mail_message_id FROM mail_tracking_value WHERE new_value_char LIKE '%Shortlist%' ORDER BY id )
and res_id = Applicant.id)  AS SHORT_LIST_DATE, 
CASE WHEN Applicant.offer_date is NULL THEN NULL  ELSE Applicant.offer_date::date::text END AS HIRE_DATE, 
CASE WHEN Applicant.acceptance_date is NULL THEN NULL  ELSE Applicant.acceptance_date::date::text END AS ACCEPTANCE_DATE, 
CASE WHEN Applicant.joining_date is NULL THEN NULL  ELSE Applicant.joining_date::date::text END AS JOINING_DATE, 
CASE WHEN MRF.code is NULL THEN NULL  ELSE MRF.code END AS MRF_NO,
CASE WHEN MRF.code is NULL THEN NULL ELSE MRF.create_date::date::text END AS MRF_DATE,
(select name from kw_job_portal  where id=Applicant.jportal_id) as JOB_PORTAL,
Applicant.exp_year as EXP_YEAR,
Applicant.exp_month as EXP_MONTH
FROM hr_applicant as Applicant
LEFT JOIN utm_source as Source ON Applicant.source_id = Source.id
LEFT JOIN kw_hr_job_positions as Job ON Applicant.job_position = Job.id
LEFT JOIN kw_recruitment_location as Location ON Applicant.job_location_id = Location.id
LEFT JOIN kw_recruitment_requisition as MRF ON Applicant.mrf_id = MRF.id;
""")   
        data = request._cr.dictfetchall()
        if data != []:
            return valid_response(data)
        else:
            return []

    @http.route('/api/get_employee_workstation', type="http", auth="public", methods=["GET"], csrf=False, cors='*',website=False)
    def get_employee_workstation(self):
        query = request._cr.execute(f"""
            SELECT 
wm.id, 
CASE WHEN emp.id is null THEN 0 ELSE emp.id END AS EMPLOYEE_ID,
CASE WHEN emp.name is null THEN 'NA' ELSE emp.name END AS EMPLOYEE_NAME,
wm.name AS WORKSTATION_CODE,
'Bhubaneswar' AS LOCATION,
wt.name AS WS_TYPE,
CASE WHEN emp.issued_system = 'pc' THEN 'Computer' WHEN emp.issued_system = 'laptop' THEN 'Laptop' ELSE 'NA' END AS COMPUTER,
CASE WHEN wm.is_wfh is true THEN 'Yes' ELSE 'No' END AS ISWFH,
wi.name AS INFRASTRUCTURE
FROM kw_workstation_master wm
LEFT JOIN kw_workstation_infrastructure wi on wi.id=wm.infrastructure
LEFT JOIN kw_workstation_type wt on wt.id=wm.workstation_type
LEFT JOIN kw_workstation_hr_employee_rel  we_rel on we_rel.wid=wm.id
LEFT JOIN hr_employee  emp on we_rel.eid=emp.id
ORDER BY wm.id ASC""")  

        data = request._cr.dictfetchall()
        if data != []:
            return valid_response(data)
        else:
            return []

    @http.route('/api/get_interview_panel', type="http", auth="public", methods=["GET"], csrf=False, cors='*',website=False)
    def get_interview_panel(self):
        query = request._cr.execute(f""" 
            SELECT 
Applicant.id as CANDIDATE_ID,
Meeting.id as INTERVIEW_ID, 
Employee.id as EMPLOYEE_ID,
Meeting.meeting_code, 
Meeting.name, 
ApplicantRelation.hr_applicant_id, 
Applicant.partner_name, 
Employee.name
FROM kw_meeting_events as Meeting
LEFT JOIN hr_applicant_kw_meeting_events_rel as ApplicantRelation ON Meeting.id = ApplicantRelation.kw_meeting_events_id
LEFT JOIN hr_applicant as Applicant ON ApplicantRelation.hr_applicant_id = Applicant.id
LEFT JOIN hr_employee_kw_meeting_events_rel as EmployeeRelation ON Meeting.id = EmployeeRelation.kw_meeting_events_id
LEFT JOIN hr_employee as Employee ON Employee.id = EmployeeRelation.hr_employee_id
LEFT JOIN calendar_event_type as event_type ON event_type.id = Meeting.meeting_type_id
where event_type.code = 'interview'
""")   
        data = request._cr.dictfetchall()
        if data != []:
            return valid_response(data)
        else:
            return []

    @http.route('/api/get_interview_candidate', type="http", auth="public", methods=["GET"], csrf=False, cors='*',website=False)
    def get_interview_candidate(self):
        query = request._cr.execute(f"""
SELECT 
max(Meeting.id) AS INTERVIEW_ID, 
Applicant.id as CANDIDATE_ID,
max(Meeting.kw_start_meeting_date) AS INTERVIEW_DATE, 
max(Stage.sequence) as ROUND_TYPE_SEQUENCE,
max(Stage.name) as ROUND_TYPE
FROM kw_meeting_events as Meeting
LEFT JOIN hr_applicant_kw_meeting_events_rel as ApplicantRelation ON Meeting.id = ApplicantRelation.kw_meeting_events_id
LEFT JOIN hr_applicant as Applicant ON ApplicantRelation.hr_applicant_id = Applicant.id
LEFT JOIN hr_recruitment_stage Stage on Stage.id=Applicant.stage_id
LEFT JOIN calendar_event_type as event_type ON event_type.id = Meeting.meeting_type_id
where event_type.code = 'interview'
GROUP BY Applicant.id
ORDER BY INTERVIEW_ID desc, ROUND_TYPE_SEQUENCE desc
""")   
        data = request._cr.dictfetchall()
        if data != []:
            return valid_response(data)
        else:
            return []

    @http.route('/api/get_recr_position_info', type="http", auth="public", methods=["GET"], csrf=False, cors='*',website=False)
    def get_recr_position_info(self):
        query = request._cr.execute(f"""SELECT Applicant.id AS CANDIDATE_ID, 
Applicant.partner_name AS CANDIDATE_NAME, 
CASE WHEN Applicant.exp_year is NULL THEN '0' ELSE Applicant.exp_year END AS CANDIDATE_EXP, 
CASE WHEN Department.name is NULL THEN 'NA' ELSE Department.name END AS DEPT,
CASE WHEN Division.name is NULL THEN 'NA' ELSE Division.name END AS DIV,
CASE WHEN Section.name is NULL THEN 'NA' ELSE Section.name END AS SECT,
CASE WHEN Practice.name is NULL THEN 'NA' ELSE Practice.name END AS PCT, 
Job.name AS DESIGNATION
FROM hr_applicant as Applicant
LEFT JOIN hr_job as Job ON Applicant.job_id=Job.id
LEFT JOIN hr_department as Department ON Applicant.department_id=Department.id and Applicant.division=Department.id
LEFT JOIN hr_department as Division ON Applicant.division=Division.id
LEFT JOIN hr_department as Section ON Applicant.section=Section.id
LEFT JOIN hr_department as Practice ON Applicant.practise=Practice.id
""")   
        data = request._cr.dictfetchall()
        if data != []:
            return valid_response(data)
        else:
            return []

    @http.route('/api/get_employee_info', type="http", auth="public", methods=["GET"], csrf=False, cors='*',website=False)
    def get_employee_info(self):
        query = request._cr.execute(f"""SELECT 
id as EMPLOYEE_ID, 
user_id as USER_ID, 
kw_id as KW_ID,
name as EMPLOYEE_NAME, 
(select name from hr_job B where A.job_id=B.id) as DESIGNATION,
(select alias from kw_res_branch C where A.base_branch_id=C.id) as LOCATION,
(select name from hr_department D where A.department_id=D.id)  as DEPARTMENT,
(select name from hr_department D where A.division=D.id) as DIVISION,
(select name from hr_department D where A.section=D.id) as SECTION,
(select name from hr_department D where A.practise=D.id) as PRACTISE,
epbx_no as EXTN,
work_phone as DIRECT_NO,
mobile_phone as MOBILE_NO,
work_email as EMAIL,
(select id from  hr_employee E where A.parent_id=E.id) as REPORTING_MANAGER_ID,
(select name from  hr_employee E where A.parent_id=E.id) as REPORTING_MANAGER_NAME,
present_addr_street as PRESENT_ADDRESS,
present_addr_city as PRESENT_CITY,
(select name from  res_country_state F where A.present_addr_state_id=F.id) as PRESENT_STATE,
(select name from  res_country G where A.present_addr_country_id=G.id) as PRESENT_COUNTRY,
permanent_addr_street as PERMANENT_ADDRESS,
permanent_addr_city as PERMANENT_CITY,
(select name from  res_country_state F where A.permanent_addr_state_id=F.id) as PERMANENT_STATE,
(select name from  res_country G where A.permanent_addr_country_id=G.id) as PERMANENT_COUNTRY,
birthday as DOB,
gender as GENDER,
(select name from  kwemp_blood_group_master H where A.blood_group=H.id) as BLOOD_GROUP,
(select name from  kwemp_grade_master I where A.grade=I.id) as GRADE,
(select name from  kwemp_band_master J where A.emp_band=J.id) as BAND,
active as ACTIVE,
date_of_joining as DATE_JOINING,
(select name from  kwmaster_role_name K where A.emp_role=K.id) as ROLE,
(select name from  kwmaster_category_name L where A.emp_category=L.id) as EMP_CATEGORY,
(select name from  kwemp_employment_type M where A.employement_type=M.id) as EMPLOYMENT_TYPE,
marital_code as MARITAL_CODE,
(select name from  kwemp_reference_mode_master N where A.emp_refered_from=N.id) as EMP_REF,
is_wfh as IS_WFH,
issued_system as ISSUED_SYSTEM,
emp_code as EMPLOYEE_CODE,
last_working_day as LAST_WORKING_DAY
FROM hr_employee A
""")   
        data = request._cr.dictfetchall()
        if data != []:
            return valid_response(data)
        else:
            return []

    @http.route('/api/get_trainer_info', type="http", auth="public", methods=["GET"], csrf=False, cors='*',website=False)
    def get_trainer_info(self):
        query = request._cr.execute(f"""
            WITH trainer_name
     AS (SELECT plan_id,
                String_agg(emp.name, ', ') AS trainer
         FROM   training_plan_hremp_rel
                join hr_employee emp
                  ON emp.id = emp_id
         GROUP  BY plan_id),
     durartion_in_hrs
     AS (SELECT training_id,
                Coalesce(Cast(To_char(( SUM(To_timestamp(to_time, 'HH24:MI:SS')
                                            -
                                            To_timestamp(from_time
                                            ,
                                            'HH24:MI:SS'))
                                        || 'hour' ) :: interval, 'HH24:MI') AS
                              VARCHAR),
                '00:00'
                ) AS duration
         FROM   kw_training_schedule
         GROUP  BY training_id)
SELECT kt.id                          AS TRAINING_ID,
       kt.name                        AS TRAINING_NAME,
       af.name                        AS FY,
       Coalesce(dh.duration, '00:00') AS TRAINING_HOURS,
       kstm.skill_type                AS SKILL_CATEGORY,
       ksm.name                       AS SKILL,
       kt.highlight                   AS IS_HIGHLIGHTED_TRAINING,
       CASE
         WHEN Now() :: DATE BETWEEN kt.start_date AND kt.end_date
              AND ktp.state = 'approved' THEN 'In Progress'
         WHEN Now() :: DATE > kt.end_date
              AND ktp.state = 'approved' THEN 'Completed'
         WHEN ktp.state = 'rejected' THEN 'Rejected'
         WHEN ktp.state = 'apply' THEN 'Applied'
         WHEN Now() :: DATE < kt.start_date
              AND ktp.state = 'approved' THEN 'Not Started'
         WHEN ktp.state IS NULL THEN 'Not Planned'
       END                            AS TRAINING_STATUS,
       kt.start_date,
       kt.end_date,
       Coalesce(ktp.cost, 0)          AS remuneration,
       Initcap(kt.instructor_type)    AS TRAINER_TYPE,
       tn.trainer                     AS TRAINER_NAME
FROM   kw_training kt
       left join account_fiscalyear af
              ON af.id = kt.financial_year
       left join kw_skill_type_master kstm
              ON kt.course_type_id = kstm.id
       left join kw_skill_master ksm
              ON kt.course_id = ksm.id
       left join kw_training_plan ktp
              ON ktp.training_id = kt.id
                 AND ktp.state = 'approved'
       left join trainer_name tn
              ON ktp.id = tn.plan_id
       left join durartion_in_hrs dh
              ON dh.training_id = kt.id 
            """)   
        data = request._cr.dictfetchall()
        if data != []:
            return valid_response(data)
        else:
            return []

    @http.route('/api/get_nominated_participants', type="http", auth="public", methods=["GET"], csrf=False, cors='*',website=False)
    def get_nominated_participants(self):
        query = request._cr.execute(f"""
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
                    select kta.id, kta.training_id, sam.emp_rel as emp_id, percentage_scored as score
                    from kw_training_assessment kta 
                    join kw_skill_answer_master sam on sam.set_config_id = kta.assessment_id and kta.test_type = 'post'
                    UNION ALL
                    select kta.id, kta.training_id, ktsd.participant_id as emp_id, ktsd.score
                    from kw_training_assessment kta 
                    join kw_training_score_details ktsd on kta.score_id = ktsd.score_id and kta.test_type = 'post'
                )
                select training_id, emp_id, score
                from pre
                where id in (select id from (select row_number() over(partition by training_id order by id desc) as slno, id from kw_training_assessment where test_type = 'post')  pr where slno=1)
            ),
            actual_attendee as
            (
                select training_id ,participant_id, session_count,
                case
                    when total_attended >= 75.00 then '1' else '0' end
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

            select np.training_id as id,np.emp_id as employee_id,np.training_id as training_id,
            case when coalesce(aa.attendance_status,'0') ='0' then 'Not Attended' else 'Attended' end as attendance_status,
            coalesce(pre.score,0) as assessment_score
            
            from nominated_participants np
            left join pretest_score pre on pre.training_id = np.training_id and pre.emp_id = np.emp_id
            left join actual_attendee aa on aa.training_id = np.training_id and aa.participant_id = np.emp_id""")   
        data = request._cr.dictfetchall()
        if data != []:
            return valid_response(data)
        else:
            return []

    @http.route('/api/get_skill_assessment_info', type="http", auth="public", methods=["GET"], csrf=False, cors='*',website=False)
    def get_skill_assessment_info(self):
        query = request._cr.execute(f"""
            SELECT A.id, A.user_id, 
(select name from kw_skill_master B where A.skill_id=B.id),
percentage_scored,
created_date,
time_taken,
(select duration from kw_skill_question_set_config C where A.set_config_id=C.id),
status
from kw_skill_answer_master A 
left join kw_skill_question_set_config  D on A.set_config_id=D.id
where  D.assessment_type = 'skill'""")   
        data = request._cr.dictfetchall()
        if data != []:
            return valid_response(data)
        else:
            return []