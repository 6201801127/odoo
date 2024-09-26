# -*- coding: utf-8 -*-
import pytz
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, tools, _,SUPERUSER_ID
from odoo.exceptions import ValidationError,UserError
from lxml import etree


class kw_lv_apply(models.Model):
    _name = 'kw_lv_apply'
    _description =  "Local Visit"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'emp_name'
    _order = 'id desc'

    @api.model
    def _get_time_list(self):
        dt = datetime.now()
        start_loop = dt.replace(hour=7, minute=45, second=0, microsecond=0)
        end_loop = dt.replace(hour=22, minute=0, second=0, microsecond=0)
        time_list = []
        while start_loop < end_loop:
            start_loop = (start_loop+relativedelta(minutes=+15))
            time_list.append((start_loop.strftime('%H:%M'),
                              start_loop.strftime('%I:%M %p')))
        return time_list
    
    @api.model
    def _get_time_list_without_relativedelta(self):
        dt = datetime.now()
        start_loop = dt.replace(hour=5, minute=0, second=0, microsecond=0)
        end_loop = dt.replace(hour=23, minute=0, second=0, microsecond=0)
        time_list = []
        while start_loop < end_loop:
            start_loop = (start_loop+relativedelta(minutes=+1))
            time_list.append((start_loop.strftime('%H:%M'),
                              start_loop.strftime('%I:%M %p')))
        return time_list
    

    lv_for = fields.Selection(string="Local Visit For",selection=[('self','Self'),('others','Others')],required=True,default='self',track_visibility='onchange')

    visit_category = fields.Many2one('kw_lv_category_master',string='Visit Category',required=True,ondelete='restrict')
    office_details = fields.Selection(related='visit_category.office_details',store=False)
    visit_details = fields.Selection(related='visit_category.visit_details',store=False)
    apply_future_date = fields.Selection(related='visit_category.apply_future_date',store=False)
    apply_back_date = fields.Selection(related='visit_category.apply_back_date',store=False)

    location = fields.Char(string='Location')
    purpose = fields.Text(string='Purpose')
    visit_date = fields.Date(string='Visit Date',default=fields.Date.context_today,required=True)
    expected_in_time = fields.Selection(string='Expected In Time',selection='_get_time_list', required=True)
    vehicle_arrange = fields.Selection(string="Vehicle Arrange",selection=[('own','Own'),('office','Company')],required=True,default='own')
    vehicle_out_time = fields.Selection(string='Vehicle Out Time',selection='_get_time_list')
    vehicle_in_time = fields.Selection(string='Vehicle In Time',selection='_get_time_list')
    emp_name = fields.Many2one('hr.employee',string='Employee Name',default=lambda self: self.env.user.employee_ids,required=True,ondelete='restrict',track_visibility='onchange')

    out_time = fields.Selection(string='Out Time',selection='_get_time_list_without_relativedelta')
    status = fields.Selection(string="Local Visit Status",selection=[('office_in','Office In'),('office_out','Office Out')],track_visibility='onchange')
    actual_in_time = fields.Selection(string='Actual In Time',selection='_get_time_list_without_relativedelta',track_visibility='onchange')
    intimate_to = fields.Many2one('hr.employee',string='Intimate To Employee',ondelete='restrict')

    organization_name = fields.Many2one(comodel_name='res.partner',string='Customer/Organization Name',ondelete='restrict')
    contact_person = fields.Many2one(comodel_name='res.partner',string='Contact Person',ondelete='restrict')

    # For Office out
    visiting_with = fields.Selection(string="Visiting With",selection=[('individual','Individual'),('group','Group')],default='individual')
    vehicle_type = fields.Many2one('kw_lv_vehicle_category_master',string='Vehicle Type',ondelete='restrict')
    settlement_required = fields.Boolean(related='vehicle_type.settlement_required')
    auto_calculation = fields.Boolean(related='vehicle_type.auto_calculation')
    visiting_group = fields.Many2many('hr.employee',string='Select Employee')
    previous_time = fields.Selection(string='In Time',selection='_get_time_list')
    time_check = fields.Boolean(compute='_compute_check_is_back_date')
    parent_lv_id = fields.Many2one('kw_lv_apply',string='Parent Local visit id',ondelete='cascade')
    parent_lv_ids = fields.One2many('kw_lv_apply','parent_lv_id')
    applied_by = fields.Many2one('hr.employee',string='Applied By',default=lambda self: self.env.user.employee_ids,ondelete='restrict')

    # For Office in
    total_km = fields.Float('Total K.M. Covered',track_visibility='onchange')
    compute_price = fields.Float('Compute Price',compute='total_price_change',store=False)
    price = fields.Float('Price',track_visibility='onchange')
    remarks = fields.Text('Remarks')
    is_others_bool =fields.Boolean(compute='compute_vehicle_type_is_others_bool')
    attachment_id = fields.Binary('Attachment')

    # For Approve
    action_remark = fields.Text(string='Action Remark')
    ra_access = fields.Boolean(string='Access to RA', compute='_compute_access_to_ra')
    check_is_user = fields.Boolean(string='Logged In User',compute='_compute_check_is_user')
    pending_at = fields.Many2one('hr.employee',string='Action to be taken by/Taken by',compute='_compute_employee_for_approval',ondelete='restrict')
    taken_on = fields.Date(string='Taken on')
    taken_by = fields.Many2one('hr.employee',string='Taken by',ondelete='restrict')
    second_approver_bool = fields.Boolean(default=False)
    ulm_forward_bool = fields.Boolean(default=False)
    forth_rem_bool = fields.Boolean(default=False)
    seventh_rem_bool = fields.Boolean(default=False)

    # For business
    business_ids = fields.One2many(comodel_name='kw_lv_business',inverse_name='lv_id')
    is_settlement_applied = fields.Boolean(string='Is Settlement Applied')

    state = fields.Selection(string="Approval Status",selection=[('office_out','Office Out'),('applied','Applied'),('approved','Approved'),('rejected','Rejected'),('no_required','Not Required')],track_visibility='onchange',default='draft')

    settlement_state = fields.Selection(string="Settlement Status",selection=[('applied','Applied'),('approved','Approved'),('rejected','Rejected')],track_visibility='onchange')
    payment_status = fields.Selection(string="Payment State",selection=[('applied','Payment Not Done'),('payment','Payment Done')])
    settlement_reject_remark = fields.Text(string='Reject Remark')
    check_back_date = fields.Boolean(compute='compute_apply_back_date')
    stage_id = fields.Many2one(comodel_name='kw_lv_stage_master',string='LV Stage',compute='change_stage_value',store=True)
    color = fields.Integer()

    branch_id = fields.Many2one('kw_res_branch',compute='_get_default_branch',store=False)
    vehicle_filter = fields.Boolean(string='Filter Vehicle',compute='_get_default_branch',store=False)

    # @api.multi
    # def _get_auto_approval_days(self):
    #     param = self.env['ir.config_parameter'].sudo()
    #     set_days = param.get_param('kw_local_visit.lv_auto_approval_days')
    #     if set_days and set_days != 0:
    #         return int(set_days)
        
    @api.multi
    def _get_default_branch(self):
        for record in self:
            if record.emp_name and record.emp_name.user_id and record.emp_name.user_id.branch_id:
                record.branch_id = record.emp_name.user_id.branch_id.id
            else:
                pass
            if record.vehicle_arrange == 'own':
                record.vehicle_filter = True
            else:
                record.vehicle_filter = False

    @api.model
    def create(self,vals):
        new_record = super(kw_lv_apply,self).create(vals)
        # others
        if new_record and new_record.lv_for == 'others' and not new_record.parent_lv_id:
            template = self.env.ref('kw_local_visit.kw_lv_apply_ofc_out_others_email_template') 
            template.send_mail(new_record.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        else:
            pass
        return new_record
    
    @api.model
    def get_travel_desk_emails(self):
        users = self.env.ref('kw_local_visit.group_kw_local_visit_travel_desk').users
        values = ','.join(str(user_email.email) for user_email in users)
        return values
        
    ## Constrains functions-------
    @api.constrains('emp_name','lv_for')
    def _validate_emp_lv_record(self):
        lv_record = self.env['kw_lv_apply'].search([]) - self
        if any(record.status in ['office_out',False] and not self.parent_lv_id and record.emp_name.id == self.emp_name.id for record in lv_record):
            raise ValidationError(f'"{self.emp_name.name}" has pending local visit(s). \n Complete them before apply for a new local visit.')
    
    @api.constrains('expected_in_time','visit_date')
    def validate_expected_in_date(self):
        if 'tz' in self._context:
            user_tz = pytz.timezone(self._context.get('tz') if self._context.get('tz') != False else 'Asia/Kolkata')
        else:
            pass
        dt = datetime.now(user_tz)
        current_time = dt.strftime('%H:%M')
        for record in self:
            if record.expected_in_time < current_time and record.visit_date == date.today():
                raise ValidationError(f'Expected-In time should greater than current time...!')
    
    @api.constrains('visit_date','visit_category')
    def validate_visit_date_with_category(self):
        for record in self:
            if record.visit_category.apply_future_date == 'no' and record.visit_date > date.today():
                raise ValidationError(f'You can not apply future date for {record.visit_category.category_name}.')
            elif record.visit_category.apply_back_date == 'no' and record.visit_date < date.today():
                raise ValidationError(f'You can not apply back date for {record.visit_category.category_name}.')
    
    @api.constrains('out_time','actual_in_time')
    def validate_out_time_and_in_time(self):
        for record in self:
            if record.out_time and record.actual_in_time and record.out_time >= record.actual_in_time:
                raise ValidationError(f'In Time should be greater than Out Time.')

    @api.constrains('vehicle_arrange','vehicle_out_time','vehicle_in_time')
    def validate_vehicle_in_out_time(self):
        if 'tz' in self._context:
            user_tz = pytz.timezone(self._context.get('tz') if self._context.get('tz') != False else 'Asia/Kolkata')
        else:
            pass
        dt = datetime.now(user_tz)
        current_time = dt.strftime('%H:%M')
        for record in self:
            if record.vehicle_arrange == 'office':
                if record.vehicle_out_time <= current_time:
                    raise ValidationError(f'Vehicle out-time should greater than current time...!')
                elif record.vehicle_out_time >= record.vehicle_in_time:
                    raise ValidationError(f'Vehicle out-time should less than Vehicle in-time...!')
                else:
                    pass
    
    @api.constrains('visit_category','business_ids')
    def check_business_case(self):
        for record in self:
            if record.visit_category.visit_details == 'yes':
                if len(record.business_ids) == 0:
                    raise ValidationError(f'Please add at least one business record...!')
                else:
                    crm_id = [business_records.crm_id.id for business_records in record.business_ids]
                    if len(crm_id) != len(set(crm_id)):
                        raise ValidationError(f'You have duplicate Opportunity/Work Order records...!')
                    else:
                        pass

    ## Computed Fields Functions-------
    @api.multi
    def _compute_employee_for_approval(self):
        for record in self:
            if record.emp_name and record.emp_name.parent_id:
                if record.state not in [False,'office_out','no_required']:
                    if record.second_approver_bool == False:
                        record.pending_at = record.emp_name.parent_id.id
                    else:
                        record.pending_at = record.emp_name.parent_id.parent_id.id
                else:
                    pass
        
    @api.multi
    def _compute_check_is_user(self):
        for record in self:
            if record.emp_name.user_id.id == self.env.user.id:
                record.check_is_user = True
            else:
                record.check_is_user = False

    @api.multi
    def _compute_check_is_back_date(self):
        current_date = date.today()
        for record in self:
            if record.visit_date != current_date:
                record.time_check = True
            else:
                record.time_check = False
    @api.multi
    def compute_vehicle_type_is_others_bool(self):
        for record in self:
            if record.vehicle_type.vehicle_category_name == 'Others':
                record.is_others_bool = True
            else:
                record.is_others_bool = False

    @api.multi
    def _compute_access_to_ra(self):
        for record in self:
            if (record.emp_name.parent_id and record.emp_name.parent_id.user_id.id == self._uid and record.second_approver_bool == False) or record.emp_name.parent_id.parent_id.user_id.id == self._uid and record.second_approver_bool == True:
                record.ra_access = True
            else:
                record.ra_access = False

    @api.multi
    def compute_apply_back_date(self):
        for record in self:
            if record.apply_back_date == 'yes' and record.visit_date < date.today():
                record.check_back_date = True
            else:
                record.check_back_date = False

    ## Custom Functions-----------       
    def ofc_status(self):
        if 'tz' in self._context:
            user_tz = pytz.timezone(self._context.get('tz') if self._context.get('tz') != False else 'Asia/Kolkata')
        else:
            pass
        dt = datetime.now(user_tz)
        for record in self:
            if not record.status:
                if (record.apply_back_date == 'yes' and record.visit_date >= date.today()) or record.apply_back_date == 'no':
                    record.update({'out_time':dt.strftime('%H:%M')})
                else:
                    pass
                record.write({
                    'status':'office_out',
                    'state':'office_out'
                })
                ## send mail while office_out
                try:
                    
                    #Travel desk
                    if record.vehicle_arrange == 'office':
                        template = self.env.ref('kw_local_visit.kw_lv_travel_desk_email_template') 
                        template.send_mail(record.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                    else:
                        pass

                    ## To RA
                    above_m8_grade = ['M8','M9','M10','E1','E2','E3','E4','E5']
                    subject = 'Office-Out' if self.emp_name.grade.name in above_m8_grade else 'Applied'
                    email_to = self.env.user.employee_ids.parent_id.work_email if self.env.user.employee_ids.parent_id else ''
                    email_cc = self.env.user.employee_ids.parent_id.work_email if self.env.user.employee_ids.parent_id else ''
                    dear_user = self.env.user.employee_ids.parent_id.name if self.env.user.employee_ids.parent_id else ''
                    template = self.env.ref('kw_local_visit.kw_lv_apply_office_out_email_template')
                    template.with_context(email_to=email_to, email_cc=email_cc,subject=subject,dear_user=dear_user).send_mail(record.id,notif_layout="kwantify_theme.csm_mail_notification_light")

                    ## Initmate To
                    if record.intimate_to and record.intimate_to.id != record.emp_name.parent_id.id:
                        template = self.env.ref('kw_local_visit.kw_lv_apply_intimate_to_office_out_email_template') 
                        template.send_mail(record.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                    else:
                        pass
                except Exception as e:
                    pass
            elif record.status == 'office_out':
                if record.settlement_required == True and not record.parent_lv_id:
                    record.update({'state':'applied'})
                elif record.settlement_required == False or record.parent_lv_id:
                    record.update({'state':'no_required'})
                else:
                    pass
                record.write({
                    'actual_in_time':dt.strftime('%H:%M'),
                    'status':'office_in',
                })
                ## attendance integration
                if self.visit_category.office_details == 'no':
                    self._compute_attendance_time()
                try:
                    email_to = self.env.user.employee_ids.parent_id.work_email if self.env.user.employee_ids.parent_id else ''
                    email_cc = self.env.user.employee_ids.parent_id.work_email if self.env.user.employee_ids.parent_id else ''
                    dear_user = self.env.user.employee_ids.parent_id.name if self.env.user.employee_ids.parent_id else ''
                    template = self.env.ref('kw_local_visit.kw_lv_apply_office_in_email_template')
                    template.with_context(email_to=email_to, email_cc=email_cc,dear_user=dear_user).send_mail(record.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                except Exception as e:
                    pass

    def dynamic_status(self):
        if self.apply_future_date == 'yes' and self.visit_date > date.today():
            raise ValidationError('You can not Office Out before your visit date.')
        if self.apply_back_date == 'yes' and self.check_back_date and not self.out_time:
            raise ValidationError('Please update office-out-time because you are applying for previous date.')
        return True

    @api.onchange('vehicle_arrange')
    def _change_vehicle_category(self):
        self.vehicle_type = False
        branch_id = self.emp_name.user_id.branch_id.id if self.emp_name.user_id.branch_id else False
        if self.vehicle_arrange == 'own':
            return {'domain': {'vehicle_type': [('settlement_required','=',True),('location','=',branch_id)]}}
        elif self.vehicle_arrange == 'office':
            return {'domain': {'vehicle_type': [('settlement_required','=',False),('location','=',branch_id)]}}

    @api.multi
    def change_ofc_in(self):
        if not self.parent_lv_id and (self.office_details == 'yes' or self.vehicle_arrange == 'office'):
            view_id = self.env.ref('kw_local_visit.kw_lv_office_in_form').id
            return {
                    'name':'Local visit in for ' + self.visit_category.category_name + ':',
                    'type': 'ir.actions.act_window',
                    'res_model': 'kw_lv_apply',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id':self.id,
                    'view_id': view_id,
                    'target': 'new',
                    'flags': {'action_buttons': True, 'mode': 'edit'},
                }
        elif self.time_check == True:
            view_id = self.env.ref('kw_local_visit.kw_lv_office_in_time_check_form').id
            return {
                    'name':'Local visit in for ' + self.visit_category.category_name + ':',
                    'type': 'ir.actions.act_window',
                    'res_model': 'kw_lv_apply',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id':self.id,
                    'view_id': view_id,
                    'target': 'new',
                    'flags': {'action_buttons': True, 'mode': 'edit'},
                }
        else:
            self.ofc_status()
            self.env.user.notify_info("Office in details updated successfully.")

    def update_ofc_out(self):
        if self.apply_future_date == 'yes' and self.visit_date > date.today():
            raise ValidationError('You can not Office Out before your visit date.')
        if (self.office_details == 'yes' or (self.office_details == 'no' and self.vehicle_arrange == 'office')) and not self.vehicle_type:
            raise ValidationError('Please update vehicle before office out.')
        if 'tz' in self._context:
            user_tz = pytz.timezone(self._context.get('tz') if self._context.get('tz') != False else 'Asia/Kolkata')
        else:
            pass
        dt = datetime.now(user_tz)
        if self.visiting_with == 'group':
            if len(self.visiting_group) == 0:
                raise ValidationError(f'Select atleast one group member...!')
            else:
                for employees in self.visiting_group:
                    new_record = self.env['kw_lv_apply'].sudo().create({
                        'lv_for':'others',
                        'applied_by':self.env.user.employee_ids.id,
                        'parent_lv_id':self.id,
                        'visit_category':self.visit_category.id,
                        'business_ids':[
                                [0, 0, 
                                {
                                'activity_name': data.activity_name.id, 
                                'sub_category': data.sub_category.id,
                                'visit_for': data.visit_for,
                                'crm_id': data.crm_id.id,
                                'purpose': data.purpose,
                                'location': data.location
                                }
                                ] for data in self.business_ids],
                        'emp_name':employees.id,
                        'location':self.location,
                        'purpose':self.purpose,
                        'visit_date':self.visit_date,
                        'expected_in_time':self.expected_in_time,
                        'vehicle_arrange':self.vehicle_arrange,
                        'vehicle_out_time':self.vehicle_out_time,
                        'vehicle_in_time':self.vehicle_in_time,
                        'out_time':dt.strftime('%H:%M'),
                        'status':'office_out',
                        'state':'office_out',
                        'organization_name':self.organization_name.id,
                        'contact_person':self.contact_person.id,
                        'visiting_with':self.visiting_with,
                        })
                    ## Mail to group employees
                    try:
                        if self.emp_name.parent_id.id != employees.parent_id.id:
                            template = self.env.ref('kw_local_visit.kw_lv_ofc_out_group_email_template')
                            body = template.body_html
                            body = body.replace('--group_emp_name--', employees.parent_id.name)
                            mail_values = {
                                'email_to': employees.parent_id.work_email,
                                'body_html': body
                                }
                            template.write(mail_values)
                            template.send_mail(new_record.id,notif_layout="kwantify_theme.csm_mail_notification_light")

                            body = body.replace(employees.parent_id.name,'--group_emp_name--')
                            mail_values = {'body_html': body}
                            template.write(mail_values)
                    except Exception as e:
                        pass
        else:
            pass
        self.ofc_status()
        self.env.user.notify_info("Office out details updated successfully.")
        
    def update_ofc_in(self):
        # print(self.price)
        if 'tz' in self._context:
            user_tz = pytz.timezone(self._context.get('tz') if self._context.get('tz') != False else 'Asia/Kolkata')
        else:
            pass
        dt = datetime.now(user_tz)
        current_time = dt.strftime('%H:%M')
        current_date = date.today()
        if self.visit_details == 'yes' and len(self.business_ids) != 0 and not self.parent_lv_id:
            for record in self.business_ids:
                if not record.purpose and not record.location:
                    raise ValidationError(f'Must update purpose and location against the business records.')
        if self.previous_time and self.previous_time < current_time:
            raise ValidationError(f'In time must be greater than current time...!')
        if self.visit_date != current_date and self.previous_time and self.status == 'office_out':
            if self.settlement_required == True and not self.parent_lv_id:
                self.update({'state':'applied'})
            elif self.settlement_required == False or self.parent_lv_id:
                self.update({'state':'no_required'})
            else:
                pass
            self.write({'actual_in_time':self.previous_time,'status':'office_in'})
            ## attendance integration
            if self.visit_category.office_details == 'no':
                self._compute_attendance_time()
            try:
                email_to = self.env.user.employee_ids.parent_id.work_email if self.env.user.employee_ids.parent_id else ''
                email_cc = self.env.user.employee_ids.parent_id.work_email if self.env.user.employee_ids.parent_id else ''
                dear_user = self.env.user.employee_ids.parent_id.name if self.env.user.employee_ids.parent_id else ''
                template = self.env.ref('kw_local_visit.kw_lv_apply_office_in_email_template')
                template.with_context(email_to=email_to, email_cc=email_cc,dear_user=dear_user).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
            except Exception as e:
                pass
        else:
            self.ofc_status()
        self.env.user.notify_info("Office in details updated successfully.")

    ## Approval Buttons Actions -----
    def lv_action_approve(self):
        self.write({'state':'approved','taken_on':date.today(),'taken_by':self.env.user.employee_ids.id})

        mail_template = self.env.ref('kw_local_visit.kw_lv_ra_or_upper_ra_approval_mail_template')
        action_user = self.env.user.employee_ids.name
        email_from = self.env.user.employee_ids.work_email
        email_cc = self.emp_name.parent_id.work_email if self.emp_name.parent_id else ''
        mail_template.with_context(email_from=email_from,email_cc=email_cc,action_user=action_user).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")

        self.env.user.notify_success("Local visit has been approved.")
        action_id = self.env.ref('kw_local_visit.kw_lv_take_action_act_window_new').id
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=kw_lv_apply&view_type=list',
            'target': 'self',
        }

    def lv_action_reject(self):
        self.write({'state':'rejected','taken_on':date.today(),'taken_by':self.env.user.employee_ids.id})

        mail_template = self.env.ref('kw_local_visit.kw_lv_ra_or_upper_ra_approval_mail_template')
        action_user = self.env.user.employee_ids.name
        email_from = self.env.user.employee_ids.work_email
        email_cc = self.emp_name.parent_id.work_email if self.emp_name.parent_id else ''
        mail_template.with_context(email_from=email_from,email_cc=email_cc,action_user=action_user).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        self.env.user.notify_danger("Local visit has been rejected.")
        self.env.user.notify_danger("Local visit has been rejected.")

    def reject_from_settlement(self):
        settlement_id = False
        for r  in self.env['kw_lv_settlement'].sudo().search([('state','=','applied')]):
            jai_hind = r.filtered(lambda x : self.id in x.lv_id.ids)
            if jai_hind:
                settlement_id = jai_hind
        view_id = self.env.ref('kw_local_visit.kw_lv_many2many_records_settlement_reject_remark_form_view').id
        return {
                'name':'Reject Reason',
                'type': 'ir.actions.act_window',
                'res_model': 'kw_lv_apply',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id':self.id,
                'view_id': view_id,
                'target': 'new',
                'context': {'settlement_id':settlement_id.id},
                'flags': {'create': False}
                }
    
    def update_reject_from_settlement(self):
        context_data = self._context
        if context_data.get('settlement_id',False):
            settlement_record = self.env['kw_lv_settlement'].browse(int(context_data.get('settlement_id')))
            lv_id_records = []
            for record in settlement_record.lv_id:
                if 'active_ids' in context_data and record.id in context_data.get('active_ids'):
                    record.write({
                        'settlement_state':'rejected',
                    })
                    lv_id_records.append([3, record.id, False])
                    settlement_record.write({
                        'lv_id':lv_id_records,
                    })
                    self.env.user.notify_danger("Local visit rejected.")

    ## Onchange Functions------------
    @api.onchange('lv_for','vehicle_arrange')
    def _change_respected_field_values(self):
        if self.lv_for in ['self']:
            self.emp_name = self.env.user.employee_ids
        else:
            self.emp_name = False
        if self.vehicle_arrange == 'own':
            self.vehicle_out_time = False
            self.vehicle_in_time = False
        else:
            pass
    
    @api.onchange('organization_name')
    def _set_organisation_and_contact(self):
        self.contact_person = False
        if self.organization_name:
            return {'domain': {'contact_person': [('parent_id', 'in', self.organization_name.ids)]}}
        else:
            pass
    
    @api.onchange('visiting_with')
    def _change_visiting_values(self):
        if self.visiting_with == 'individual':
            self.visiting_group = False
        else:
            pass

    @api.depends('total_km','vehicle_type')
    def total_price_change(self):
        for record in self:
            if 'active_id' in self._context:
                active_id = self._context.get('active_id') if self._context.get('active_id') != False else 0
            else:
                active_id = 0
            lv_record = self.env[self._table].search([('id','=',int(active_id))])
            if record.total_km and record.auto_calculation == True:
                if len(lv_record) > 0:
                    if lv_record.vehicle_type.rate_per_km:
                        record.price = record.total_km * lv_record.vehicle_type.rate_per_km
                    else:
                        pass
                else:
                    record.price = record.total_km * record.vehicle_type.rate_per_km
            else:
                pass
    @api.multi
    @api.depends('status','state','settlement_state','payment_status')
    def change_stage_value(self):
        stage_master = self.env['kw_lv_stage_master']
        for record in self:
            # print(record.payment_status)
            if record.status == 'office_out':
                record.stage_id = stage_master.search([('sequence','=',1)]).id
            elif record.status == 'office_in' and record.settlement_required == False:
                record.stage_id = stage_master.search([('sequence','=',2)]).id
            else:
                record.stage_id = False
            if record.state == 'applied':
                record.stage_id = stage_master.search([('sequence','=',3)]).id
            elif record.state == 'approved' and record.settlement_state == False:
                record.stage_id = stage_master.search([('sequence','=',4)]).id
            elif record.state == 'rejected':
                record.stage_id = stage_master.search([('sequence','=',5)]).id
            elif record.state == 'approved' and record.settlement_state == 'applied' and not record.payment_status:
                record.stage_id = stage_master.search([('sequence','=',6)]).id
            elif record.state == 'approved' and record.settlement_state == 'approved' and not record.payment_status:
                record.stage_id = stage_master.search([('sequence','=',7)]).id
            elif record.state == 'approved' and record.settlement_state == 'rejected' and not record.payment_status:
                record.stage_id = stage_master.search([('sequence','=',8)]).id
            elif record.payment_status == 'payment':
                # print(record.payment_status,"Payment")
                record.stage_id = stage_master.search([('sequence','=',9)]).id
            else:
                pass

    @api.multi
    def unlink(self):
        if any(record.status in ['office_out','office_in'] for record in self):
            raise UserError(_('You can not delete the local visits once you have applied.'))
        else:
            self.env.user.notify_success(message='Local visit deleted successfully')
        return super(kw_lv_apply, self).unlink()

    # Visit category business logic
    @api.onchange('visit_category')
    def _onchange_visit_category(self):
        if self.visit_category.apply_back_date == 'no' and self.visit_category.apply_future_date == 'no':
            self.visit_date = date.today()
        else:
            self.visit_date = False
        if self.visit_category.visit_details == 'yes':
            self.location = False
            self.organization_name = False
            self.contact_person = False
            self.purpose = False
        else:
            self.business_ids = False
        if self.visit_category.office_details == 'no':
            self.organization_name = False
            self.contact_person = False
            self.business_ids = False
            self.visiting_with = 'individual'
            self.visiting_group = False
        else:
            pass
        if self.visit_category.office_details == 'no' and self.vehicle_arrange == 'own':
            self.vehicle_type = False
        else:
            pass
        
    @api.onchange('visit_date')
    def _change_back_date_with_visit_date(self):
        if self.apply_back_date == 'yes' and self.visit_date and self.visit_date < date.today():
            self.check_back_date = True
        else:
            self.check_back_date = False

## Cron Job for approve or forward
    def LocalVisitAutoApprove(self):
        auto_approve_days = self.env['ir.config_parameter'].sudo().get_param('auto_approval_days')
        try:
            above_m8_grade = ['M8','M9','M10','E1','E2','E3','E4','E5']
            lv_records = self.env['kw_lv_apply'].sudo().search([('state','=','applied')])
            # filter_lv_records = lv_records.filtered(lambda x : x.visit_date < (date.today() - relativedelta(days=int(auto_approve_days))) and x.state == 'applied')

            for record in lv_records:
                attendance_rec = self.env['kw_daily_employee_attendance'].sudo().search([('employee_id', '=', record.emp_name.id),('day_status', 'in', ['0','3']),('attendance_recorded_date', '<', date.today()),('attendance_recorded_date', '>', record.visit_date)])
                if len(attendance_rec) >= int(auto_approve_days):
                    if record.emp_name.grade.name in above_m8_grade:
                        record.sudo().write({
                            'state':'approved',
                            'taken_on':date.today(),
                            'taken_by':record.emp_name.parent_id.id if record.emp_name.parent_id else False,
                            'action_remark':'Auto Approved.',})
                        try:
                            email_cc = record.emp_name.parent_id.work_email if record.emp_name.parent_id else ''
                            template = self.env.ref('kw_local_visit.kw_lv_auto_approve_email_template')
                            template.with_context(auto_days = auto_approve_days,email_cc=email_cc).send_mail(record.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                        except Exception as e:
                            pass
                    else:
                        try:
                            if record.second_approver_bool == False and record.ulm_forward_bool == False :
                                if record.emp_name.parent_id.parent_id.parent_id:
                                    email_cc = record.emp_name.parent_id.work_email if record.emp_name.parent_id else ''
                                    template = self.env.ref('kw_local_visit.kw_lv_forward_to_upper_ra_template')
                                    template.with_context(auto_days = auto_approve_days,email_cc=email_cc).send_mail(record.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                                    record.sudo().write({'second_approver_bool':True})
                                else:
                                    pass
                                record.sudo().write({'ulm_forward_bool': True})
                        except Exception as e:
                            pass
        except Exception as e:
            pass

## Cron Job for reminders
    def LocalVisitAutoReminders(self):
        above_m8_grade = ['M8','M9','M10','E1','E2','E3','E4','E5']
        lv_records = self.env['kw_lv_apply'].sudo().search([('state','=','applied')])
        # two_month_records = lv_records.filtered(lambda x : x.visit_date < (date.today() - relativedelta(months=2)))
        weekly_records = lv_records.filtered(lambda x: x.visit_date in [(date.today() - relativedelta(days=d)) for d in [15, 22, 29, 36, 43, 50]])
        
        for record in lv_records:
            attendance_rec = self.env['kw_daily_employee_attendance'].sudo().search([('employee_id', '=', record.emp_name.id),('day_status', 'in', ['0','3']),('attendance_recorded_date', '<', date.today()),('attendance_recorded_date', '>', record.visit_date)])
            
            if len(attendance_rec) == 3 and record.emp_name.grade.name not in above_m8_grade and record.forth_rem_bool == False:
                template = self.env.ref('kw_local_visit.kw_lv_auto_reminder_email_template')
                email_to = record.emp_name.parent_id.work_email if record.emp_name.parent_id else ''
                email_cc = record.emp_name.parent_id.work_email if record.emp_name.parent_id else ''
                dear_user = record.emp_name.parent_id.name
                template.with_context(email_to=email_to,email_cc=email_cc,dear_user=dear_user).send_mail(record.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                record.sudo().write({'forth_rem_bool': True})
            
            elif len(attendance_rec) == 6 and record.emp_name.grade.name not in above_m8_grade and record.seventh_rem_bool == False:
                template = self.env.ref('kw_local_visit.kw_lv_auto_reminder_email_template')
                email_to = record.emp_name.parent_id.work_email if record.emp_name.parent_id else ''
                email_cc = record.emp_name.parent_id.work_email if record.emp_name.parent_id else ''
                dear_user = record.emp_name.parent_id.name
                template.with_context(email_to=email_to,email_cc=email_cc,dear_user=dear_user).send_mail(record.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                record.sudo().write({'seventh_rem_bool': True})

        # for record in two_month_records:
        #     record.sudo().write({'state':'rejected'})

        for record in weekly_records:
            if record.emp_name.grade.name not in above_m8_grade and record.emp_name.parent_id.parent_id.parent_id and record.second_approver_bool == True:
                template = self.env.ref('kw_local_visit.kw_lv_auto_reminder_email_template')
                email_to = record.emp_name.parent_id.parent_id.work_email
                dear_user = record.emp_name.parent_id.parent_id.name
                template.with_context(email_to=email_to,dear_user=dear_user).send_mail(record.id,notif_layout="kwantify_theme.csm_mail_notification_light")

           
# ## Cron Job for monthly mail
    @api.multi
    def LocalVisitAutoApproveMonthlyMail(self):
        # auto_approve_days = self._get_auto_approval_days()
        auto_approve_days = self.env['ir.config_parameter'].sudo().get_param('auto_approval_days')
        current_month_start = date.today().replace(day=1)
        current_month_end = (current_month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        auto_approved_records = self.env['kw_lv_apply'].search([
            ('action_remark', '=', 'Auto Approved.'),
            ('taken_on', '>=', current_month_start),
            ('taken_on', '<', current_month_end),
        ])
        
        records_by_ra = {}
        email_to_set = set()

        for record in auto_approved_records:
            ra = record.emp_name.parent_id.parent_id or record.emp_name.parent_id
            if ra:
                records_by_ra.setdefault(ra, []).append(record)
                if ra.work_email:
                    email_to_set.add(ra.work_email)

        for ra, records in records_by_ra.items():
            employee_list = []
            for record in records:
                purpose_value = record.purpose if record.purpose else ", ".join(business_id.purpose for business_id in record.business_ids)
                employee_list.append(
                    f"{record.visit_date or '--'}: {record.emp_name.name or '--'}: "
                    f"{record.emp_name.department_id.name or '--'}: {record.emp_name.division.name or '--'}: "
                    f"{record.emp_name.parent_id.name or '--'}: {record.vehicle_type.vehicle_category_name or '--'}: "
                    f"{record.total_km or '--'}: {record.price or '--'} : {purpose_value}"
                )

            if employee_list:
                email_to = ra.work_email
                extra_params = {'employee_list': employee_list, 'email_to_set': email_to, 'mail_to_name': ra.name,'auto_days':auto_approve_days}
                self.env['kw_lv_apply'].employee_send_custom_mail(
                    res_id=auto_approved_records[0].id,
                    notif_layout='kwantify_theme.csm_mail_notification_light',
                    template_layout='kw_local_visit.monthly_auto_approval_mail_template',
                    ctx_params=extra_params,
                    description="Local Visit"
                )

            
    def employee_send_custom_mail(self, res_id, force_send=False, raise_exception=False, email_values=None,notif_layout=False, template_layout=False, ctx_params=None, description=False):
        template = self.env.ref(template_layout)
        if template:
            # template.with_context(extra_params).send_mail(emp_rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            values = template.with_context(ctx_params).generate_email(res_id)
            values['recipient_ids'] = [(4, pid) for pid in values.get('partner_ids', list())]
            values.update(email_values or {})
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
                        'message': self.env['mail.message'].sudo().new(dict(body=values['body_html'], record_name=record.display_name)),
                        'model_description': description if description else self.env['ir.model']._get(record._name).display_name,
                        'company': 'company_id' in record and record['company_id'] or self.env.user.company_id,
                    }
                    body = notif_template.render(template_ctx, engine='ir.qweb', minimal_qcontext=True)
                    values['body_html'] = self.env['mail.thread']._replace_local_links(body)

            mail = self.env['mail.mail'].create(values)

            if force_send:
                mail.send(raise_exception=raise_exception)

            mail.model = False
            return mail.id

    
    @api.multi
    def _compute_attendance_time(self):
        self.ensure_one()
        pass
        # if self.actual_in_time and self.out_time:
        #     curr_date = date.today()
        #     visit_date = self.visit_date
        #     in_time = self.actual_in_time
        #     out_time = self.out_time
        #     ofc_in_time = datetime(curr_date.year, curr_date.month, curr_date.day,
        #                             int(in_time.split(':')[0]), int(in_time.split(':')[1]), 0)
        #     print(ofc_in_time)

        #     ofc_out_time = datetime(visit_date.year, visit_date.month, visit_date.day,
        #                             int(out_time.split(':')[0]), int(out_time.split(':')[1]), 0)
        #     print(ofc_out_time)
        #     print(ofc_in_time - ofc_out_time)
        #     total_time = ofc_in_time.hour - ofc_out_time.hour
        #     print(total_time)
        #     if total_time >= 2:
        #         print('Leave apply')
        #     else:
        #         print("Go ahead")
            # raise ValidationError('Error')

class res_partner_inherit_lv(models.Model):
    _inherit = 'res.partner'

    def _get_name(self):
        """ Utility method to allow name_get to be overrided without re-browse the partner """

        partner = self
        name = partner.name or ''
        if self._context.get('partner_name'):
            name = partner.name
        return name