# -*- coding: utf-8 -*-

from locale import currency
from odoo import models, fields, api, tools
from odoo.exceptions import ValidationError
from datetime import date, datetime
import re


class kw_advance_claim_category(models.Model):
    _inherit = 'kw_advance_claim_category'
    _order = 'name'
    
    type = fields.Selection([('project_budget','Project'),('treasury_budget','Treasury')],track_visibility='onchange')

class ClaimCategory(models.Model):
    _name = 'claim_category_master'

    name = fields.Char()

    # @api.constrains('name')
    # def _check_category(self):
    #     for rec in self:
    #         record = self.env['claim_category_master'].search(
    #             [('name', 'ilike', rec.name)]) - self
    #         if record:
    #             raise ValidationError(f'{rec.name} already exists.')


class SubCategoryAmountConfig(models.Model):
    _name = 'sub_category_item_amount_config'

    amount = fields.Float(compute="calculate_total_amount")
    item_model = fields.Char(string="Make/Model/Description")
    item_unit = fields.Char(string="Unit")
    item_quantity = fields.Integer(string="Qty")
    item_rate = fields.Integer(string="Rate")
    sub_category_id = fields.Many2one('claim_sub_category_master')
    claim_category_id = fields.Many2one('kw_advance_claim_type')
    claim_id = fields.Many2one('kw_claim', ondelete="cascade")
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id.id, )

    @api.constrains('amount','item_quantity')
    def _check_amount(self):
        for rec in self:
            if rec.amount < 1:
                raise ValidationError("Cost should be greater than 0")
            
        for rec in self:
            if rec.item_quantity < 0 :
                raise ValidationError("Quantity should not be in negative")

    @api.depends('amount', 'item_quantity', 'item_rate')
    def calculate_total_amount(self):
        for total_amount in self:
            total_amount.amount = (total_amount.item_quantity * total_amount.item_rate)

    @api.onchange('item_quantity','item_rate')
    def check_digits(self):
        if self.item_quantity >= 100000:
            raise ValidationError("Item Quantity should not be greater than 1 Lakh")
        elif self.item_rate >= 1000000:
            raise ValidationError("Item Price should not be greater than 10 Lakh")

    @api.constrains('item_unit')
    def validate_unit(self):
        for data in self:
            if not re.match(r"^[a-zA-Z ]*$", data.item_unit):
                raise ValidationError(f"{data.item_unit} : Unit Type not acceptable")


class ClaimSubCategory(models.Model):
    _name = 'claim_sub_category_master'

    name = fields.Char()
    category_id = fields.Many2one('kw_advance_claim_category', domain="[('category','=','claim')]")

    @api.constrains('name', 'category_id')
    def _check_category(self):
        for rec in self:
            record = self.env['claim_sub_category_master'].search(
                [('name', 'ilike', rec.name), ('category_id', 'ilike', rec.category_id.name)]) - self
            if record:
                raise ValidationError(f'{rec.name} already exists for category {rec.category_id.name} .')


class CategoryLimit(models.Model):
    _name = 'claim_category_limit'
    _order = 'category_id'

    category_id = fields.Many2one('kw_advance_claim_category', required=True, domain="[('category','=','claim')]")
    grade_ids = fields.Many2many('kwemp_grade_master')
    employee_ids = fields.Many2many('hr.employee','emp_claim_rel','claim_id','emp_id')
    limit = fields.Float()
    limit_to = fields.Float()
    enable_reviewer = fields.Boolean()
    sort_no = fields.Integer()
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env['res.currency'].search([('name', '=', 'INR')]))

    @api.onchange('enable_reviewer')
    def get_false_field(self):
        if self.enable_reviewer:
            self.grade_ids = [(5,)]
        else:
            self.employee_ids = [(5,)]

    # def write(self, vals):
    #     if vals.get('enable_reviewer', False):
    #         vals['grade_ids'] = [(5,)]
    #     else:
    #         if not self.enable_reviewer or not vals.get('enable_reviewer', False):
    #             vals['employee_ids'] = [(5,)]
    #     return super(CategoryLimit, self).write(vals)

    # def write(self, vals):
    #     if vals.get('enable_reviewer', False):
    #         vals['grade_ids'] = [(5,)]
    #     else:
    #         if not self.enable_reviewer:
    #             if not vals.get('enable_reviewer', False):
    #                 vals['employee_ids'] = [(5,)]
    #         elif not vals.get('enable_reviewer', False) and self.enable_reviewer:
    #             vals['employee_ids'] = [(5,)]
    #     return super(CategoryLimit, self).write(vals)

    @api.constrains('limit_to', 'limit')
    def _check_category(self):
        for rec in self:
            if rec.limit_to <= 0 or rec.limit <= 0:
                raise ValidationError(f'Amount should not be less than or equal with 0 against {rec.category_id.name}.')


