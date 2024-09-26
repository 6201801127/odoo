# Commit HIstory
# amount,minimum eligible amount,deduction logic changes 7 June 2021(Gouranga kala)
# 
from odoo import models, fields, api,_
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError


class PfWidthdrawl(models.Model):
    _name = "pf.widthdrawl"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "PF Withdrawl"
    # _rec_name = 'employee_id'


    def _default_employee(self):
        return self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)], limit=1)

    @api.depends('employee_id')
    def compute_emp_empr_contrib(self):
        for rec in self:
            if rec.employee_id:
                pf_employee = self.env['pf.employee'].sudo().search([('employee_id', '=', rec.employee_id.id)])
                rec.emp_contrib_bal, rec.empr_contrib_bal = pf_employee.cepf_vcpf, pf_employee.cpf
            if self.env.user.has_group('pf_withdrawl.group_pf_withdraw_approver'):
                rec.check_approver = True

    name = fields.Char(string='Name',track_visibility='always')
    date = fields.Date(string="Requested Date", default=fields.Date.today())
    employee_id=fields.Many2one('hr.employee', string="Request By", default=_default_employee,track_visibility='always', store=True)
    advance_amount=fields.Float(string="Requested Amount",track_visibility='always',)
    interest=fields.Float(string="Interest",track_visibility='always',)
    designation=fields.Many2one('hr.job', string="Designation",track_visibility='always',)
    center=fields.Char(string="Work Location",track_visibility='always',)
    approval_workflow=fields.Text(string="Approval Workflow",track_visibility='always',)
    present_pay=fields.Float(string="Present Pay", compute='_compute_present_pay',track_visibility='always')
    bank_account_number=fields.Char(string="Bank Account",track_visibility='always',)
    cepf_vcpf = fields.Boolean('MPF + VPF')
    cpf = fields.Boolean('EPF')
    rule=fields.Selection([('A','23(1)(A)'),
                           ('B','23(1)(B)'),
                           ('E','23(1)(E)')],string="Rules",track_visibility='always', store=True)
    pf_type = fields.Many2one('pf.type',string="PF Withdrawal Type",track_visibility='always')
    maximum_withdrawal = fields.Float(string='Eligible Amount',track_visibility='always')
#     purpose=fields.Selection([('a','Purchase of dwelling sight/flat/ construction of house/ renovation of house'),
#                               ('b','Repayment of loans'),
#                               ('e','For marriage and Education')],
    purpose = fields.Text(string="Purpose",track_visibility='always',related="pf_type.purpose")
#     attachment_document=fields.Selection([('ai',""""""'1) Declaration form for purchase of dwelling site.'
#                                                 '2) Declaration & Undertaking for non-encumbrance.'
#                                                 '3) Agreement of sale/Copy of Sale Deed/Allotment Letter.'
#                                                 '4) Copy of prior intimation under rule 18(2) of CCS Conduct Rules, 1964.'
#                                                 '5) Estimate of Repairs, Renovation, Construction.'""""""),
#                                  ('bi','1) Certificate of Home Loan Sanctioned. 2) Copy of Sale Deed.3) Certificate of Outstanding Home Loan. 4) Copy of prior intimation under rule 18(2) of CCS Conduct Rules, 1964.'),
#                                  ('ei','Marriage 1) Copy of invitation card. Education 1) Admission letter/Fee Details/Other')],
#                                 string='Attach Documents',track_visibility='always',)
    attachment_document = fields.Text(string="Attachment Document",track_visibility='always',related="pf_type.attachment_document")
