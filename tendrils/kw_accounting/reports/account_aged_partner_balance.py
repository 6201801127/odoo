# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _
from odoo.tools.misc import format_date
from datetime import datetime


class report_account_aged_partner(models.AbstractModel):
    _name = "account.aged.partner"
    _description = "Aged Partner Balances"
    _inherit = 'account.report'

    filter_date = {'date': '', 'filter': 'today'}
    filter_unfold_all = False
    filter_partner = True

    def _get_columns_name(self, options):
        columns = [{}]
        columns += [
            {'name': v, 'class': 'number', 'style': 'white-space:nowrap;'}
            for v in [_("JRNL"), _("Account"), _("Reference"), _("Advance"),_("Not due"),
                      _("1 - 30"), _("31 - 60"), _("61 - 90"), _("91 - 180"),_("181 - 365"),_("1yr - 2yr"), _(">2yr"), _(">3yr"), _("Total")]
        ]
        return columns

    def _get_templates(self):
        templates = super(report_account_aged_partner, self)._get_templates()
        templates['main_template'] = 'kw_accounting.template_aged_partner_balance_report'
        try:
            self.env['ir.ui.view'].get_view_id('kw_accounting.template_aged_partner_balance_line_report')
            templates['line_template'] = 'kw_accounting.template_aged_partner_balance_line_report'
        except ValueError:
            pass
        return templates

    @api.model
    def _get_lines(self, options, line_id=None):
        sign = -1.0 if self.env.context.get('aged_balance') else 1.0
        lines = []
        account_types = [self.env.context.get('account_type')]
        period_length = [365,365,365,185,60,30,30,30]
        results, total, amls = self.env['report.accounting_pdf_reports.report_agedpartnerbalance'].with_context(include_nullified_amount=True)._get_partner_move_lines(account_types, self._context['date_to'], 'posted', period_length)
        for values in results:
            if line_id and 'partner_%s' % (values['partner_id'],) != line_id:
                continue
            vals = {
                'id': 'partner_%s' % (values['partner_id'],),
                'name': values['name'],
                'level': 2,
                'columns': [{'name': ''}] * 3 + [{'name': (self.with_context(accounting_format=True).format_value((sign * v)))} for v in [values['advance'],values['direction'],values['7'],values['6'],values['5'],values['4'],
                                                                                                 values['3'], values['2'],
                                                                                                 values['1'], values['0'], values['total']]],
                'trust': values['trust'],
                'unfoldable': True,
                'unfolded': 'partner_%s' % (values['partner_id'],) in options.get('unfolded_lines'),
            }
            lines.append(vals)
            if 'partner_%s' % (values['partner_id'],) in options.get('unfolded_lines'):
                for line in amls[values['partner_id']]:
                    aml = line['line']
                    caret_type = 'account.move'
                    if aml.invoice_id:
                        caret_type = 'account.invoice.in' if aml.invoice_id.type in ('in_refund', 'in_invoice') else 'account.invoice.out'
                    elif aml.payment_id:
                        caret_type = 'account.payment'
                    line_date = aml.date_maturity or aml.date
                    if not self._context.get('no_format'):
                        line_date = format_date(self.env, line_date)
                    vals = {
                        'id': aml.id,
                        'name': line_date,
                        'class': 'date',
                        'caret_options': caret_type,
                        'level': 4,
                        'parent_id': 'partner_%s' % (values['partner_id'],),
                        'columns': [{'name': v} for v in [aml.journal_id.code, aml.account_id.code, self._format_aml_name(aml)]] +\
                                   [{'name': v} for v in [line['period'] == 10-i and self.with_context(accounting_format=True).format_value((sign * line['amount'])) or '' for i in range(11)]],
                        'action_context': aml.get_action_context(),
                    }
                    lines.append(vals)
        if total and not line_id:
            total_line = {
                'id': 0,
                'name': _('Total'),
                'class': 'total',
                'level': 2,
                'columns': [{'name': ''}] * 3 + [{'name': (self.with_context(accounting_format=True).format_value((sign * v)))} for v in [total[10],total[9],total[7],total[6], total[5],total[4], total[3], total[2], total[1], total[0], total[8]]],
            }
            lines.append(total_line)
        return lines


class report_account_aged_receivable(models.AbstractModel):
    _name = "account.aged.receivable"
    _description = "Aged Receivable"
    _inherit = "account.aged.partner"

    def _set_context(self, options):
        ctx = super(report_account_aged_receivable, self)._set_context(options)
        ctx['account_type'] = 'receivable'
        return ctx

    def _get_report_name(self):
        date_object = datetime.strptime(self._context.get('date_to'), '%Y-%m-%d').date().strftime("%d-%b-%Y") if self._context.get('date_to') else ''
        return _("Receivable Ageing on %s") % date_object

    def _get_templates(self):
        templates = super(report_account_aged_receivable, self)._get_templates()
        templates['line_template'] = 'kw_accounting.line_template_aged_receivable_report'
        return templates


class report_account_aged_payable(models.AbstractModel):
    _name = "account.aged.payable"
    _description = "Aged Payable"
    _inherit = "account.aged.partner"

    def _set_context(self, options):
        ctx = super(report_account_aged_payable, self)._set_context(options)
        ctx['account_type'] = 'payable'
        ctx['aged_balance'] = True
        return ctx

    def _get_report_name(self):
        date_object = datetime.strptime(self._context.get('date_to'), '%Y-%m-%d').date().strftime("%d-%b-%Y") if self._context.get('date_to') else ''
        return _("Payable Ageing as on %s") % date_object

    def _get_templates(self):
        templates = super(report_account_aged_payable, self)._get_templates()
        templates['line_template'] = 'kw_accounting.line_template_aged_payable_report'
        return templates
