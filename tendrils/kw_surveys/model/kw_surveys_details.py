# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.addons.http_routing.models.ir_http import slug
from werkzeug import urls
from odoo.exceptions import ValidationError
import logging
from datetime import datetime, date
from odoo.addons.http_routing.models.ir_http import slug

_logger = logging.getLogger(__name__)


class kw_surveys_details(models.Model):
    _name = 'kw_surveys_details'
    _description = 'Your Feedback'
    _rec_name = 'employee_ids'

    survey_name = fields.Char('Survey Name', required=True)
    survey_id = fields.Many2one(comodel_name='survey.survey', string='Template Type', required=True)

    kw_surveys_id = fields.Many2one(comodel_name='kw_surveys', string='Survey', required=True, ondelete='restrict')

    start_date = fields.Date(string='Start Date', autocomplete="off", required=True)
    end_date = fields.Date(string='End Date', autocomplete="off", required=True)
    employee_ids = fields.Many2one(string='Employees', comodel_name='hr.employee')

    user_input_id = fields.Many2one(string='User Input', comodel_name='survey.user_input')
    portal = fields.Boolean(string="Portal", default=False)
    log_in = fields.Boolean(string='Log In', default=False)
    email = fields.Boolean(string="E-Mail", default=False)
    state = fields.Selection(
        string='Status', required=True, default='1',
        selection=[('1', 'Not Started'), ('2', 'Draft'), ('3', 'Completed'), ('4', 'Published')]
    )
   
    # #computed fields ---
    from_date = fields.Boolean(string="Compare from date", compute='_from_date', store=False)
    to_date = fields.Boolean(string="Compare to date", compute='_to_date', store=False)
    date_time = fields.Date(string='Current Date', compute='_find_current_date', store=False)
    completed_on = fields.Date(string='Complete On')

    start_survey_url = fields.Char("Survey Public link", compute="_compute_survey_url")
    view_survey_url = fields.Char("Survey View Result", compute="_compute_survey_url")
    duration = fields.Integer(related='user_input_id.duration',string='Duration')
    quizz_score = fields.Float('Total Score',compute="_compute_quizz_score")
    survey_create_time = fields.Datetime(string='Started On')
    survey_duration = fields.Char(string='Duration',compute='_from_date')

    @api.multi
    def _compute_quizz_score(self):
        for record in self:
            record.quizz_score = record.user_input_id.quizz_score

    
    @api.model
    def create(self, vals):
        current_employee_email = self.env.user.employee_ids[-1].work_email if self.env.user.employee_ids else 'tendrils@csm.tech'
        new_record = super(kw_surveys_details, self).create(vals)
        if new_record.email is True:
            response = self.env['survey.user_input'].sudo().create(
                {'survey_id': new_record.survey_id.id,
                 'partner_id': new_record.employee_ids.user_id.partner_id.id or False,
                 'deadline': new_record.end_date,
                 'email': new_record.employee_ids.work_email or '',
                 })
            new_record.write({'user_input_id': response.id})

        subject = new_record.kw_surveys_id.email_subject_line
        body = new_record.kw_surveys_id.email_body

        template = self.env.ref('kw_surveys.kwantify_surveys_email_template')
        template.with_context(user_email=current_employee_email, kw_email_body=body, kw_subject_line=subject).send_mail(
            new_record.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        return new_record

    @api.multi
    def _find_current_date(self):
        for record in self:
            current_dt = date.today()
            record.date_time = current_dt

    @api.multi
    def _from_date(self):
        for record in self:
            if record.start_date > record.date_time:
                record.from_date = True
            if record.survey_create_time and record.write_date:
                duration_time=record.write_date-record.survey_create_time
                difference_in_seconds = duration_time.total_seconds()
                record.survey_duration = difference_in_seconds
                # print('record.survey_duration======',record.survey_duration)

    @api.multi
    def _to_date(self):
        for record in self:
            if record.end_date < record.date_time:
                record.to_date = True

    @api.multi
    def _give_feedback(self, user_id):
        user_input = self.env['survey.user_input'].sudo()
        today_date = date.today()
        survey_data = self.env['kw_surveys_details'].search(
            [('employee_ids', '=', user_id.employee_ids.id),
             ('start_date', '<=', today_date), ('end_date', '>=', today_date),
             ('log_in', '=', True), ('state', 'in', ['1', '2'])],
            limit=1)
        try:
            env_employee = self.env['hr.employee'].search([('user_id', '=', user_id.id)], limit=1)
            env_partner = user_id.partner_id.id if user_id.partner_id else False

            if survey_data:
                if survey_data.user_input_id:
                    if survey_data.user_input_id.state == 'done':
                        return False
                    else:
                        token = survey_data.user_input_id.sudo().token
                        u_token = "/%s" % token if token else ""
                        url = "/kwantify/custom-survey/begin/%s" % (slug(survey_data))
                        return url + u_token
                else:
                    if env_partner:
                        response = user_input.create(
                            {'survey_id': survey_data.survey_id.id,
                             'partner_id': env_partner,
                             'deadline': survey_data.end_date,
                             'email': env_employee.work_email or user_id.partner_id.email,
                             })
                        survey_data.write({'user_input_id': response.id})

                        token = response.token

                        u_token = "/%s" % token if token else ""
                        url = "/kwantify/custom-survey/begin/%s" % (slug(survey_data))

                        return url + u_token
                    else:
                        return False
            else:
                return False
        except Exception as e:
            _logger.warning("Tendrils Survey :", e)

    @api.multi
    def give_survey_portal(self):
        self.ensure_one()
        user_input = self.env['survey.user_input'].sudo()
        self.survey_create_time = datetime.now()
        # self.survey_duration = (self.write_date - datetime.now())
        if self.employee_ids.user_id.id == self._uid and self.portal:
            if self.user_input_id and self.user_input_id.sudo().partner_id.id == self.employee_ids.user_id.partner_id.id:
                self.user_input_id.sudo().write({'deadline': self.end_date, 'survey_id': self.survey_id.id})
                token = self.user_input_id.sudo().token
            else:
                response = user_input.create(
                    {'survey_id': self.survey_id.id,
                     'partner_id': self.employee_ids.user_id.partner_id.id if self.employee_ids.user_id and self.employee_ids.user_id.partner_id else False,
                     'deadline': self.end_date,
                     'email': self.employee_ids.work_email if self.employee_ids.work_email else False,
                     })
                self.user_input_id = response.id
                token = response.token
            u_token = "/%s" % token if token else ""
            return {
                'type': 'ir.actions.act_url',
                'name': 'Tendrils Survey',
                'target': 'self',
                'url': self.with_context(relative_url=True).start_survey_url + u_token
            }
        else:
            raise ValidationError(
                f"You are not allowed to give {self.employee_ids.name}'s survey.\nKindly contact to HR dept. if any queries.")

    @api.multi
    def edit_survey_manager(self):
        self.ensure_one()
        if self.state in ['2','3'] and self.user_input_id:
            token = self.user_input_id.sudo().token
            u_token = "/%s" % token if token else ""
            return {
                'type': 'ir.actions.act_url',
                'name': 'Tendrils Survey',
                'target': 'self',
                'url': self.with_context(relative_url=True).start_survey_url + u_token + '/' + slug(self.env.user)
            }
        else:
            raise ValidationError(
                f"To edit {self.employee_ids.name} survey you need 'Manager' access.\nKindly contact to 'HR dept.' if any queries.")

    @api.multi
    def _compute_survey_url(self):
        base_url = '/' if self.env.context.get('relative_url') else \
            self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            record.start_survey_url = urls.url_join(base_url, "kwantify/custom-survey/begin/%s" % (slug(record)))
            record.view_survey_url = urls.url_join(base_url, "kwantify/custom-survey/results/%s" % (slug(record)))

    @api.multi
    def view_survey_portal(self):
        self.ensure_one()
        token = self.user_input_id.sudo().token
        u_token = "/%s" % token if token else ""
        return {
            'type': 'ir.actions.act_url',
            'name': 'Tendrils Survey',
            'target': 'self',
            'url': self.with_context(relative_url=True).view_survey_url + u_token
        }

    @api.model
    def get_survey_url(self):
        token = self.user_input_id.sudo().token
        return self.with_context(relative_url=True).start_survey_url + '/' + token

    @api.multi
    def publish_survey_manager(self):
        self.ensure_one()
        if self.state == '3' and self.env.user.has_group('survey.group_survey_manager'):
            self.state = '4'