class LevelConfiguration(models.Model):
    _name = 'level_configuration'

    grade_ids = fields.Many2many('kwemp_grade_master')
    sort_no = fields.Integer()


class remarkwizard(models.TransientModel):
    _name = 'remark_wizard'

    remark = fields.Text()

    def claim_send_custom_mail(self, res_id, force_send=False, raise_exception=False, email_values=None,
                               notif_layout=False, template_layout=False, ctx_params=None, description=False):
        template = self.env.ref(template_layout)
        if template:
            # template.with_context(extra_params).send_mail(emp_rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")

            values = template.with_context(ctx_params).generate_email(res_id)
            values['recipient_ids'] = [(4, pid) for pid in values.get('partner_ids', list())]
            values.update(email_values or {})
            # print(values)                    

            # add a protection against void email_from
            if 'email_from' in values and not values.get('email_from'):
                values.pop('email_from')
            # encapsulate body
            if notif_layout and values['body_html']:
                try:
                    notif_template = self.env.ref(notif_layout, raise_if_not_found=True)
                except ValueError:
                    pass
                else:
                    record = self.env[template.model].browse(res_id)
                    template_ctx = {
                        'message': self.env['mail.message'].sudo().new(
                            dict(body=values['body_html'], record_name=record.display_name)),
                        'model_description': description if description else self.env['ir.model']._get(
                            record._name).display_name,
                        'company': 'company_id' in record and record['company_id'] or self.env.user.company_id,
                    }
                    body = notif_template.render(template_ctx, engine='ir.qweb', minimal_qcontext=True)
                    values['body_html'] = self.env['mail.thread']._replace_local_links(body)

            mail = self.env['mail.mail'].create(values)

            if force_send:
                mail.send(raise_exception=raise_exception)
            return mail.id
        

    def action_confirm_btn(self):
        for record in self:
            if self.env.context.get('current_id'):
                current_id = self.env.context.get('current_id')
                claim = self.env['kw_claim'].sudo().search([('id', '=', current_id)])
                if claim:
                    for rec in claim:
                        if self.env.context.get('action') == 1:
                            rec.write({
                                'pending_at': "Pending at Finance",
                                'show_revert_boolean': True,
                                'state': 'approved',
                                'log_ids': [[0, 0, {
                                    'date': date.today(),
                                    'action_taken_by': self.env.user.employee_ids.id,
                                    'state': 'Approved',
                                    'claim_id': rec.id,
                                    'remark': record.remark,
                                }]]
                            })
                            emp_data = self.env['res.users'].sudo().search([])
                            finance_officer = emp_data.filtered(
                                lambda user: user.has_group('kw_advance_claim.group_kw_advance_claim_account') == True)
                            if finance_officer:
                                for users in finance_officer:
                                    to_mail = users.employee_ids.work_email if users.employee_ids.work_email else ''
                                    user_name = users.employee_ids.name if users.employee_ids.name else ''
                                    extra_params = {'to_mail': to_mail, 'user_name': user_name}
                                    if to_mail:
                                        self.claim_send_custom_mail(res_id=rec.id,
                                                                    notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                    template_layout='claim.claim_notification_mail_template',
                                                                    ctx_params=extra_params,
                                                                    description="Claim Request")
                            self.env.user.notify_success("Claim Notifcation Sent Successfully.")
                        else:
                            rec.write({
                                'pending_at': "Rejected",
                                'show_revert_boolean': True,
                                'state': 'reject',
                                'log_ids': [[0, 0, {
                                    'date': date.today(),
                                    'action_taken_by': self.env.user.employee_ids.id,
                                    'state': 'Rejected',
                                    'claim_id': rec.id,
                                    'remark': record.remark,
                                }]]
                            })

    # def action_confirm_btn(self):
    #     for record in self:
    #         # get the id of the record from Context
    #         if self.env.context.get('current_id'):
    #             claim = self.env['kw_claim'].sudo().search([('id', '=', self.env.context.get('current_id'))],
    #                                                                        limit=1)
    #             if claim:
    #                 if self.env.context.get('action'):
    #                     # action 1=first approver approve,2=Second Approver Approve,3=Reject
    #                     if self.env.context.get('action') == 1:
    #                         for rec in claim:
    #                             # find the record of claim category limit agnaist record category and grade    
    #                             limit_record = self.env['claim_category_limit'].sudo().search([('category_id','=',rec.category_id.id)])
    #                             limit_rec = limit_record.filtered(lambda x:rec.first_approver_id.grade.id in x.grade_ids.ids)
    #                             approval_employee = limit_record.filtered(lambda x:rec.first_approver_id.id in x.employee_ids.ids)
    #                             print('==========',limit_rec,approval_employee,limit_record)
    #                             if limit_rec :
    #                                 # find level configuration to check the record grade belongs to which level
    #                                 level_rec = self.env['level_configuration'].sudo().search([])
    #                                 filtered_level = level_rec.filtered(lambda x : rec.grade_id.id in x.grade_ids.ids)
    #                                 if filtered_level:
    #                                     # if the applied employee belongs to grade below M8
    #                                     if filtered_level.sort_no == 1:
    #                                         # if amount is less than limit then approve the record and send notification to finance
    #                                         if rec.amount <= limit_rec.limit:
    #                                             rec.write({ 'show_revert_boolean':True,
    #                                                         'state': 'approved',
    #                                                         'log_ids':[[0,0,{
    #                                                         'date':date.today(),
    #                                                         'action_taken_by':self.env.user.employee_ids.id,
    #                                                         'state':'Approved',
    #                                                         'claim_id':rec.id,
    #                                                         'remark':record.remark,
    #                                                 }]]

    #                                             })
    #                                             emp_data = self.env['res.users'].sudo().search([])
    #                                             finance_officer = emp_data.filtered(lambda user: user.has_group('kw_advance_claim.group_kw_advance_claim_account')==True)
    #                                             if finance_officer:
    #                                                 for users in finance_officer:
    #                                                     to_mail = users.employee_ids.work_email if users.employee_ids.work_email else '' 
    #                                                     user_name = users.employee_ids.name if users.employee_ids.name else '' 
    #                                                     extra_params = {'to_mail': to_mail, 'user_name': user_name}
    #                                                     if to_mail:
    #                                                         self.claim_send_custom_mail(res_id=rec.id,
    #                                                                                                         notif_layout='kwantify_theme.csm_mail_notification_light',
    #                                                                                                         template_layout='claim.claim_notification_mail_template',
    #                                                                                                         ctx_params=extra_params,
    #                                                                                                         description="Claim Request")
    #                                                         self.env.user.notify_success("Claim Notifcation Sent Successfully.")
    #                                         else:
    #                                             if rec.employee_id.id in limit_rec.employee_ids.ids:
    #                                                 rec.write({'show_revert_boolean':True,
    #                                                         'state': 'approved',
    #                                                         'log_ids':[[0,0,{
    #                                                         'date':date.today(),
    #                                                         'action_taken_by':self.env.user.employee_ids.id,
    #                                                         'state':'Approved',
    #                                                         'claim_id':rec.id,
    #                                                         'remark':record.remark,
    #                                                 }]]

    #                                                     })
    #                                                 emp_data = self.env['res.users'].sudo().search([])
    #                                                 finance_officer = emp_data.filtered(lambda user: user.has_group('kw_advance_claim.group_kw_advance_claim_account')==True)
    #                                                 if finance_officer:
    #                                                     for users in finance_officer:
    #                                                         to_mail = users.employee_ids.work_email if users.employee_ids.work_email else '' 
    #                                                         user_name = users.employee_ids.name if users.employee_ids.name else '' 
    #                                                         extra_params = {'to_mail': to_mail, 'user_name': user_name}
    #                                                         if to_mail:
    #                                                             self.claim_send_custom_mail(res_id=rec.id,
    #                                                                                                             notif_layout='kwantify_theme.csm_mail_notification_light',
    #                                                                                                             template_layout='claim.claim_notification_mail_template',
    #                                                                                                             ctx_params=extra_params,
    #                                                                                                             description="Claim Request")
    #                                                             self.env.user.notify_success("Claim Notifcation Sent Successfully.")
    #                                             else:
    #                                                 # if amount is greater than limit the send the record to first approver ra for approval
    #                                                 rec.write({'show_revert_boolean':True,
    #                                                             'second_approver_id': rec.first_approver_id.parent_id.id,
    #                                                             'log_ids':[[0,0,{
    #                                                             'date':date.today(),
    #                                                             'action_taken_by':self.env.user.employee_ids.id,
    #                                                             'state':'Approved',
    #                                                             'claim_id':rec.id,
    #                                                             'remark':record.remark,
    #                                                     }]]
    #                                                 })
    #                                                 # notification to first approver should be sent
    #                                                 to_mail = rec.second_approver_id.work_email if rec.second_approver_id.work_email else '' 
    #                                                 user_name = rec.second_approver_id.name if rec.second_approver_id.name else '' 
    #                                                 extra_params = {'to_mail': to_mail, 'user_name': user_name}
    #                                                 if to_mail:
    #                                                     self.env['remark_wizard'].claim_send_custom_mail(res_id=rec.id,
    #                                                                                                     notif_layout='kwantify_theme.csm_mail_notification_light',
    #                                                                                                     template_layout='claim.claim_notification_approver',
    #                                                                                                     ctx_params=extra_params,
    #                                                                                                     description="Claim Request")
    #                                                     self.env.user.notify_success("Claim Notifcation Sent Successfully.")

    #                                     # if the applied employee belongs to grade above M8
    #                                     else:
    #                                         # approve the record and send notification to finance
    #                                         rec.write({'show_revert_boolean':True,
    #                                                     'state': 'approved',
    #                                                     'log_ids':[[0,0,{
    #                                                     'date':date.today(),
    #                                                     'action_taken_by':self.env.user.employee_ids.id,
    #                                                     'state':'Approved',
    #                                                     'claim_id':rec.id,
    #                                                     'remark':record.remark,
    #                                             }]]

    #                                         })
    #                                         # notification to finance should be sent
    #                                         emp_data = self.env['res.users'].sudo().search([])
    #                                         finance_officer = emp_data.filtered(lambda user: user.has_group('kw_advance_claim.group_kw_advance_claim_account')==True)
    #                                         if finance_officer:
    #                                             for users in finance_officer:
    #                                                 to_mail = users.employee_ids.work_email if users.employee_ids.work_email else '' 
    #                                                 user_name = users.employee_ids.name if users.employee_ids.name else '' 
    #                                                 extra_params = {'to_mail': to_mail, 'user_name': user_name}
    #                                                 if to_mail:
    #                                                     self.claim_send_custom_mail(res_id=rec.id,
    #                                                                                                     notif_layout='kwantify_theme.csm_mail_notification_light',
    #                                                                                                     template_layout='claim.claim_notification_mail_template',
    #                                                                                                     ctx_params=extra_params,
    #                                                                                                     description="Claim Request")
    #                                                     self.env.user.notify_success("Claim Notifcation Sent Successfully.")

    #                                                     # template_id=self.env.ref('claim.claim_notification_mail_template').with_context(to_mail=to_mail,user_name=user_name)
    #                                                     # template_id.send_mail(self.id)
    #                                                     # self.env.user.notify_success("Claim Notifcation Sent Successfully.")

    #                                 else:
    #                                     raise ValidationError('Level is not set')
    #                             else:
    #                                 if approval_employee:
    #                                     # if amount is less than limit then approve the record and send notification to finance
    #                                     if rec.amount <= approval_employee.limit:
    #                                         rec.write({'show_revert_boolean':True,
    #                                                     'state': 'approved',
    #                                                     'log_ids':[[0,0,{
    #                                                     'date':date.today(),
    #                                                     'action_taken_by':self.env.user.employee_ids.id,
    #                                                     'state':'Approved',
    #                                                     'claim_id':rec.id,
    #                                                     'remark':record.remark,
    #                                             }]]

    #                                         })
    #                                         emp_data = self.env['res.users'].sudo().search([])
    #                                         finance_officer = emp_data.filtered(lambda user: user.has_group('kw_advance_claim.group_kw_advance_claim_account')==True)
    #                                         if finance_officer:
    #                                             for users in finance_officer:
    #                                                 to_mail = users.employee_ids.work_email if users.employee_ids.work_email else '' 
    #                                                 user_name = users.employee_ids.name if users.employee_ids.name else '' 
    #                                                 extra_params = {'to_mail': to_mail, 'user_name': user_name}
    #                                                 if to_mail:
    #                                                     self.claim_send_custom_mail(res_id=rec.id,
    #                                                                                                     notif_layout='kwantify_theme.csm_mail_notification_light',
    #                                                                                                     template_layout='claim.claim_notification_mail_template',
    #                                                                                                     ctx_params=extra_params,
    #                                                                                                     description="Claim Request")
    #                                                     self.env.user.notify_success("Claim Notifcation Sent Successfully.")
    #                                     else:
    #                                         rec.check_second_approver(rec.first_approver_id)
    #                                         if rec.second_approver_id:
    #                                             rec.write({'show_revert_boolean':True,
    #                                                             'log_ids':[[0,0,{
    #                                                             'date':date.today(),
    #                                                             'action_taken_by':self.env.user.employee_ids.id,
    #                                                             'state':'Approved',
    #                                                             'claim_id':rec.id,
    #                                                             'remark':record.remark,
    #                                                     }]]
    #                                                 })
    #                                             # notification to first approver should be sent
    #                                             to_mail = rec.second_approver_id.work_email if rec.second_approver_id.work_email else '' 
    #                                             user_name = rec.second_approver_id.name if rec.second_approver_id.name else '' 
    #                                             extra_params = {'to_mail': to_mail, 'user_name': user_name}
    #                                             if to_mail:
    #                                                 self.env['remark_wizard'].claim_send_custom_mail(res_id=rec.id,
    #                                                                                                 notif_layout='kwantify_theme.csm_mail_notification_light',
    #                                                                                                 template_layout='claim.claim_notification_approver',
    #                                                                                                 ctx_params=extra_params,
    #                                                                                                 description="Claim Request")
    #                                                 self.env.user.notify_success("Claim Notifcation Sent Successfully.")

    #                     if self.env.context.get('action') == 2:
    #                         for rec in claim:
    #                             rec.write({'show_revert_boolean':True,
    #                                         'state': 'approved',
    #                                         'log_ids':[[0,0,{
    #                                         'date':date.today(),
    #                                         'action_taken_by':self.env.user.employee_ids.id,
    #                                         'state':'Approved',
    #                                         'claim_id':rec.id,
    #                                         'remark':record.remark,
    #                                             }]]

    #                                     })
    #                             # notification to finance should be sent
    #                             emp_data = self.env['res.users'].sudo().search([])
    #                             finance_officer = emp_data.filtered(lambda user: user.has_group('kw_advance_claim.group_kw_advance_claim_account')==True)
    #                             if finance_officer:
    #                                 for users in finance_officer:
    #                                     to_mail = users.employee_ids.work_email if users.employee_ids.work_email else '' 
    #                                     user_name = users.employee_ids.name if users.employee_ids.name else '' 
    #                                     extra_params = {'to_mail': to_mail, 'user_name': user_name}
    #                                     if to_mail:
    #                                         self.claim_send_custom_mail(res_id=rec.id,
    #                                                                                         notif_layout='kwantify_theme.csm_mail_notification_light',
    #                                                                                         template_layout='claim.claim_notification_mail_template',
    #                                                                                         ctx_params=extra_params,
    #                                                                                         description="Claim Request")
    #                                         self.env.user.notify_success("Claim Notifcation Sent Successfully.")
    #                     if self.env.context.get('action') == 3:
    #                         for rec in claim:
    #                             rec.write({'show_revert_boolean':True,
    #                                         'state': 'reject',
    #                                         'log_ids':[[0,0,{
    #                                         'date':date.today(),
    #                                         'action_taken_by':self.env.user.employee_ids.id,
    #                                         'state':'Rejected',
    #                                         'claim_id':rec.id,
    #                                         'remark':record.remark,
    #                                             }]]

    #                                     })


