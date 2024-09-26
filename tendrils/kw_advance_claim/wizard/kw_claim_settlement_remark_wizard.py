import datetime
from datetime import date, datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import locale

class kw_adv_claim_cancel_remark_wizard(models.TransientModel):
    _name = 'kw_advance_claim_cancel_remark_wizard'
    _description = 'kw Advance Claim Cancel Wizard'

    claim_record_id = fields.Many2one('kw_advance_claim_settlement', string='Claim Ref')
    remark = fields.Text('Comment', size=40, required=True)

    @api.multi
    def cancel_claim(self):
        self.claim_record_id.write({'state': 'cancel', 'action_remark': self.remark,'pending_status':False})
        self.env.user.notify_success("Advance has been cancelled.")


class kw_adv_claim_approve_remark_wizard(models.TransientModel):
    _name = 'kw_advance_claim_approve_remark_wizard'
    _description = 'Claim Settlement Approve Wizard'

    claim_record_id = fields.Many2one('kw_advance_claim_settlement', string='Claim Ref')
    remark = fields.Text('Comment', size=40, required=True)

    @api.multi
    def approve_claim(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1)
        emp_name = current_employee and current_employee.name or self.env.user.name
        accounts_group = self.env.ref('kw_advance_claim.group_kw_advance_claim_account')
        accounts_employees = accounts_group.users.mapped('employee_ids') or False
        email_ids =  accounts_employees and ','.join(accounts_employees.mapped('work_email')) or ''

        self.claim_record_id.write({'state': 'approve',
                                    'approved_on': date.today(),
                                    'approved_by': self.env.user.employee_ids.id,
                                    'ra_remark': self.remark,
                                    'action_to_be_taken_by': self.env.user.employee_ids.id,
                                    'action_taken_by': self.env.user.employee_ids.id,
                                    'pending_status': 'accounts'})
        self.env.user.notify_success("Claim has been approved.")

        # mail Ra to accounts
        mail_context = 'Approved'
        claim_category_list = []
        claim_type_list = []
        for record in self.claim_record_id.claim_bill_line_ids:
            claim_category_list.append(record.category_id.name if record.category_id else '')
            claim_type_list.append(record.claim_type_id.claim_type if record.claim_type_id else '')
        claim_category = ','.join(claim_category_list)
        claim_type = ','.join(claim_type_list)
        template = self.env.ref('kw_advance_claim.kw_claim_settlement_approve_mail_template')
        applied_date=self.claim_record_id.applied_date.strftime("%d-%b-%Y")
        employee_name= self.claim_record_id.empl_id.name
        employee_code=self.claim_record_id.empl_id.emp_code
        email_from_ra = self.claim_record_id.empl_id.parent_id.work_email
        ra_name=self.claim_record_id.empl_id.parent_id.name
        claim_ref=self.claim_record_id.petty_cash_id.name
        currency= self.claim_record_id.currency_id.symbol
        expenses = f"{currency}{(float(self.claim_record_id.expenses)):,.2f}"
        amt_total = f"{currency}{(float(self.claim_record_id.amount_total)):,.2f}" 
        nt_total= f"{currency}{(float(self.claim_record_id.net_total)):,.2f}"   
        remark= self.claim_record_id.ra_remark
        ra_user=self.claim_record_id.empl_id.parent_id.user_id.id
        ra_signature=self.claim_record_id.empl_id.parent_id.user_id.signature
        emp_email=self.claim_record_id.empl_id.work_email
        cc =self.claim_record_id.users_status_cc() or '' 

        template.with_context(applied_date=applied_date,employee_name=employee_name,employee_code=employee_code,email_from_ra=email_from_ra,ra_name=ra_name,claim_ref=claim_ref,currency=currency,expenses=expenses,amt_total=amt_total,nt_total=nt_total,remark=remark,ra_user=ra_user,ra_signature=ra_signature,accounts_email=email_ids, user_name=emp_name, get_state=mail_context,
                              claim_category=claim_category, claim_type=claim_type).send_mail(self.claim_record_id.id,
                                                                                              notif_layout="kwantify_theme.csm_mail_notification_light")

        # mail Ra to user
        template_id = self.env.ref('kw_advance_claim.kw_Claim_settlement_user_status_email_template')
        template_id.with_context(cc=cc,emp_email=emp_email,applied_date=applied_date,employee_name=employee_name,employee_code=employee_code,email_from_ra=email_from_ra,ra_name=ra_name,claim_ref=claim_ref,currency=currency,expenses=expenses,amt_total=amt_total,nt_total=nt_total,remark=remark,ra_user=ra_user,ra_signature=ra_signature,accounts_email=email_ids, user_name=emp_name,get_state=mail_context, claim_category=claim_category,
                                 claim_type=claim_type).send_mail(self.claim_record_id.id,
                                                                  notif_layout="kwantify_theme.csm_mail_notification_light")
        

