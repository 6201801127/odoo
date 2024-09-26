from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.exceptions import ValidationError,UserError
from odoo.tools.safe_eval import safe_eval
from odoo.http import request

class AccountMoveInherit(models.Model):
    _name = 'account.move'
    _inherit = ['account.move','portal.mixin', 'mail.thread', 'mail.activity.mixin']

    branch_id = fields.Many2one('accounting.branch.unit', 'Branch',states={'draft': [('readonly', False)]},required=True,track_visibility='onchange')
    state = fields.Selection([('draft', 'Unposted'), ('posted', 'Posted')],
                             string='Status',
                             required=True, readonly=True, copy=False, default='draft',
                             help='All manually created new journal entries are usually in the status \'Unposted\', '
                                  'but you can set the option to skip that status on the related journal. '
                                  'In that case, they will behave as journal entries automatically created by the '
                                  'system on document validation (invoices, bank statements...) and will be created '
                                  'in \'Posted\' status.',track_visibility='onchange')
    exchange_rate = fields.Float('Exchange Rate',track_visibility='onchange')
    company_currency_id = fields.Many2one('res.currency', 'Company Currency',default=lambda self: self.env.user.company_id.currency_id,track_visibility='onchange')
    is_foreign_currency = fields.Boolean('Is Foreign Currency', default=False)
    csm_acc_conf = fields.Boolean('csm account conf', compute="compute_csm_config")
    is_payment_receipt = fields.Boolean(compute='compute_csm_config', default=False)
    ref = fields.Char(string='Description', copy=False)
    move_type = fields.Selection([('receipt','Receipt'),('payment','Payment'),('contra','Contra'),('general','General')],string="Move Type", states={'draft': [('readonly', False)]})
    mode_of_payment = fields.Many2one('account.payment.method',string="Mode of Payment")
    particulars = fields.Char(string="Particulars",compute="_get_particulars")
    tds_applicable = fields.Selection([('Draft','Draft'),('payable','payable'),('receivable','Receivable')],string="TDS", states={'draft': [('readonly', False)]})
    tds_line_ids = fields.One2many('account.tds.line', 'move_id', string='TDS Lines',
        readonly=True, states={'draft': [('readonly', False)]}, copy=True,track_visibility='onchange')
    narration = fields.Text(string='Narration', states={'draft': [('readonly', False)]},track_visibility='onchange')
    cheque_date = fields.Date(string="Cheque Date", autocomplete="off")
    cheque_reference = fields.Char(string="Cheque Reference", autocomplete="off")
    payment_method_type = fields.Selection([('Draft','Draft'),('NEFT','NEFT'),('RTGS','RTGS'),('Cheque','Cheque')],string="Payment Method")
    sync_status = fields.Integer("Sync Status")
    kw_voucher_no = fields.Char("Tendrils Voucher No.")
    current_financial_year = fields.Boolean("Current Financial Year",compute='_compute_current_financial_year',search="_register_search_current_financial_year")
    last_updated_user_id = fields.Many2one('res.users',string="Last Updated By",track_visibility='always')
    last_update_date = fields.Datetime(string="Last Updated Date",track_visibility='always',)
    posted_user_id = fields.Many2one('res.users',string="Posted By",track_visibility='always',)
    posted_date = fields.Datetime(string="Posted Date",track_visibility='always',)
    
    currency_id = fields.Many2one('res.currency', compute='_compute_currency', store=True, string="Currency",)
    line_ids = fields.One2many('account.move.line', 'move_id', string='Journal Items',states={'posted': [('readonly', True)]}, copy=True,track_visibility='always')
    amount = fields.Monetary(compute='_amount_compute', store=True,track_visibility='onchange')
    # Dummy Account field to search on account.move by account_id
    date = fields.Date(required=True, states={'posted': [('readonly', True)]}, index=True, default=fields.Date.context_today,copy=False)

    @api.multi
    def unlink(self):
        print(self.name)
        if self.name != '/':
            raise ValidationError("Deletion is not allowed.")
        self.mapped('line_ids').unlink()
        return super(AccountMoveInherit, self).unlink()
    
    @api.onchange('partner_id')
    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        self.line_ids._onchange_branch_id()

    @api.multi
    def preview_moves(self):
        self.ensure_one()
        request.session['move_id'] = self.id
        view_id = self.env.ref('kw_accounting.preview_move_form1').id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Preview Voucher'),
            'view_mode': 'form',
            'res_model': 'account.move',
            'target': 'new',
            'res_id': self.id,
            'views': [[view_id, 'form']],
        }

    @api.model
    def preview_vouchers(self,**args):
        move_id = args.get('voucher_id',False)
        request.session['move_id'] = int(move_id)
        view_id = self.env.ref('kw_accounting.preview_move_form1').id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Preview Voucher'),
            'view_mode': 'form',
            'res_model': 'account.move',
            'target': 'new',
            'res_id': int(move_id),
            'views': [[view_id, 'form']],
        }

    @api.multi
    def print_voucher(self):
        return self.env.ref('kw_accounting.account_print_vouchers').report_action(self)

    @api.multi
    def _compute_current_financial_year(self):
        for record in self:
            pass
        
    @api.multi
    def _register_search_current_financial_year(self, operator, value):
        start_date , end_date = self.env['hr.leave'].lv_get_current_financial_dates()
        domain = [('date', '>=', start_date),('date', '<=', end_date)]
        return domain
        
    @api.constrains('line_ids','tds_line_ids')
    def tds_value_match(self):
        for rec in self:
            tds_invoice_line_amount = sum(line.debit for line in rec.line_ids if line.account_id.tds == True) + sum(line.credit for line in rec.line_ids if line.account_id.tds == True)
            tds_line_amount = sum(line.ds_amount for line in rec.tds_line_ids)

            if tds_invoice_line_amount != tds_line_amount and rec.tds_applicable != False:
                raise ValidationError("TDS Amount is mismatched")
            
    @api.onchange('line_ids.account_id')
    @api.multi
    def _get_particulars(self):
        for rec in self:
            account_ids = rec.line_ids.mapped('account_id')
            account_name = account_ids.mapped('name')
            rec.particulars = ', '.join(account_name)

    @api.multi
    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.multi
    def post(self, invoice=False):
        self._post_validate()
        posted_data = {}
        # Create the analytic lines in batch is faster as it leads to less cache invalidation.
        self.mapped('line_ids').create_analytic_lines()
        for move in self:
            if move.name == '/':
                new_name = False
                journal = move.journal_id

                if invoice and invoice.move_name and invoice.move_name != '/':
                    new_name = invoice.move_name
                else:
                    if journal.sequence_id:
                        # If invoice is actually refund and journal has a refund_sequence then use that one or use the regular one
                        sequence = journal.sequence_id
                        if invoice and invoice.type in ['out_refund', 'in_refund'] and journal.refund_sequence:
                            if not journal.refund_sequence_id:
                                raise UserError(_('Please define a sequence for the credit notes'))
                            sequence = journal.refund_sequence_id

                        new_name = sequence.with_context(ir_sequence_date=move.date).next_by_id()
                    else:
                        raise UserError(_('Please define a sequence on the journal.'))

                if new_name:
                    move.name = new_name

            if move == move.company_id.account_opening_move_id and not move.company_id.account_bank_reconciliation_start:
                # For opening moves, we set the reconciliation date threshold
                # to the move's date if it wasn't already set (we don't want
                # to have to reconcile all the older payments -made before
                # installing Accounting- with bank statements)
                move.company_id.account_bank_reconciliation_start = move.date

            for r in move.line_ids:
                    r.clear_date = move.date
            if not move.posted_user_id:
                posted_data['posted_user_id']=  move.env.user.id
                posted_data['posted_date']=datetime.today()
                posted_data['state']= 'posted'
            else:
                posted_data['state']= 'posted'
        return self.write(posted_data)
    
    @api.multi
    def action_post(self):
        for rec in self:
            if rec.is_payment_receipt:
                for r in rec.line_ids:
                    r.clear_date = rec.date
                    if r.invoice_id:
                        r.invoice_id.assign_outstanding_credit(r.id)
        res = super().action_post()
        return res

    @api.depends('date')
    def compute_csm_config(self):
        for rec in self:
            enable_csm_account_conf_status = self.env['ir.config_parameter'].sudo().get_param(
                'kw_accounting.enable_csm_account_conf_status')
            rec.csm_acc_conf = enable_csm_account_conf_status
            if self._context.get('search_default_receipt_filter') or self._context.get('search_default_payment_filter'):
                rec.is_payment_receipt = True

    @api.onchange('exchange_rate')
    def _onchange_exchange_rate(self):
        currency_rate_obj = self.env['res.currency.rate'].sudo()
        for invoice in self:
            if (invoice.currency_id.id != invoice.company_currency_id.id) and invoice.exchange_rate > 0:
                currency_obj = currency_rate_obj.search(
                    [('name', '=', date.today()), ('currency_id', '=', invoice.currency_id.id)])
                delete_query = f'delete from res_currency_rate where currency_id = {invoice.currency_id.id}'
                self.env.cr.execute(delete_query)
                currency_rate_obj.create({
                    'name': date.today(), 'rate': 1 / invoice.exchange_rate, 'currency_id': invoice.currency_id.id})

    @api.multi
    def write(self, vals):
        if self.posted_user_id and 'line_ids' in vals:
            vals['last_updated_user_id'] = self.env.user.id,
            vals['last_update_date'] = datetime.today()
            
        res = super(AccountMoveInherit, self).write(vals)        
        return res

    # @api.model
    # def default_get(self, default_fields):
    #     res = super().default_get(default_fields)
    #     journal_obj = self.env['account.journal'].sudo()
    #     if self._context.get('search_default_receipt_filter'):
    #         res['journal_id'] = journal_obj.search([('code', 'in', ['BNK','CSH'])]).id
    #     if self._context.get('search_default_payment_filter'):
    #         res['journal_id'] = journal_obj.search([('code', 'in', ['BNK','CSH'])]).id
    #     if self._context.get('search_default_general_journal_filter'):
    #         res['journal_id'] = journal_obj.search([('code', '=', 'GJ')]).id
    #     if self._context.get('search_default_contra_filter'):
    #         res['journal_id'] = journal_obj.search([('code', '=', 'CV')]).id
    #     return res
    @api.onchange('move_type')
    def get_journals(self):
        for move in self:
            if move.move_type == 'contra':
                return {'domain': {'journal_id': [('code', '=','CV')]}}
            if move.move_type == 'payment':
                return {'domain': {'journal_id': [('code', 'in',['PVBNK','PVCSH'])]}}
            if move.move_type == 'receipt' :
                return {'domain': {'journal_id': [('code', 'in',['RVBNK','RVCSH'])]}}
            if move.move_type == 'general':
                return {'domain': {'journal_id': [('code', '=','MISC')]}}
            
    @api.multi
    def _get_report_base_filename(self):
        self.ensure_one()
        return  self.move_type == 'contra' and self.state == 'draft' and _('Contra Voucher') or \
                self.move_type == 'contra' and self.state in ('posted') and _('Contra Voucher - %s') % (self.name) or \
                self.move_type == 'payment' and self.state == 'draft' and _('Payment Voucher') or \
                self.move_type == 'payment' and self.state in ('posted') and _('Payment Voucher - %s') % (self.name) or \
                self.move_type == 'receipt' and self.state == 'draft' and _('Receipt Voucher') or \
                self.move_type == 'receipt' and self.state in ('posted') and _('Receipt Voucher - %s') % (self.name) or \
                self.move_type == 'general' and self.state == 'draft' and _('General Voucher') or \
                self.move_type == 'general' and self.state in ('posted') and _('General Voucher - %s') % (self.name)
                
    @api.onchange('currency_id')
    def onchange_currency(self):
        for rec in self:
            if rec.currency_id.id != rec.company_currency_id.id:
                rec.is_foreign_currency = True

    # def apply_journal(self):
    #     for rec in self:
    #         rec.write({'state': 'to_approve'})
    #     return True

    def receipt_voucher_action(self):
        company_id,branch_id,fy_id = self.env['account.invoice'].get_session_details()
        tree_view_id = self.env.ref('account.view_move_tree').id
        form_view_id = self.env.ref('account.view_move_form').id
        action = {'type': 'ir.actions.act_window',
                'name': 'Receipt Voucher',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,kanban,form,calendar,pivot,graph,activity',
                'res_model': 'account.move',
                'domain': [('state','not in',['draft']),('company_id','=',int(company_id)),('branch_id','=',int(branch_id)),('date','>=',fy_id.date_start),('date','<=',fy_id.date_stop)],
                'context': {'search_default_receipt_filter':1,'default_move_type':'receipt','default_company_id': int(company_id),'default_branch_id':int(branch_id),'create':0,'edit':0,'import':0},
                }
        return action

    def payment_voucher_action(self):
        company_id,branch_id,fy_id = self.env['account.invoice'].get_session_details()
        tree_view_id = self.env.ref('account.view_move_tree').id
        form_view_id = self.env.ref('account.view_move_form').id
        action = {'type': 'ir.actions.act_window',
                'name': 'Payment Voucher',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,kanban,form,calendar,pivot,graph,activity',
                'res_model': 'account.move',
                'domain': [('state','not in',['draft']),('company_id','=',int(company_id)),('branch_id','=',int(branch_id)),('date','>=',fy_id.date_start),('date','<=',fy_id.date_stop)],
                'context': {'search_default_payment_filter':1,'default_move_type':'payment','default_company_id': int(company_id),'default_branch_id':int(branch_id),'create':0,'edit':0,'import':0},
                }
        return action

    def general_voucher_action(self):
        company_id,branch_id,fy_id = self.env['account.invoice'].get_session_details()
        tree_view_id = self.env.ref('account.view_move_tree').id
        form_view_id = self.env.ref('account.view_move_form').id
        action = {'type': 'ir.actions.act_window',
                'name': 'General Voucher',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,kanban,form,calendar,pivot,graph,activity',
                'res_model': 'account.move',
                'domain': [('state','not in',['draft']),('company_id','=',int(company_id)),('branch_id','=',int(branch_id)),('date','>=',fy_id.date_start),('date','<=',fy_id.date_stop)],
                'context': {'search_default_general_journal_filter':1,'default_move_type':'general','default_company_id': int(company_id),'default_branch_id':int(branch_id),'create':0,'edit':0,'import':0},
                }
        return action

    def contra_voucher_action(self):
        company_id,branch_id,fy_id = self.env['account.invoice'].get_session_details()
        tree_view_id = self.env.ref('account.view_move_tree').id
        form_view_id = self.env.ref('account.view_move_form').id
        action = {'type': 'ir.actions.act_window',
                'name': 'Contra Voucher',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,kanban,form,calendar,pivot,graph,activity',
                'res_model': 'account.move',
                'domain': [('state','not in',['draft']),('company_id','=',int(company_id)),('branch_id','=',int(branch_id)),('date','>=',fy_id.date_start),('date','<=',fy_id.date_stop)],
                'context': {'search_default_contra_filter':1,'default_move_type':'receipt','default_company_id': int(company_id),'default_branch_id':int(branch_id),'create':0,'edit':0,'import':0},
                }
        return action

    
    def draft_receipt_voucher_action(self):
        company_id,branch_id,fy_id = self.env['account.invoice'].get_session_details()
        tree_view_id = self.env.ref('account.view_move_tree').id
        form_view_id = self.env.ref('account.view_move_form').id
        action = {'type': 'ir.actions.act_window',
                'name': 'Receipt Voucher',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,kanban,form,calendar,pivot,graph,activity',
                'res_model': 'account.move',
                'domain': [('state','=','draft'),('company_id','=',int(company_id)),('branch_id','=',int(branch_id)),('date','>=',fy_id.date_start),('date','<=',fy_id.date_stop)],
                'context': {'search_default_receipt_filter':1,'default_move_type':'receipt','default_company_id': int(company_id),'default_branch_id':int(branch_id)},
                }
        return action

    def draft_payment_voucher_action(self):
        company_id,branch_id,fy_id = self.env['account.invoice'].get_session_details()
        tree_view_id = self.env.ref('account.view_move_tree').id
        form_view_id = self.env.ref('account.view_move_form').id
        action = {'type': 'ir.actions.act_window',
                'name': 'Payment Voucher',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,kanban,form,calendar,pivot,graph,activity',
                'res_model': 'account.move',
                'domain': [('state','=','draft'),('company_id','=',int(company_id)),('branch_id','=',int(branch_id)),('date','>=',fy_id.date_start),('date','<=',fy_id.date_stop)],
                'context': {'search_default_payment_filter':1,'default_move_type':'payment','default_company_id': int(company_id),'default_branch_id':int(branch_id)},
                }
        return action

    def draft_general_voucher_action(self):
        company_id,branch_id,fy_id = self.env['account.invoice'].get_session_details()
        tree_view_id = self.env.ref('account.view_move_tree').id
        form_view_id = self.env.ref('account.view_move_form').id
        action = {'type': 'ir.actions.act_window',
                'name': 'General Voucher',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,kanban,form,calendar,pivot,graph,activity',
                'res_model': 'account.move',
                'domain': [('state','=','draft'),('company_id','=',int(company_id)),('branch_id','=',int(branch_id)),('date','>=',fy_id.date_start),('date','<=',fy_id.date_stop)],
                'context': {'search_default_general_journal_filter':1,'default_move_type':'general','default_company_id': int(company_id),'default_branch_id':int(branch_id)},
                }
        return action

    def draft_contra_voucher_action(self):
        company_id,branch_id,fy_id = self.env['account.invoice'].get_session_details()
        tree_view_id = self.env.ref('account.view_move_tree').id
        form_view_id = self.env.ref('account.view_move_form').id
        action = {'type': 'ir.actions.act_window',
                'name': 'Contra Voucher',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,kanban,form,calendar,pivot,graph,activity',
                'res_model': 'account.move',
                'domain': [('state','=','draft'),('company_id','=',int(company_id)),('branch_id','=',int(branch_id)),('date','>=',fy_id.date_start),('date','<=',fy_id.date_stop)],
                'context': {'search_default_contra_filter':1,'default_move_type':'contra','default_company_id': int(company_id),'default_branch_id':int(branch_id)},
                }
        return action

    @api.constrains('line_ids')
    def _check_amount_greater_than_zero(self):
        for record in self:
            if sum(record.line_ids.mapped('debit'))  == sum(record.line_ids.mapped('credit')) == 0:
                raise ValidationError('Amount should be greater than zero!')

    @api.multi
    def reverse_moves(self, date=None, journal_id=None, auto=False):
        date = date or fields.Date.today()
        reversed_moves = self.env['account.move']
        for ac_move in self:
            #unreconcile all lines reversed
            aml = ac_move.line_ids.filtered(lambda x: x.account_id.reconcile or x.account_id.internal_type == 'liquidity')
            aml.remove_move_reconcile()
            reversed_move = ac_move._reverse_move(date=date,
                                                  journal_id=journal_id,
                                                  auto=auto)
            reversed_moves |= reversed_move
            #reconcile together the reconcilable (or the liquidity aml) and their newly created counterpart
            for account in set([x.account_id for x in aml]):
                to_rec = aml.filtered(lambda y: y.account_id == account)
                to_rec |= reversed_move.line_ids.filtered(lambda y: y.account_id == account)
                #reconciliation will be full, so speed up the computation by using skip_full_reconcile_check in the context
                to_rec.reconcile()
        if reversed_moves:
            return [x.id for x in reversed_moves]
        return []

    @api.onchange('date')
    def _onchange_date(self):
        '''On the form view, a change on the date will trigger onchange() on account.move
        but not on account.move.line even the date field is related to account.move.
        Then, trigger the _onchange_amount_currency manually.
        '''
        pass
        
