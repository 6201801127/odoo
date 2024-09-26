from odoo import models, fields, api, tools, _
import math

IG, LE, PR, EX, RM = 'Ignorant', 'Learner', 'Practitioner', 'Expert', 'Role Model'

class appraisal_progress_report(models.Model):
    _name = "appraisal_progress_report"
    _description = "Appraisal Year Wise Report"
    _auto = False

    employee_id = fields.Many2one('hr.employee', string="Employee Id")
    emp_name = fields.Char(string="Employee Name", related='employee_id.name')
    emp_code = fields.Char(string="Employee Code", related='employee_id.emp_code')
    designation = fields.Char(string="Designation", related='employee_id.job_id.name')
    department = fields.Char(string="Department", related='employee_id.department_id.name')

    first_score = fields.Float(string='2020 Score', compute="_compute_year_wise_appraisal")
    first_stage = fields.Char(string='2020 Stage', compute="_compute_year_wise_appraisal")

    second_score = fields.Float(string='2019 Score', compute="_compute_year_wise_appraisal")
    second_stage = fields.Char(string='2019 Stage', compute="_compute_year_wise_appraisal")

    third_score = fields.Float(string='2018 Score', compute="_compute_year_wise_appraisal")
    third_stage = fields.Char(string='2018 Stage', compute="_compute_year_wise_appraisal")

    fourth_score = fields.Float(string='2021 Score', compute="_compute_year_wise_appraisal")
    fourth_stage = fields.Char(string='2021 Stage', compute="_compute_year_wise_appraisal")

    fifth_score = fields.Float(string='2022 Score', compute="_compute_year_wise_appraisal")
    fifth_stage = fields.Char(string='2022 Stage', compute="_compute_year_wise_appraisal")

    sixth_score = fields.Float(string='2023 Score', compute="_compute_year_wise_appraisal")
    sixth_stage = fields.Char(string='2023 Stage', compute="_compute_year_wise_appraisal")
    
    def _get_stage(self, score):
        value = False
        if 0 <= math.ceil(score) <= 20:
            value = IG
        elif 21 <= math.ceil(score) <= 40:
            value = LE
        elif 41 <= math.ceil(score) <= 60:
            value = PR
        elif 61 <= math.ceil(score) <= 80:
            value = EX
        elif 81 <= math.ceil(score) <= 100 or math.ceil(score) > 100:
            value = RM
        return value
    
    @api.multi
    def _compute_year_wise_appraisal(self):
        period_master = self.env['kw_assessment_period_master'].sudo().search([], order='id desc')
        appraisal_model = self.env['hr.appraisal'].sudo()

        first_period = second_period = third_period = fourth_period = fifth_period = sixth_period = False

        if period_master:
            first_period = appraisal_model.search([('appraisal_year_rel', '=', period_master[0].id or False)])

        if len(period_master) >= 2:
            second_period = appraisal_model.search([('appraisal_year_rel', '=', period_master[1].id or False)])

        third_period = self.env['kw_employee_score'].sudo().search([('year_id.kw_period_id', '=', 22)])  # 2018-19 (static)

        if len(period_master) >= 3:
            fourth_period = appraisal_model.search([('appraisal_year_rel', '=', period_master[2].id or False)])

        if len(period_master) >= 4:
            fifth_period = appraisal_model.search([('appraisal_year_rel', '=', period_master[3].id or False)])

        if len(period_master) >= 5:
            sixth_period = appraisal_model.search([('appraisal_year_rel', '=', period_master[4].id or False)])

        for app in self:
            if first_period:
                emp_data_exist = first_period.filtered(lambda first: first.emp_id.id == app.employee_id.id and first.state.sequence in [5, 6])
                if emp_data_exist:
                    app.first_score = emp_data_exist[0].total_score
                    app.first_stage = self._get_stage(emp_data_exist[0].total_score)

            if second_period:
                sec_emp_data_exist = second_period.filtered(lambda sec: sec.emp_id.id == app.employee_id.id and sec.state.sequence in [5, 6])
                if sec_emp_data_exist:
                    app.second_score = sec_emp_data_exist[0].total_score
                    app.second_stage = self._get_stage(sec_emp_data_exist[0].total_score)

            # #2018-19 (static)
            if third_period:
                trd_emp_data_exist = third_period.filtered(lambda trd: trd.employee_id.id == app.employee_id.id)
                if trd_emp_data_exist:
                    app.third_score = float(trd_emp_data_exist[0].appraisal_mark)
                    app.third_stage = self._get_stage(float(trd_emp_data_exist[0].appraisal_mark))

            if fourth_period:
                fourth_emp_data_exist = fourth_period.filtered(lambda fourth: fourth.emp_id.id == app.employee_id.id and fourth.state.sequence in [5, 6])
                if fourth_emp_data_exist:
                    app.fourth_score = fourth_emp_data_exist[0].total_score
                    app.fourth_stage = self._get_stage(fourth_emp_data_exist[0].total_score)

            if fifth_period:
                fifth_emp_data_exist = fifth_period.filtered(lambda fifth: fifth.emp_id.id == app.employee_id.id and fifth.state.sequence in [5, 6])
                if fifth_emp_data_exist:
                    app.fifth_score = fifth_emp_data_exist[0].total_score
                    app.fifth_stage = self._get_stage(fifth_emp_data_exist[0].total_score)

            if sixth_period:
                sixth_emp_data_exist = sixth_period.filtered(lambda sixth: sixth.emp_id.id == app.employee_id.id and sixth.state.sequence in [5, 6])
                if sixth_emp_data_exist:
                    app.sixth_score = sixth_emp_data_exist[0].total_score
                    app.sixth_stage = self._get_stage(sixth_emp_data_exist[0].total_score)
                    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""CREATE or REPLACE VIEW %s as (
                    
        select ROW_NUMBER () OVER (ORDER BY e.id) as id,
        e.id as employee_id
        from hr_employee e where id in (
        select emp_id from hr_appraisal WHERE appraisal_year_rel in (
        SELECT ID FROM (select ROW_NUMBER() OVER(ORDER BY ID DESC) AS SLNO, ID from kw_assessment_period_master) A WHERE SLNO=1))
        )""" % (self._table))   