class kw_adv_claim_hold_remark_wizard(models.TransientModel):
    _name = 'kw_advance_claim_hold_remark_wizard'
    _description = 'kw Claim Settlement Cash Onhold Wizard'

    claim_record_id = fields.Many2one('kw_advance_claim_settlement', string='Claim Ref')
    remark = fields.Text('Comment', size=40, required=True)

    @api.multi
    def onhold_claim(self):
        self.claim_record_id.write({'state': 'hold', 'approved_on': date.today(),
                                    'approved_by': self.env.user.employee_ids.id,
                                    'ra_remark': self.remark,
                                    'action_taken_by': self.env.user.employee_ids.id})
        mail_context = 'Hold'
        claim_category_list = []
        claim_type_list = []
        for record in self.claim_record_id.claim_bill_line_ids:
            claim_category_list.append(record.category_id.name if record.category_id else '')
            claim_type_list.append(record.claim_type_id.claim_type if record.claim_type_id else '')
        claim_category = ','.join(claim_category_list)
        claim_type = ','.join(claim_type_list)
        ra_remark = self.claim_record_id.ra_remark
        template = self.env.ref('kw_advance_claim.kw_claim_settlement_hold_mail_template')
        template.with_context(status=mail_context, ra_remark=ra_remark, claim_category=claim_category,
                              claim_type=claim_type).send_mail(self.claim_record_id.id,
                                                               notif_layout="kwantify_theme.csm_mail_notification_light")
        
        self.env.user.notify_success("Claim is on Hold.")
        return {'type': 'ir.actions.act_window_close'}


class kw_adv_claim_acc_hold_remark_wizard(models.TransientModel):
    _name = 'kw_advance_claim_acc_hold_remark_wizard'
    _description = 'kw Claim Settlement Cash Accounts Onhold Wizard'

    claim_record_id = fields.Many2one('kw_advance_claim_settlement', string='Claim Ref')
    remark = fields.Text('Comment', size=40, required=True)

    @api.multi
    def onhold_claim_acc(self):
        self.claim_record_id.write({'state': 'hold', 'approved_on': date.today(),
                                    'approved_by': self.env.user.employee_ids.id,
                                    'acc_remark': self.remark,
                                    'action_taken_by': self.env.user.employee_ids.id})
        mail_context = 'Hold'
        claim_category_list = []
        claim_type_list = []
        for record in self.claim_record_id.claim_bill_line_ids:
            claim_category_list.append(record.category_id.name if record.category_id else '')
            claim_type_list.append(record.claim_type_id.claim_type if record.claim_type_id else '')
        claim_category = ','.join(claim_category_list)
        claim_type = ','.join(claim_type_list)
        acc_remark = self.claim_record_id.acc_remark
        template = self.env.ref('kw_advance_claim.kw_claim_settlement_hold_mail_template')
        template.with_context(status=mail_context, acc_remark=acc_remark, claim_category=claim_category,
                              claim_type=claim_type).send_mail(self.claim_record_id.id,
                                                               notif_layout="kwantify_theme.csm_mail_notification_light")
        
        self.env.user.notify_success("Claim is on Hold.")
        return {'type': 'ir.actions.act_window_close'}


