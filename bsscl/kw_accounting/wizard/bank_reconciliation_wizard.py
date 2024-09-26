from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date
from odoo.http import request



class BankReconciliationWizard(models.TransientModel):
    _name = 'bank.reconciliation.wizard'
    _description = 'Bank Reconciliation Wizard'
    _rec_name = 'bank_account_id'

    @api.model
    def _get_bank_account_ledgers(self):
        return [('ledger_type','=','bank')]
    
    
    filter_by = fields.Selection([('current_date','Current Date'),('fiscal_year','Financial Year'),('date_range','Date Range')],default="current_date")
    financial_year_id = fields.Many2one('account.fiscalyear',string="Financial Year",order="id desc")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    bank_account_id = fields.Many2one('account.account',string="Bank Account",domain=_get_bank_account_ledgers)


    @api.onchange('filter_by','financial_year_id')
    def get_dates(self):
        self.date_from,self.date_to = False,False
        if self.filter_by == 'current_date':
            self.date_from = date.today()
            self.date_to = date.today()
        elif self.filter_by == 'fiscal_year':
            self.date_from = self.financial_year_id.date_start
            self.date_to = self.financial_year_id.date_stop


    
    def get_bank_reconciliation(self):
        view_id = self.env.ref("kw_accounting.bank_reconciliation_tree_view").id
        request.session['bank_reconciliation_ledger_id'] = self.bank_account_id.id
        request.session['start_date'] = self.date_from
        request.session['end_date'] = self.date_to

        action =  {
            'name': _("Bank Reconcilitation"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move.line',
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'self',
            'domain': [('account_id','=',self.bank_account_id.id),('reconciled','in',[True,False]),('date','>=',self.date_from),('date','<=',self.date_to)]
        }
        return action
    
class BankReconcileEntries(models.TransientModel):
    _name = 'bank_reconcile_entries_wizard'
    _description = 'Bank Reconcile Entries Wizard'

    def _get_default_line_ids(self):
        return self.env['account.move.line'].browse(self.env.context.get('active_ids'))

    bank_reconcile_ids = fields.Many2many('account.move.line', readonly=1, default=_get_default_line_ids)


    def action_menu_bank_reconcile(self):
        for rec in self:
            for reconcile in rec.bank_reconcile_ids:
                if not reconcile.clear_date:
                    raise ValidationError("Please enter the clear date.")
                else:
                    reconcile.reconciled = True
                request.session['reconciled'] = True
                

    