# -*- coding: utf-8 -*-

from odoo import models, fields, api,_,exceptions
from odoo.exceptions import ValidationError,UserError
import re
from datetime import date, datetime, timedelta ,time
from urllib.parse import quote
from odoo.http import request


import logging
_logger = logging.getLogger(__name__)


class TendrilsInternship(models.Model):
    _name = 'tendrils_internship'
    _rec_name = 'intern_name'
    _order = 'id desc'
    _description = 'Internship'


    @api.model
    def _default_refered_by(self):
        return self.env.user.employee_ids.id

    refered_by = fields.Many2one('hr.employee',string="Refered By" ,default=_default_refered_by)
    intern_name = fields.Char(string="Intern Name")
    contact_no = fields.Char(string="Contact No")
    email_id = fields.Char(string="Email Id")
    highest_qualification = fields.Char(string="Highest Qualification")
    college_name = fields.Char(string="College Name")
    latest_resume = fields.Binary("Latest Resume")
    resume_filename = fields.Char(string='Resume Filename')

    internship_topic = fields.Text("Internship Topic")
    stage = fields.Selection([('Draft', 'Draft'), ('Applied', 'Applied'),('Approve','Approved'),('Reject','Reject'),('Grant','Granted')],string="Stage",default='Draft')
    employee_id =fields.Many2one('hr.employee',string = "Employee")
    hepartment_id =fields.Many2one('hr.department',string = "Department")
    approval_user = fields.Many2one('hr.employee', string='Approval User', domain=lambda self: [("user_id.groups_id", "in", self.env.ref( "tendrils_internship.group_tendrils_internship_chro" ).id)])
    pending_at = fields.Many2many('hr.employee', string='Pending At', compute='_check_pending_at_status')
    # pending_at_users = fields.Char(string='Pending at user')
    store_remark = fields.Text(string="Remark")
    approve_reject_dept_head_bool = fields.Boolean(string = "Take Action Bool" ,default=False)
    btn_grant_bool = fields.Boolean(string = "Grant Take Action Bool" ,default=False)
    btn_reject_bool = fields.Boolean(string = "Chro Reject Take Action Bool" ,default=False)
    internship_ids = fields.One2many('tendrils_internship_action_lg', 'tendril_internship_id', string='field_name')
    user_access_compute = fields.Boolean(default = False,string = 'User Access To Apply')
    is_lk = fields.Boolean(string="Is LK?", default=False)
    is_attended = fields.Boolean(default = False,string = 'Is Attended')
    intern_document_upload = fields.Binary(string = 'Upload Document')
    intern_doc_filename = fields.Char(string='Intern Document')

    is_level = fields.Boolean(default = False,string = 'Is Level',compute = '_check_l3_apply')
    # applied_by = fields.Many2one('hr.employee', default=lambda self: self.env.user.employee_ids.id,
    #                                  string="Applied By", compute = 'get_level_user_check_to_apply')
    # user_access_to_apply = fields.Char(strnig = 'Apply User',compute = 'get_level_user_check_detailss')
    is_grant_view = fields.Boolean(string='is Granted', compute='_check_view_id')


    def _check_view_id(self):
        for rec in self:
            if rec.stage == 'Grant'and self._context.get('hide_quotation'):
                request.session['hide_quotation'] = self._context.get('hide_quotation')
                rec.is_grant_view = True
            else:
                rec.is_grant_view = False
                request.session['hide_quotation'] = False

    def _check_pending_at_status(self):
        for rec in self:
            rec.pending_at = [(5, 0, 0)] 
            if rec.stage == 'Applied':
                rec.pending_at = [(4, rec.employee_id.department_id.manager_id.id)]
                # print(rec.pending_at,"rec.pending_at======111111111=============")
            elif rec.stage == 'Approve':
                chro_group = self.env.ref('tendrils_internship.group_tendrils_internship_chro').users
                # print(chro_group,"chro group===================")
                rec.pending_at = [(4, user.employee_ids.id, False) for user in chro_group ]
            else:
                rec.pending_at = []
                    

    def send_chrp_auto_grant_mail(self):
        template_id = self.env.ref('tendrils_internship.internship_chro_self_grant_email_template')
            
        email_from = self.env.user.employee_ids.work_email

        l_and_k_manager = self.env.ref('tendrils_internship.group_tendrils_internship_training_manager')
        email_to = ','.join([user.email for user in l_and_k_manager.users if user.email])
        applied_name = self.env.user.employee_ids.name
        name =  ','.join([user.name for user in l_and_k_manager.users if user.name])


        if template_id:
            for user in l_and_k_manager.users:
                    if user.email:
                        email_to = user.email
                        name = user.name

                        template_id.with_context(email_from=email_from, email_to=email_to,name=name,applied_name=applied_name).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")



    def btn_internship_apply(self):
        user_id = self.env.user.employee_ids
        level_data = ['L3', 'L4', 'L5']
        department_head_emp = self.env['hr.department'].sudo().search([('manager_id.id','=',user_id.id)])
        
        if user_id.level.name in level_data and department_head_emp and self.env.user.has_group('tendrils_internship.group_tendrils_internship_chro'):
            self.send_chrp_auto_grant_mail()

            # print("enter in 2nd if=======================")
            
            self.write({'stage': 'Grant',
                        'employee_id': user_id.id,
                        'btn_grant_bool':True,
                        'internship_ids': [(0, 0, {
                                'date': datetime.now(),
                                # 'remark': 'NA',
                                'action_taken_by': self.env.user.employee_ids.id,
                                'stage': 'Grant'
                            })]
                       
                        })

        elif user_id.level.name in level_data and self.env.user.has_group('tendrils_internship.group_tendrils_internship_chro'):
            self.send_chrp_auto_grant_mail()

            # print("enter in 2nd if=======================")
            self.write({'stage': 'Grant',
                        'employee_id': user_id.id,
                        'btn_grant_bool':True,
                        'internship_ids': [(0, 0, {
                                'date': datetime.now(),
                                # 'remark': 'NA',
                                'action_taken_by': self.env.user.employee_ids.id,
                                'stage': 'Grant'
                            })]
                       
                        })
     
        elif user_id.level.name in level_data and department_head_emp and not self.env.user.has_group('tendrils_internship.group_tendrils_internship_chro'):
            # print("enter in 1st elif=======================")
            self.write({'stage': 'Approve',
                        'employee_id': user_id.id,
                        'approve_reject_dept_head_bool':True,
                        'internship_ids': [(0, 0, {
                                'date': datetime.now(),
                                # 'remark': 'NA',
                                'action_taken_by': self.env.user.employee_ids.id,
                                'stage': 'Approve'
                            })]
                        })
        elif user_id.level.name in level_data and not department_head_emp or not self.env.user.has_group('tendrils_internship.group_tendrils_internship_chro') or not self.env.user.has_group('tendrils_internship.group_tendrils_internship_training_manager'):
            print("enter in if=======================",user_id.level.name in level_data,"=======",department_head_emp,"=========",self.env.user.has_group('tendrils_internship.group_tendrils_internship_chro'))
            template_id = self.env.ref('tendrils_internship.internship_apply_email_template')
            
            email_from = self.env.user.employee_ids.work_email
            email_to = self.env.user.employee_ids.department_id.manager_id.work_email
            name = self.env.user.employee_ids.department_id.manager_id.name
            name_applied = self.env.user.employee_ids.name
            
                
            if template_id:
                template_id.with_context(email_from=email_from, email_to=email_to,name=name,name_applied=name_applied).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")

            self.write({'stage': 'Applied',
                        'employee_id': user_id.id,
                        # 'internship_ids': [(0, 0, {
                        #         'date': datetime.now(),
                        #         # 'remark': 'NA',
                        #         'action_taken_by': self.env.user.employee_ids.id,
                        #         'stage': 'Applied'
                        #     })]
                       

                        })
        elif user_id.level.name in level_data and not department_head_emp or self.env.user.has_group('tendrils_internship.group_tendrils_internship_chro') or self.env.user.has_group('tendrils_internship.group_tendrils_internship_training_manager'):
            template_id = self.env.ref('tendrils_internship.internship_apply_email_template')
            
            email_from = self.env.user.employee_ids.work_email
            email_to = self.env.user.employee_ids.department_id.manager_id.work_email
                
            if template_id:
                # print(template_id,"template_id====2222222===========")
                template_id.with_context(email_from = email_from,email_to=email_to).send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")

            self.write({'stage': 'Applied',
                        'employee_id': user_id.id,
                        #   'internship_ids': [(0, 0, {
                        #         'date': datetime.now(),
                        #         # 'remark': 'NA',
                        #         'action_taken_by': self.env.user.employee_ids.id,
                        #         'stage': 'Applied'
                        #     })]

                        })
        else:
            # print("in else===============")
            raise ValidationError("You Can't Apply.")


   
    @api.constrains('contact_no','email_id')
    def _check_(self):
        if not self.contact_no:
            raise ValidationError("Please Fill The Contact Number.")    
        if len(self.contact_no) > 10 or len(self.contact_no) <10:
                raise ValidationError("Contact number should be exactly 10 digits.")    

        if self.email_id:
            if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", self.email_id) != None:
                raise ValidationError(f'Email is invalid for : {self.email_id}')
    

    def btn_internship_approve(self):
        view_id = self.env.ref("tendrils_internship.internship_remark_approve_form_view").id
        menu_id = self.env.ref("tendrils_internship.internship_root_menu").id
        action = {
            'name': 'Approve',
            'type': 'ir.actions.act_window',
            'res_model': 'dept_head_approval_wiz',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'current_id': self.id,'menu_id':menu_id}

        }
        return action

    def btn_internship_reject(self):
        view_id = self.env.ref("tendrils_internship.internship_remark_reject_form_view").id
        menu_id = self.env.ref("tendrils_internship.internship_root_menu").id
        action = {
            'name': 'Reject',
            'type': 'ir.actions.act_window',
            'res_model': 'dept_head_approval_wiz',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'current_id': self.id,'menu_id':menu_id}

        }
        return action

    def btn_internship_grant(self):
        view_id = self.env.ref("tendrils_internship.internship_grant_form_view").id
        menu_id = self.env.ref("tendrils_internship.internship_root_menu").id

        action = {
            'name': 'Grant',
            'type': 'ir.actions.act_window',
            'res_model': 'dept_head_approval_wiz',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'current_id': self.id,'menu_id':menu_id}

        }
        return action
        
    def btn_chro_reject(self):
        view_id = self.env.ref("tendrils_internship.chro_reject_form_view").id
        menu_id = self.env.ref("tendrils_internship.internship_root_menu").id

        action = {
            'name': 'Reject',
            'type': 'ir.actions.act_window',
            'res_model': 'dept_head_approval_wiz',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'current_id': self.id,'menu_id':menu_id}

        }
        return action


    @api.multi
    def resume_download(self):
        self.ensure_one()
        if not self.latest_resume:
            raise exceptions.UserError("No resume found.")
        
        intern_name = self.intern_name or "resume"
        safe_intern_name = quote(intern_name)
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{self._name}/{self.id}/latest_resume/{self.resume_filename}?download=true&filename={safe_intern_name}.pdf',
            'target': 'self',
        }

    def _check_l3_apply(self):
        user = self.env.user
        employee = user.employee_ids
        
        level_data = ['L3', 'L4', 'L5']
        if not employee.level.name in level_data:
            self.is_level = True
            raise UserError('You cannot apply. Please contact your administrator for more information.')
        
             
    # @api.depends('applied_by')
    # def get_level_user_check_to_apply(self):
    #     for rec in self:
    #         print("function called=================")
    #         employee_ids = rec.env.user.employee_ids
    #         print(employee_ids, "user_data=====,")
    #         level_data = ['L3', 'L4', 'L5']
            
    #         for employee in employee_ids:
    #             if employee.level.name not in level_data:
    #                 print("employee.level.name in level_data:============", employee.level.name)
    #                 rec.user_access_compute = True
    #                 print(rec.user_access_compute, "self.user_activity_bool==========")
               
    #             # else:
    #                 # print("in else================")
    #                 raise UserError('You cannot apply. Please contact your administrator for more information.')

    # @api.model
    # def get_level_user_check_details(self):
    
    #     tree_view_id = self.env.ref('tendrils_internship.tendrils_internship_list').id
    #     form_view_id = self.env.ref('tendrils_internship.tendrils_internship_form').id
    #     print(tree_view_id,"===========",form_view_id)

    #     employee_ids = self.env.user.employee_ids
    #     print(employee_ids, "user_data=====,")
    #     level_data = ['L3', 'L4', 'L5']
        
    #     # Check if any of the employee levels match the allowed levels
    #     if any(employee.level.name in level_data for employee in employee_ids):

    #         action = {
    #             'type': 'ir.actions.act_window',
    #             'name': 'Internship',
    #             'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
    #             'view_mode': 'tree,form',
    #             'view_type': 'form',
    #             'res_model': 'tendrils_internship',
    #             'target': 'main',
    #             "domain":[('create_uid','=',self.env.user.id)],
    #             # 'context': {'edit': False, 'create': False,}
    #             }
    #         return action
    #     else:
    #         # Error handling in case the user's level is not allowed
    #         raise UserError('You cannot apply. Please contact your administrator for more information.')


    # @api.model
    # def internship_take_action(self):
    #     print("function called============")
    #     tree_view_id = self.env.ref('tendrils_internship.internship_takeaction_list').id
    #     form_view_id = self.env.ref('tendrils_internship.internship_takeaction_form').id

    #     action = {
    #         'name': 'Take Action',
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form,tree',
    #         'res_model': 'tendrils_internship',
    #         'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
    #         'domain': [],
    #     }

    #     domain = []

        # if self.employee_id.department_id.manager_id.user_id.id == self._uid and self.env.user.has_group('tendrils_internship.group_tendrils_internship_chro'):
        #     print("in 3rd =============")
        #     domain = [('stage', 'in', ['Applied', 'Approve'])]
        # if self.employee_id.department_id.manager_id.user_id.id == self._uid:
        #     print("in 1st =============")
        #     domain = [('stage', '=', 'Applied')]
        # elif self.env.user.has_group('tendrils_internship.group_tendrils_internship_chro'):
        #     print("in 2nd =============")
        #     domain = [('stage', '=', 'Approve')]

        # action['domain'] = domain
        # return action