class Claim(models.Model):
    _name = 'claim_log_details'
    # _rec_name = "code"

    date = fields.Date()
    action_taken_by = fields.Many2one('hr.employee')
    state = fields.Char()
    remark = fields.Text()
    claim_id = fields.Many2one('kw_claim', ondelete='cascade')


class claimreport(models.Model):
    _name = 'claim_report'
    _description = 'Claim Report'
    _auto = False
    _order = "code desc"

    code = fields.Char(string='Claim No')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    department_id = fields.Many2one('hr.department', string='Department')
    job_id = fields.Many2one('hr.job', string='Designation')
    grade_id = fields.Many2one('kwemp_grade_master', string='Level')
    category_id = fields.Many2one('kw_advance_claim_category', string='Category', domain="[('category','=','claim')]")
    sub_category_id = fields.Char(string='Sub Category Items')
    currency_id = fields.Many2one('res.currency')
    amount = fields.Float(string="Amount")
    first_approver_id = fields.Many2one('hr.employee', string='First Approver')
    second_approver_id = fields.Many2one('hr.employee', string='Second Approver')
    state = fields.Char(string='State')
    year = fields.Integer(string='Year')
    month = fields.Integer(string='Month')
    pending_at = fields.Char('Application Status/Progress')
    applied_date = fields.Date('Applied On')
    claim_id = fields.Many2one('kw_claim')

    # claim_category_id,
    # kw_advance_claim_type
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
        SELECT  row_number() over() as id,code,employee_id,department_id,job_id,grade_id,category_id,pending_at,
        
        (select string_agg(claim_type,', ')from sub_category_item_amount_config sc join kw_advance_claim_type cc 
		 on sc.claim_category_id = cc.id 
        where claim_id = a.id)  
        as sub_category_id,currency_id,
        amount,first_approver_id,second_approver_id,year,month,
		case
		when state = 'applied' then 'Applied'
		when state = 'approved' then 'Approved'
        when state = 'verified' then 'Verified'
        when state = 'disbursed' then 'Disbursed'
        when state = 'reject' then 'Rejected'
		end as state,
        (select date from claim_log_details where state in ('Applied','Auto Approved') and claim_id = a.id ORDER BY date DESC LIMIT 1) as applied_date,
        id as claim_id
        from kw_claim a where state != 'draft'
         )""" % (self._table))

    def action_button_view_form(self):
        # for rec in self:
            # claim = self.env['kw_claim'].sudo().search(
                # [('employee_id', '=', rec.employee_id.id), ('code', '=', rec.code)]).id
            view_id = self.env.ref('claim.kw_claim_view_form').id
            return {
                'name': 'Claim',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(view_id, 'form')],
                'res_model': 'kw_claim',
                'view_id': view_id,
                'res_id': self.claim_id.id,
                'target': 'self',
                'context': {'edit': False, 'create': False, 'delete': False}
            }

class CancelRejectClaimReport(models.Model):
    """
    Class: CancelRejectClaimReport

    This class defines the CancelRejectClaimReport model for generating reports on canceled or rejected claims.

    """
    _name ='claim_cancel_reject_report'
    _auto = False


    code = fields.Char(string='Claim No')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    department_id = fields.Many2one('hr.department', string='Department')
    job_id = fields.Many2one('hr.job', string='Designation')
    grade_id = fields.Many2one('kwemp_grade_master', string='Level')
    category_id = fields.Many2one('kw_advance_claim_category', string='Category', domain="[('category','=','claim')]")
    sub_category_id = fields.Char(string='Sub Category Items')
    currency_id = fields.Many2one('res.currency')
    amount = fields.Float(string="Amount")
    state = fields.Char(string="State")
    year = fields.Char(string='Year')
    month = fields.Char(string='Month')
    pending_at = fields.Char('Application Status/Progress')
    log_id = fields.Many2one('claim_log_details', string='Rejected By')
    action_taken_by = fields.Many2one('hr.employee', related='log_id.action_taken_by', string='Rejected By', store=False)
    claim_id = fields.Many2one('kw_claim')


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = """
            CREATE or REPLACE VIEW %s as (                         
                                SELECT
                row_number() over(order by a.id) as id,
                a.code,
                a.employee_id,
                a.department_id,
                a.job_id,
                a.grade_id,
                a.category_id,
                (SELECT string_agg(claim_type, ', ') FROM sub_category_item_amount_config sc JOIN kw_advance_claim_type cc ON sc.claim_category_id = cc.id WHERE claim_id = a.id) as sub_category_id,
                a.currency_id,
                a.amount,
                a."year",
                to_char(to_date(a."month"::text, 'MM'), 'Month') as month,

                CASE
                    WHEN a.state = 'applied' THEN 'Applied'
                    WHEN a.state = 'approved' THEN 'Approved'
                    when a.state = 'verified' then 'Verified'
                    WHEN a.state = 'disbursed' THEN 'Disbursed'
                    WHEN a.state = 'reject' THEN 'Rejected'
                END AS state,
                a.pending_at,
                log.id as log_id,
                emp.name as action_taken_by,
                a.id as claim_id
                
            FROM
                kw_claim a
            LEFT JOIN (
                SELECT DISTINCT ON (claim_id) claim_id, id, action_taken_by
                FROM claim_log_details
                ORDER BY claim_id, id DESC
            ) log ON a.id = log.claim_id
            LEFT JOIN
                hr_employee emp ON log.action_taken_by = emp.id
            WHERE
                a.state IN ('reject')
            )

        """ % (self._table)

        self.env.cr.execute(query)

    def action_button_view_form(self):
        view_id = self.env.ref('claim.kw_claim_view_form').id
        return {
            'name': 'Claim',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'kw_claim',
            'view_id': view_id,
            'res_id': self.claim_id.id,
            'target': 'self',
            'context': {'edit': False, 'create': False, 'delete': False}
        }

class SettlementClaimReport(models.Model):
    """
    Class: SettlementClaimReport

    This class defines the SettlementClaimReport model for generating reports on settled claims.

    """

    _name = 'settlement_claim_report'
    _auto = False

    code = fields.Char(string='Claim No')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    department_id = fields.Many2one('hr.department', string='Department')
    job_id = fields.Many2one('hr.job', string='Designation')
    grade_id = fields.Many2one('kwemp_grade_master', string='Level')
    category_id = fields.Many2one('kw_advance_claim_category', string='Category', domain="[('category','=','claim')]")
    sub_category_id = fields.Char(string='Sub Category Items')
    currency_id = fields.Many2one('res.currency')
    amount = fields.Float(string="Amount")
    state = fields.Char(string="State")
    year = fields.Char(string='Year')
    month = fields.Char(string='Month')
    claim_id = fields.Many2one('kw_claim')



    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = """
            CREATE or REPLACE VIEW %s as (
                SELECT  row_number() over(order by id) as id,
                a.code as code,
                a.employee_id as employee_id,
                a.department_id as department_id,
                a.job_id as job_id,
                a.grade_id as grade_id,
                a.amount as amount,
                a.category_id as category_id,
                        (select string_agg(claim_type,', ')from sub_category_item_amount_config sc join kw_advance_claim_type cc on sc.claim_category_id = cc.id where claim_id = a.id)  
                as sub_category_id,
                a.currency_id as currency_id,
                a.year as year,
                to_char(to_date("month"::text, 'MM'), 'Month') as month,
                CASE
                    WHEN a.state = 'applied' THEN 'Applied'
                    WHEN a.state = 'approved' THEN 'Approved'
                    when a.state = 'verified' then 'Verified'
                    WHEN a.state = 'disbursed' THEN 'Disbursed'
                    WHEN a.state = 'reject' THEN 'Rejected'
                END AS state,
                id as claim_id

            from kw_claim a where state = 'disbursed'
                            )
        """ % (self._table)

        self.env.cr.execute(query)


    def action_button_view_form(self):
        view_id = self.env.ref('claim.kw_claim_view_form').id
        return {
            'name': 'Claim',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'kw_claim',
            'view_id': view_id,
            'res_id': self.claim_id.id,
            'target': 'self',
            'context': {'edit': False, 'create': False, 'delete': False}
        }