#     attachment_ids=fields.Many2many('abc.ab',string="Attachment")
    attachment_ids = fields.Many2many('ir.attachment', string='Files',track_visibility='always')
    branch_id = fields.Many2one('res.branch',string="Center",track_visibility='onchange', store=True)
    department_id = fields.Many2one('hr.department','Department',track_visibility='onchange', store=True)
    
    state = fields.Selection(
        [('draft', 'Draft'), ('to_approve', 'To Approve'), ('approved', 'Approved'), ('rejected', 'Rejected')
         ], required=True, default='draft',string="Status",track_visibility='always',)
    
    emp_cepf_vcpf_bal = fields.Float('Deduction from Employee Contribution')
    emp_cpf_bal = fields.Float('Deduction from Employer Contribution')
    emp_contrib_bal = fields.Float('Employee Contribution Balance', compute='compute_emp_empr_contrib')
    empr_contrib_bal = fields.Float('Employer Contribution Balance', compute='compute_emp_empr_contrib')
    check_approver = fields.Boolean('Check Approver', default=False, compute='compute_emp_empr_contrib')
    applied_refund = fields.Boolean('Applied Refund', default=False)
    payment_advice = fields.Boolean('Payment Advice', track_visibility='onchange')

    @api.multi
    def create_payment_advices(self):
        line_ids, emp_lis = [], []
        for rec in self.filtered(lambda x: x.payment_advice == False):
            if any(tuple(filter(lambda x: x.state != 'approved', self))):
                raise ValidationError('You can create payment advice for approved PF.')
            if rec.employee_id.id not in emp_lis:
                line_ids.append((0, 0, {
                    'employee_id': rec.employee_id.id,
                    'bank_name': rec.employee_id.bank_account_id.bank_id.name,
                    'account_no': rec.employee_id.bank_account_id.acc_number,
                    'ifsc_code': rec.employee_id.bank_account_id.bank_id.bic or '',
                    'amount': rec.advance_amount,
                }))
                emp_lis.append(rec.employee_id.id)
            else:
                # filter(lambda x: x[2]['employee_id'] == rec.employee_id.id, line_ids).amount += rec.approved_amount
                for line in line_ids:
                    if line[2]['employee_id'] == rec.employee_id.id:
                        line[2]['amount'] += rec.advance_amount
            rec.payment_advice = True
        self.env['pf.payment.advice'].create({
            'date': fields.Date.today(),
            'name': 'PF: Payment Advice',
            'line_ids': line_ids
        })
        self.env.user.notify_info('Payment advice has been created successfully.')
        return True

    # added by Gouranga Kala on 10 june 2021
    def get_employee_birthday(self,employee):
        if not employee.birthday:
            raise ValidationError("Employee don't have birthday configured.")
        return employee.birthday

    @api.constrains('pf_type')
    def validate_employee_age(self):
        for withdraw in self:
            if withdraw.pf_type.min_age > 0 and (self.get_employee_birthday(withdraw.employee_id) + \
                relativedelta(years=withdraw.pf_type.min_age)) >  date.today():
                raise ValidationError(f"Minimum age of {withdraw.pf_type.min_age} is required against this PF Withdrawl Category.")


    @api.onchange('pf_type','employee_id')
    @api.constrains('pf_type','employee_id')
    def onchange_pf_type(self):
        for rec in self:
            rec.designation = rec.employee_id.job_id.id
            rec.branch_id = rec.employee_id.branch_id.id
            pf_employee = self.env['pf.employee'].sudo().search([('employee_id', '=', rec.employee_id.id)])
            print('============================================pf employee=================')
            # amt = 0.00
            max_all = 0.00
            maximum_allowed = 0.00
            if pf_employee:
                for pf_emp in pf_employee:
                    # cepf_vcpf_percentage   cpf_percentage basic_da_percentage  (Percentage fields)
                    pf_emp.amount = pf_emp.amount - self.advance_amount # not working
                    pf_emp.pf_withdrwal_amount = pf_emp.amount # not working

                    if rec.pf_type.cepf_vcpf == True and rec.pf_type.cpf == True:
                        cepf_vcpf   = pf_emp.cepf_vcpf
                        cpf         = pf_emp.cpf

                        if rec.pf_type.cepf_vcpf_percentage > 0:
                            cepf_vcpf = cepf_vcpf * (rec.pf_type.cepf_vcpf_percentage / 100)

                        if rec.pf_type.cpf_percentage > 0:
                            cpf = cpf * (rec.pf_type.cpf_percentage / 100)

                        # max_all = pf_emp.cepf_vcpf + pf_emp.cpf
                        max_all = cepf_vcpf + cpf

                    elif rec.pf_type.cepf_vcpf == True and rec.pf_type.cpf == False:
                        cepf_vcpf = pf_emp.cepf_vcpf

                        if rec.pf_type.cepf_vcpf_percentage > 0:
                             cepf_vcpf = cepf_vcpf * (rec.pf_type.cepf_vcpf_percentage / 100)

                        # max_all = pf_emp.cepf_vcpf
                        max_all = cepf_vcpf
                    
                    elif rec.pf_type.cepf_vcpf == False and rec.pf_type.cpf == True:
                        cpf = pf_emp.cpf
                        if rec.pf_type.cpf_percentage > 0:
                            cpf = cpf * (rec.pf_type.cpf_percentage / 100)
                        # max_all = pf_emp.cpf
                        max_all = cpf
                    
                    # elif rec.pf_type.cepf_vcpf == False and rec.pf_type.cpf == False:
                    #     cepf_vcpf = pf_emp.cepf_vcpf
                    #     cpf = pf_emp.cpf

                    #     if rec.pf_type.cepf_vcpf_percentage > 0:
                    #         cepf_vcpf = cepf_vcpf * (rec.pf_type.cepf_vcpf_percentage / 100)
                            
                    #     if rec.pf_type.cpf_percentage > 0:
                    #         cpf = cpf * (rec.pf_type.cpf_percentage / 100)

                    #     # max_all = pf_emp.cepf_vcpf + pf_emp.cpf
                    #     max_all = cepf_vcpf + cpf

            contract_obj = self.env['hr.contract'].sudo().search([('employee_id', '=', rec.employee_id.id)], limit=1)
            maximum_allowed = contract_obj.updated_basic * rec.pf_type.months
            if rec.pf_type.basic_da_percentage > 0:
                maximum_allowed = maximum_allowed * (rec.pf_type.basic_da_percentage / 100)

            # if max_all < maximum_allowed:
            #     amt = max_all
            # else:
            #     amt = maximum_allowed

            # rec.maximum_withdrawal = amt
            epf_list = [max_all,maximum_allowed]
            if rec.pf_type.epf_limit > 0:
                epf_list.append(rec.pf_type.epf_limit)

            
            if min(epf_list) ==  max_all:
                if rec.pf_type.cepf_vcpf and rec.pf_type.cpf:
                    rec.maximum_withdrawal = min(epf_list) - (rec.pf_type.min_limit * 2)
                elif rec.pf_type.cepf_vcpf or rec.pf_type.cpf:
                    rec.maximum_withdrawal = min(epf_list) - rec.pf_type.min_limit
            else:
                rec.maximum_withdrawal = min(epf_list)

    @api.constrains('emp_cepf_vcpf_bal', 'emp_cpf_bal', 'maximum_withdrawal')
    def check_emp_empr_balance(self):
        for rec in self:
            if rec.emp_cepf_vcpf_bal and rec.emp_cpf_bal and rec.maximum_withdrawal:
                final_amount = min(rec.advance_amount, rec.maximum_withdrawal)
                if final_amount != (rec.emp_cpf_bal + rec.emp_cepf_vcpf_bal):
                    raise ValidationError('Advance amount should be equal to sum of Employee and Employer contribution')

    @api.onchange('pf_type', 'advance_amount', 'maximum_withdrawal')
    def _onchange_pf_type(self):
        for rec in self:
            if rec.advance_amount and rec.pf_type and rec.maximum_withdrawal:
                final_amount = min(rec.advance_amount, rec.maximum_withdrawal)
                rec.emp_cpf_bal, rec.emp_cepf_vcpf_bal = False, False
                if rec.pf_type.cepf_vcpf and rec.pf_type.cpf:
                    if (final_amount * 0.5) <= rec.emp_contrib_bal and \
                                (final_amount * 0.5) <= rec.empr_contrib_bal:
                        rec.emp_cepf_vcpf_bal, rec.emp_cpf_bal = (final_amount * 0.5), (final_amount * 0.5)
                    elif (final_amount * 0.5) > rec.emp_contrib_bal:
                        rec.emp_cepf_vcpf_bal, rec.emp_cpf_bal = rec.emp_contrib_bal, (final_amount - rec.emp_contrib_bal)
                    elif (final_amount * 0.5) > rec.empr_contrib_bal:
                        rec.emp_cpf_bal, rec.emp_cepf_vcpf_bal,  = rec.empr_contrib_bal, (final_amount - rec.empr_contrib_bal)

                elif rec.pf_type.cpf:
                    rec.emp_cpf_bal = min(final_amount, rec.advance_amount)
                elif rec.pf_type.cepf_vcpf:
                    rec.emp_cepf_vcpf_bal = min(final_amount, rec.advance_amount)

    @api.multi
    def button_to_approve(self):
        for rec in self:
            rec.write({'state': 'to_approve'})

    @api.multi
    def button_approved(self):
        for rec in self:
            pf_details_ids = []
            pf_emp = self.env['pf.employee'].sudo().search([('employee_id', '=', rec.employee_id.id)])
            if rec.emp_cepf_vcpf_bal > 0:
                pf_details_ids.append([0, 0, {
                    'employee_id': pf_emp.employee_id.id,
                    'type': 'Withdrawal',
                    'pf_code': 'CEPF + VCPF',
                    'description': rec.pf_type.name,
                    'date': fields.Date.today(),
                    'amount': rec.emp_cepf_vcpf_bal,
                    'reference': rec.name,
                }])

            if rec.emp_cpf_bal > 0:
                pf_details_ids.append([0, 0, {
                    'employee_id': pf_emp.employee_id.id,
                    'type': 'Withdrawal',
                    'pf_code': 'CPF',
                    'description': rec.pf_type.name,
                    'date': fields.Date.today(),
                    'amount': rec.emp_cpf_bal,
                    'reference': rec.name,
                }])

            pf_emp.write({'pf_details_ids': pf_details_ids})
            rec.write({'state': 'approved'})
        return True

    # @api.multi
    # def button_approved(self):
    #     for rec in self:
    #         rec.write({'state': 'approved'})
    #         pf_details_ids = []
    #         pf_balance = self.env['pf.employee'].sudo().search([('employee_id', '=', rec.employee_id.id)],limit=1)
    #         if pf_balance:
    #             for i in pf_balance:
    #                 if (rec.pf_type.cepf_vcpf == True and rec.pf_type.cpf == True) or (rec.pf_type.cepf_vcpf == False and rec.pf_type.cpf == False):
    #                     cepf_balance    = i.cepf_vcpf
    #                     cpf_balance     = i.cpf

    #                     max_balance         = max([cepf_balance,cpf_balance])
    #                     max_balance_code    = 'CPF' if max_balance == cpf_balance else 'CEPF + VCPF'
    #                     min_balance_code    = 'CPF' if max_balance_code == 'CEPF + VCPF' else 'CEPF + VCPF'
    #                     if rec.advance_amount <= max_balance:
    #                         pf_details_ids.append((0, 0, {
    #                             'pf_details_id': i.id,
    #                             'employee_id': i.employee_id.id,
    #                             'type': 'Withdrawal',
    #                             # 'pf_code': 'CPF',
    #                             'pf_code':max_balance_code,
    #                             'description': rec.pf_type.name,
    #                             'date': rec.date,
    #                             # 'amount': rec.advance_amount / 2,
    #                             'amount': rec.advance_amount,
    #                             'reference': rec.name,
    #                         }))
    #                     else:
    #                         pf_details_ids.append((0, 0, {
    #                             'pf_details_id': i.id,
    #                             'employee_id': i.employee_id.id,
    #                             'type': 'Withdrawal',
    #                             # 'pf_code': 'CPF',
    #                             'pf_code':max_balance_code,
    #                             'description': rec.pf_type.name,
    #                             'date': rec.date,
    #                             # 'amount': rec.advance_amount,
    #                             'amount':max_balance,
    #                             'reference': rec.name,
    #                         }))
    #                         pf_details_ids.append((0, 0, {
    #                             'pf_details_id': i.id,
    #                             'employee_id': i.employee_id.id,
    #                             'type': 'Withdrawal',
    #                             # 'pf_code': 'CEPF + VCPF',
    #                             'pf_code':min_balance_code,
    #                             'description': rec.pf_type.name,
    #                             'date': rec.date,
    #                             'amount': rec.advance_amount - max_balance,
    #                             'reference': rec.name,
    #                         }))
    #                 elif rec.pf_type.cepf_vcpf == True and rec.pf_type.cpf == False:
    #                     pf_details_ids.append((0, 0, {
    #                         'pf_details_id': i.id,
    #                         'employee_id': i.employee_id.id,
    #                         'type': 'Withdrawal',
    #                         'pf_code': 'CEPF + VCPF',
    #                         'description': rec.pf_type.name,
    #                         'date': rec.date,
    #                         'amount': rec.advance_amount,
    #                         'reference': rec.name,
    #                     }))
    #                 elif rec.pf_type.cepf_vcpf == False and rec.pf_type.cpf == True:
    #                     pf_details_ids.append((0, 0, {
    #                         'pf_details_id': i.id,
    #                         'employee_id': i.employee_id.id,
    #                         'type': 'Withdrawal',
    #                         'pf_code': 'CPF',
    #                         'description': rec.pf_type.name,
    #                         'date': rec.date,
    #                         'amount': rec.advance_amount,
    #                         'reference': rec.name,
    #                     }))
    #                 print('==========================================', pf_details_ids)
    #                 i.pf_details_ids = pf_details_ids

    @api.multi
    def button_reject(self):
        for rec in self:
            rec.write({'state': 'rejected'})

    @api.multi
    def button_reset_to_draft(self):
        for rec in self:
            rec.write({'state': 'draft'})


    @api.model
    def create(self, vals):
        res =super(PfWidthdrawl, self).create(vals)
        sequence = ''
        seq = self.env['ir.sequence'].next_by_code('pf.widthdrawl')
        sequence = 'PF - ' + str(seq)
        res.name = sequence
        # contract_obj = self.env['hr.contract'].sudo().search([('employee_id', '=', res.employee_id.id)], limit=1)
        # maximum_allowed = contract_obj.updated_basic * res.pf_type.months
        my_emp = self.env['hr.employee'].sudo().search(
            [('id', '=', res.employee_id.id)
             ], limit=1)
        if res.pf_type.min_years < (my_emp.birthday - datetime.now().date()).days:
            raise ValidationError(
                "You are not able to apply as minimum age for PF should be atleast %s" % res.pf_type.min_years)
        if res.advance_amount > res.maximum_withdrawal:
            raise ValidationError("You are not able to take advance amount more than2 %s" % res.maximum_withdrawal)
        pf_count = self.env['pf.widthdrawl'].sudo().search(
            [('employee_id', '=', res.employee_id.id), ('state', 'not in', ('approved','rejected')), ('id', '!=', res.id),
             ])
        if pf_count:
            raise ValidationError(_("You already have a PF request in a pending request,\
                                        either cancel or process that request"))
        if res.pf_type.avail_once:
            pf = self.env['pf.widthdrawl'].sudo().search([('employee_id', '=', res.employee_id.id),
                                                            ('state', '!=', 'rejected'),
                                                            ('pf_type', '=', res.pf_type.id)]) - res
            if pf:
                raise ValidationError(_("You already have a PF request with this withdrawl type,\
                                            which can be availed once in a lifetime."))
        return res

    @api.multi
    @api.depends('name')
    def name_get(self):
        res = []
        for record in self:
            if record.name:
                name = record.name
            else:
                name = 'PF'
            res.append((record.id, name))
        return res

    @api.multi
    def unlink(self):
        for pf in self:
            if pf.state not in ('draft'):
                raise UserError(
                    'You cannot delete a PF which is not in draft or cancelled state')
        return super(PfWidthdrawl, self).unlink()



    @api.constrains('employee_id')
    @api.onchange('employee_id')
    def onchange_basic_details(self):
        for res in self:
            rec = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)], limit=1)
            rec.designation = rec.job_id.id
            rec.bank_account_number = rec.bank_account_number
            rec.center = rec.work_location
            rec.branch_id = rec.branch_id.id
            rec.department_id = rec.department_id.id
            

    @api.depends('employee_id')
    def _compute_present_pay(self):
        for rec in self:
            contract_obj = self.env['hr.contract'].sudo().search([('employee_id', '=', rec.employee_id.id), 
                                                                    ('state', '=', 'open')], limit=1)
            if contract_obj:
                for contract in contract_obj:
                    rec.present_pay = contract.updated_basic

    @api.constrains('advance_amount')
    @api.onchange('advance_amount')
    def _onchange_advance_amount(self):
        for rec in self:
            max_balance = self.env['pf.employee'].sudo().search([('employee_id', '=', rec.employee_id.id)], limit=1)
            if max_balance:
                for empbal in max_balance:
                    print('================', empbal,empbal.amount)
                    if rec.pf_type.cepf_vcpf == True and rec.pf_type.cpf == False:
                        if rec.advance_amount > empbal.cepf_vcpf:
                            raise ValidationError("You are not able to take advance amount more than %s"%empbal.cepf_vcpf +"/-")
                    if rec.pf_type.cepf_vcpf == False and rec.pf_type.cpf == True:
                        if rec.advance_amount > empbal.cpf:
                            raise ValidationError("You are not able to take advance amount more than %s"%empbal.cpf +"/-")
                    if rec.pf_type.cepf_vcpf == True and rec.pf_type.cpf == True:
                        if rec.advance_amount > empbal.advance_left:
                            raise ValidationError("You are not able to take advance amount more than %s"%empbal.advance_left +"/-")
                    if rec.pf_type.min_years:
                        if empbal.pf_start_data :
                            if rec.date <= (empbal.pf_start_data + relativedelta(years=rec.pf_type.min_years)):
                                raise ValidationError(f"You are not able to withdraw PF before\
                                                    {empbal.pf_start_data + relativedelta(years=rec.pf_type.min_years)}")
                        else:
                            if rec.date <= (rec.employee_id.date_of_join + relativedelta(years=rec.pf_type.min_years)):
                                raise ValidationError(f"You are not able to withdraw PF before\
                                                    {rec.employee_id.date_of_join + relativedelta(years=rec.pf_type.min_years)}")

                  



