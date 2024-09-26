from odoo import models, fields, api
from odoo import tools

class KwantifySurveyReport(models.Model):
    _name = 'kw_survey_report'
    _description = 'Kwantify Survey Report'
    _auto = False
    
    employee = fields.Char(string="Employee")
    department = fields.Char(string="Department")
    division = fields.Char(string="Division")
    section = fields.Char(string="Section")
    practise = fields.Char(string="Practise")
    designation = fields.Char(string="Designation")
    work_location = fields.Char(string="Work Location")
    mode_of_work = fields.Char(string="Mode of work")
    current_location = fields.Char(string="Mention your current location (City)")
    power_supply_condition = fields.Char(string="Power supply condition")
    computer_information = fields.Char(string="Computer information")
    internet_connectivity = fields.Char(string="Internet Connectivity")
    type_of_internet_connectivity = fields.Char(string="Type of internet connectivity")
    vpn_accessibility = fields.Char(string="VPN accessibility")
    how_is_your_office_setup_at_home = fields.Char(string="How is your office set-up at home")
    work_environment_at_home = fields.Char(string="Work environment at home")
    status = fields.Char(string="Status")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(""" CREATE or REPLACE VIEW %s as (

            with ans as
            (
	            select sui.survey_id,sq.sequence, sq.question,sui.partner_id,
                row_number() over(partition by sq.sequence, sui.partner_id) as slno,
                case 
                when suil.answer_type = 'text' then suil.value_text
                when suil.answer_type = 'suggestion' then Concat(sl.value,' ',suil.value_text)
                else ''
                end as value
                from survey_user_input sui 
                join survey_user_input_line suil on suil.user_input_id = sui.id
                join survey_question sq on sq.id = suil.question_id
                left join survey_label sl on sl.question_id = sq.id and sl.id = suil.value_suggested
            )
            select ROW_NUMBER () OVER (ORDER BY he.id) as id ,
            concat(he.name,' (',he.emp_code,')') as employee, 
            (select name from hr_department where id = he.department_id) as department,
            (select name from hr_department where id = he.division) as division,
            (select name from hr_department where id = he.section) as section,
            (select name from hr_department where id = he.practise) as practise,
            (select name from hr_job where id = he.job_id) as designation,
            (select alias from kw_res_branch where id = he.job_branch_id) as work_location,
            (select value from ans where ans.survey_id = ks.survey_id and ans.partner_id = ru.partner_id and ans.sequence = 1) as "mode_of_work",
            (select value from ans where ans.survey_id = ks.survey_id and ans.partner_id = ru.partner_id and ans.sequence = 2) as "current_location",
            (select value from ans where ans.survey_id = ks.survey_id and ans.partner_id = ru.partner_id and ans.sequence = 3) as "power_supply_condition",
            (select value from ans where ans.survey_id = ks.survey_id and ans.partner_id = ru.partner_id and ans.sequence = 4) as "computer_information",
            (select value from ans where ans.survey_id = ks.survey_id and ans.partner_id = ru.partner_id and ans.sequence = 6) as "internet_connectivity",
	        concat((select value from ans where ans.survey_id = ks.survey_id and ans.partner_id = ru.partner_id and ans.sequence = 7 and ans.slno=1), ' ',
            (select value from ans where ans.survey_id = ks.survey_id and ans.partner_id = ru.partner_id and ans.sequence = 7 and ans.slno=2)) as "type_of_internet_connectivity",
            (select value from ans where ans.survey_id = ks.survey_id and ans.partner_id = ru.partner_id and ans.sequence = 8) as "vpn_accessibility",
            (select value from ans where ans.survey_id = ks.survey_id and ans.partner_id = ru.partner_id and ans.sequence = 9) as "how_is_your_office_setup_at_home",
            (select value from ans where ans.survey_id = ks.survey_id and ans.partner_id = ru.partner_id and ans.sequence = 10) as "work_environment_at_home",
            (select 
                case 
                    when state = 'new' then 'Not Started Yet'
                    when state = 'skip' then 'Partially Completed'
                    when state = 'done' then 'Completed'
                    else ''
                
                    
                end as status from survey_user_input s where s.id = (select user_input_id from kw_surveys_details where employee_ids = he.id and kw_surveys_id = ks.id)

            ) as status
            from kw_surveys ks
            join kw_surveys_config_hr_employee_rel se on se.kw_survey_id = ks.id
            join hr_employee he on he.id = se.employee_id
            join res_users ru on ru.id = he.user_id
            join res_partner rp on rp.id = ru.partner_id

        )""" % (self._table))