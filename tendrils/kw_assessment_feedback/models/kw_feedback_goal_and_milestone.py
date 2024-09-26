# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import calendar


class kw_feedback_goal_and_milestone(models.Model):
    _name       = 'kw_feedback_goal_and_milestone'
    # _description= 'Assessment feedback goal and milestone.'
    _description= 'Assessment goal and milestone'
    _rec_name   = 'goal_name'

    @api.model
    def _get_employee_list(self):
        emp_list = []
        emp_list2 = []

        period_name = date.today().strftime("%B")+"-"+str(date.today().year)
       
        records = self.env['kw_feedback_assessment_period'].search([('name','ilike',period_name),('map_resource_id.assessment_tagging_id.is_goal','=',True)])
        
        for record in records:
            for employees in record.assessees:
                if employees.id not in emp_list:
                    emp_list.append(employees.id)

        goal_records = self.search([('months','=',str(date.today().month)),('year','=',str(date.today().year))])
        for goals in goal_records:
            emp_list2.append(goals.emp_id.id) if goals.emp_id.id not in emp_list2 else False

        return [('parent_id.user_id','=',self.env.uid),('id','in',emp_list),('id','not in',emp_list2)]
    
    @api.model
    def _get_year_list(self):
        current_year = date.today().year
        return [(str(i),i) for i in range(current_year, 2005, -1)]
    
    MONTH_LIST= [
        ('1','January'),('2','February'),
        ('3','March'),('4','April'),
        ('5','May'),('6','June'),
        ('7','July'),('8','August'),
        ('9','September'),('10','October'),
        ('11','November'),('12','December')
        ]
 
    emp_id      = fields.Many2one('hr.employee', string='Employee', required=True,domain=_get_employee_list)
    designation = fields.Many2one('hr.job',string="Designation",related="emp_id.job_id")
    department  = fields.Many2one('hr.department',string="Department",related="emp_id.department_id")
    year        = fields.Selection(string='Year',selection='_get_year_list',default=str(date.today().year))
    months      = fields.Selection(MONTH_LIST, string='Month',default=str(date.today().month))
    goal_name   = fields.Char(string='Goal', required=True,autocomplete="off")
    milestones  = fields.One2many('kw_feedback_milestone', 'goal_id', string='Milestone')
    feedback_id = fields.Many2one(comodel_name='kw_feedback_details',string='Feedback Name')
    period_id   = fields.Many2one(comodel_name='kw_feedback_assessment_period',string='Period Name')
    state       = fields.Selection(selection=[('1','Not Started'),('2','Milestone Updated'),('3','Progress Updated'),('4','Published')],default='1',string='Goal Status')
    
    from_date   = fields.Boolean(string="Compare from date", compute='_from_date', store=False)
    date_time   = fields.Date(string='Current Date', compute='_find_current_date', store=False)

    current_month = fields.Boolean(search="_search_current_month",compute='_compute_current_month')
    last_month = fields.Boolean(search="_search_last_month",compute='_compute_last_month')

    validate_own = fields.Boolean(compute='_validate_own_record')

    @api.multi
    def _validate_own_record(self):
        for record in self:
            if record.emp_id.user_id and record.emp_id.user_id.id == self._uid:
                record.validate_own = True
            else:
                record.validate_own = False

    @api.multi
    def _compute_current_month(self):
        for record in self:
            pass
    
    @api.multi
    def _compute_last_month(self):
        for record in self:
            pass
    
    @api.multi
    def _search_current_month(self, operator, value):
        month = date.today().month
        year = date.today().year
        return ['&',('months', '=', str(month)), ('year', '=', str(year))]

    @api.multi
    def _search_last_month(self, operator, value):
        month = date.today().month-1
        year = date.today().year
        if month == 0:
            month = 12
            year = year - 1
        return ['&',('months', '=', str(month)),('year', '=', str(year))]

    @api.multi
    def _find_current_date(self):
        for record in self:
            record.date_time = date.today()

    @api.multi
    def _from_date(self):
        for record in self:
            from_date = datetime.strptime(date(int(record.year), int(record.months), 25).strftime('%Y-%m-%d'), '%Y-%m-%d').date()
            
            if from_date > record.date_time:
                record.from_date = True

    @api.constrains('goal_name','emp_id')
    def check_goal_name(self):
        record = self.env['kw_feedback_goal_and_milestone'].search([]) - self
        for info in record:
            if info.emp_id.id == self.emp_id.id and info.goal_name.lower() == self.goal_name.lower():
                raise ValidationError(
                    f'Exist! Already a same goal exist for employee {self.emp_id.name}.')
            if info.emp_id.id == self.emp_id.id and info.year == self.year and info.months == self.months:
                raise ValidationError(
                    f'Exist! Already goal exist for employee {self.emp_id.name} of same year and month.')
    
    @api.model
    def create(self,vals):
        new_record = super(kw_feedback_goal_and_milestone,self).create(vals)
        if new_record.milestones:
            new_record.write({'state':'2'})
        return new_record
    
    @api.multi
    def write(self,vals):
        updated_record = super(kw_feedback_goal_and_milestone,self).write(vals)
        if self.milestones and self.state in ['1']:
            self.write({'state':'2'})
        return updated_record

    @api.constrains('milestones')
    def check_milestones(self):
        for rec in self:
            if len(rec.milestones) == 0:
                raise ValidationError('Minimum one milestones must be there.')

    @api.multi
    def feedback_redirect(self):
        self.write({'state':'3'})
        self.env.user.notify_success("Progress updated successfully.")
        return {'type': 'ir.actions.act_window_close'}

    def update_milestone(self):

        form_res = self.env['ir.model.data'].get_object_reference('kw_assessment_feedback', 'kw_feedback_goal_and_milestone_form_reference')
        form_id = form_res and form_res[1] or False

        actions = {
            'name': 'Goal & Milestones',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'res_model': 'kw_feedback_goal_and_milestone',
            'res_id':self.id,
            'views': [(form_id, 'form')],
            'target':'new'
            }

        return actions

    @api.model
    def save_goal_data(self,args):
        # print(args)
        values = []
        feedback_details_id = args.get('feedback_details_id',False)
        token = args.get('token',False)
        values.extend([feedback_details_id,token])
        feedback_details = self.env['kw_feedback_final_config'].sudo().search([('id','=',int(feedback_details_id) if feedback_details_id else False)])

        current_goal_data = args.get('current_goal_data',False)
        next_goal_data = args.get('next_goal_data',False)

        goal_model = self.env['kw_feedback_goal_and_milestone'].sudo()

        period_date = feedback_details.feedback_details_id.period_id.period_date
        #current
        c_year = period_date.year
        c_month = period_date.month
        
        # next 
        n_year = period_date.year
        n_month = period_date.month + 1
        if n_month > 12:
            n_month = n_month - 12
            n_year = n_year + 1
        
        if current_goal_data:
            current_year_goal_data = goal_model.search([
                ('emp_id','=',feedback_details.assessee_id.id),
                ('year','=',str(c_year)),
                ('months','=',str(c_month))
            ],limit=1)
            # print(current_year_goal_data)
            if current_year_goal_data:
                milestone = []
                for data in current_goal_data.get('milestones',False):
                    milestone.append([0, 0, 
                                {
                                'milestone_name': data.get('milestone_name') if 'milestone_name' in data else False,
                                'score': float(data.get('score')) if 'score' in data else False,
                                'weightage_id': int(data.get('weightage_id')) if 'weightage_id' in data and data['weightage_id'] != '' else False,
                                }
                                ])
                milestone += [[2, milestones.id] for milestones in current_year_goal_data.milestones]

                # print(milestone)
                current_year_goal_data.write({
                    'goal_name':current_goal_data.get('goal_name',False),
                    'milestones':milestone,
                    'feedback_id':feedback_details.feedback_details_id.id,
                    'period_id':feedback_details.feedback_details_id.period_id.id,
                })
        
        if next_goal_data:
            next_year_goal_data = goal_model.search([
                ('emp_id','=',feedback_details.assessee_id.id),
                ('year','=',str(n_year)),
                ('months','=',str(n_month))
            ],limit=1)
            # print(next_year_goal_data)
            
            next_goal_name = next_goal_data.get('goal_name',False)
            next_milestone = []
            if next_goal_data.get('milestones',False):
                for data in next_goal_data.get('milestones',False):
                    # print(data.get('weightage_id'))
                    next_milestone.append([0, 0, 
                                {
                                'milestone_name': data.get('milestone_name',False),
                                # 'score': float(data.get('score')) if data.get('score') else 0.0,
                                # 'weightage_id': int(data.get('weightage_id')) if data.get('weightage_id') else False,
                                }
                                ])
                if next_year_goal_data:
                    next_milestone += [[2, milestones.id] for milestones in next_year_goal_data.milestones]

                    # print(next_milestone)
                    next_year_goal_data.write({
                        'goal_name':next_goal_name,
                        'milestones':next_milestone,
                    })
                else:
                    goal_model.create({
                        'emp_id':feedback_details.assessee_id.id,
                        'goal_name': next_goal_name,
                        'milestones': next_milestone,
                        'year': str(n_year),
                        'months': str(n_month)
                    })
            else:
                pass

        return values