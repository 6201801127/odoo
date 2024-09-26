
from odoo import models, fields, api,_
from odoo.exceptions import UserError
from datetime import datetime, date


class AccountMove(models.Model):
    _inherit = 'account.move'

    credit_limit_amount = fields.Float(string='Credit Limit Amount',related='partner_id.blocking_stage')#wagisha

# (wagisha) to check credit limit in vendor bills
    @api.onchange('amount_total')
    @api.constrains('amount_total')
    def _validate_credit_limit(self):
        for rec in self:
            if rec.credit_limit_amount !=0 and rec.amount_total > rec.partner_id.blocking_stage:
                raise UserError(_(
                    "untaxed amount should be less than Credit Limit"))
        
# (wagisha) to check due months in customer invoice
    def action_register_payment(self):
        if self.invoice_date_due:
            my_credit_date = (datetime.now().date() - self.invoice_date_due ).days
            if self.invoice_date_due and my_credit_date > 60:
                raise UserError(_(
                        "Sorry!!! your due months is crossed 2 months ago you can't pay further."))
            # self.invoice_date_due
            return super(AccountMove, self).action_register_payment()

#(wagisha) overwrite validation on function of add button      
    def js_assign_outstanding_line(self, line_id):
        if self.invoice_date_due:
            my_credit_date = (datetime.now().date() - self.invoice_date_due ).days
            if self.invoice_date_due and my_credit_date > 60:
                raise UserError(_(
                    "Sorry!!! your due months is crossed 2 months ago you can't pay further."))
        return super(AccountMove, self).js_assign_outstanding_line(line_id)
    

class AccountReconciliation(models.AbstractModel):
    _inherit = 'account.reconciliation.widget'
    _description = 'Account Reconciliation widget'


    @api.model
    def _process_move_lines(self, move_line_ids, new_mv_line_dicts):
        """ Create new move lines from new_mv_line_dicts (if not empty) then call reconcile_partial on self and new move lines

            :param new_mv_line_dicts: list of dicts containing values suitable for account_move_line.create()
        """
        #(wagisha) cannot pay after 60 days
       
        record = self.env['account.move.line'].sudo().search([('id','in',move_line_ids)])
        for rec in record:
            # print("rec------------------------------------------------------",rec)
            # print("due date------------------------------------------------------",rec.date_maturity)
            if rec.date_maturity:
                my_credit_date = (datetime.now().date() - rec.date_maturity ).days
                if rec.date_maturity and my_credit_date > 60:
                    raise UserError(_(
                            "Sorry!!! your due months is crossed 2 months ago you can't pay further."))
        #end (wagisha)
        if len(move_line_ids) < 1 or len(move_line_ids) + len(new_mv_line_dicts) < 2:
            raise UserError(_('A reconciliation must involve at least 2 move lines.'))

        account_move_line = self.env['account.move.line'].browse(move_line_ids)
        writeoff_lines = self.env['account.move.line']

        # Create writeoff move lines
        if len(new_mv_line_dicts) > 0:
            company_currency = account_move_line[0].account_id.company_id.currency_id
            same_currency = False
            currencies = list(set([aml.currency_id or company_currency for aml in account_move_line]))
            if len(currencies) == 1 and currencies[0] != company_currency:
                same_currency = True
            # We don't have to convert debit/credit to currency as all values in the reconciliation widget are displayed in company currency
            # If all the lines are in the same currency, create writeoff entry with same currency also
            for mv_line_dict in new_mv_line_dicts:
                if not same_currency:
                    mv_line_dict['amount_currency'] = False
                writeoff_lines += account_move_line._create_writeoff([mv_line_dict])

            (account_move_line + writeoff_lines).reconcile()
        else:
            account_move_line.reconcile()


# Khusboo changes for adding fields
class ResPartner(models.Model):
    _inherit = "res.partner"

    pan_no = fields.Char("PAN No")
    tin_no = fields.Char("TIN No")
    gst = fields.Char("GST No")