class PfEmployee(models.Model):
    _name = "pf.employee"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "PF Employee"
    _rec_name = 'employee_id'

    def _default_employee(self):
        return self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)], limit=1)

    @api.multi
    def _balance_ason_label(self):
        apr_dt = date(date.today().year, 4, 1)
        string = f"Balance as on {apr_dt.strftime('%d-%B-%Y')}"
        for rec in self:
            rec.balance_ason_label = string
    
    def _compute_check_approver(self):
        for rec in self:
            if self.env.user.has_group('pf_withdrawl.group_pf_withdraw_approver'):
                rec.check_approver = True
            if rec.employee_id:
                rec.eps_deduct = rec.employee_id.eps_deduct  

    pf_start_data = fields.Date('PF Start Date',track_visibility='always')
    employee_id=fields.Many2one('hr.employee', string="Employee", default=_default_employee,track_visibility='always')
    branch_id = fields.Many2one('res.branch',string="Center",track_visibility='onchange')
    advance_amount = fields.Float('Withdrawal Amount', compute='_compute_amount', track_visibility='always')
    advance_left = fields.Float('Balance', compute='_compute_amount',track_visibility='always')
    amount = fields.Float('Amount', compute='_compute_amount',track_visibility='always')
    cepf_vcpf = fields.Float('MPF + VPF', compute='_compute_amount',track_visibility='always')
    cpf = fields.Float('EPF', compute='_compute_amount',track_visibility='always')
    pf_details_ids=fields.One2many('pf.employee.details', 'pf_details_id',track_visibility='always')
    currency_id = fields.Many2one('res.currency', string='Currency',
                              default=lambda self: self.env.user.company_id.currency_id)
    eps_deduct = fields.Boolean('EPS Deduction', compute='_compute_check_approver')
    check_approver = fields.Boolean('Check Approver', compute='_compute_check_approver')
    is_closed = fields.Boolean('Closed', default=False)
    closed_on = fields.Date('Closed On')

    # Compute fields for PF Report
    balance_ason_label = fields.Char('balance_ason', compute='_balance_ason_label')
    pf_number = fields.Char('PF Number', related='employee_id.pf_number')


    @api.multi
    def _current_fy(self):
        curr_date = date.today()
        dateRangeObj = self.env['date.range'].sudo().search([('type_id.name', '=', 'Fiscal Year'),
                                                                ('date_start', '<=', curr_date),
                                                                ('date_end', '>=', curr_date)])
        if not dateRangeObj:
            raise ValidationError('Please set date range for current financial year')
        return dateRangeObj

    @api.multi
    def _fy_months(self):
        apr_dt = date(date.today().year, 4, 1)
        list_fy = [(apr_dt + relativedelta(months=x)).strftime('%B')
                                                for x in range(0, 12)]
        return list_fy

    @api.multi
    def calc_opening_bal(self, code):
        pass
        # for rec in self:
        #     result = 0
        #     if code == 'CEPF':
        #         result = sum(rec.pf_details_ids.filtered(lambda x: x.type == 'Deposit' and x.pf_code == 'CEPF'
        #                                                      and x.date <= date(date.today().year, 4, 1)).mapped('amount'))
        #     elif code == 


    @api.constrains('employee_id')
    @api.onchange('employee_id')
    def onchange_basic_detailsss(self):
        for rec in self:
            rec.branch_id = rec.employee_id.branch_id.id

    @api.multi
    def button_transfer_pf(self):
        pass


    @api.depends('pf_details_ids')
    def _compute_amount(self):
        for rec in self:
            # Start : added on 7 june 2021 (Gouranga kala)
            cepf_deposit    = sum(rec.pf_details_ids.filtered(lambda r:r.type == 'Deposit' and r.pf_code in ['CEPF + VCPF','VCPF','CEPF']).mapped('amount'))
            cepf_withdraw   = sum(rec.pf_details_ids.filtered(lambda r:r.type == 'Withdrawal' and r.pf_code in ['CEPF + VCPF','VCPF','CEPF']).mapped('amount'))

            cpf_deposit     = sum(rec.pf_details_ids.filtered(lambda r:r.type == 'Deposit' and r.pf_code == 'CPF').mapped('amount'))
            cpf_withdraw    = sum(rec.pf_details_ids.filtered(lambda r:r.type == 'Withdrawal' and r.pf_code == 'CPF').mapped('amount'))

            total_deposit   = cepf_deposit + cpf_deposit
            total_withdraw  = cepf_withdraw + cpf_withdraw

            rec.cepf_vcpf   = cepf_deposit - cepf_withdraw
            rec.cpf         = cpf_deposit - cpf_withdraw

            rec.amount      = total_deposit

            rec.advance_amount  = total_withdraw
            rec.advance_left    = total_deposit - total_withdraw
            # print('-------=======', total_deposit)
            # End : added on 7 june 2021 (Gouranga kala)

            # sum = 0.00
            # sum1 = 0.00
            # cv = 0.00
            # cpf = 0.00
            # advance_amount = 0.00
            # for details in rec.pf_details_ids:
            #     sum += details.amount
            #     if details.pf_code == 'CEPF + VCPF' or details.pf_code == 'VCPF' or details.pf_code == 'CEPF':
            #         if details.type == 'Deposit':
            #             cv += details.amount
            #         elif details.type == 'Withdrawal':
            #             cv -= details.amount
            #     if details.pf_code == 'CPF':
            #         if details.type == 'Deposit':
            #             cpf += details.amount
            #         elif details.type == 'Withdrawal':
            #             cpf -= details.amount
            # rec.cepf_vcpf = cv
            # rec.cpf = cpf
            # print("CV and CPF",cv,cpf)
            # print("DATA IS",rec.cepf_vcpf,rec.cpf)
            # pf_advance = self.env['pf.widthdrawl'].sudo().search(
            #     [('employee_id', '=', rec.employee_id.id),
            #      ('state', '=', 'approved')], limit=1)
            # for ad in pf_advance:
            #     sum1 += ad.advance_amount
            # rec.amount = sum
            # # rec.advance_amount = sum1
            # rec.advance_left = rec.amount - rec.advance_amount
            # for lines in rec.pf_details_ids:
            #     if lines.type == 'Withdrawal':
            #         advance_amount += lines.amount
            # rec.advance_amount = advance_amount


    @api.model
    def create(self, vals):
        res =super(PfEmployee, self).create(vals)
        pf_count = self.env['pf.employee'].sudo().search(
            [('employee_id', '=', res.employee_id.id), ('id', '!=', res.id),
             ])
        if pf_count:
            raise ValidationError(_("You already have a PF Employee creadted"))
        return res


    @api.multi
    def get_pf_details(self):
        pf_details_ids = []
        for rec in self:
            advance_amount = 0.00
            rec.pf_details_ids.unlink()
            if rec.employee_id:
                pay_rules = self.env['hr.payslip.line'].sudo().search(
                    [('slip_id.employee_id', '=', rec.employee_id.id),
                     ('slip_id.state', '=', 'done'),
                     ('salary_rule_id.pf_register', '=', True),
                     ])
                if pay_rules:
                    for i in pay_rules:
                        pf_details_ids.append((0, 0, {
                            'pf_details_id': rec.id,
                            'employee_id': rec.employee_id.id,
                            'type': 'Deposit',
                            'pf_code': i.code,
                            'description': i.name,
                            'date': datetime.now().date(),
                            'amount': i.total,
                            'reference': i.slip_id.number,
                        }))
                pf_advance = self.env['pf.widthdrawl'].sudo().search(
                    [('employee_id', '=', rec.employee_id.id),
                     ('state', '=', 'approved')])
                if pf_advance:
                    for i in pf_advance:
                        pf_details_ids.append((0, 0, {
                            'pf_details_id': rec.id,
                            'employee_id': rec.employee_id.id,
                            'type': 'Withdrawal',
                            'pf_code': i.pf_type.name,
                            'description': ' ',
                            'date': i.date,
                            'amount': i.advance_amount,
                            'reference': i.name,
                        }))
                rec.pf_details_ids = pf_details_ids
                for lines in rec.pf_details_ids:
                    if lines.type == 'Withdrawal':
                        advance_amount += lines.amount
                rec.advance_amount = advance_amount


class PfEmployeeDetails(models.Model):
    _name = "pf.employee.details"
    _description = "PF Employee Details"


    pf_details_id = fields.Many2one('pf.employee')
    employee_id=fields.Many2one('hr.employee', string="Employee")
    date = fields.Date('Date')
    type = fields.Selection([
                            ('Deposit', 'Deposit'),
                            ('Withdrawal', 'Withdrawal'),
                            ], string="Type")
    # pf_code = fields.Char(string='PF code')
    pf_code = fields.Selection([('CEPF', 'MPF'), ('VCPF', 'VPF'),
                                ('CPF', 'EPF'), ('CEPF + VCPF', 'MPF + VPF')], string='PF Code')
    description = fields.Char(string='Description')
    amount = fields.Float('Amount')
    reference = fields.Char('Reference')

class AbcAb(models.Model):
    _name = "abc.ab"
    _description = "abc ab"

    name=fields.Binary(string="Upload File")
