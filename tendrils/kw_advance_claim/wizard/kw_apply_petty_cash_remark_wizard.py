from odoo import models, fields, api
import datetime
from datetime import date, datetime
from odoo.exceptions import ValidationError


class kw_adv_petty_cash_approv_remark_wizard(models.TransientModel):
    _name = 'kw_advance_petty_cash_approv_remark_wizard'
    _description = 'Advance Petty Cash Approve Wizard'

    petty_cash_id = fields.Many2one(
        'kw_advance_apply_petty_cash', string='Petty Cash Ref')
    remark = fields.Text('Comment', size=40, required=True)

    @api.multi
    def approve_petty_cash(self):
        current_employee = self.env['hr.employee'].search([('user_id','=',self._uid)],limit=1)
        emp_name = current_employee and current_employee.name or self.env.user.name
        accounts_group = self.env.ref('kw_advance_claim.group_kw_advance_claim_account')
        accounts_employees = accounts_group.users.mapped('employee_ids') or False
        email_ids =  accounts_employees and ','.join(accounts_employees.mapped('work_email')) or ''

        self.petty_cash_id.write({'state': 'approve', 'approved_on': date.today(),
                               'approved_by': self.env.user.employee_ids.id, 'remark': self.remark,
                                'action_to_be_taken_by':self.env.user.employee_ids.id,
                                 'action_taken_by':self.env.user.employee_ids.id,'pending_status':'accounts'})
        self.env.user.notify_success("Petty cash has been approved.")

        #mail Ra to account
        mail_context = {'state': 'Approved'}
        template = self.env.ref('kw_advance_claim.kw_petty_cash_approve_mail_template')
        template.with_context(mail_context,accounts_email=email_ids,user_name=emp_name).send_mail(self.petty_cash_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        
        #mail Ra to user
        template_id = self.env.ref('kw_advance_claim.kw_petty_cash_user_status_email_template')
        template_id.with_context(mail_context).send_mail(self.petty_cash_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")


class kw_adv_petty_cash_cancel_remark_wizard(models.TransientModel):
    _name = 'kw_advance_petty_cash_cancel_remark_wizard'
    _description = 'Advance Petty Cash Cancel Wizard'

    petty_cash_id = fields.Many2one(
        'kw_advance_apply_petty_cash', string='Petty Cash Ref')
    remark = fields.Text('Comment', size=40, required=True)

    @api.multi
    def cancel_petty_cash(self):
        self.petty_cash_id.write({'state': 'cancel', 'approved_on': date.today(),
                               'approved_by': self.env.user.employee_ids.id, 'remark': self.remark,'pending_status':False})
        self.env.user.notify_success("Petty Cash has been cancelled.")
        return {'type': 'ir.actions.act_window_close'}


class kw_adv_petty_cash_onhold_remark_wizard(models.TransientModel):
    _name = 'kw_advance_petty_cash_onhold_remark_wizard'
    _description = 'Advance Petty Cash Onhold Wizard'

    petty_cash_id = fields.Many2one(
        'kw_advance_apply_petty_cash', string='Petty Cash Ref')
    remark = fields.Text('Comment', size=40, required=True)

    @api.multi
    def onhold_petty_cash(self):
        self.petty_cash_id.write({'state': 'hold', 'approved_on': date.today(),
                               'approved_by': self.env.user.employee_ids.id, 'remark': self.remark, 'action_taken_by':self.env.user.employee_ids.id})
        # mail Ra to user
        mail_context = {'state': 'Hold'}
        remark = self.remark
        template_id = self.env.ref('kw_advance_claim.kw_adv_apply_petty_cash_hold_mail_template')
        template_id.with_context(mail_context,remark=remark).send_mail(self.petty_cash_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        self.env.user.notify_success("Petty Cash is on Hold.")
        return {'type': 'ir.actions.act_window_close'}


class kw_adv_petty_cash_accounts_onhold_remark_wizard(models.TransientModel):
    _name = 'kw_advance_petty_cash_accounts_onhold_remark_wizard'
    _description = 'Advance Petty Cash Onhold Wizard'

    petty_cash_id = fields.Many2one(
        'kw_advance_apply_petty_cash', string='Petty Cash Ref')
    remark = fields.Text('Comment', size=40, required=True)

    @api.multi
    def onhold_petty_cash_acc(self):
        self.petty_cash_id.write({'state': 'hold', 'approved_on': date.today(),
                               'approved_by': self.env.user.employee_ids.id, 'accounts_remark': self.remark, 'action_taken_by':self.env.user.employee_ids.id})
        # mail Ra to user
        mail_context = {'state': 'Hold'}
        remark = self.remark
        template_id = self.env.ref('kw_advance_claim.kw_adv_apply_petty_cash_accounts_hold_mail_template')
        template_id.with_context(mail_context,remark=remark).send_mail(self.petty_cash_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        self.env.user.notify_success("Petty Cash is on Hold.")
        return {'type': 'ir.actions.act_window_close'}


class kw_adv_petty_cash_reject_remark_wizard(models.TransientModel):
    _name = 'kw_advance_petty_cash_reject_remark_wizard'
    _description = 'Advance Petty Cash Reject Wizard'

    petty_cash_id = fields.Many2one(
        'kw_advance_apply_petty_cash', string='Petty Cash Ref')
    remark = fields.Text('Comment', size=40, required=True)

    @api.multi
    def reject_petty_cash(self):
        self.petty_cash_id.write({'state': 'reject', 'approved_on': date.today(),
                               'approved_by': self.env.user.employee_ids.id, 'remark': self.remark, 'action_taken_by':self.env.user.employee_ids.id,'pending_status':False})
        self.env.user.notify_success("Petty cash has been rejected.")
        
        #mail Ra to user rejected mail
        mail_context = {'state': 'Rejected'}
        template_id = self.env.ref('kw_advance_claim.kw_petty_cash_user_status_reject_email_template')
        template_id.with_context(mail_context).send_mail(self.petty_cash_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")


class kw_adv_petty_cash_accounts_reject_remark_wizard(models.TransientModel):
    _name = 'kw_advance_petty_cash_accounts_reject_remark_wizard'
    _description = 'Advance Petty Cash Accounts Reject Wizard'

    petty_cash_id = fields.Many2one('kw_advance_apply_petty_cash', string='Petty Cash Ref')
    remark = fields.Text('Comment', size=40, required=True)

    @api.multi
    def reject_petty_cash_acc(self):
        self.petty_cash_id.write({'state': 'reject', 'approved_on': date.today(),
                               'approved_by': self.env.user.employee_ids.id, 'accounts_remark': self.remark, 'action_taken_by':self.env.user.employee_ids.id,'pending_status':False})
        self.env.user.notify_success("Petty cash has been rejected.")
        
        #mail Ra to user rejected mail
        mail_context = {'state': 'Rejected'}
        template_id = self.env.ref('kw_advance_claim.kw_petty_cash_user_status_account_reject_email_template')
        template_id.with_context(mail_context).send_mail(self.petty_cash_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")


class kw_adv_petty_cash_grant_remark_wizard(models.TransientModel):
    _name = 'kw_advance_petty_cash_grant_remark_wizard'
    _description = 'Advance Petty cash Grant Wizard'

    petty_cash_id = fields.Many2one('kw_advance_apply_petty_cash', string='Petty Cash Ref')
    remark = fields.Text('Comment', size=40, required=True)


    @api.multi
    def grant_petty_cash(self):     
        self.petty_cash_id.write({'state': 'grant', 'accounts_remark': self.remark,'approved_by': self.env.user.employee_ids.id, 'action_taken_by':self.env.user.employee_ids.id,'pending_status':False})
        #mail accounts to user mail
        mail_context = {'state': 'Granted'}
        template_id = self.env.ref('kw_advance_claim.kw_petty_cash_grant_mail_template')
        template_id.with_context(mail_context).send_mail(self.petty_cash_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        self.env.user.notify_success("Petty Cash has been granted.")
        return {'type': 'ir.actions.act_window_close'}


class kw_adv_petty_cash_release_remark_wizard(models.TransientModel):
    _name = 'kw_advance_petty_cash_release_remark_wizard'
    _description = 'Petty Cash Release Remark'

    petty_cash_id = fields.Many2one(
        'kw_advance_apply_petty_cash', string='Petty Cash Ref')
    remark = fields.Text('Comment', size=40, required=True)
    release_date = fields.Date('Date', default=fields.Date.today(), readonly=True)

    @api.multi
    def release_petty_cash(self):
        self.petty_cash_id.write({
            'state': 'release',
            'approved_on': date.today(),
            'approved_by': self.env.user.employee_ids.id,
            'accounts_remark': self.remark,
            'payment_date': self.release_date,
            'action_taken_by':self.env.user.employee_ids.id})
        self.env.user.notify_success("Petty Cash has been granted.")

    @api.constrains('release_date')
    def release_date_check(self):
        if self.petty_cash_id.create_date.date() < self.release_date > date.today():
          raise ValidationError(_("Release date should be after Applied date: %s")%(self.petty_cash_id.create_date.date()))


