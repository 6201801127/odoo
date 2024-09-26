# -*- coding: utf-8 -*-
from werkzeug import urls
from datetime import date
import bs4 as bs
from odoo import models, fields, api
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class kw_surveys(models.Model):
    _name = 'kw_surveys'
    _description = 'Kwantify Survey'
    _rec_name = 'name'

    name = fields.Char('Survey Name', required=True)
    survey_id = fields.Many2one(comodel_name='survey.survey', string='Template Name',
                                domain=[('survey_type.code', 'in', ['covid19survey','ignite'])], required=True)
    start_date = fields.Date(string='Start Date', autocomplete="off", required=True)
    end_date = fields.Date(string='End Date', autocomplete="off", required=True)

    employee_ids = fields.Many2many(
        string='Employees',
        comodel_name='hr.employee',
        relation='kw_surveys_config_hr_employee_rel',
        column1='kw_survey_id',
        column2='employee_id',
    )

    portal = fields.Boolean(string="Portal")
    log_in = fields.Boolean(string='Log In')
    email = fields.Boolean(string="E-Mail")

    feedback_status = fields.Selection(string='Status',
                                       selection=[('unpublished', 'Unpublished'), ('published', 'Published')],
                                       default='unpublished')

    survey_details_id = fields.One2many(comodel_name='kw_surveys_details', inverse_name='kw_surveys_id',
                                        string='Survey Details Ids')

    email_subject_line = fields.Text("Email Subject Line", required=True)
    email_body = fields.Html("Email Body", required=True)

    total_employee = fields.Integer(string='No. of Employees', compute='compute_total_all')
    pending = fields.Integer(string='No. of Pending', compute='compute_total_all')
    completed = fields.Integer(string='No. of Completed', compute='compute_total_all')
    result_url = fields.Char("Results link", compute="_compute_survey_url")
    gender = fields.Many2one("hr.employee" , string ='Gender')
    # quizz_score = fields.Float("Score for the quiz", compute="_compute_quizz_score", default=0.0)

    # @api.depends('quizz_score')
    # def _compute_quizz_score(self):
    #     for user_input in self:
    #         user_input.quizz_score = sum(survey_id.question_ids.mapped('quizz_mark'))

    def _compute_survey_url(self):
        """ Computes a public URL for the survey """
        base_url = '/' if self.env.context.get('relative_url') else \
            self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for survey in self:
            survey.result_url = urls.url_join(base_url, "survey/results/%s" % (slug(survey)))

    @api.constrains('name', )
    def validate_survey_name(self):
        record = self.env['kw_surveys'].search([]) - self
        for info in record:
            if info.name.lower() == self.name.lower():
                raise ValidationError("This survey name \"" + self.name + "\" is already exists.")

    @api.constrains('email_body')
    def _validate_email_body(self):
        for survey in self:
            if len((bs.BeautifulSoup(survey.email_body, features="lxml")).text.strip()) == 0:
                raise ValidationError('Email body cannot be empty.')

    @api.constrains('start_date', 'end_date')
    def _validate_start_end_dates(self):
        for survey in self:
            if survey.end_date < survey.start_date:
                raise ValidationError("End date can't be less than start date.")

    @api.constrains('portal', 'log_in', 'email')
    def _validate_survey_mode(self):
        for survey in self:
            if not any([survey.portal, survey.log_in, survey.email]):
                raise ValidationError("Please choose at least one survey mode.")

    @api.multi
    def compute_total_all(self):
        for record in self:
            record.total_employee = len(record.employee_ids) if record.employee_ids else 0
            record.pending = len(record.survey_details_id.filtered(lambda res: res.state in ['1', '2']))
            record.completed = len(record.survey_details_id.filtered(lambda res: res.state in ['3', '4']))

    @api.multi
    def create_survey_details(self):
        for record in self:
            model_survey_details = self.env['kw_surveys_details']
            kw_surveys_details_record = model_survey_details.search([('kw_surveys_id', '=', record.id)])

            for employee in record.employee_ids:
                existing_records = kw_surveys_details_record.filtered(lambda rec: rec.employee_ids.id == employee.id)
                if not existing_records:
                    new_record = model_survey_details.create({
                        'survey_name': record.name,
                        'survey_id': record.survey_id.id,
                        'kw_surveys_id': record.id,
                        'start_date': record.start_date,
                        'end_date': record.end_date,
                        'employee_ids': employee.id,
                        'portal': True if record.portal else False,
                        'log_in': True if record.log_in else False,
                        'email': True if record.email else False,
                    })
                elif existing_records and existing_records.state in ['1', '2']:
                    existing_records.write({
                        'survey_name': record.name,
                        'survey_id': record.survey_id.id,
                        'start_date': record.start_date,
                        'end_date': record.end_date,
                        'portal': True if record.portal else False,
                        'log_in': True if record.log_in else False,
                        'email': True if record.email else False,
                    })
                    if existing_records.email and not existing_records.user_input_id:
                        # create user input for employee
                        response = self.env['survey.user_input'].sudo().create(
                            {'survey_id': record.survey_id.id,
                             'partner_id': employee.user_id and employee.user_id.partner_id.id or False,
                             'deadline': existing_records.end_date,
                             'email': employee.work_email or '',
                             })
                        existing_records.write({'user_input_id': response.id})
                else:
                    pass

            if record.feedback_status == 'unpublished':
                record.write({'feedback_status': 'published'})

            if kw_surveys_details_record:
                dup_rec = kw_surveys_details_record.filtered(
                    lambda rec: rec.employee_ids.id not in record.employee_ids.ids)

                if dup_rec:
                    dup_rec.unlink()
        return

    @api.multi
    def write(self, vals):
        update = super(kw_surveys, self).write(vals)
        if self.feedback_status == 'published':
            self.create_survey_details()
        return update

    @api.multi
    def view_survey_data(self):
        ctx = self.env.context.copy()
        ctx.update({'surveys_id': self.id})
        self.env['kw_survey_result_report'].with_context(ctx).init()
        res = self.env['ir.actions.act_window'].for_xml_id('kw_surveys', 'action_kw_survey_result_report_act_window')
        return res

    @api.multi
    def view_survey_result(self):
        self.ensure_one()
        base_url = '/' if self.env.context.get('relative_url') else self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        result_url = f"{base_url}/export-survey-result/{self.id}"
        return {
            'type': 'ir.actions.act_url',
            'name': "Results of the Survey",
            # 'target': 'self',
            'url': result_url
        }

    @api.multi
    def action_result_survey(self):
        """ Open the website page with the survey results view """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'name': "Results of the Survey",
            'target': 'self',
            'url': f"{self.survey_id.result_url}?sid={self.id}"
        }
    @api.multi
    def view_survey_records(self):
        for rec in self:
            view_id = self.env.ref('survey.survey_user_input_tree').id
            form_view_id = self.env.ref('kw_appraisal.kw_survey_user_input_form_inherits').id
            return {
                'name': 'Survey Result',
                'type': 'ir.actions.act_window',
                'res_model': 'survey.user_input',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'views': [(view_id, 'tree'),(form_view_id, 'form')],
                'target': 'self',
                'domain': [ ('id', 'in', rec.mapped('survey_details_id.user_input_id').ids)],
                'view_id': view_id,
            }
