from odoo import api, fields, models
from werkzeug import urls
from odoo.addons.http_routing.models.ir_http import slug

class Kw_Survey(models.Model):
    _inherit = "survey.survey"

    applicant_feedback_survey_url = fields.Char("Applicant Feedback Public link", compute="_compute_candidate_survey_url")
    applicant_feedback_print_url = fields.Char("Applicant Feedback Print link", compute="_compute_candidate_survey_url")

    @api.model
    def _compute_candidate_survey_url(self):
        base_url = '/' if self.env.context.get('relative_url') else \
            self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for survey in self:
            survey.applicant_feedback_survey_url = urls.url_join(base_url, "/candidate/feedback/start/%s" % (slug(survey)))
            survey.applicant_feedback_print_url = urls.url_join(base_url, "/candidate/feedback/print/%s" % (slug(survey)))

class survey_user_input(models.Model):
    _inherit = "survey.user_input"

    @api.multi
    def _compute_qualification(self):
        qualification_list = []
        for rec in self:
            qualification_list.clear()
            if rec.applicant_id.qualification_ids and rec.applicant_id.other_qualification:
                for record in rec.applicant_id.qualification_ids:
                    if record.code == 'others':
                        qualification_list.append(rec.applicant_id.other_qualification)
                    else:
                        qualification_list.append(record.name)
                rec.qualification = ','.join(qualification_list)
            else:
                rec.qualification = ','.join(qualification_list)

    def _compute_experience(self):
        for rec in self:
            if rec.applicant_id:
                rec.experience = str(rec.applicant_id.exp_year) + " years - " + str(rec.applicant_id.exp_month) + " months"


    position = fields.Many2one('kw_hr_job_positions',related="applicant_id.job_position", string="Applicant ID")
    department_id = fields.Many2one('hr.department',related="applicant_id.department_id",string="Department")
    qualification = fields.Char(compute='_compute_qualification',string="Qualification")
    experience = fields.Char(string="Experience",compute="_compute_experience")
    date = fields.Date(string="Date",related="kw_meeting_id.kw_start_meeting_date")
