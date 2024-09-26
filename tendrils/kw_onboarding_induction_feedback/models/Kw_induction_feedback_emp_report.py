from datetime import date
from odoo import tools
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class OnboardingInductionReport(models.Model):
    _name = 'onboarding_feedback_assessment_report'
    _description = "Onboarding Assessment Feedback Report"
    _auto = False

    emp_id = fields.Many2one('hr.employee', string="Employee Name")
    department_id = fields.Many2one('hr.department', string='Department')
    designation_id = fields.Many2one('hr.job', string="Designation")
    work_email = fields.Char()
    status_feedback = fields.Char(string="Status")
    onboarding_id = fields.Many2one('kw_onboarding_feedback')
    hr_accessment_mark = fields.Char("HR induction assessment feedback score")
    it_accessment_mark = fields.Char("IT induction assessment feedback score")
    comp_accessment_mark = fields.Char("KYC induction assessment feedback score")

    # @api.model_cr
    # def init(self):
    #     tools.drop_view_if_exists(self.env.cr, self._table)

    #     query = f""" CREATE or REPLACE VIEW {self._table} as (
    #         SELECT row_number() over() AS id, 
    #             hr.emp_id AS emp_id,
    #             hr.id AS onboarding_id,
    #             hr.dept_id AS department_id, 
    #             hr.deg_id AS designation_id,
    #             hr.work_email AS work_email,
    #             hr.status_feedback AS status_feedback,
    #             CONCAT(
    #                 CONCAT(hr.secure_total_mark_hr, '/'),
    #                 CONCAT(hr.total_mark_hr, '  ('),
    #                 CONCAT(to_char(hr.hr_calculate, 'FM999990.00'), '%)')
    #             ) AS hr_accessment_mark , 

    #             CONCAT(
    #                 CONCAT(hr.secure_total_mark_it, '/'),
    #                 CONCAT(hr.total_mark_it,'  ('),
    #                 CONCAT(to_char(hr.it_calculate, 'FM999990.00'), '%)')
    #             ) AS it_accessment_mark,
    #             CONCAT(
    #                 CONCAT(hr.secure_total_mark_comp, '/'),
    #                 CONCAT(hr.total_mark_comp, '  ('),
    #                 CONCAT(to_char(hr.company_calculate, 'FM999990.00'), '%)')
    #             ) AS comp_accessment_mark
    #         FROM kw_onboarding_feedback AS hr 
    #         WHERE hr.id is not null
    #     )"""

    #     # print("tracker quey",query)
    #     self.env.cr.execute(query)

    # def get_emp_feedback_data(self):
    #     form_view_id = self.env.ref('kw_onboarding_induction_feedback.kw_onboarding_feedback_form').id
    #     tree_view_id =  self.env.ref('kw_onboarding_induction_feedback.kw_feedback_page_list').id
    #     action = {
    #         'name': 'Assessment Feedback',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'kw_onboarding_feedback',
    #         'view_type': 'form',
    #         'view_mode': 'tree',
    #         'target': 'self',
    #         'domain': [('id', '=', self.onboarding_id.id)],
    #         'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
    #         'context': {'edit': False, 'create': False, 'delete': False}
    #     }
    #     return action
