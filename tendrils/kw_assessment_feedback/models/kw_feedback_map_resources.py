# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import time
import re
from odoo.exceptions import  ValidationError, UserError
from datetime import datetime, timedelta,date
from collections import OrderedDict
import calendar
from dateutil import rrule as rrule_module
from dateutil.relativedelta import relativedelta


class kw_feedback_map_resources(models.Model):
    _name       = 'kw_feedback_map_resources'
    _description= 'Assessment feedback Map resouces model'
    _rec_name   = 'assessment_tagging_id'

    assessment_tagging_id =  fields.Many2one('kw_feedback_assessment',string='Assessment Type',required=True,ondelete='restrict')
    assessment_from_date = fields.Date(string='Start Date ',autocomplete="off")
    assessment_to_date  = fields.Date(string='End Date ',autocomplete="off")
    assessment_date  = fields.Date(string='Assessment Date ',autocomplete="off")
    select_assessee     = fields.Many2many('hr.employee','kw_feedback_assessee_rel','feedback_id','emp_id',string='Select Assessee')
    select_assessor     = fields.Many2many('hr.employee','kw_feedback_assessor_rel','feedback_id','emp_id',string='Select Assessor',domain="[('id','not in',select_assessee)]")

    # def _get_default_survey_template(self):
    #     feedback_survey_id = self.env.ref('kw_assessment_feedback.kw_feedback_assessment_survey_type_form')
    #     if feedback_survey_id:
    #         return feedback_survey_id.id
    #     else:
    #         return False

    survey_id           = fields.Many2one(comodel_name ='survey.survey',string='Template Type',required=True,domain="[('survey_type.code','=','assessment_feedback')]",ondelete='restrict')
    total_answers       = fields.Integer(string="Count Answers", compute="_compute_completed_answers")
    period_ids          = fields.One2many('kw_feedback_assessment_period','map_resource_id',string='Feedback Periods')
    hide_period_action_buttons = fields.Boolean(string="Hide Period Action Buttons",compute="_hide_period_action_buttons",default=False)
    rrule_type      = fields.Selection(related='assessment_tagging_id.frequency', string='Recurrence', help="Let the event automatically repeat at that interval")

    mo              = fields.Boolean('Mon')
    tu              = fields.Boolean('Tue')
    we              = fields.Boolean('Wed')
    th              = fields.Boolean('Thu')
    fr              = fields.Boolean('Fri')
    sa              = fields.Boolean('Sat')
    su              = fields.Boolean('Sun')

    month_by        = fields.Selection([
        ('date', 'Date of month'),
        ('day', 'Day of month')
    ], string='Option', default='date')
    day             = fields.Integer('Date of month', default=1)
    week_list       = fields.Selection([
        ('MO', 'Monday'),
        ('TU', 'Tuesday'),
        ('WE', 'Wednesday'),
        ('TH', 'Thursday'),
        ('FR', 'Friday'),
        ('SA', 'Saturday'),
        ('SU', 'Sunday')
    ], string='Weekday')
    byday           = fields.Selection([
        ('1', 'First'),
        ('2', 'Second'),
        ('3', 'Third'),
        ('4', 'Fourth'),
        ('5', 'Fifth'),
        ('-1', 'Last')
    ], string='By day')
    rrule = fields.Char('Recurrent Rule', compute='_compute_rrule', store=True)
    active = fields.Boolean(string="Active", default=True)

    # deactive_records = fields.Boolean(compute='_get_deactivate_records', store=False)

    # @api.multi
    # @api.depends('assessment_to_date','select_assessee')
    # def _get_deactivate_records(self):
    #     for record in self:
    #         if (record.assessment_to_date and record.assessment_to_date < date.today()) or not record.select_assessee:
    #             record.write({'active':False})
    #         else:
    #             record.write({'active':True})

    @api.depends('byday', 'assessment_from_date', 'assessment_to_date','rrule_type','assessment_tagging_id', 'month_by','mo',
                 'tu', 'we', 'th', 'fr', 'sa', 'su', 'day', 'week_list')
    def _compute_rrule(self):
        """ Gets Recurrence rule string according to value type RECUR of iCalendar from the values given.
            :return dictionary of rrule value.
        """
        for record in self:
            if record.assessment_from_date and record.assessment_tagging_id.frequency == 'monthly':
                record.day = int(record.assessment_from_date.day)
                record.month_by = 'date'
            if record.assessment_tagging_id.frequency in ['weekly','monthly','yearly','daily']:
                record.rrule = record._rrule_serialize()
            else:
                record.rrule = False

    @api.multi
    def _rrule_serialize(self):
        """ Compute rule string according to value type RECUR of iCalendar
            :return: string containing recurring rule (empty if no rule)
        """
        if self.assessment_to_date and self.assessment_from_date and self.assessment_to_date < self.assessment_from_date:
            raise UserError('End date can not be less than start date.')       

        def get_week_string(freq):
            weekdays = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']
            if freq == 'weekly':
                byday = [field.upper() for field in weekdays if self[field]]
                if byday:
                    return ';BYDAY=' + ','.join(byday)
            return ''

        def get_month_string(freq):
            if freq == 'monthly':
                if self.month_by == 'date' and (self.day < 1 or self.day > 31):
                    raise UserError("Please select a proper day of the month.")

                if self.month_by == 'day' and self.byday and self.week_list:  # Eg : Second Monday of the month
                    return ';BYDAY=' + self.byday + self.week_list
                elif self.month_by == 'date':  # Eg : 16th of the month
                    return ';BYMONTHDAY=' + str(self.day)
            return ''

        def get_end_date():
            final_date      = fields.Date.to_string(self.assessment_to_date)
            end_date_new    = ''.join((re.compile('\d')).findall(final_date)) + 'T235959Z' if final_date else False
            return  ((end_date_new and (';UNTIL=' + end_date_new)) or '')

        freq    = self.assessment_tagging_id.frequency  # day/week/month/year
        result  = ''
        if freq:
            result = 'FREQ=' + freq.upper() + get_week_string(
                freq) + get_end_date() + get_month_string(freq)
        return result

    @api.multi
    @api.constrains('assessment_from_date', 'assessment_to_date')
    def feedback_date_constrains(self):
        for record in self:
            if record.assessment_to_date < record.assessment_from_date:
                raise ValidationError('Feedback assessment from date must be less than to date...!')

    @api.constrains('select_assessee','select_assessor','assessment_tagging_id')
    def _validate_minimum_records(self):
        mapping_records = self.env['kw_feedback_map_resources'].search([]) - self

        for record in self:
            if not record.select_assessor or not record.select_assessee:
                raise ValidationError("Assessee or Assessor list should not be blank.")

            for resources in mapping_records:

                duplicate = list(set(resources.select_assessee.ids) & set(record.select_assessee.ids)) ## Intersections between two sets

                if duplicate and record.assessment_tagging_id.id == resources.assessment_tagging_id.id:
                    raise ValidationError(f'Some assessees were already tagged with the same "{record.assessment_tagging_id.name}"')
    @api.multi
    def action_clear_periods(self):
        self.ensure_one()
        # clear all periods
        self.env['kw_feedback_assessment_period'].search([('map_resource_id','=',self.id)]).unlink()
        self.env.user.notify_warning("Assessment periods deleted successfully.")
        return

    @api.multi
    def _compute_completed_answers(self):
        for record in self:
            answers = self.env['kw_feedback_details'].search(['&',('feedback_status', 'in', ['3','4']),('map_resource_id', '=', record.ids[0])])
            record.total_answers = len(answers)

    @api.multi
    def action_get_answers(self):
        tree_res = self.env['ir.model.data'].get_object_reference('kw_assessment_feedback', 'kw_feedback_feedback_answers_tree_view')
        tree_id = tree_res and tree_res[1] or False

        form_res = self.env['ir.model.data'].get_object_reference('kw_assessment_feedback', 'kw_feedback_feedback_answers_form_view')
        form_id = form_res and form_res[1] or False

        return {
            'model': 'ir.actions.act_window',
            'name': 'Answers',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'kw_feedback_details',
            'views': [(tree_id, 'tree'), (form_id, 'form')],
            'domain': ['&',('feedback_status', 'in', ['3','4']), ('map_resource_id', '=', self.ids[0])],
        }

    @api.multi
    def action_generate_periods(self):
        self.ensure_one()
        try:
            if self.assessment_tagging_id and ((self.assessment_from_date and self.assessment_to_date) or self.assessment_date):
                periods = self.env['kw_feedback_assessment_period'].search([('map_resource_id','=',self.id)])

                date_set=[]
                vals = []

                if self.assessment_tagging_id.frequency in ['weekly','monthly','yearly','daily']:
                    date_set = list(rrule_module.rrulestr(str(self.rrule), dtstart=self.assessment_from_date, forceset=True,ignoretz=True))

                elif self.assessment_tagging_id.frequency in ['quarterly','half_yearly','bi_monthly']:

                    start_date, end_date = self.assessment_from_date,self.assessment_to_date
                    delta = relativedelta(end_date, start_date)
                    month_gap = 0

                    if self.assessment_tagging_id.frequency == 'quarterly':
                        month_gap = 3
                    elif self.assessment_tagging_id.frequency == 'half_yearly':
                        month_gap = 6
                    elif self.assessment_tagging_id.frequency == 'bi_monthly':
                        month_gap = 2

                    date_set = [datetime.strptime(datetime.strftime(start_date + relativedelta(months=i), '%d-%m-%Y'), '%d-%m-%Y')for i in range(0, delta.years * 12 + delta.months + 1, month_gap)]
                
                elif self.assessment_tagging_id.frequency in ['custom']:
                    date_set = [datetime.strptime(datetime.strftime(self.assessment_date, '%d-%m-%Y'),'%d-%m-%Y')]

                if len(date_set) > 0:
                    # self.env['kw_feedback_assessment_period'].search([('map_resource_id','=',self.id)]).unlink()
                    name_list = []
                    for all_dates in date_set:
                        
                        period_dict = {}

                        dates = all_dates.date()

                        last_date = calendar.monthrange(int(dates.year), int(dates.month))[1]

                        name = all_dates.date().strftime("%B")+"-"+str(all_dates.date().year)
                        filtered_periods = periods.filtered(lambda period:period.name == name and period.active in [True,False])
                        name_list.append(name)
                        if filtered_periods:
                            if filtered_periods.state == '1':
                                period_dict.update({
                                    'assessees':[(6,False,self.select_assessee.ids)],
                                    'assessors':[(6,False,self.select_assessor.ids)],
                                    'survey_id': self.survey_id.id,
                                    'from_date': (date(int(dates.year), int(dates.month), 25)).strftime('%Y-%m-%d'),
                                    'to_date':(date(int(dates.year), int(dates.month), int(last_date))).strftime('%Y-%m-%d'),
                                })
                                vals.append([1,filtered_periods.id,period_dict])
                            else:
                                pass
                        else:
                            period_dict.update({
                                'name':all_dates.date().strftime("%B")+"-"+str(all_dates.date().year),
                                'period_date':dates,
                                'assessees':self.select_assessee.ids,
                                'assessors':self.select_assessor.ids,
                                'survey_id': self.survey_id.id,
                            })

                            if self.assessment_tagging_id.frequency in ['custom']:
                                period_dict.update({
                                    'assessment_date': self.assessment_date,
                                })
                            else:
                                period_dict.update({
                                    'from_date': (date(int(dates.year), int(dates.month), 25)).strftime('%Y-%m-%d'),
                                    'to_date': (date(int(dates.year), int(dates.month), int(last_date))).strftime('%Y-%m-%d'),
                                })
                            vals.append([0,0,period_dict])

                    for period in periods:
                        if period.state == '1' and period.name not in name_list:
                            period.unlink()
                        else:
                            pass

                    self.period_ids = vals

                self.env.user.notify_success("Assessment periods generated successfully.")
        except Exception as e:
            # print("Assessment Map Resource error : ",e) 
            pass   
        return
    
    @api.multi
    def _hide_period_action_buttons(self):
        for record in self:
            result = record.period_ids.filtered(lambda period:period.state == '2')
            record.hide_period_action_buttons = True if result else False
    
    @api.model
    def create(self,vals):
        new_record = super(kw_feedback_map_resources,self).create(vals)
        new_record._add_to_specific_group()
        return new_record
    
    @api.multi
    def write(self,vals):
        update_record = super(kw_feedback_map_resources,self).write(vals)
        if 'select_assessor' in vals or 'select_assessee' in vals:
            self._add_to_specific_group()
        return update_record

    def _add_to_specific_group(self):
        assessor_group = self.env.ref('kw_assessment_feedback.group_assessment_feedback_assessor')
        assessee_group = self.env.ref('kw_assessment_feedback.group_assessment_feedback_assessee')
        assessor_users = self.select_assessor.mapped('user_id')
        for user in assessor_users:
            if not user.has_group('kw_assessment_feedback.group_assessment_feedback_assessor'):
                assessor_group.sudo().write({'users': [(4, user.id)]})

        assessee_users = self.select_assessee.mapped('user_id')
        for user in assessee_users:
            if not user.has_group('kw_assessment_feedback.group_assessment_feedback_assessee'):
                assessee_group.sudo().write({'users': [(4, user.id)]})
