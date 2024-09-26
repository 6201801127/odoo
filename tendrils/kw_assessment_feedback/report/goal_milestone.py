from odoo import api, fields, models, _, tools
from odoo.exceptions import ValidationError

class goal_milestone(models.Model):
    _name = "kw_goal_milestone"
    _description = "Goal Milestone Report"
    _auto = False
    _rec_name = 'emp_name'
    _order = 'period_date desc'

    MONTH_LIST= [
        ('1','January'),('2','February'),
        ('3','March'),('4','April'),
        ('5','May'),('6','June'),
        ('7','July'),('8','August'),
        ('9','September'),('10','October'),
        ('11','November'),('12','December')
        ]

    emp_name = fields.Char(string="Employee")
    period_date = fields.Date(string='Period Date')
    period_name = fields.Char(string='Period Name')
    gm_id = fields.Integer(string='Gaol milestone')
    ra = fields.Char(string='Reporting Authority')
    department = fields.Char(string='Department')
    designation = fields.Char(string='Designation')
    goal_name = fields.Char(string="Goal")
    months = fields.Selection(MONTH_LIST, string='Month')
    year = fields.Char(string="Year")
    status = fields.Selection(selection=[('1','Not Started'),('2','Milestone Updated'),('3','Progress Updated'),('4','Published')],string='Status')
    milestones = fields.Integer(string="No. of Milestones")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""CREATE or REPLACE VIEW %s as (
            SELECT row_number() Over(order by (select 0)) as id,
                coalesce(gm.id, 0) AS gm_id,
                p.period_date as period_date,
                p.name as period_name,
                CONCAT(emp.name,' (',emp.emp_code,')') as emp_name,
                dept.name as department,
                (select CONCAT(name,' (',emp_code,')') as emp_name from hr_employee where id = emp.parent_id) as ra,
                job.name as designation,
                gm.goal_name as goal_name,
                gm.year as year,
                gm.months as months,
				case
					when gm.state IS NULL THEN '1'
					else gm.state
				End  AS status,
                (select count(mil.id) from kw_feedback_milestone mil where mil.goal_id = gm.id) as  milestones
                FROM kw_feedback_assessment asessment
                join kw_feedback_map_resources map on
                    map.assessment_tagging_id = asessment.id and asessment.is_goal is True
                join kw_feedback_assessment_period p on
                    p.map_resource_id = map.id
                join kw_feedback_period_assessee_rel par on par.period_id = p.id
                join hr_employee emp on emp.id = par.emp_id
                JOIN hr_department dept on
                    dept.id = emp.department_id
                JOIN hr_job job on
                    job.id = emp.job_id
                left outer JOIN kw_feedback_goal_and_milestone gm on
                    emp.id = gm.emp_id and date_trunc('month',p.period_date)::date = make_date(gm.year::integer, gm.months::integer, 01)
            ORDER BY emp_name asc

        )""" % (self._table))   

    @api.multi
    def view_goal_details(self):
        self.ensure_one()
        view_id = self.env.ref('kw_assessment_feedback.kw_feedback_goal_and_milestone_form_reference3').id
        if self.gm_id:
            return {
                    'name':'Goal Details',
                    'type': 'ir.actions.act_window',
                    'res_model': 'kw_feedback_goal_and_milestone',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id': self.gm_id,
                    'view_id': view_id,
                    'target': 'new',
                    'flags': {'mode':'readonly','toolbar':False, 'action_buttons': False},
                    }
        else:
            raise ValidationError("Not given any goal and milestones yet.")

