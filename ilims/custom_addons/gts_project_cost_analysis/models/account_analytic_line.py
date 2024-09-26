from odoo import api, fields, models, _


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    entry_type = fields.Selection([('income', 'Income'), ('expenses', 'Expenses')], string='Entry Type',
                                  compute='_compute_entry_type', store=True, copy=False)

    @api.depends('general_account_id')
    def _compute_entry_type(self):
        for record in self:
            if record.general_account_id:
                # for type in self.general_account_id.user_type_id:
                if (record.general_account_id.user_type_id.name == 'Other Income' or
                            record.general_account_id.user_type_id.name == 'Income'):
                    record.entry_type = 'income'
                elif (record.general_account_id.user_type_id.name == 'Expenses' or
                              record.general_account_id.user_type_id.name == 'Depreciation' or
                              record.general_account_id.user_type_id.name == 'Cost of Revenue'):
                    record.entry_type = 'expenses'
                else:
                    record.entry_type = '' or False
            else:
                record.entry_type = '' or False
