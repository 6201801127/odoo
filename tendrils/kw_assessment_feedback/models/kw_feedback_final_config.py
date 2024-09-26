from odoo import models, fields, api
from odoo.addons.http_routing.models.ir_http import slug
from werkzeug import urls
from odoo.exceptions import ValidationError
from datetime import datetime,date, timedelta
import pytz
import calendar


class kw_feedback_final_config(models.Model):
    _name           = 'kw_feedback_final_config'
    _description    = 'Assessment'
    _rec_name       = 'feedback_details_id'

    assessor_id = fields.Many2one('hr.employee',string='Assessor',domain="[('id','!=',assessee_id)]",required=True)
    assessee_id = fields.Many2one('hr.employee',string='Assessee',required=True)
    image_small = fields.Binary(related='assessee_id.image', store=False)

    feedback_details_id = fields.Many2one('kw_feedback_details',ondelete='restrict',required=True)
    period_id           = fields.Many2one(related='feedback_details_id.period_id')
    assessment_tagging_id   = fields.Many2one(related='feedback_details_id.assessment_tagging_id')
    survey_id               = fields.Many2one(comodel_name='survey.survey',string='Template Type',domain="[('survey_type.code','=','assessment_feedback')]",required=True,ondelete='restrict')

    assessment_from_date    = fields.Date(string='Start Date',autocomplete="off")
    assessment_to_date      = fields.Date(string='End Date',autocomplete="off")
    assessment_date = fields.Date(string='Assessment Date',autocomplete="off")
    rrule_type      = fields.Selection(related='feedback_details_id.assessment_tagging_id.frequency', string='Recurrence')

    feedback_status         = fields.Selection(string='Feedback Status',selection=[('1', 'Not Started'), ('2', 'Draft'), ('3', 'Completed'),('4', 'Published')], default='1')
    total_score     = fields.Float(string='Score (in %)',help='Score will visible after complete your feedback')
    user_input_id   = fields.Many2one('survey.user_input',string='User Input/Feedback ID',ondelete='cascade')

    positive_remark = fields.Text(string='Positive Area')
    weak_remark     = fields.Text(string='Weak Area')
    improve_remark  = fields.Text(string='Suggestion')

    ##Computed URLs
    start_feedback_url  = fields.Char("Assessment Feedback Public link", compute="_compute_feedback_url")
    start_goal_url  = fields.Char("Assessment Goal Public link", compute="_compute_feedback_url")
    view_feedback_url   = fields.Char("Assessment Feedback View Result", compute="_compute_feedback_url")

    ##computed fields ---
    color       = fields.Integer("Color Index", compute="change_color", store=False)
    check_date   = fields.Boolean(string="Compare from date", compute='_check_available_date', store=False)
    count_score = fields.Boolean(compute='compute_count_score',store=False)

    @api.multi
    def change_color(self):
        for record in self:
            color = 0
            if record.feedback_status == '1':
                color = 1
            elif record.feedback_status == '2':
                color = 3
            elif record.feedback_status == '3':
                color = 4
            elif record.feedback_status == '4':
                color = 10
            record.color = color
    
    @api.multi
    @api.depends('feedback_status')
    def compute_count_score(self):
        for record in self:
            record.controller_count_score()

    def controller_count_score(self):
        if self.feedback_status in ['3', '4']:
            total_score = 0
            questions = 0.0
            user_input_line = self.env['survey.user_input_line'].sudo().search([('user_input_id', '=', self.user_input_id.id)])

            if user_input_line:

                for lines in user_input_line:
                    if lines.answer_type == 'number':
                        total_score += lines.value_number

                        for quest_ids in lines.question_id:
                            questions += quest_ids.validation_max_float_value 

            if questions != 0:
                score = (total_score / questions) * 100
                self.write({'total_score' : '%.3f' % (score)})

    @api.multi
    def _check_available_date(self):
        for record in self:

            if record.rrule_type not in ['custom'] and record.assessment_from_date and record.assessment_to_date:
                record.check_date = True if record.assessment_from_date <= date.today() and record.feedback_details_id.feedback_status not in ['6'] else False
        #    if record.assessment_from_date <= date.today() <= record.assessment_to_date,
            ###### It will be change as per swagatika maam requirment #######
            elif record.rrule_type in ['custom'] and record.assessment_date:
                record.check_date = True if date.today() >= record.assessment_date else False

    @api.multi
    def give_feedback(self):
        user_input = self.env['survey.user_input'].sudo()
        url = False
        if self.assessor_id.user_id.id == self._uid or self._context.get('eos_ra_takeaction'):
            if self.user_input_id and self.user_input_id.sudo().partner_id.id == self.assessee_id.user_id.partner_id.id:
                self.user_input_id.sudo().write({'deadline': self.assessment_to_date,'survey_id': self.survey_id.id})
                token = self.user_input_id.sudo().token
            else:
                response = user_input.create(
                    {'survey_id': self.survey_id.id,
                     'partner_id': self.assessee_id.user_id.partner_id.id if self.assessee_id.user_id and self.assessee_id.user_id.partner_id else False,
                     'deadline': self.assessment_to_date,
                     'email': self.assessee_id.work_email if self.assessee_id.work_email else False,
                    })
                self.user_input_id = response.id
                token = response.token
            u_token = "/%s" % token if token else ""

            if self.feedback_details_id.assessment_tagging_id.is_goal:
                url = self.with_context(relative_url=True).start_goal_url
            else:
                url = self.with_context(relative_url=True).start_feedback_url

            return {
                        'type': 'ir.actions.act_url',
                        'name': 'Give Assessment Feedback',
                        'target': 'self',
                        'url': url + u_token
                        }   
        else:
            if not self._context.get('eos_ra_takeaction'):
                raise ValidationError(f"You are not allowed to give {self.assessee_id.name}'s feedback.\nKindly contact to HR dept. if any queries.")
    
    @api.multi
    def _compute_feedback_url(self):
        base_url = '/' if self.env.context.get('relative_url') else \
            self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            record.start_feedback_url = urls.url_join(base_url, "kw/feedback/begin/%s" % (slug(record)))
            record.start_goal_url = urls.url_join(base_url, "kw/feedback/goal/%s" % (slug(record)))
            record.view_feedback_url = urls.url_join(base_url, "kw/feedback/results/%s" % (slug(record)))

    @api.multi
    def view_feedback(self):
        token = self.user_input_id.sudo().token
        u_token = "/%s" % token if token else ""
        return {
            'type': 'ir.actions.act_url',
            'name': 'View Assessment Feedback',
            'target': 'self',
            'url': self.with_context(relative_url=True).view_feedback_url + u_token
        }

    def view_final_feedback(self):
        return self.feedback_details_id.view_feedback()
    
    ## Main Cron
    def _cron_system_reminder_mail(self):
        model_final_config = self.env['kw_feedback_final_config'].search([])

        period_name = date.today().strftime("%B")+"-"+str(date.today().year)
        model_feedback_periods = self.env['kw_feedback_assessment_period'].search([('name','ilike',period_name),('map_resource_id.assessment_tagging_id.is_goal','=',True)])

        last_date = calendar.monthrange(int(date.today().year), int(date.today().month))[1]
        from_date = datetime.strptime(date(int(date.today().year), int(date.today().month), 25).strftime('%Y-%m-%d'), '%Y-%m-%d').date()
        
        to_date = datetime.strptime(date(int(date.today().year), int(date.today().month), int(last_date)).strftime('%Y-%m-%d'), '%Y-%m-%d').date()
        
        dt_now = date.today()
        
        current_dt = dt_now.strftime("%d")
        try:
            for model_records in model_final_config:
                if model_records.feedback_details_id.assessment_tagging_id.assessment_type == 'periodic':
                    end_date = model_records.assessment_to_date.strftime("%d")
                    difference_date = int(end_date) - int(current_dt)
                    
                    if date.today() <= model_records.assessment_to_date and difference_date <= 3 and model_records.feedback_status in ['1','2']:

                        template = self.env.ref('kw_assessment_feedback.kw_assessment_feedback_reminder_email_template')
                        if template:
                            template.send_mail(model_records.id,notif_layout="kwantify_theme.csm_mail_notification_light")

                elif model_records.feedback_details_id.assessment_tagging_id.assessment_type == 'probationary':

                    if date.today() > model_records.assessment_date and model_records.feedback_status in ['1','2']:

                        template = self.env.ref('kw_assessment_feedback.kw_assessment_probationary_reminder_email_template')
                        if template:
                            template.send_mail(model_records.id,notif_layout="kwantify_theme.csm_mail_notification_light")

            for periods in model_feedback_periods:
                for employees in periods.assessees:
                    filtered_employees = self.env['kw_feedback_goal_and_milestone'].search([('emp_id','=',employees.id),('months','=',str(date.today().month)),('year','=',str(date.today().year))],limit=1)

                    if not filtered_employees:

                        template = self.env.ref('kw_assessment_feedback.kw_assessment_goal_email_template')
                        body = template.body_html
                        body = body.replace("--ra_name--", employees.parent_id.name).replace("--employee_name--", employees.name)
                        
                        mail_values = {
                            'email_from': employees.company_id.email if employees.company_id else employees.work_email,
                            'subject': "Update Goal & Milestone for " + employees.name +" | "+ periods.name,
                            'email_to': employees.parent_id.work_email,
                            'body_html': body,
                            }
                        
                        template.write(mail_values)
                        if template:
                            template.send_mail(periods.id,notif_layout="kwantify_theme.csm_mail_notification_light")

                        body = body.replace(employees.parent_id.name,"--ra_name--").replace(employees.name,"--employee_name--")
                        mail_values = {'body_html': body}
                        template.write(mail_values)

                    elif filtered_employees and filtered_employees.state in ['2'] and date.today() >= from_date:
                        template = self.env.ref('kw_assessment_feedback.kw_assessment_update_progress_email_template')

                        body = template.body_html
                        body = body.replace("--ra_name--", employees.parent_id.name).replace("--employee_name--", employees.name)

                        mail_values = {
                            'email_from': employees.company_id.email if employees.company_id else employees.work_email,
                            'subject': "Update Milestone score for " + employees.name +" | "+ periods.name,
                            'email_to': employees.parent_id.work_email,
                            'body_html': body,
                            }

                        template.write(mail_values)
                        if template:
                            template.send_mail(periods.id,notif_layout="kwantify_theme.csm_mail_notification_light")

                        body = body.replace(employees.parent_id.name,"--ra_name--").replace(employees.name,"--employee_name--")
                        mail_values = {'body_html': body}
                        template.write(mail_values)

        except Exception as e:
            # print("From Assessment Feedback Cron : ",e)
            pass
        
    def probation_assessment_due_data(self):
        ir_config_params = self.env['ir.config_parameter'].sudo()
        start_day = ir_config_params.get_param('kw_assessment_feedback.probation_assessment_start_date') or 0
        end_day = ir_config_params.get_param('kw_assessment_feedback.probation_assessment_end_date') or 0
        current_month = datetime.today().month
        current_year = datetime.today().year
        start_date = datetime.strptime(f"{current_year}-{current_month}-{start_day}", "%Y-%m-%d").date()
        end_date = datetime.strptime(f"{current_year}-{current_month}-{end_day}", "%Y-%m-%d")
        current_day = datetime.now().day
        
        next_month = (end_date.month % 12) + 1
        next_year = end_date.year + (end_date.month // 12)
        next_month_date = datetime(next_year,next_month,end_date.day)
        next_month_date_string = next_month_date.strftime("%Y-%m-%d")
        
        
        
        employee_probation = self.env['hr.employee'].sudo().search([
            ('active','=',True),
            ('on_probation','=',True),
            ('date_of_completed_probation', '>=', start_date.strftime('%Y-%m-%d')),
            ('date_of_completed_probation', '<=', next_month_date_string)
        ])
       
        if employee_probation:
            if start_day <= str(current_day) <= end_day:
                template = self.env.ref('kw_assessment_feedback.probation_completion_record')
                users = self.env['res.users'].sudo().search([])
                manager = users.filtered(lambda user: user.has_group('kw_assessment_feedback.group_assessment_feedback_manager') == True)
                email_to = ','.join(manager.mapped('email'))
                template_data=self.env['mail.template'].sudo().browse(template.id)
                if template:
                    template_data.with_context(records=employee_probation,mail_to=email_to).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                    
                
       

        
           
        