class AccountMoveLineInherit(models.Model):
    _name = "account.move.line"
    _inherit = ['account.move.line']
    _order = "date desc, id asc"

    def get_row(self):
        count=0
        for record in self:
            record.sl_no = count + 1
            count = count + 1

    department_id = fields.Many2one('hr.department', 'Department', domain=[('dept_type.code', '=', 'department')])
    division_id = fields.Many2one('hr.department', 'Division')
    section_id = fields.Many2one('hr.department', 'Section')
    employee_id = fields.Many2one('hr.employee', 'Employee',domain=['|', ('active', '=', False), ('active', '=', True)])
    sl_no=fields.Integer("SL#",compute="get_row")
    
    # group_id = fields.Many2one('account.group', 'Group', domain="[('account_type_id.code','=', 'gn')]")
    # account_head_id = fields.Many2one('account.group', 'Account Head', domain="[('account_type_id.code','=', 'ah')]")
    # account_subhead_id = fields.Many2one('account.group', 'Account Sub-Head',
    #                                      domain="[('account_type_id.code','=', 'ash')]")
    is_payment_receipt = fields.Boolean()
    is_budget_mandatory = fields.Boolean(related='account_id.is_budget_mandatory')
    invoice_id = fields.Many2one('account.invoice', 'Invoice')
    product_category = fields.Selection([('product','Goods'),('service','Service')],string="Category")
    clear_date = fields.Date(string="Clear Date")
    branch_id = fields.Many2one('accounting.branch.unit', related='move_id.branch_id', string='Branch', store=True, readonly=True)
    tds_applicable = fields.Boolean(string="TDS",related="account_id.tds")
    budget_type = fields.Selection([('treasury','Treasury'),('project','Project'),('capital','Capital'),('other','Other')],string="Budget Type",default="other")
    cheque_date = fields.Date(related="move_id.cheque_date",string="Cheque Date", autocomplete="off")
    cheque_reference = fields.Char(related="move_id.cheque_reference",string="Cheque Reference", autocomplete="off")
    payment_method_type = fields.Selection(related="move_id.payment_method_type",string="Payment Method")
    narration = fields.Text("Narration",required=True)
    particulars = fields.Char(related="move_id.particulars")
    move_type =  fields.Selection(related="move_id.move_type",string="Type")
    project_id = fields.Many2one('kw_sales_workorder_master',string="Project")
    update_capital_budget = fields.Boolean(related="account_id.user_type_id.budget_update")
    budget_update = fields.Boolean(string="Capital Budget Update")
    ledger_name = fields.Char(related="account_id.name",string="Ledger Name")
    ledger_code = fields.Char(related="account_id.code",string="Ledger Code")

    debit = fields.Monetary(default=0.0, currency_field='company_currency_id',track_visibility="always")
    credit = fields.Monetary(default=0.0, currency_field='company_currency_id',track_visibility="always")
    balance = fields.Monetary(compute='_store_balance', store=True, currency_field='company_currency_id',help="Technical field holding the debit - credit in order to open meaningful graph views from reports",track_visibility="always")
    debit_cash_basis = fields.Monetary(currency_field='company_currency_id', compute='_compute_cash_basis', store=True,track_visibility="always")
    credit_cash_basis = fields.Monetary(currency_field='company_currency_id', compute='_compute_cash_basis', store=True,track_visibility="always")
    balance_cash_basis = fields.Monetary(compute='_compute_cash_basis', store=True, currency_field='company_currency_id',help="Technical field holding the debit_cash_basis - credit_cash_basis in order to open meaningful graph views from reports",track_visibility="always")
    amount_currency = fields.Monetary(default=0.0, help="The amount expressed in an optional other currency if it is a multi-currency entry.",track_visibility="always")
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True,help='Utility field to express amount currency', store=True,track_visibility="always")
    amount_residual = fields.Monetary(compute='_amount_residual', string='Residual Amount', store=True, currency_field='company_currency_id',help="The residual amount on a journal item expressed in the company currency.",track_visibility="always")
    amount_residual_currency = fields.Monetary(compute='_amount_residual', string='Residual Amount in Currency', store=True,help="The residual amount on a journal item expressed in its currency (possibly not the company currency).",track_visibility="always")
    tax_base_amount = fields.Monetary(string="Base Amount", compute='_compute_tax_base_amount', currency_field='company_currency_id', store=True,track_visibility="always")
    account_id = fields.Many2one('account.account', string='Account', required=True, index=True,ondelete='restrict', domain=[('deprecated', '=', False)], default=lambda self: self._context.get('account_id', False),track_visibility="always")
    purchase_order_id = fields.Many2one('purchase.order',string="Po. No.")
    options = fields.Selection([('outstanding','Outstanding'),('adv_against_po','Adv. Ag. Po.'),('adv_non_po','Adv. Non Po.')],string="Options")
    
    @api.onchange('partner_id','invoice_id')
    def get_purchase_order(self):
        self.account_id = self.partner_id.property_account_payable_id.id if self.partner_id.supplier == True else self.partner_id.property_account_receivable_id.id
        if self.invoice_id.purchase_order_id:
            self.purchase_order_id = self.invoice_id.purchase_order_id.id
        else:
            return {'domain': {'purchase_order_id': [('partner_id', '=',self.partner_id.id),('state','=','purchase')]}}

    @api.multi
    def open_voucher(self):
        for record in self:
            if record.move_id.move_type in ['contra','general','payment','receipt']:
                form_view_id = self.env.ref('account.view_move_form').id
                return {
                    'type': 'ir.actions.act_window',
                    'views': [(form_view_id, 'form')],
                    'view_mode': 'form',
                    'res_model': 'account.move',
                    'res_id': record.move_id.id,
                }
            else:
                invoice_id = self.env['account.invoice'].search([('move_id','=',record.move_id.id)],limit=1)
                if invoice_id:
                    if invoice_id.type in ('out_invoice','out_refund'):
                        form_view_id = self.env.ref('account.invoice_form').id
                    else:
                        form_view_id = self.env.ref('account.invoice_supplier_form').id
                    return {
                        'type': 'ir.actions.act_window',
                        'views': [(form_view_id, 'form')],
                        'view_mode': 'form',
                        'res_model': 'account.invoice',
                        'res_id': invoice_id.id,
                    }
   
    @api.multi
    def print_voucher(self):
        return self.env.ref('kw_accounting.brs_print_vouchers').report_action(self)
        
    @api.constrains('clear_date')
    def _check_future_clear_date(self):
        for record in self:
            if record.move_id.state == 'posted' and record.clear_date and record.clear_date < record.date:
                raise ValidationError("Clear date should not be less than transaction date.")
            
    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        return {'domain':{'account_id':[('branch_id','=',self.move_id.branch_id.id)]}}

    @api.multi
    @api.constrains('currency_id', 'amount_currency')
    def _check_currency_and_amount(self):
        return True

    @api.onchange('amount_currency')
    def _onchange_amount_currency(self):
        for rec in self:
            rec.debit, rec.credit = False, False
            if rec.move_id.is_foreign_currency:
                if rec.amount_currency > 0:
                    rec.debit = rec.amount_currency * rec.move_id.exchange_rate
                else:
                    rec.credit = abs(rec.amount_currency * rec.move_id.exchange_rate)
            else:
                if rec.amount_currency > 0:
                    rec.debit = rec.amount_currency
                else:
                    rec.credit = abs(rec.amount_currency)

    @api.onchange('account_id')
    def onchange_account_id(self):
        for rec in self:
            if self._context.get('search_default_receipt_filter') or self._context.get('search_default_payment_filter'):
                rec.is_payment_receipt = True
            if rec.move_id.company_currency_id.id != rec.move_id.currency_id.id:
                if rec.move_id.exchange_rate == 0:
                    return {'warning': {
                        'title': _('Warning'),
                        'message': _('Please set exchange rate.')
                    }}

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        for rec in self:
            rec.department_id, rec.analytic_account_id, rec.debit, rec.credit, rec.invoice_id = False, False, False, False, False
            if rec.partner_id:
                user_id = self.env['res.users'].sudo().search([('partner_id', '=', rec.partner_id.id)]).id
                if user_id:
                    employee_dept = self.env['hr.employee'].sudo().search([('user_id', '=', user_id)]).department_id
                    rec.department_id = employee_dept if employee_dept else False
            return {'domain': {'invoice_id': [('partner_id', '=', rec.partner_id.id), ('state', '=', 'open')]}}

    @api.onchange('debit')
    def _onchange_debit(self):
        for rec in self:
            if rec.debit > 0:
                if rec.analytic_account_id:
                    analytic_rec = self.env['account.analytic.account'].sudo().browse(rec.analytic_account_id.id)
                    budget_lines = analytic_rec.crossovered_budget_line
                    for budget_line in budget_lines:
                        line_account_ids = budget_line.general_budget_id.account_ids.ids
                        for line_account_id in line_account_ids:
                            if self.env['account.account'].sudo().browse(line_account_id).code == rec.account_id.code:
                                if (budget_line.planned_amount - budget_line.practical_amount) < rec.debit:
                                    return {'warning': {
                                        'title': _('Validation Error'),
                                        'message': _('Transaction amount is more than Available amount.')
                                    }}

    @api.onchange('account_id', 'analytic_account_id')
    def _check_budget_head(self):
        account_ids_lst = []
        for rec in self:
            if rec.account_id and rec.analytic_account_id:
                analytic_rec = self.env['account.analytic.account'].sudo().browse(rec.analytic_account_id.id)
                budget_lines = analytic_rec.crossovered_budget_line
                for budget_line in budget_lines:
                    line_account_ids = budget_line.general_budget_id.account_ids.ids
                    for line_account_id in line_account_ids:
                        account_ids_lst.append(line_account_id)
                if rec.account_id.id not in account_ids_lst:
                    return {'warning': {
                        'title': ('Validation Error'),
                        'message': (
                            f'{rec.account_id.code} {rec.account_id.name} is not available in {rec.analytic_account_id.name}.')
                    }}
    @api.multi
    def _update_check(self):
        """ Raise Warning to cause rollback if the move is posted, some entries are reconciled or the move is older than the lock date"""
        move_ids = set()
        for line in self:
            err_msg = _('Move name (id): %s (%s)') % (line.move_id.name, str(line.move_id.id))
            if line.move_id.state not in ['draft']:
                raise UserError(_('You cannot do this modification on a posted journal entry, you can just change some non legal fields. You must revert the journal entry to cancel it.\n%s.') % err_msg)
            if line.reconciled and not (line.debit == 0 and line.credit == 0):
                raise UserError(_('You cannot do this modification on a reconciled entry. You can just change some non legal fields or you must unreconcile first.\n%s.') % err_msg)
            if line.move_id.id not in move_ids:
                move_ids.add(line.move_id.id)
        self.env['account.move'].browse(list(move_ids))._check_lock_date()
        return True
    
    @api.model
    def create(self, vals):
        result = super(AccountMoveLineInherit, self).create(vals)
        partner_id = self.env['res.partner'].search(['|',('parent_id','=',False),('property_account_payable_id','=',result.account_id.id),('property_account_receivable_id','=',result.account_id.id)],limit=1) 
        result.partner_id = partner_id
        return result
    
    @api.multi
    def write(self, vals):
        result = super(AccountMoveLineInherit, self).write(vals)
        if 'account_id' in vals and vals['account_id']:
            for move_line in self:
                partner_id = self.env['res.partner'].search(['|',('parent_id','=',False),('property_account_payable_id','=',move_line.account_id.id),('property_account_receivable_id','=',move_line.account_id.id)],limit=1) 
                move_line.partner_id = partner_id
        if set(vals) & set(self._get_tracked_fields(list(vals))):
            self._track_changes(vals)
        return result
    
    @api.model
    def _get_tracked_fields(self, updated_fields):
        """ Return a structure of tracked fields for the current model.
            :param list updated_fields: modified field names
            :return dict: a dict mapping field name to description, containing on_change fields
        """
        tracked_fields = []
        for name, field in self._fields.items():
            # if getattr(field, 'track_visibility', False):
            tracked_fields.append(name)

        if tracked_fields:
            return self.fields_get(tracked_fields)
        return {}

    def _track_changes(self,vals):
        # self.write({
        #     'last_updated_user_id' : self.env.user.id,
        #     'last_update_date' : datetime.today()
        # })
        if 'budget_type' in vals:
            msg = _('Budget Type: ') + vals['budget_type']
            self.move_id.message_post(body=msg)
        if 'account_id' in vals and vals['account_id'] != False:
            account_id = self.env['account.account'].browse(int(vals['account_id']))
            msg = _('Account: ') + account_id.code + " " + account_id.name
            self.move_id.message_post(body=msg)
        if 'department_id' in vals and vals['department_id'] != False:
            department_id = self.env['hr.department'].browse(int(vals['department_id']))
            msg = _('Department: ') + department_id.name
            self.move_id.message_post(body=msg)
        if 'division_id' in vals and vals['division_id'] != False:
            division_id = self.env['hr.department'].browse(int(vals['division_id']))
            msg = _('Division: ') + division_id.name
            self.move_id.message_post(body=msg)
        if 'section_id' in vals and vals['section_id'] != False:
            section_id = self.env['hr.department'].browse(int(vals['section_id']))
            msg = _('Section: ') + section_id.name
            self.move_id.message_post(body=msg)
        if 'employee_id' in vals and vals['employee_id'] != False:
            employee_id = self.env['hr.employee'].browse(int(vals['employee_id']))
            msg = _('Employee: ') + employee_id.name + " (" + employee_id.emp_code + ")"
            self.move_id.message_post(body=msg)
        if 'debit' in vals and vals['debit'] != False:
            msg = _('Debit: ') + str(self.debit)
            self.move_id.message_post(body=msg)
        if 'credit' in vals and vals['credit'] != False:
            msg = _('Credit: ') + str(self.credit)
            self.move_id.message_post(body=msg)
        if 'project_wo_id' in vals and vals['project_wo_id'] != False:
            project_id = self.env['kw_project_budget_master_data'].browse(int(vals['project_wo_id']))
            msg = _('Project: ') + project_id.workorder_name
            self.move_id.message_post(body=msg)

        
        
    @api.model
    def _query_get(self, domain=None):
        self.check_access_rights('read')

        context = dict(self._context or {})
        domain = domain or []
        if not isinstance(domain, (list, tuple)):
            domain = safe_eval(domain)

        date_field = 'date'
        if context.get('aged_balance'):
            date_field = 'date_maturity'
        if context.get('date_to'):
            domain += [(date_field, '<=', context['date_to'])]
        if context.get('date_from'):
            if not context.get('strict_range'):
                domain += ['|', (date_field, '>=', context['date_from']), ('account_id.user_type_id.include_initial_balance', '=', True)]
            elif context.get('initial_bal'):
                domain += [(date_field, '<', context['date_from'])]
            else:
                domain += [(date_field, '>=', context['date_from'])]

        if context.get('journal_ids'):
            domain += [('journal_id', 'in', context['journal_ids'])]

        state = context.get('state')
        if state and state.lower() != 'all':
            domain += [('move_id.state', '=', state)]

        if context.get('company_id'):
            domain += [('company_id', '=', context['company_id'])]

        if context.get('company_type'):
            domain += [('branch_id.code', 'in', [j['id'] for j in context['company_type'] if j.get('selected')])]

        if 'company_ids' in context:
            domain += [('company_id', 'in', context['company_ids'])]

        if context.get('reconcile_date'):
            domain += ['|', ('reconciled', '=', False), '|', ('matched_debit_ids.max_date', '>', context['reconcile_date']), ('matched_credit_ids.max_date', '>', context['reconcile_date'])]

        if context.get('account_tag_ids'):
            domain += [('account_id.tag_ids', 'in', context['account_tag_ids'].ids)]

        if context.get('account_ids'):
            domain += [('account_id', 'in', context['account_ids'].ids)]

        if context.get('analytic_tag_ids'):
            domain += [('analytic_tag_ids', 'in', context['analytic_tag_ids'].ids)]

        if context.get('analytic_account_ids'):
            domain += [('analytic_account_id', 'in', context['analytic_account_ids'].ids)]

        if context.get('partner_ids'):
            domain += [('partner_id', 'in', context['partner_ids'].ids)]

        if context.get('partner_categories'):
            domain += [('partner_id.category_id', 'in', context['partner_categories'].ids)]

        where_clause = ""
        where_clause_params = []
        tables = ''
        if domain:
            query = self._where_calc(domain)

            # Wrap the query with 'company_id IN (...)' to avoid bypassing company access rights.
            self._apply_ir_rules(query)

            tables, where_clause, where_clause_params = query.get_sql()
        return tables, where_clause, where_clause_params

    def branch_wise_untagged_vouchers(self):
        company_id,branch_id,fy_id = self.env['account.invoice'].get_session_details()
        tree_view_id = self.env.ref('kw_accounting.untagged_budget_line_tree_view').id
        domain = [('move_id.state','=','posted'),('move_id.company_id','=',int(company_id)),('move_id.branch_id','=',int(branch_id)),('date','>=',fy_id.date_start),('date','<=',fy_id.date_stop)]
        move_line_ids = self.search(domain + [('budget_type','=','treasury'),('budget_line','=',False)]) + self.search(domain + [('budget_type','=','project'),('project_line','=',False)]) + self.search(domain + [('budget_type','=','capital'),('capital_line','=',False)])
        action = {'type': 'ir.actions.act_window',
                'name': 'Contra Voucher',
                'views': [(tree_view_id, 'tree')],
                'view_mode': 'tree',
                'res_model': 'account.move.line',
                'domain': [('id', 'in', move_line_ids.ids)],
                'context': {"create": False,"edit": True,"import":True},
                }
        return action