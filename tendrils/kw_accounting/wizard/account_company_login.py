from odoo import models, fields, api, _
from odoo.http import request


class AccountingCompanyLogin(models.TransientModel):
    _name="accounting.company.login"
    _description = "Accounting Company Login Wizard"

    company_id = fields.Many2one('res.company',string="Company", default=lambda self: self.env.user.company_id, readonly="1")
    branch_id = fields.Many2one('accounting.branch.unit',string="Branch")
    financial_year = fields.Many2one('account.fiscalyear',string="Financial Year",domain=[('date_start','>','2023-03-31')])

    def submit_company_login(self):
        if 'accounting_company_id' not in request.session:
            request.session['accounting_company_id'] = self.company_id.id
            request.session['accounting_branch_id'] = self.branch_id.id
            request.session['accounting_financial_year'] = self.financial_year.id
        request.session['accounting_company_id'] = self.company_id.id
        request.session['accounting_branch_id'] = self.branch_id.id
        request.session['accounting_financial_year'] = self.financial_year.id
        action_id = self.env.ref('account.open_account_journal_dashboard_kanban').id
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=account.journal&view_type=kanban',
            'target': 'self',
        }

    @api.model
    def setting_init_fiscal_year_action(self):
        """ Called by the 'Fiscal Year Opening' button of the setup bar."""
        if 'accounting_company_id' not in request.session:
            request.session['accounting_company_id'] = self.company_id.id
            request.session['accounting_branch_id'] = self.branch_id.id
            request.session['accounting_financial_year'] = self.financial_year.id
        request.session['accounting_company_id'] = self.company_id.id
        request.session['accounting_branch_id'] = self.branch_id.id
        request.session['accounting_financial_year'] = self.financial_year.id
        view_id = self.env.ref('kw_accounting.company_login_menu_wizard_form_view').id

        return {
            'type': 'ir.actions.act_window',
            'name': _('Accounting:Company Login'),
            'view_mode': 'form',
            'res_model': 'accounting.company.login',
            'target': 'new',
            'views': [[view_id, 'form']],
        }