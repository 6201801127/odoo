# -*- coding: utf-8 -*-
import pytz
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, tools, _
from odoo.exceptions import ValidationError,UserError
from lxml import etree
import calendar

class kw_lv_settlement(models.Model):
    _name = 'kw_lv_settlement'
    _description =  "Local Visit Settlement"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'emp_name'
    _order = 'id desc'

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

    emp_name = fields.Many2one('hr.employee',string='Employee Name',default=lambda self: self.env.user.employee_ids,ondelete='restrict')
    job_id = fields.Many2one('hr.job',related='emp_name.job_id')
    department_id = fields.Many2one('hr.department',related='emp_name.department_id')
    division = fields.Many2one('hr.department',related='emp_name.division')
    section = fields.Many2one('hr.department',related='emp_name.section')
    practise = fields.Many2one('hr.department',related='emp_name.practise')
    grade_id = fields.Many2one('kwemp_grade_master',related='emp_name.grade')
    
    lv_id = fields.Many2many('kw_lv_apply','kw_lv_apply_and_lv_settlement',string='Local Visits',domain="['&','&','&',('emp_name','=',emp_name),('vehicle_type.settlement_required','=',True),('state','in',['approved']),('is_settlement_applied','=',False)]",track_visibility='onchange',compute='filter_lv_records',store=True)
    total_km = fields.Integer('Total K.M.',compute='_compute_total_km_and_price',store=True)
    price = fields.Float('Price',compute='_compute_total_km_and_price',store=True)

    payment_mode = fields.Selection(string='Payment Mode',selection=[('cash','Cash'),('ac','Account Transfer')],default='cash')
    remark = fields.Text(string='Remarks')
    applied_date = fields.Date(string='Applied On',default=fields.Date.context_today)
    group_access = fields.Boolean(string='Access to Group', compute='_compute_access_to_group')
    to_be_taken_by = fields.Char(string='Action to be taken by',compute='_compute_group_members')
    taken_by = fields.Many2one('hr.employee',string='Action Taken by',ondelete='restrict')
    taken_on = fields.Date(string='Action Taken on')
    state = fields.Selection(string="Status",selection=[('applied','Applied'),('approved','Approved'),('rejected','Rejected')],track_visibility='onchange')

    # payment details
    payment_date = fields.Date(string='Payment Date')
    payment_taken_by = fields.Many2one('hr.employee',string='Payment Action to be taken by/Taken by',ondelete='restrict')
    payment_taken_on = fields.Date(string='Payment Taken On')
    payment_state = fields.Selection(string="Payment Status",selection=[('applied','Payment Not Done'),('payment','Payment Done')],track_visibility='onchange')

    stage_id = fields.Many2one(comodel_name='kw_lv_stage_master',string='Settlement Stage',compute='change_settlement_stage_value',store=True,ondelete='restrict')
    month = fields.Selection(MONTH_LIST, string='Month', required=True,default=str(date.today().month))
    year = fields.Selection(string='Year',selection='_get_year_list', required=True,default=str(date.today().year))
    
    @api.depends('lv_id','state','payment_state')
    def change_settlement_stage_value(self):
        stage_master = self.env['kw_lv_stage_master']
        for record in self:
            for lv_record in record.lv_id:
                if lv_record.state == 'approved' and record.state == 'applied':
                    record.stage_id = stage_master.search([('sequence','=',6)]).id
                elif lv_record.state == 'approved' and record.state == 'approved' and record.payment_state == 'applied':
                    record.stage_id = stage_master.search([('sequence','=',7)]).id
                elif lv_record.state == 'approved' and record.state == 'rejected':
                    record.stage_id = stage_master.search([('sequence','=',8)]).id
                elif lv_record.state == 'approved' and record.state == 'approved' and record.payment_state == 'payment':
                    record.stage_id = stage_master.search([('sequence','=',9)]).id
                else:
                    pass

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            record_name = str(record.emp_name.name)+ ' | ' + str(len(record.lv_id))+' - local visit(s)'
            result.append((record.id, record_name))
        return result

    @api.constrains('lv_id')
    def check_lv_ids(self):
        for record in self:
            if len(record.lv_id) == 0:
                raise ValidationError('Minimum one local visit must be there.')
            else:
                pass
    
    # @api.constrains('month','year')
    # def check_month_year_duplicate(self):
    #     record = self.env['kw_lv_settlement'].search([]) - self
    #     for info in record:
    #         if info.emp_name.id == self.emp_name.id and info.month == self.month and info.year == self.year:
    #             MONTH_LIST = {'1':'January','2':'February',
    #                         '3':'March','4':'April',
    #                         '5':'May','6':'June',
    #                         '7':'July','8':'August',
    #                         '9':'September','10':'October',
    #                         '11':'November','12':'December'
    #             }
    #             month = MONTH_LIST[self.month]
    #             raise ValidationError(f"You have already applied settlement for :- \n Month : {month}\n Year : {self.year}.")

    @api.depends('month','year')
    def filter_lv_records(self):
        for record in self:
            record.lv_id = False
            if record.month and record.year:
                last_date = calendar.monthrange(int(record.year), int(record.month))[1]
                domain=[('emp_name','=',record.emp_name.id),('vehicle_type.settlement_required','=',True),('state','in',['approved']),('is_settlement_applied','=',False),('visit_date', '>=',(date(int(record.year),int(record.month), 1)).strftime('%Y-%m-%d')),('visit_date', '<=', (date(int(record.year),int(record.month), last_date)).strftime('%Y-%m-%d'))]
                apply_records = self.env['kw_lv_apply'].search(domain)
                record.lv_id = [(4, apply_record.id) for apply_record in apply_records]
            else:
                pass 

    @api.multi
    def _compute_group_members(self):
        for record in self:
            settlement_users = ''
            group_users = self.env.ref('kw_local_visit.group_kw_local_visit_settlement').users
            for members in group_users:
                settlement_users += members.name +', '
                record.to_be_taken_by = settlement_users.rstrip(', ')

    @api.model
    def create(self, values):
        result = super(kw_lv_settlement, self).create(values)
        total_km = 0
        price = 0
        for lv_records in result.lv_id:
            lv_records.write({
                'is_settlement_applied':True,
                'settlement_state':'applied',
                })
            total_km +=lv_records.total_km
            price += lv_records.price
        result.write({
            'state':'applied',
            'total_km':total_km,
            'price':price,
            })

        try:
            template = self.env.ref('kw_local_visit.kw_lv_settlement_apply_email_template')
            email_to = self.env.user.employee_ids.parent_id.work_email if self.env.user.employee_ids.parent_id else ''
            email_cc = self.env.user.employee_ids.parent_id.work_email if self.env.user.employee_ids.parent_id else ''
            dear_user = self.env.user.employee_ids.parent_id.name if self.env.user.employee_ids.parent_id else ''
            template.with_context(email_to=email_to, email_cc=email_cc,dear_user=dear_user).send_mail(result.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        except Exception as e:
            pass

        self.env.user.notify_success("Settlement applied successfully.")
        return result

    @api.depends('lv_id')
    def _compute_total_km_and_price(self):
        for record in self:
            price = 0
            km = 0
            for lv_ids in record.lv_id:
                price += float(lv_ids.price)
                record.price = price
                km += int(lv_ids.total_km)
                record.total_km = km       

    @api.multi
    def _compute_access_to_group(self):
        for record in self:
            if self.env.user.has_group('kw_local_visit.group_kw_local_visit_settlement'):
                record.group_access = True
            else:
                record.group_access = False
    
    def lv_settlement_action_approve(self):
        if self.lv_id:
            for records in self.lv_id:
                records.write({
                    'settlement_reject_remark':False, 
                    'settlement_state':'approved'
                })
        else:
            pass
        self.write({'state':'approved','taken_by':self.env.user.employee_ids.id,'taken_on':date.today(),'payment_state':'applied'})

        try:
            template = self.env.ref(
                'kw_local_visit.kw_lv_settlement_take_action_email_template')
            template.send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        except Exception as e:
            pass

        self.env.user.notify_success("Settlement has been approved.")

    def lv_settlement_action_reject(self):
        if self.lv_id:
            for records in self.lv_id:
                records.write({
                    'settlement_state':'rejected'
                })
        else:
            pass
        self.write({'state':'rejected','taken_by':self.env.user.employee_ids.id,'taken_on':date.today()})

        try:
            template = self.env.ref(
                'kw_local_visit.kw_lv_settlement_take_action_email_template')
            template.send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        except Exception as e:
            pass

        self.env.user.notify_danger("Settlement has been rejected.")

    ## Payment
    def action_payment(self):
        if self.payment_state == 'applied':
            view_id = self.env.ref('kw_local_visit.kw_lv_settlement_payment_form').id
            return {
                    'name':'Payment for ' + str(self.emp_name.name) + ':',
                    'type': 'ir.actions.act_window',
                    'res_model': 'kw_lv_settlement',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id':self.id,
                    'view_id': view_id,
                    'target': 'new',
                    'flags': {'toolbar': False}
                }
        else:
            pass

    def confirm_payment(self):
        if self.lv_id:
            for records in self.lv_id:
                records.write({
                    'payment_status':'payment'
                })
        else:
            pass
        self.write({
                'payment_taken_by':self.env.user.employee_ids.id,
                'payment_taken_on':date.today(),
                'payment_state':'payment',
        })

        try:
            template = self.env.ref(
                'kw_local_visit.kw_lv_settlement_paid_email_template')
            template.send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        except Exception as e:
            pass

        self.env.user.notify_success("Payment Successfully.")
