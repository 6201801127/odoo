# -*- coding: utf-8 -*-
from asyncio.constants import LOG_THRESHOLD_FOR_CONNLOST_WRITES
from syslog import LOG_NOTICE
from odoo.exceptions import ValidationError
from odoo import models, fields, api
from datetime import date, datetime
import re


class Claim(models.Model):
    _name = 'kw_claim'
    _rec_name = "code"
    _inherit = ['mail.thread', 'mail.activity.mixin']
        
    def _default_employee(self):
        return self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)], limit=1)
    
    # @api.depends('first_approver_id','reviewer_ids')
    # def check_pending_at(self):
    #     for record in self:
    #         reviewers =[]
    #         if record.first_approver_id and record.state=='applied':
    #             record.pending_at = f"Pending at {record.first_approver_id.name}"
    #         # elif record.second_approver_id and record.state=='applied':
    #         #     record.pending_at = f"Pending at {record.second_approver_id.name}"
    #         elif record.state=='approved':
    #             record.pending_at = 'Pending at Finance'
    #         elif record.state=='disbursed':
    #             record.pending_at = 'Disbursed'
    #         else:
    #             record.pending_at = '--'

    #         if record.reviewer_ids.ids and  record.state == 'applied':
    #             for rec in record.reviewer_ids:
    #                 reviewers.append(rec.name)
    #             reviewer_emp = ', '.join(reviewers)
    #             record.pending_at = f"Pending at {reviewer_emp}"
                
    @api.depends('state','employee_id')
    def _check_enable_editing(self):
        for rec in self:
            if rec.employee_id.user_id.id == self.env.user.id and rec.state == 'draft':
                rec.check_user_boolean = True
            if self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_account') and rec.state == 'approved':
                rec.check_user_boolean = True
                
    
    
    employee_id = fields.Many2one('hr.employee',default=_default_employee)
    department_id = fields.Many2one('hr.department')
    division = fields.Many2one('hr.department')
    section = fields.Many2one('hr.department' ,string="Practice")
    practise = fields.Many2one('hr.department', string="Section")
    job_id = fields.Many2one('hr.job')
    grade_id = fields.Many2one('kwemp_grade_master')
    category_id = fields.Many2one('kw_advance_claim_category',domain="[('category','=','claim')]", track_visibility='onchange')
    # sub_category_id = fields.Many2many('claim_sub_category_master')
    remark = fields.Text()
    amount = fields.Float(string="Amount",compute='_compute_total_amount',store=True)
    state = fields.Selection([('draft','Draft'),('applied','Applied'),('approved','Approved'),('reject','Rejected'),('verified','Verified'),('disbursed','Disbursed')],default='draft',track_visibility='onchange')
    first_approver_id = fields.Many2one('hr.employee')
    second_approver_id = fields.Many2one('hr.employee')
    reviewer_ids = fields.Many2many('hr.employee','kw_employee_claim_rel','employee_id','claim_id',string='Reviewer')
    reviewer_id = fields.Many2one('hr.employee',string='Reviewer')
    user_id = fields.Many2one('res.users')
    code = fields.Char()
    currency_id = fields.Many2one('res.currency', string='Currency',default=lambda self: self.env.user.company_id.currency_id.id,)
    direct_parent = fields.Boolean(compute='check_direct_parent')
    second_parent = fields.Boolean(compute='check_second_parent')
    show_reject_first = fields.Boolean(compute='check_reject_option_first')
    show_reject_second = fields.Boolean(compute='check_reject_option_second')
    log_ids = fields.One2many('claim_log_details','claim_id',string='Action Log')
    pending_at = fields.Char('Application Status/Progress')
    year = fields.Integer(string='Year')
    month = fields.Integer(string='Month')
    sub_category_ids = fields.One2many('sub_category_item_amount_config','claim_id',string='Sub Category')
    show_revert_boolean = fields.Boolean()
    check_revert_boolean = fields.Boolean(compute='check_revert_option') 
    apply_boolean=fields.Boolean(compute='check_revert_option')
    write_uid = fields.Many2one('res.users',track_visibility='onchange')
    write_date= fields.Datetime(track_visibility='onchange') 
    upload_doc = fields.Binary(string='Supporting Document', attachment=True)
    file_name = fields.Char("File Name", track_visibility='onchange')
    check_user_boolean = fields.Boolean(compute='_check_enable_editing')
    project_id = fields.Many2one(comodel_name='crm.lead',string='Work Order',track_visibility='onchange',domain= [('stage_id.code', '=', 'workorder')])
    budget = fields.Selection([('project_budget','Project'),('treasury_budget','Treasury')],compute='_budget_type')




    @api.depends('category_id')
    def _budget_type(self):
        for rec in self:
            category = rec.category_id
            rec.budget = 'project_budget' if category and category.type == 'project_budget' else 'treasury_budget'


    def action_revert(self):
        self.write({ 'show_revert_boolean':False,
                    'state':'draft',
                    'log_ids':[[0,0,{
                    'date':date.today(),
                    'action_taken_by':self.env.user.employee_ids.id,
                    'state':'Draft',
                    'claim_id':self.id,
                    'remark':f"Reverted by {self.env.user.employee_ids.name}",
                     }]]
                                    
                })
   
        
    @api.onchange('employee_id')
    def _change_employee(self):
        for rec in self:
            rec.department_id = rec.employee_id.department_id.id if rec.employee_id.department_id else False
            rec.division = rec.employee_id.division.id if rec.employee_id.division else False
            rec.section = rec.employee_id.section.id if rec.employee_id.section else False
            rec.practise = rec.employee_id.practise.id if rec.employee_id.practise else False
            rec.job_id = rec.employee_id.job_id.id if rec.employee_id.job_id else False
            rec.grade_id = rec.employee_id.grade.id if rec.employee_id.grade else False
            # rec.currency_id = rec.employee_id.company_id.currency_id.id if rec.employee_id.company_id.currency_id else False
            
    @api.constrains('employee_id','sub_category_ids')
    def check_sub_category_ids(self):
        for rec in self:
            if len(rec.sub_category_ids) == 0:
                raise ValidationError("Please choose sub-category items.")

            
    @api.constrains('category_id')
    def check_limit(self):
        amt = 0
        for rec in self:
            if self.env.user.employee_ids.company_id.currency_id.name == 'INR':
                claim_limit = self.env['claim_category_limit'].sudo().search([('currency_id.name','=','INR')])
                amt = sum(rec.sub_category_ids.mapped('amount'))
                config_record = claim_limit.filtered(lambda x:x.category_id.id == rec.category_id.id and x.limit_to >= amt)
                config_set_rec = claim_limit.search([('category_id','=',rec.category_id.id)],order='limit_to desc',limit=1)
                if not config_record:
                    # if len(config_set_rec) == 1:
                        raise ValidationError(f"Apply within the configured amount {self.env.user.employee_ids.company_id.currency_id.name} {config_set_rec.limit_to}.")

                    
    @api.depends('sub_category_ids') 
    def _compute_total_amount(self):
        for rec in self.sub_category_ids:
            self.amount +=rec.amount 
            
            
    @api.onchange('category_id')
    def _change_category(self):
        for rec in self:
            rec.sub_category_ids = False
            rec.project_id = False
            if self.category_id and self.env.user.employee_ids.company_id.currency_id.name == 'INR':
                limit_rec = self.env['claim_category_limit'].sudo().search([('category_id','=',self.category_id.id),('currency_id.name','=','INR')])
                if not limit_rec:
                    raise ValidationError(f"Configure the amount against {self.category_id.name}")

           
    @api.onchange('sub_category_ids')
    def validate_unit(self):
        for data in self.sub_category_ids:
            if data.item_unit:
                if not re.match(r"^[a-zA-Z ]*$",data.item_unit):
                    return {'warning': {
                    'title': ('Validation Error'),
                    'message': (f"{data.item_unit} : Unit Type not acceptable")
                    }}
    
    # def check_parent(self,employee_id,filtered_claim_limit_rec):
    #     # if employee_id.grade.id in filtered_claim_limit_rec.grade_ids.ids and employee_id.budget_type=='project' and employee_id.employement_type.code in ['S','C']:
    #     #      self.check_parent(employee_id.parent_id,filtered_claim_limit_rec)
    #     # else:
    #     if employee_id.grade.id in filtered_claim_limit_rec.grade_ids.ids and employee_id.parent_id:
    #         self.first_approver_id = employee_id.id
    #     else:
    #         self.check_parent(employee_id.parent_id,filtered_claim_limit_rec)
            
            
    def check_parent_sort_num1(self,employee_id,sort_num):
        if employee_id.parent_id:
            if employee_id.grade.id in sort_num.grade_ids.ids:
                self.first_approver_id =  employee_id.id
            else:
                self.check_parent_sort_num1(employee_id.parent_id,sort_num)
        else:
            self.first_approver_id = False
    
    def check_parent_sort_num2(self,employee_id,sort_num):
        if employee_id.parent_id :
            if employee_id.grade.id in sort_num.grade_ids.ids:
                self.second_approver_id =  employee_id.id
            else:
                self.check_parent_sort_num2(employee_id.parent_id,sort_num)
        else:
             self.second_approver_id = False
       
       
    def check_parent_sort_num_reviewer(self,employee_id,sort_num):
        if employee_id.parent_id:
            if employee_id.id in sort_num.employee_ids.ids:
                self.reviewer_id = employee_id.id
            else:
                self.check_parent_sort_num_reviewer(employee_id.parent_id,sort_num)
        else:
            self.reviewer_id = False



    def action_apply_btn(self):
        level_rec = self.env['level_configuration'].sudo().search([])
        claim_limit_rec = self.env['claim_category_limit'].sudo().search([])
        for rec in self:
            rec.year = int(date.today().year)
            rec.month = int(date.today().month)
            filtered_level = level_rec.filtered(lambda x : rec.grade_id.id in x.grade_ids.ids)
            sort1_rec = claim_limit_rec.filtered(lambda x : x.sort_no == 1 and x.category_id.id == rec.category_id.id )
            sort2_rec = claim_limit_rec.filtered(lambda x : x.sort_no == 2 and x.category_id.id == rec.category_id.id )
            sort3_rec = claim_limit_rec.filtered(lambda x : x.sort_no == 3 and x.category_id.id == rec.category_id.id )
            """For employee grade below M8"""
            if self.env.user.employee_ids.company_id.currency_id.name == 'INR':
                if filtered_level.sort_no == 1:
                    
                    """check limit"""
                    if rec.amount <= sort1_rec.limit_to:
                        rec.check_parent_sort_num1(rec.employee_id,sort1_rec)
                        if rec.first_approver_id.id:
                            rec.write({ 
                                'user_id':rec.first_approver_id.user_id.id,
                                'pending_at':f"Pending at {rec.first_approver_id.name}",
                                'show_revert_boolean':False,
                                'state':'applied',
                                'log_ids':[[0,0,{
                                    'date':date.today(),
                                    'action_taken_by':self.env.user.employee_ids.id,
                                    'state':'Applied',
                                    'claim_id':rec.id,
                                    'remark':f"Applied by {rec.employee_id.name}",
                                    }]]
                                }) 
                            #   mail to first approver
                            to_mail = rec.first_approver_id.work_email if rec.first_approver_id.work_email else '' 
                            user_name = rec.first_approver_id.name if rec.first_approver_id.name else '' 
                            extra_params = {'to_mail': to_mail, 'user_name': user_name}
                            if to_mail:
                                self.env['remark_wizard'].claim_send_custom_mail(res_id=rec.id,
                                                                                notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                                template_layout='claim.claim_notification_approver',
                                                                                ctx_params=extra_params,
                                                                                description="Claim Request")
                                self.env.user.notify_success("Claim Notifcation Sent Successfully.")
                    if rec.amount <= sort2_rec.limit_to:
                        if not rec.user_id:
                            rec.check_parent_sort_num1(rec.employee_id,sort1_rec)
                            rec.check_parent_sort_num2(rec.employee_id,sort2_rec)
                            if rec.second_approver_id:
                                        # 'second_approver_id': sort_2.id,
                                rec.write({ 
                                        'user_id':rec.second_approver_id.user_id.id,
                                        'pending_at':f"Pending at {rec.second_approver_id.name}",
                                        'show_revert_boolean':False,
                                        'state':'applied',
                                        'log_ids':[[0,0,{
                                            'date':date.today(),
                                            'action_taken_by':self.env.user.employee_ids.id,
                                            'state':'Applied',
                                            'claim_id':rec.id,
                                            'remark':f"Applied by {rec.employee_id.name}",
                                            }]]
                                        })
                                to_mail = rec.second_approver_id.work_email if rec.second_approver_id.work_email else '' 
                                user_name = rec.second_approver_id.name if rec.second_approver_id.name else '' 
                                extra_params = {'to_mail': to_mail, 'user_name': user_name}
                                if to_mail:
                                    self.env['remark_wizard'].claim_send_custom_mail(res_id=rec.id,
                                                                                    notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                                    template_layout='claim.claim_notification_approver',
                                                                                    ctx_params=extra_params,
                                                                                    description="Claim Request")
                            # if rec.first_approver_id:
                            #     # send notification to sort 1
                            #     to_mail = rec.first_approver_id.work_email if rec.first_approver_id.work_email else '' 
                            #     user_name = rec.first_approver_id.name if rec.first_approver_id.name else '' 
                            #     extra_params = {'to_mail': to_mail, 'user_name': user_name}
                            #     if to_mail:
                            #         self.env['remark_wizard'].claim_send_custom_mail(res_id=rec.id,
                            #                                                         notif_layout='kwantify_theme.csm_mail_notification_light',
                            #                                                         template_layout='claim.claim_notification_approver',
                            #                                                         ctx_params=extra_params,
                            #                                                         description="Claim Request")
                            self.env.user.notify_success("Claim Notifcation Sent Successfully.")
                
                    if rec.amount <= sort3_rec.limit_to:
                        if not rec.user_id:
                            rec.check_parent_sort_num_reviewer(rec.employee_id,sort3_rec)
                            rec.check_parent_sort_num1(rec.employee_id,sort1_rec)
                            rec.check_parent_sort_num2(rec.employee_id,sort2_rec)
                            if rec.reviewer_id:
                                rec.write({ 
                                    'user_id':rec.reviewer_id.user_id.id,
                                    'pending_at':f"Pending at {rec.reviewer_id.name}",
                                    'show_revert_boolean':False,
                                    'state':'applied',
                                    # 'first_approver_id': sort_3.id,
                                    'log_ids':[[0,0,{
                                        'date':date.today(),
                                        'action_taken_by':self.env.user.employee_ids.id,
                                        'state':'Applied',
                                        'claim_id':rec.id,
                                        'remark':f"Applied by {rec.employee_id.name}",
                                        }]]
                                    })
                                to_mail = rec.reviewer_id.work_email if rec.reviewer_id.work_email else '' 
                                user_name = rec.reviewer_id.name if rec.reviewer_id.name else '' 
                                extra_params = {'to_mail': to_mail, 'user_name': user_name}
                                if to_mail:
                                    self.env['remark_wizard'].claim_send_custom_mail(res_id=rec.id,
                                                                                    notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                                    template_layout='claim.claim_notification_approver',
                                                                                    ctx_params=extra_params,
                                                                                    description="Claim Request")
                                # if rec.first_approver_id != rec.reviewer_id.id:
                                #     # send notification to sort 1
                                #     to_mail = rec.first_approver_id.work_email if rec.first_approver_id.work_email else '' 
                                #     user_name = rec.first_approver_id.name if rec.first_approver_id.name else '' 
                                #     extra_params = {'to_mail': to_mail, 'user_name': user_name}
                                #     if to_mail:
                                #         self.env['remark_wizard'].claim_send_custom_mail(res_id=rec.id,
                                #                                                         notif_layout='kwantify_theme.csm_mail_notification_light',
                                #                                                         template_layout='claim.claim_notification_approver',
                                #                                                         ctx_params=extra_params,
                                #                                                         description="Claim Request")
                                # if rec.second_approver_id.id != rec.reviewer_id.id:
                                #     # send notification to sort2 
                                #     to_mail = rec.second_approver_id.work_email if rec.second_approver_id.work_email else '' 
                                #     user_name = rec.second_approver_id.name if rec.second_approver_id.name else '' 
                                #     extra_params = {'to_mail': to_mail, 'user_name': user_name}
                                #     if to_mail:
                                #         self.env['remark_wizard'].claim_send_custom_mail(res_id=rec.id,
                                #                                                         notif_layout='kwantify_theme.csm_mail_notification_light',
                                #                                                         template_layout='claim.claim_notification_approver',
                                #                                                         ctx_params=extra_params,
                                #                                                         description="Claim Request")
                                self.env.user.notify_success("Claim Notifcation Sent Successfully.")
                    elif (not sort1_rec and not sort2_rec and sort3_rec ) or (not sort1_rec and sort2_rec and not sort3_rec) or (sort1_rec and not sort2_rec and not sort3_rec):
                        category = claim_limit_rec.filtered(lambda x : x.category_id.id == rec.category_id.id)
                        if len(category) == 1:
                            rec.check_parent_sort_num_reviewer(rec.employee_id,sort3_rec)
                            rec.check_parent_sort_num1(rec.employee_id,sort1_rec)
                            rec.check_parent_sort_num2(rec.employee_id,sort2_rec)
                            if not rec.reviewer_id and not rec.first_approver_id and not rec.second_approver_id and rec.employee_id.parent_id:
                                rec.write({ 
                                            'user_id':rec.employee_id.parent_id.user_id.id,
                                            'pending_at':f"Pending at {rec.employee_id.parent_id.user_id.name}",
                                            'show_revert_boolean':False,
                                            'state':'applied',
                                            # 'first_approver_id': sort_3.id,
                                            'log_ids':[[0,0,{
                                                'date':date.today(),
                                                'action_taken_by':self.env.user.employee_ids.id,
                                                'state':'Applied',
                                                'claim_id':rec.id,
                                                'remark':f"Applied by {rec.employee_id.name}",
                                                }]]
                                            })
                                to_mail = rec.employee_id.parent_id.work_email if rec.employee_id.parent_id.work_email else '' 
                                user_name = rec.employee_id.parent_id.name if rec.employee_id.parent_id.name else '' 
                                extra_params = {'to_mail': to_mail, 'user_name': user_name}
                                if to_mail:
                                    self.env['remark_wizard'].claim_send_custom_mail(res_id=rec.id,
                                                                                    notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                                    template_layout='claim.claim_notification_approver',
                                                                                    ctx_params=extra_params,
                                                                                    description="Claim Request")
                                self.env.user.notify_success("Claim Notifcation Sent Successfully.")
                else:
                    if rec.employee_id.id in sort3_rec.employee_ids.ids:
                        # print('1111111111111111111111')
                        rec.write({ 
                                    'pending_at':"Pending at Finance",
                                    'show_revert_boolean':False,
                                    'state':'approved',
                                    'log_ids':[[0,0,{
                                        'date':date.today(),
                                        'action_taken_by':self.env.user.employee_ids.id,
                                        'state':'Applied',
                                        'claim_id':rec.id,
                                        'remark':f"Applied by {rec.employee_id.name}",
                                        }]]
                                    })
                                # mail to finance
                        emp_data = self.env['res.users'].sudo().search([])
                        finance_officer = emp_data.filtered(lambda user: user.has_group('kw_advance_claim.group_kw_advance_claim_account')==True)
                        if finance_officer:
                            for users in finance_officer:
                                to_mail = users.employee_ids.work_email if users.employee_ids.work_email else '' 
                                user_name = users.employee_ids.name if users.employee_ids.name else '' 
                                extra_params = {'to_mail': to_mail, 'user_name': user_name}
                                self.env['remark_wizard'].claim_send_custom_mail(res_id=rec.id,
                                                                                notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                                template_layout='claim.claim_notification_mail_template',
                                                                                ctx_params=extra_params,
                                                                                description="Claim Request")
                            self.env.user.notify_success("Claim Notifcation Sent Successfully.")
                    elif rec.employee_id.grade.id in sort2_rec.grade_ids.ids:
                        # print('22222222222222222222222')

                        if rec.amount <= sort2_rec.limit_to:
                            rec.write({ 
                                        'pending_at':"Pending at Finance",
                                        'show_revert_boolean':False,
                                        'state':'approved',
                                        'log_ids':[[0,0,{
                                            'date':date.today(),
                                            'action_taken_by':self.env.user.employee_ids.id,
                                            'state':'Applied',
                                            'claim_id':rec.id,
                                            'remark':f"Applied by {rec.employee_id.name}",
                                            }]]
                                        })
                                    # mail to finance
                            emp_data = self.env['res.users'].sudo().search([])
                            finance_officer = emp_data.filtered(lambda user: user.has_group('kw_advance_claim.group_kw_advance_claim_account')==True)
                            if finance_officer:
                                for users in finance_officer:
                                    to_mail = users.employee_ids.work_email if users.employee_ids.work_email else '' 
                                    user_name = users.employee_ids.name if users.employee_ids.name else '' 
                                    extra_params = {'to_mail': to_mail, 'user_name': user_name}
                                    self.env['remark_wizard'].claim_send_custom_mail(res_id=rec.id,
                                                                                    notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                                    template_layout='claim.claim_notification_mail_template',
                                                                                    ctx_params=extra_params,
                                                                                    description="Claim Request")
                                self.env.user.notify_success("Claim Notifcation Sent Successfully.")
                        else:
                            rec.check_parent_sort_num_reviewer(rec.employee_id,sort3_rec)
                            if rec.reviewer_id:
                                rec.write({ 
                                    'user_id':rec.reviewer_id.user_id.id,
                                    'pending_at':f"Pending at {rec.reviewer_id.name}",
                                    'show_revert_boolean':False,
                                    'state':'applied',
                                    # 'first_approver_id': sort_3.id,
                                    'log_ids':[[0,0,{
                                        'date':date.today(),
                                        'action_taken_by':self.env.user.employee_ids.id,
                                        'state':'Applied',
                                        'claim_id':rec.id,
                                        'remark':f"Applied by {rec.employee_id.name}",
                                        }]]
                                    })
                                to_mail = rec.reviewer_id.work_email if rec.reviewer_id.work_email else '' 
                                user_name = rec.reviewer_id.name if rec.reviewer_id.name else '' 
                                extra_params = {'to_mail': to_mail, 'user_name': user_name}
                                if to_mail:
                                    self.env['remark_wizard'].claim_send_custom_mail(res_id=rec.id,
                                                                                    notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                                    template_layout='claim.claim_notification_approver',
                                                                                    ctx_params=extra_params,
                                                                                    description="Claim Request")
                            else:
                                raise ValidationError('No Reviewer Found for the Claim Amount')
                    elif rec.employee_id.grade.id in sort1_rec.grade_ids.ids:
                        # print('33333333333333333333333')

                        if rec.amount <= sort1_rec.limit_to:
                            rec.write({ 
                                        'pending_at':"Pending at Finance",
                                        'show_revert_boolean':False,
                                        'state':'approved',
                                        'log_ids':[[0,0,{
                                            'date':date.today(),
                                            'action_taken_by':self.env.user.employee_ids.id,
                                            'state':'Applied',
                                            'claim_id':rec.id,
                                            'remark':f"Applied by {rec.employee_id.name}",
                                            }]]
                                        })
                                    # mail to finance
                            emp_data = self.env['res.users'].sudo().search([])
                            finance_officer = emp_data.filtered(lambda user: user.has_group('kw_advance_claim.group_kw_advance_claim_account')==True)
                            if finance_officer:
                                for users in finance_officer:
                                    to_mail = users.employee_ids.work_email if users.employee_ids.work_email else '' 
                                    user_name = users.employee_ids.name if users.employee_ids.name else '' 
                                    extra_params = {'to_mail': to_mail, 'user_name': user_name}
                                    self.env['remark_wizard'].claim_send_custom_mail(res_id=rec.id,
                                                                                    notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                                    template_layout='claim.claim_notification_mail_template',
                                                                                    ctx_params=extra_params,
                                                                                    description="Claim Request")
                                self.env.user.notify_success("Claim Notifcation Sent Successfully.")
                        else:
                            # print('4444444444444444444444444')

                            if rec.amount <= sort2_rec.limit_to:
                                if not rec.user_id:
                                    rec.check_parent_sort_num1(rec.employee_id,sort1_rec)
                                    rec.check_parent_sort_num2(rec.employee_id,sort2_rec)
                                    if rec.second_approver_id:
                                            # 'second_approver_id': sort_2.id,
                                        rec.write({ 
                                                'user_id':rec.second_approver_id.user_id.id,
                                                'pending_at':f"Pending at {rec.second_approver_id.name}",
                                                'show_revert_boolean':False,
                                                'state':'applied',
                                                'log_ids':[[0,0,{
                                                    'date':date.today(),
                                                    'action_taken_by':self.env.user.employee_ids.id,
                                                    'state':'Applied',
                                                    'claim_id':rec.id,
                                                    'remark':f"Applied by {rec.employee_id.name}",
                                                    }]]
                                                })
                                        to_mail = rec.second_approver_id.work_email if rec.second_approver_id.work_email else '' 
                                        user_name = rec.second_approver_id.name if rec.second_approver_id.name else '' 
                                        extra_params = {'to_mail': to_mail, 'user_name': user_name}
                                        if to_mail:
                                            self.env['remark_wizard'].claim_send_custom_mail(res_id=rec.id,
                                                                                            notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                                            template_layout='claim.claim_notification_approver',
                                                                                            ctx_params=extra_params,
                                                                                            description="Claim Request")
                            
                                            self.env.user.notify_success("Claim Notifcation Sent Successfully.")
                
                            if rec.amount <= sort3_rec.limit_to:
                                # print('55555555555555555555')

                                if not rec.user_id:
                                    rec.check_parent_sort_num_reviewer(rec.employee_id,sort3_rec)
                                    rec.check_parent_sort_num1(rec.employee_id,sort1_rec)
                                    rec.check_parent_sort_num2(rec.employee_id,sort2_rec)
                                    if rec.reviewer_id:
                                        rec.write({ 
                                            'user_id':rec.reviewer_id.user_id.id,
                                            'pending_at':f"Pending at {rec.reviewer_id.name}",
                                            'show_revert_boolean':False,
                                            'state':'applied',
                                            # 'first_approver_id': sort_3.id,
                                            'log_ids':[[0,0,{
                                                'date':date.today(),
                                                'action_taken_by':self.env.user.employee_ids.id,
                                                'state':'Applied',
                                                'claim_id':rec.id,
                                                'remark':f"Applied by {rec.employee_id.name}",
                                                }]]
                                            })
                                        to_mail = rec.reviewer_id.work_email if rec.reviewer_id.work_email else '' 
                                        user_name = rec.reviewer_id.name if rec.reviewer_id.name else '' 
                                        extra_params = {'to_mail': to_mail, 'user_name': user_name}
                                        if to_mail:
                                            self.env['remark_wizard'].claim_send_custom_mail(res_id=rec.id,
                                                                                            notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                                            template_layout='claim.claim_notification_approver',
                                                                                            ctx_params=extra_params,
                                                                                            description="Claim Request")
                                    
                                        # if rec.second_approver_id.id != rec.reviewer_id.id:
                                            # # send notification to sort2 
                                            # to_mail = rec.second_approver_id.work_email if rec.second_approver_id.work_email else '' 
                                            # user_name = rec.second_approver_id.name if rec.second_approver_id.name else '' 
                                            # extra_params = {'to_mail': to_mail, 'user_name': user_name}
                                            # if to_mail:
                                            #     self.env['remark_wizard'].claim_send_custom_mail(res_id=rec.id,
                                            #                                                     notif_layout='kwantify_theme.csm_mail_notification_light',
                                            #                                                     template_layout='claim.claim_notification_approver',
                                            #                                                     ctx_params=extra_params,
                                            #                                                     description="Claim Request")
                                        self.env.user.notify_success("Claim Notifcation Sent Successfully.")
                    elif (not sort1_rec and not sort2_rec and sort3_rec ) or (not sort1_rec and sort2_rec and not sort3_rec) or (sort1_rec and not sort2_rec and not sort3_rec):
                        category = claim_limit_rec.filtered(lambda x : x.category_id.id == rec.category_id.id)

                        if len(category) == 1:
                            rec.check_parent_sort_num_reviewer(rec.employee_id,sort3_rec)
                            rec.check_parent_sort_num1(rec.employee_id,sort1_rec)
                            rec.check_parent_sort_num2(rec.employee_id,sort2_rec)
                            # print('rec.reviewer_id=========',rec.reviewer_id,'rec.first_approver_id==========',rec.first_approver_id,'rec.second_approver_id===========',rec.second_approver_id)
                            if not rec.first_approver_id and not rec.second_approver_id and rec.employee_id.parent_id:
                                # not rec.reviewer_id and 
                                rec.write({ 
                                            'user_id':rec.employee_id.parent_id.user_id.id if not rec.reviewer_id else  rec.reviewer_id.user_id.id,
                                            'pending_at':f"Pending at {rec.employee_id.parent_id.user_id.name if not rec.reviewer_id else  rec.reviewer_id.user_id.name}",
                                            'show_revert_boolean':False,
                                            'state':'applied',
                                            # 'first_approver_id': sort_3.id,
                                            'log_ids':[[0,0,{
                                                'date':date.today(),
                                                'action_taken_by':self.env.user.employee_ids.id,
                                                'state':'Applied',
                                                'claim_id':rec.id,
                                                'remark':f"Applied by {rec.employee_id.name}",
                                                }]]
                                            })
                                user_name,to_mail = '',''
                                if not rec.reviewer_id:
                                    to_mail = rec.employee_id.parent_id.work_email if rec.employee_id.parent_id.work_email else '' 
                                    user_name = rec.employee_id.parent_id.name if rec.employee_id.parent_id.name else ''
                                else:
                                    to_mail = rec.reviewer_id.work_email if rec.reviewer_id.work_email else '' 
                                    user_name = rec.reviewer_id.name if rec.reviewer_id.name else ''
                                extra_params = {'to_mail': to_mail, 'user_name': user_name}
                                if to_mail:
                                    self.env['remark_wizard'].claim_send_custom_mail(res_id=rec.id,
                                                                                    notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                                    template_layout='claim.claim_notification_approver',
                                                                                    ctx_params=extra_params,
                                                                                    description="Claim Request")
                                self.env.user.notify_success("Claim Notifcation Sent Successfully.")
                            
                    else:
                        if not rec.employee_id.parent_id:
                            rec.write({ 
                                        'pending_at':"Pending at Finance",
                                        'show_revert_boolean':False,
                                        'state':'approved',
                                        'log_ids':[[0,0,{
                                            'date':date.today(),
                                            'action_taken_by':self.env.user.employee_ids.id,
                                            'state':'Applied',
                                            'claim_id':rec.id,
                                            'remark':f"Applied by {rec.employee_id.name}",
                                            }]]
                                        })
                                        # mail to finance
                            emp_data = self.env['res.users'].sudo().search([])
                            finance_officer = emp_data.filtered(lambda user: user.has_group('kw_advance_claim.group_kw_advance_claim_account')==True)
                            if finance_officer:
                                for users in finance_officer:
                                    to_mail = users.employee_ids.work_email if users.employee_ids.work_email else '' 
                                    user_name = users.employee_ids.name if users.employee_ids.name else '' 
                                    extra_params = {'to_mail': to_mail, 'user_name': user_name}
                                    self.env['remark_wizard'].claim_send_custom_mail(res_id=rec.id,
                                                                                    notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                                    template_layout='claim.claim_notification_mail_template',
                                                                                    ctx_params=extra_params,
                                                                                    description="Claim Request")
                                self.env.user.notify_success("Claim Notifcation Sent Successfully.")
                    
            else:
                ceo = self.env['hr.employee'].sudo().search([('parent_id','=',False),('department_id.code','=','CEO')],limit=1)
                rec.write({ 
                    'user_id':ceo.user_id.id,
                    'pending_at':f"Pending at {ceo.name}",
                    'show_revert_boolean':False,
                    'state':'applied',
                    # 'first_approver_id': sort_3.id,
                    'log_ids':[[0,0,{
                        'date':date.today(),
                        'action_taken_by':self.env.user.employee_ids.id,
                        'state':'Applied',
                        'claim_id':rec.id,
                        'remark':f"Applied by {rec.employee_id.name}",
                        }]]
                    })
                user_name,to_mail = '',''
                to_mail = ceo.work_email if ceo.work_email else '' 
                user_name = ceo.name if ceo.name else ''
                
                extra_params = {'to_mail': to_mail, 'user_name': user_name}
                if to_mail:
                    self.env['remark_wizard'].claim_send_custom_mail(res_id=rec.id,
                                                                    notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                    template_layout='claim.claim_notification_approver',
                                                                    ctx_params=extra_params,
                                                                    description="Claim Request")
                self.env.user.notify_success("Claim Notifcation Sent Successfully.")
            
    def action_reject_btn_first(self):
        for rec in self:
            view_id = self.env.ref('claim.remark_wizard_view_form').id
            return {
                'name':'Reject Remark',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(view_id, 'form')],
                'res_model': 'remark_wizard',
                'view_id': view_id,
                'context': {'current_id':rec.id,'action': 3},
                'target': 'new',
            }
            
   
            
    def action_level1_approve_btn(self):
        for rec in self:
            view_id = self.env.ref('claim.remark_wizard_view_form').id
            return {
                'name':'Approve Remark',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(view_id, 'form')],
                'res_model': 'remark_wizard',
                'view_id': view_id,
                'context': {'current_id':rec.id,'action': 1},
                'target': 'new',
            }
            
            
    @api.depends('first_approver_id','reviewer_ids','state')
    def check_direct_parent(self):
        for rec in self:
            if rec.user_id.id == self.env.user.id and rec.state=='applied' :
                rec.direct_parent = True
                
                
    @api.depends('second_approver_id')
    def check_second_parent(self):
        for rec in self:
            if rec.second_approver_id == self.env.user.employee_ids and rec.state=='applied':
                rec.second_parent = True
                
    @api.depends('employee_id')
    def check_reject_option_first(self):
        for rec in self:
            if rec.first_approver_id == self.env.user.employee_ids and rec.state=='applied' and not rec.second_approver_id:
                rec.show_reject_first = True
                
    @api.depends('employee_id')
    def check_reject_option_second(self):
        for rec in self:
            if rec.second_approver_id == self.env.user.employee_ids and rec.state=='applied':
                rec.show_reject_second = True
            
    @api.depends('show_revert_boolean','employee_id','state')
    def check_revert_option(self):
        for rec in self:
            if rec.employee_id == self.env.user.employee_ids and rec.show_revert_boolean == False and rec.state=='applied':
                rec.check_revert_boolean = True
            if rec.employee_id.user_id.id == self.env.user.id and rec.state=='draft':
                rec.apply_boolean = True

                  
            
            
    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code('claim') or '/'
        res = super(Claim, self).create(vals)
        return res
    
    def action_button_disbursed(self):
        for rec in self:
            rec.write({
                        'pending_at':"Disbursed",
                        'state':'disbursed',
                        'log_ids':[[0,0,{
                        'date':date.today(),
                        'action_taken_by':self.env.user.employee_ids.id,
                        'state':'Disbursed',
                        'claim_id':rec.id,
                        'remark':f"Disbursed by {self.env.user.employee_ids.name}",
                }]]
                    
            })

    def action_button_view_form(self):
        for rec in self:
            view_id = self.env.ref('claim.kw_claim_view_form').id
            return {
                'name':'Claim',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(view_id, 'form')],
                'res_model': 'kw_claim',
                'view_id': view_id,
                'res_id': rec.id,
                'target': 'self',
                'context':{'edit':True,'create':False},
            }
        
    def action_button_verified(self):
        self.state = 'verified'
        self.env['claim_log_details'].create({
                            'claim_id':self.id,
                            'date': datetime.now(),
                            'action_taken_by': self.env.user.employee_ids.id,
                            'state': self.state,
                            'remark': 'Verified by finance'
                        })

    def action_button_set_to_draft(self):
        self.state = 'draft'
        self.pending_at = False
        self.env['claim_log_details'].create({
                            'claim_id':self.id,
                            'date': datetime.now(),
                            'action_taken_by': self.env.user.employee_ids.id,
                            'state': self.state,
                            'remark': 'Set to Draft by finance'
                        })
