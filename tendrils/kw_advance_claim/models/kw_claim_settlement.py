from odoo import models, fields, api
from ast import literal_eval
from datetime import datetime
from odoo.exceptions import ValidationError

state_selection = [('draft', 'New'), ('applied', 'Applied'),
                   ('approve', 'Approved'), ('cancel', 'Cancelled'),
                   ('hold', 'Hold'), ('reject', 'Rejected'),
                   ('grant', 'Grant'), ('reject', 'Rejected')]


class kw_adv_claim_settlement(models.Model):
    _name = 'kw_advance_claim_settlement'
    _description = 'Petty Cash Settlement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"

    @api.depends('claim_bill_line_ids')
    def get_net_total(self):
        expense = 0
        if self.claim_bill_line_ids:
            # print("inside if=================")
            for rec in self.claim_bill_line_ids:
                if self.advance_taken == 'yes':
                    # print("inside seconfd iffff===================")
                    expense = expense + rec.amount
                    # print("inside expense===================",expense)

                    self.expenses = expense
                    self.amount_total = self.advance_amt
                    self.net_total = self.amount_total - self.expenses
                    # print("inside net total==================",self.net_total)

                else:
                    # print("inside else=====================")
                    expense = expense + rec.amount
                    self.total_expenditure = expense
                    self.net_total = expense
        else:
            self.amount_total = self.advance_amt



    @api.depends('petty_cash_id')
    @api.multi
    def _compute_btn_access(self):
        for record in self:
            if self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_user'):
                if self.env.user.employee_ids and not self.env.user.employee_ids.child_ids:
                    record.hide_btn_cancel = True
                if record.state == 'applied' and record.env.uid == record.action_to_be_taken_by.user_id.id and self.env.user.has_group(
                        'kw_employee.group_hr_ra'):
                    record.show_ra_button = True
                if record.state == 'forward' and record.env.uid == record.action_to_be_taken_by.user_id.id and self.env.user.has_group(
                        'kw_employee.group_hr_ra'):
                    record.show_ra_button = True
                if record.state == 'hold' and record.env.uid == record.action_to_be_taken_by.user_id.id and self.env.user.has_group(
                        'kw_employee.group_hr_ra'):
                    record.show_ra_button = True

                if record.state == 'approve' and self.env.user.has_group(
                        'kw_advance_claim.group_kw_advance_claim_account'):
                    record.show_accounts_button = True
                if record.state == 'hold' and self.env.user.has_group(
                        'kw_advance_claim.group_kw_advance_claim_account'):
                    record.show_accounts_button = True
                if record.state == 'grant' and self.env.user.has_group(
                        'kw_advance_claim.group_kw_advance_claim_account'):
                    record.show_accounts_button = True

    @api.model
    def _get_petty_cash_id(self):
        if not self.env.context.get('get_pettycash_id'):
            return [('state','not in',['cancel','reject']),('claim_id','=',False),('user_emp_id.user_id','=',self._uid)]

    #Form fields
    name = fields.Char(string="Ref No", required=True, default="New", readonly="1")
    petty_cash_id = fields.Many2one('kw_advance_apply_petty_cash',string="Petty Cash Ref", ondelete='cascade', domain= _get_petty_cash_id)
    purpose = fields.Text(string="Purpose",related='petty_cash_id.description',store=True)
    empl_id = fields.Many2one('hr.employee',string="Employee")
    applied_date = fields.Datetime(string='Applied Date')
    currency_id = fields.Many2one('res.currency',string="Currency")
    petty_cash_type = fields.Selection(string ="Petty Cash Type",selection=[('others', 'Others') ])
    advance_amt = fields.Float(string="Advance Amount",readonly=False)

    # eligible_amount = fields.Char(related="petty_cash_id.eligible_amount",string="Eligible amount")
    claim_bill_line_ids = fields.One2many('kw_advance_claim_bill_line', 'claim_line_id', string="Claim Bill Lines")
    expenses = fields.Float(string="Total Expenses", compute='get_net_total', store=True)
    amount_total = fields.Float(string="Advance Taken", compute='get_net_total', store=True)
    net_total = fields.Float(string="Payable/Receivable", compute='get_net_total', store=True)
    state = fields.Selection(string='Status', selection=state_selection, default='draft', track_visibility='onchange')
    department_id = fields.Many2one('hr.department', string="Department", related='empl_id.department_id', store=True)
    division = fields.Many2one('hr.department', string="Division", related='empl_id.division', store=True)
    section = fields.Many2one('hr.department', string="Practice", related='empl_id.section', store=True)
    practise = fields.Many2one('hr.department', string="Section", related='empl_id.practise', store=True)
    job_id = fields.Many2one('hr.job', string="Designation", related='empl_id.job_id', store=True)
    payment_date = fields.Date(string="Disburse Date", track_visibility='onchange')
    mode_of_payment = fields.Selection(string="Mode of Payment", selection=[('cash', 'Cash'), ('bank', 'Bank')],
                                       track_visibility='onchange')
    bank_id = fields.Many2one('res.bank', string="Bank Name")
    # # remark action on button
    action_remark = fields.Text(string="Remarks")
    ra_remark = fields.Text(string="RA Remarks")
    acc_remark = fields.Text(string="Accounts Remarks")
    approved_on = fields.Date(string="Approved On")
    approved_by = fields.Char(string="Approved By")
    active = fields.Boolean(string="Active", default=True)
    action_to_be_taken_by = fields.Many2one('hr.employee', string="Action to be Taken By")
    action_taken_by = fields.Many2one('hr.employee', string="Action Taken By")
    forwarded_by = fields.Many2one('hr.employee', string="Forwarded By")
    """#button hide/show"""
    hide_btn_cancel = fields.Boolean(compute='_compute_btn_access')
    show_ra_button = fields.Boolean(compute='_compute_btn_access')
    show_accounts_button = fields.Boolean(compute='_compute_btn_access')
    show_apply_btn = fields.Boolean(string="Show Apply Button")

    pending_status = fields.Selection(string='Pending At',selection=[('ra', 'Pending at RA'), ('accounts', 'Pending at Accounts')], track_visibility='onchange')
    advance_taken = fields.Selection(string='Advance Taken',selection=[('yes', 'Yes'), ('no', 'No')],default='no', track_visibility='onchange')
    total_expenditure = fields.Float(string="Total Expenditure",compute='get_net_total',store=True)
    pending_at_status = fields.Char(string='Pending At',compute='get_pending_at_status')
    
    @api.depends('state')
    def get_pending_at_status(self):
        for rec in self:
            if rec.state in ['applied','forward']:
                rec.pending_at_status = rec.action_to_be_taken_by.name
            elif rec.state in ['grant','approve'] :
                rec.pending_at_status = 'Pending at Accounts'
            else:
                rec.pending_at_status= ' '
                
    # @api.constrains('payment_date')
    # def payment_date_check(self):
    #     if self.payment_date:
    #         if self.payment_date > self.applied_date.date() or self.payment_date < datetime.today().date():
    #             raise ValidationError("Release date can be less than Applied date & can't be future date.")

    @api.multi
    def apply_claim_request(self):
        status = "Applied"
        claim_category_list = []
        claim_type_list = []
        dept_head_mail = self.empl_id.department_id.manager_id.work_email
        self.write({'state': 'applied', 'action_to_be_taken_by': self.empl_id.parent_id.id, 'pending_status': 'ra'})
        for record in self.claim_bill_line_ids:
            claim_category_list.append(record.category_id.name)
            claim_type_list.append(record.claim_type_id.claim_type if record.claim_type_id else '')
        claim_category = ','.join(claim_category_list)

        claim_type = ','.join(claim_type_list)

        template_id = self.env.ref('kw_advance_claim.kw_claim_settlement_apply_mail_template')
        template_id.with_context(status=status, work_email=dept_head_mail, claim_category=claim_category,
                                 claim_type=claim_type).send_mail(self.id,
                                                                  notif_layout="kwantify_theme.csm_mail_notification_light")
        self.env.user.notify_success("Claim applied successfully.")

    @api.model
    def create(self, vals):
        vals['show_apply_btn'] = True
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('kw_apply_claim') or '/'
        res = super(kw_adv_claim_settlement, self).create(vals)
        if res.petty_cash_id:
            res.petty_cash_id.write({'claim_id': res.id})
        return res

    @api.multi
    def write(self, vals):
        if vals.get('state') == 'grant' and self.mode_of_payment == False:
            raise ValidationError("Please add mode of payment.")

        res = super(kw_adv_claim_settlement, self).write(vals)
        return res

    @api.multi
    def claim_take_action_button(self):
        view_id = self.env.ref('kw_advance_claim.kw_adv_claim_settlement_takeaction_form').id
        target_id = self.id
        return {
            'name': 'Take Action',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_advance_claim_settlement',
            'res_id': target_id,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(view_id, 'form')],
            'target': 'self',
            'view_id': view_id,
        }

    @api.multi
    def claim_account_take_action_button(self):
        view_id = self.env.ref('kw_advance_claim.kw_adv_claim_settlement_takeaction_account_form').id
        target_id = self.id
        return {
            'name': 'Take Action',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_advance_claim_settlement',
            'res_id': target_id,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(view_id, 'form')],
            'target': 'self',
            'view_id': view_id,
        }

    @api.multi
    def get_emp_email(self):
        emp_name = self.env['hr.employee'].sudo().search([('user_id', '=', self.create_uid.id)], limit=1)
        if emp_name:
            return emp_name.work_email
        else:
            return ""

    def get_ra_email(self):
        emp_id = self.env['hr.employee'].sudo().search([('user_id', '=', self.create_uid.id)], limit=1)
        ra_email = ''
        if emp_id:
            ra_email = emp_id.parent_id.work_email if emp_id.parent_id else ""
        return ra_email

    def get_emp_name(self):
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.create_uid.id)], limit=1)
        username = employee and employee.name or self.create_uid.name
        return username

    @api.multi
    def get_cc_email(self):
        param = self.env['ir.config_parameter'].sudo()
        cc_group = literal_eval(param.get_param('kw_advance_claim.notification_cc_ids'))
        email_list = []
        if cc_group:
            all_jobs = self.env['hr.job'].browse(cc_group)
            employee_list = self.env['hr.employee'].search([('job_id', 'in', all_jobs.ids)]).mapped('work_email')
            if employee_list:
                email_list = employee_list
                # email_list = [emp.work_email for emp in empls if emp.work_email]
        return ",".join(email_list)

    @api.multi
    def users_status_cc(self):
        emp_cc_mail_list = []
        param = self.env['ir.config_parameter'].sudo()
        cc_hr_mails = param.get_param('kw_advance_claim.individual_hr_email')
        emp_cc_mail_list += self.empl_id.department_id.manager_id.mapped('work_email')
        if cc_hr_mails and cc_hr_mails != "False":
            emp_cc_mail_list += cc_hr_mails.split(',')
        return ','.join(set(emp_cc_mail_list))

    @api.multi
    def users_grant_cc(self):
        unique_mail_list = []
        unique_mail_list += self.empl_id.department_id.manager_id.mapped('work_email')
        unique_mail_list += self.empl_id.parent_id.mapped('work_email')
        param = self.env['ir.config_parameter'].sudo()
        cc_notify = param.get_param('kw_advance_claim.individual_hr_email')
        cc_group = literal_eval(param.get_param('kw_advance_claim.notification_cc_ids'))
        all_jobs = self.env['hr.job'].browse(cc_group)
        if cc_group:
            employee_list = self.env['hr.employee'].search([('job_id', 'in', all_jobs.ids)]).mapped('work_email')
            if employee_list:
                unique_mail_list += employee_list
        if cc_notify and cc_notify != "False":
            unique_mail_list.append(cc_notify)
        return ','.join(set(unique_mail_list))

    @api.model
    def default_get(self, fields):
        res = super(kw_adv_claim_settlement, self).default_get(fields)
        res['empl_id'] = self.env.user.employee_ids.id
        res['applied_date'] = datetime.today()
        res['currency_id'] = self.env.user.company_id.currency_id.id
        return res

    @api.onchange('petty_cash_id')
    def onchange_petty_cash_id(self):
        if self.petty_cash_id:
            self.applied_date = self.petty_cash_id.create_date
            self.currency_id = self.petty_cash_id.currency_id
            self.advance_amt = self.petty_cash_id.advance_amt

    @api.onchange('advance_taken')
    def onchange_advance_taken(self):
        if self.advance_taken == 'no':
            self.petty_cash_id = False
        self.applied_date = False
        self.currency_id = False
        self.advance_amt = False

    @api.onchange('mode_of_payment')
    def onchange_mode_of_payment(self):
        if self.mode_of_payment == 'cash' and (self.net_total >= 10000 or self.total_expenditure >= 10000):
            raise ValidationError("Mode of payment can't be 'Cash' if the settlement amount is more than Rs.10,000.")
        
    def get_claim_record_for_reaply(self):
        self.write({'state': 'draft'})
        view_id = self.env.ref('kw_advance_claim.kw_adv_claim_settlement_redirect_form').id
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Petty Cash Settlement',
            'view_mode': 'tree,form',
            'views': [(view_id, 'form')],
            'res_model': 'kw_advance_claim_settlement',
            'target': 'self',
            'view_id': view_id,
            'res_id':self.id,
            'context': {'default_petty_cash_id': self.petty_cash_id.id,
                        'default_applied_date': self.petty_cash_id.create_date,
                        'default_currency_id': self.petty_cash_id.currency_id.id,
                        'default_petty_cash_type': self.petty_cash_id.petty_cash_type,
                        'default_advance_amt': self.petty_cash_id.advance_amt,
                        'default_advance_taken': 'yes'
                        },
            'flags':{'mode':'edit'},
        }
        return action

    @api.constrains('claim_bill_line_ids','petty_cash_id')
    def claim_settlement_apply_validation(self):
        if len(self.claim_bill_line_ids) == 0:
            raise ValidationError("Please Add Claim Details")
