from odoo import models, fields, api, _
import datetime
import calendar
import re
from dateutil import relativedelta
from datetime import date, datetime
from odoo.exceptions import ValidationError

class kw_adv_sal_approv_remark_wiz(models.TransientModel):
    _name = 'kw_advance_sal_approv_remark_wiz'
    _description = 'kw advance Salary Approve'

    sal_adv_id = fields.Many2one(
        'kw_advance_apply_salary_advance', string='Salary Advance Ref')
    remark = fields.Text('Comment', size=40, required=True)

    @api.constrains('remark')
    @api.onchange('remark')	
    def _onchange_remark(self):
        for rec in self:
            if rec.remark and not re.match(r'^[A-Za-z]{1}[A-Za-z\s]*$',str(rec.remark)):
                raise ValidationError("White space not allowed in first position")
            if rec.remark:
                if len(rec.remark) > 40:
                    raise ValidationError('Number of characters must not exceed 40')

    
    def approve_salary_advance(self):
        current_employee = self.env['hr.employee'].search([('user_id','=',self._uid)],limit=1)
        emp_name = current_employee and current_employee.name or self.env.user.name
        accounts_group = self.env.ref('kw_advance_claim.group_kw_advance_claim_account')
        accounts_employees = accounts_group.users.mapped('employee_ids') or False
        email_ids =  accounts_employees and ','.join(accounts_employees.mapped('work_email')) or ''
        mail_context = 'Approved'
        self.sal_adv_id.write({
            'state': 'approve',
            'approved_on': date.today(),
            'approved_by': self.env.user.employee_ids.id,
            'remark': self.remark,
            'action_to_be_taken_by':self.env.user.employee_ids.id,
            'action_taken_by':self.env.user.employee_ids.id,
            'approval_id':self.env.user.employee_ids.id,
            'approval_amount': self.sal_adv_id.adv_amnt,
            'pending_status':'accounts',
        })
        #mail Ra to user
        template_id = self.env.ref('kw_advance_claim.kw_salary_advance_user_status_email_template')
        template_id.with_context(get_state=mail_context).send_mail(self.sal_adv_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        #mail Ra to accounts
        template = self.env.ref('kw_advance_claim.kw_salary_advance_approve_mail_template')
        template.with_context(accounts_email=email_ids,user_name=emp_name,get_state=mail_context).send_mail(self.sal_adv_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        
        # self.env.user.notify_success("Advance has been approved.")
        
        return {'type': 'ir.actions.act_window_close'}


class kw_adv_sal_cancel_remark_wiz(models.TransientModel):
    _name = 'kw_advance_sal_cancel_remark_wiz'
    _description = 'kw advance Salary Cancel'

    sal_adv_id = fields.Many2one(
        'kw_advance_apply_salary_advance', string='Salary Advance Ref')
    remark = fields.Text('Comment', size=40, required=True)

    
    def cancel_salary_advance(self):
        self.sal_adv_id.write({'state': 'cancel', 'approved_on': date.today(),
                               'approved_by': self.env.user.employee_ids.id, 'remark': self.remark,'pending_status':False,})
        # self.env.user.notify_success("Advance has been cancelled.")


class kw_adv_sal_onhold_remark_wiz(models.TransientModel):
    _name = 'kw_advance_sal_onhold_remark_wiz'
    _description = 'kw advance Salary Onhold'

    sal_adv_id = fields.Many2one('kw_advance_apply_salary_advance', string='Salary Advance Ref')
    remark = fields.Text('Comment', size=40, required=True)

    
    def onhold_salary_advance(self):
        self.sal_adv_id.write({'state': 'hold', 'approved_on': date.today(),
                               'approved_by': self.env.user.employee_ids.id, 'remark': self.remark, 'action_taken_by':self.env.user.employee_ids.id})
        #mail Ra to user
        mail_context = 'Hold'
        remark = self.remark
        template_id = self.env.ref('kw_advance_claim.kw_salary_advance_hold_mail_template')
        template_id.with_context(get_state=mail_context,remark=remark).send_mail(self.sal_adv_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        # self.env.user.notify_success("Advance is on Hold.")


class kw_adv_sal_accounts_onhold_remark_wiz(models.TransientModel):
    _name = 'kw_advance_sal_accounts_onhold_remark_wiz'
    _description = 'kw advance Salary Onhold'

    sal_adv_id = fields.Many2one('kw_advance_apply_salary_advance', string='Salary Advance Ref')
    remark = fields.Text('Comment', size=40, required=True)

    
    def onhold_salary_advance_acc(self):
        self.sal_adv_id.write({'state': 'hold', 'approved_on': date.today(),
                               'approved_by': self.env.user.employee_ids.id, 'accounts_remark': self.remark, 'action_taken_by':self.env.user.employee_ids.id})
        #mail Ra to user
        mail_context = 'Hold'
        remark = self.remark
        template_id = self.env.ref('kw_advance_claim.kw_salary_advance_acounts_hold_mail_template')
        template_id.with_context(get_state=mail_context,remark=remark).send_mail(self.sal_adv_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        # self.env.user.notify_success("Advance is on Hold.")


class kw_adv_sal_reject_remark_wiz(models.TransientModel):
    _name = 'kw_advance_sal_reject_remark_wiz'
    _description = 'kw advance Salary Reject'

    sal_adv_id = fields.Many2one(
        'kw_advance_apply_salary_advance', string='Salary Advance Ref')
    remark = fields.Text('Comment', size=40, required=True)

    @api.constrains('remark')
    @api.onchange('remark')	
    def _onchange_remark(self):
        for rec in self:
            if rec.remark and not re.match(r'^[A-Za-z]{1}[A-Za-z\s]*$',str(rec.remark)):
                raise ValidationError("White space not allowed in first position")
            if rec.remark:
                if len(rec.remark) > 40:
                    raise ValidationError('Number of characters must not exceed 40')

    
    def reject_salary_advance(self):
        self.sal_adv_id.write({'state': 'reject', 'approved_on': date.today(),
                               'approved_by': self.env.user.employee_ids.id, 'remark': self.remark, 'action_taken_by':self.env.user.employee_ids.id,'pending_status':False,})
        # self.env.user.notify_success("Advance has been rejected.")
        
        #mail Ra to user rejected mail
        mail_context = {'state': 'Rejected'}
        template_id = self.env.ref('kw_advance_claim.kw_salary_advance_user_status_reject_email_template')
        template_id.with_context(mail_context).send_mail(self.sal_adv_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")


class kw_adv_sal_accounts_reject_remark_wiz(models.TransientModel):
    _name = 'kw_advance_sal_accounts_reject_remark_wiz'
    _description = 'kw advance Salary Accounts Reject'

    sal_adv_id = fields.Many2one(
        'kw_advance_apply_salary_advance', string='Salary Advance Ref')
    remark = fields.Text('Comment', size=40, required=True)

    @api.constrains('remark')
    @api.onchange('remark')	
    def _onchange_remark(self):
        for rec in self:
            if rec.remark and not re.match(r'^[A-Za-z]{1}[A-Za-z\s]*$',str(rec.remark)):
                raise ValidationError("White space not allowed in first position")
            if rec.remark:
                if len(rec.remark) > 40:
                    raise ValidationError('Number of characters must not exceed 40')

    
    def reject_salary_advance_acc(self):
        self.sal_adv_id.write({'state': 'reject', 'approved_on': date.today(),
                               'approved_by': self.env.user.employee_ids.id, 'accounts_remark': self.remark, 'action_taken_by':self.env.user.employee_ids.id,'pending_status':False,})
        # self.env.user.notify_success("Advance has been rejected.")
        
        #mail accounts to user rejected mail
        mail_context = {'state': 'Rejected'}
        template_id = self.env.ref('kw_advance_claim.kw_salary_advance_user_status_accounts_reject_email_template')
        template_id.with_context(mail_context).send_mail(self.sal_adv_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")


class kw_adv_sal_grant_remark_wiz(models.TransientModel):
    _name = 'kw_advance_sal_grant_remark_wiz'
    _description = 'Advance Salary Grant'

    sal_adv_id = fields.Many2one('kw_advance_apply_salary_advance', string='Salary Advance Ref')
    remark = fields.Text('Comment', size=40, required=True)

    @api.constrains('remark')
    @api.onchange('remark')	
    def _onchange_remark(self):
        for rec in self:
            if rec.remark and not re.match(r'^[A-Za-z]{1}[A-Za-z\s]*$',str(rec.remark)):
                raise ValidationError("White space not allowed in first position")
            if rec.remark:
                if len(rec.remark) > 40:
                    raise ValidationError('Number of characters must not exceed 40')

    
    def grant_salary_advance(self):
        self.sal_adv_id.write({'state': 'grant', 'approved_on': date.today(),
                               'approved_by': self.env.user.employee_ids.id, 'accounts_remark': self.remark, 'action_taken_by':self.env.user.employee_ids.id,'pending_status':False,})
        #mail accounts to user rejected mail
        # mail_context = {'state': 'Granted'}
        mail_context = 'Granted'

        # template_id = self.env.ref('kw_advance_claim.kw_salary_advance_grant_mail_template')
        # template_id.with_context(get_state=mail_context).send_mail(self.sal_adv_id.id,
        #                                                            notif_layout="kwantify_theme.csm_mail_notification_light")
        # template_id.with_context(mail_context).send_mail(self.sal_adv_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        # self.env.user.notify_success("Advance has been granted.")
        """ 1)EMI datas added to Main deduction line
            2)Data from Temp deduction line is flushed
            3)logs are updated
        """
        # if self.sal_adv_id.temp_deduction_line_ids:
        #     self.sal_adv_id.move_deduction_line_data()
        return {'type': 'ir.actions.act_window_close'}


class kw_adv_sal_release_remark_wiz(models.TransientModel):
    _name = 'kw_advance_sal_release_remark_wiz'
    _description = 'kw advance Salary Release Remark'

    sal_adv_id = fields.Many2one(
        'kw_advance_apply_salary_advance', string='Salary Advance Ref')
    remark = fields.Text('Comment', size=40, required=True)
    release_date = fields.Date('Date', default=fields.Date.today(), readonly=True)

    

    
    def release_salary_advance(self):
        # self.sal_adv_id.write({
        #     'state': 'release',
        #     'approved_on': date.today(),
        #     'accounts_remark': self.remark,
        #     'payment_date': self.release_date,
        #     'action_taken_by': self.env.user.employee_ids.id,})
        query = f"UPDATE kw_advance_apply_salary_advance set state='{'release'}',approved_on='{date.today()}',accounts_remark='{self.remark}',payment_date='{self.release_date}',action_taken_by='{self.env.user.employee_ids.id}' where id = '{self.sal_adv_id.id}';"
        self._cr.execute(query)
        # self.sal_adv_id.req_date = self.sal_adv_id.create_date.date()
        self.sal_adv_id.calculate_emi()
        temp_data = self.sal_adv_id.deduction_line_ids
        self.sal_adv_id.deduction_line_ids = [(2, rec.id) for rec in temp_data]
        if self.sal_adv_id.temp_deduction_line_ids:
            self.sal_adv_id.move_deduction_line_data()
        # self.env.user.notify_success("Advance has been granted.")

    @api.constrains('release_date')
    def release_date_check(self):
        if self.sal_adv_id.create_date.date() < self.release_date > date.today():
            raise ValidationError(_("Release date should be after Applied date: %s")%(self.sal_adv_id.create_date.date()))
        
    @api.constrains('remark')
    @api.onchange('remark')	
    def _onchange_remark(self):
        for rec in self:
            if rec.remark and not re.match(r'^[A-Za-z]{1}[A-Za-z\s]*$',str(rec.remark)):
                raise ValidationError("White space not allowed in first position")
            if rec.remark:
                if len(rec.remark) > 40:
                    raise ValidationError('Number of characters must not exceed 40')