class kw_adv_claim_reject_remark_wizard(models.TransientModel):
    _name = 'kw_advance_claim_reject_remark_wizard'
    _description = 'kw Claim Settlement Cash Reject Wizard'

    claim_record_id = fields.Many2one('kw_advance_claim_settlement', string='Claim Ref')
    remark = fields.Text('Comment', size=40, required=True)

    @api.multi
    def reject_claim(self):
        self.claim_record_id.write({'state': 'reject', 'approved_on': date.today(),
                                    'approved_by': self.env.user.employee_ids.id,
                                    'ra_remark': self.remark,
                                    'action_taken_by': self.env.user.employee_ids.id,
                                    'pending_status': False})
        self.env.user.notify_success("Claim request has been rejected.")
        # mail Ra to user rejected mail
        mail_context = {'state': 'Rejected'}
        claim_category_list = []
        claim_type_list = []
        for record in self.claim_record_id.claim_bill_line_ids:
            claim_category_list.append(record.category_id.name if record.category_id else '')
            claim_type_list.append(record.claim_type_id.claim_type if record.claim_type_id else '')
        claim_category = ','.join(claim_category_list)
        claim_type = ','.join(claim_type_list)
        template_id = self.env.ref('kw_advance_claim.kw_claim_settlement_user_status_reject_email_template')
        template_id.with_context(mail_context, claim_category=claim_category, claim_type=claim_type).send_mail(
            self.claim_record_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        

class kw_adv_claim_accounts_reject_remark_wizard(models.TransientModel):
    _name = 'kw_advance_claim_accounts_reject_remark_wizard'
    _description = 'kw Claim Settlement Accounts Reject Wizard'

    claim_record_id = fields.Many2one('kw_advance_claim_settlement', string='Claim Ref')
    remark = fields.Text('Comment', size=40, required=True)

    @api.multi
    def accounts_reject_claim_(self):
        self.claim_record_id.write({'state': 'reject',
                                    'approved_on': date.today(),
                                    'approved_by': self.env.user.employee_ids.id,
                                    'acc_remark': self.remark,
                                    'action_taken_by': self.env.user.employee_ids.id,
                                    'pending_status': False})
        self.env.user.notify_success("Claim has been rejected.")
        # mail accounts to user rejected mail
        mail_context = {'state': 'Rejected'}
        claim_category_list = []
        claim_type_list = []
        for record in self.claim_record_id.claim_bill_line_ids:
            claim_category_list.append(record.category_id.name if record.category_id else '')
            claim_type_list.append(record.claim_type_id.claim_type if record.claim_type_id else '')
        claim_category = ','.join(claim_category_list)
        claim_type = ','.join(claim_type_list)
        template_id = self.env.ref('kw_advance_claim.kw_claim_settlement_user_status_account_reject_email_template')
        template_id.with_context(mail_context, claim_category=claim_category, claim_type=claim_type).send_mail(
            self.claim_record_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        

class kw_adv_claim_grant_remark_wizard(models.TransientModel):
    _name = 'kw_advance_claim_grant_remark_wizard'
    _description = 'Claim Settlement cash Grant Wizard'

    claim_record_id = fields.Many2one('kw_advance_claim_settlement', string='Claim Ref')
    remark = fields.Text('Comment', size=40, required=True)

    @api.multi
    def grant_claim(self):
        self.claim_record_id.write(
            {'state': 'grant',
             'acc_remark': self.remark,
             'action_taken_by': self.env.user.employee_ids.id,
             'pending_status': False})
        mail_context = {'state': 'Granted'}
        claim_category_list = []
        claim_type_list = []
        for record in self.claim_record_id.claim_bill_line_ids:
            claim_category_list.append(record.category_id.name if record.category_id else '')
            claim_type_list.append(record.claim_type_id.claim_type if record.claim_type_id else '')
        claim_category = ','.join(claim_category_list)
        claim_type = ','.join(claim_type_list)
        template_id = self.env.ref('kw_advance_claim.kw_Claim_settlement_grant_mail_template')
        template_id.with_context(mail_context, claim_category=claim_category, claim_type=claim_type).send_mail(
            self.claim_record_id.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        self.env.user.notify_success("Claim has been granted.")
        return {'type': 'ir.actions.act_window_close'}


class kw_adv_claim_release_remark_wiz(models.TransientModel):
    _name = 'kw_advance_claim_release_remark_wiz'
    _description = 'Claim Settlement Release Remark'

    claim_record_id = fields.Many2one('kw_advance_claim_settlement', string='Claim Ref')
    remark = fields.Text('Comment', size=40, required=True)
    release_date = fields.Date('Date', default=fields.Date.today(), readonly=True)

    @api.multi
    def release_claim(self):
        self.claim_record_id.write({
            'state': 'release',
            'approved_on': date.today(),
            'approved_by': self.env.user.employee_ids.id,
            'acc_remark': self.remark,
            'payment_date': self.release_date,
            'action_taken_by':self.env.user.employee_ids.id,
            })
        self.claim_record_id.petty_cash_id.sudo().write({'settlement_status':'settle'})
        self.env.user.notify_success("Advance has been granted.")

    # @api.constrains('release_date')
    # def release_date_check(self):
    #     if self.release_date < self.claim_record_id.applied_date.date():
    #         raise ValidationError("Release date can be less than Applied date & can't be future date.")