class TendrilsActionLog(models.Model):
    _name = 'tendrils_internship_action_lg'


    date = fields.Date('Date')
    remark = fields.Char('Remark')
    action_taken_by = fields.Many2one('hr.employee','Action Taken By')
    stage = fields.Char('Stage')
    tendril_internship_id = fields.Many2one('Internship Id')
   


class LKBatch(models.TransientModel):
    _name = "l_k_batch_wiz"
    _description = "Batch Create"

    def _default_financial_yr(self):
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        return current_fiscal
    @api.model
    def default_get(self, fields):
        res = super(LKBatch, self).default_get(fields)
        active_ids = self.env.context.get('active_ids', [])

        res.update({
            'employee_ids': active_ids,
        })
        return res


    financial_year_id = fields.Many2one('account.fiscalyear', 'Financial Year', default=_default_financial_yr,
                                        required=True)
    batch_name = fields.Char(string="Batch Name")
    start_date = fields.Date(string='Start Date',track_visibility='onchange')
    close_date = fields.Date(sring = 'Close Date')
    employee_ids = fields.Many2many(
        string='Employee Info',
        comodel_name='tendrils_internship',
        relation='tendrils_internship_employee_rel',
        column1='wiz_id',
        column2='tendrils_internship_id',
    )

    @api.constrains('start_date')
    def _check_start_date(self):
        for batch in self:
            if batch.start_date and batch.start_date < fields.Date.today():
                raise ValidationError("Start date cannot be less than today.")

    @api.constrains('close_date')
    def _onchange_close_date(self):
        if self.start_date > self.close_date:
            raise ValidationError("The close date should be greater than the start date.")

    def create_batches(self):
        for rec in self:
            related_records = self.env['tendrils_internship'].browse(rec.employee_ids.ids)
            if related_records.filtered(lambda r: r.stage != 'Grant'):
                raise ValidationError("You cannot create batches before the 'Grant' stage.")
        else:
            for rec in self:
                employee_records = rec.employee_ids
                employee_records.write({
                    'is_lk': True
                })
                batch_data = {
                    'batch_name': rec.batch_name,
                    'start_date': rec.start_date,
                    'close_date': rec.close_date,
                    'financial_year_id':rec.financial_year_id.id,
                    'employee_ids': [(4, emp.id) for emp in employee_records],  
                } 
                self.env['lk_training_batch'].sudo().create(batch_data)

