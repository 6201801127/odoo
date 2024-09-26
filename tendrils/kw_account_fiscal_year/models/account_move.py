
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    fiscalyear_id = fields.Many2one('account.fiscalyear', string='Fiscal Year', index=True)
    period_id = fields.Many2one('account.period', string='Period', index=True)

    @api.model
    def create(self, vals):
        """
        This method overwrite to link fiscal year and period in account move based on date
        :param vals: dictionary of fields and it's values
        :return: new created recordset of account move
        """
        fy_obj = self.env['account.fiscalyear']
        period_obj = self.env['account.period']
        move = super(AccountMove, self).create(vals)
        if move.date and move.company_id:
            fy = fy_obj.finds(dt=move.date, company_id=move.company_id.id)
            fy_date_stop = fy.date_stop.strftime('%d-%b-%Y')
            if not fy:
                raise UserError(_('Fiscal Year is not defined for journal entry date'))
            period = period_obj.find(dt=move.date, company_id=move.company_id.id)
            pr_date_stop = period.date_stop.strftime('%d-%b-%Y')
            if not period:
                raise UserError(_('Period is not defined for journal entry date'))
            if period.lock_in:
                raise UserError(_('Period has been Locked, You can\'t add new entry.'))
            if move.date != period.date_stop and not period.lock_in and period.lock_in_flag == 1:
                raise UserError(_(f'You can create entry only on the date {pr_date_stop}.'))
            if fy.lock_in:
                raise UserError(_('Fiscal Year has been Locked, You can\'t add new entry.'))
            if move.date != fy.date_stop and not fy.lock_in and fy.lock_in_flag == 1:
                raise UserError(_(f'You can create entry only on the date {fy_date_stop}.'))
            move.fiscalyear_id = fy and fy.id
            move.period_id = period and period.id
        return move

    # @api.multi
    # def write(self, vals):
    #     """
    #     This method overwrite to link fiscal year and period in account move based on date
    #     :param vals: dictionary of updated fields and it's values
    #     :return: True after update data
    #     """
    #     fy_obj = self.env['account.fiscalyear']
    #     period_obj = self.env['account.period']
    #     res = super(AccountMove, self).write(vals)
    #     if 'date' in vals and vals['date']:
    #         for move in self:
    #             if move.date and move.company_id:
    #                 fy = fy_obj.finds(dt=move.date, company_id=move.company_id.id)
    #                 fy_date_stop = fy.date_stop.strftime('%d-%b-%Y')
    #                 if not fy:
    #                     raise UserError(_('Fiscal Year is not defined for journal entry date'))
    #                 period = period_obj.find(dt=move.date, company_id=move.company_id.id)
    #                 pr_date_stop = period.date_stop.strftime('%d-%b-%Y')
    #                 if not period:
    #                     raise UserError(_('Period is not defined for journal entry date'))
    #                 if move.date != period.date_stop and not period.lock_in and period.lock_in_flag == 1:
    #                     raise UserError(_(f'You can create entry only on the date {pr_date_stop}.'))
    #                 if move.date != fy.date_stop and not fy.lock_in and fy.lock_in_flag == 1:
    #                     raise UserError(_(f'You can create entry only on the date {fy_date_stop}.'))
    #                 move.fiscalyear_id = fy and fy.id
    #                 move.period_id = period and period.id
    #     return res

    @api.multi
    def post(self, invoice=False):
        """
        This method overwrite to link fiscal year and period on posting journal entry
        :return: true after successfully posted entry
        """
        fy_obj = self.env['account.fiscalyear']
        period_obj = self.env['account.period']
        result = super(AccountMove, self).post()
        for move in self:
            if move.date:
                fy = fy_obj.finds(dt=move.date, company_id=move.company_id.id)
                if not fy:
                    raise UserError(_('Fiscal Year is not defined for journal entry date'))
                period = period_obj.find(dt=move.date, company_id=move.company_id.id)
                if not period:
                    raise UserError(_('Period is not defined for journal entry date'))
                move.fiscalyear_id = fy and fy.id
                move.period_id = period and period.id
        return result


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    fiscalyear_id = fields.Many2one('account.fiscalyear', related='move_id.fiscalyear_id', string='Fiscal Year', index=True, store=True)
    period_id = fields.Many2one('account.period', related='move_id.period_id', string='Period', index=True, store=True)
