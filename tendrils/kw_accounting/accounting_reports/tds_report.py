from odoo import models, fields, api, tools


class SalesRegisterReport(models.Model):
    _name = "tds_register_report"
    _description = "TDS Register Report"
    _auto = False

    month_name = fields.Char(string="Month")
    partner_id = fields.Many2one('res.partner', string="Party Name")
    partner_name = fields.Char(related='partner_id.name', string="Partner")
    pan_no = fields.Char(string="PAN")
    fiscal_year = fields.Many2one(
        'account.fiscalyear', string="Financial Year")
    voucher_number = fields.Char(string="Voucher No")
    transaction_date = fields.Date(string="Transaction Date")
    invoice_date = fields.Date(string="Invoice Date")
    invoice_no = fields.Char(string="Invoice No")
    payment_date = fields.Date(string="Payment Date")
    base_amount = fields.Float(string="Base Amount")
    tds_amount = fields.Float(string="TDS Amount")
    tds_rate = fields.Float(string="TDS Rate(%)")
    deposit_date = fields.Date(string="Deposit Date")
    bank_name = fields.Char(string="Bank Name")
    cheque_no = fields.Char(string="Cheque No")
    challan_no = fields.Char(string="Challan No")
    bsr_code = fields.Char(string="BSR Code")
    under_section = fields.Char(string="U/s")
    nature_of_payment = fields.Char(string="Nature of Payment")
    narration = fields.Text(string="Narration")
    tds_expm_cert = fields.Char(string="TDS Expm. Cert#")
    tds_type = fields.Selection(
        [('payable', 'Payable'), ('receivabale', 'Receivabale')], string="TDS Type")
    current_financial_year = fields.Boolean(
        "Current Financial Year", compute='_compute_current_financial_year', search="_register_search_current_financial_year")

    @api.multi
    def _compute_current_financial_year(self):
        for record in self:
            pass

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
            select ROW_NUMBER() OVER (ORDER BY transaction_date asc) AS id, * from (

                select concat(to_char(ai.date,'Mon'),'-',to_char(ai.date, 'YY')) as month_name,
                ai.partner_id as partner_id,
                rp.pan as pan_no,
                (select id from account_fiscalyear afy where afy.date_start <= ai.date and afy.date_stop >= ai.date) as fiscal_year,
                ai.move_name as voucher_number,
                ai.date as transaction_date,
                ai.date_invoice as invoice_date,
                ai.reference_number as invoice_no,
                '' as payment_date,
                atl.base_amount as base_amount,
                atl.ds_amount as tds_amount,
                atl.percentage as tds_rate,
                aa.nature_of_payment as nature_of_payment,
                aa.under_section as under_section,
                ai.comment as narration,
                '' as deposit_date,
                '' as bank_name,
                '' as cheque_no,
                '' as challan_no,
                '' as bsr_code,
                '' as tds_expm_cert,

                aa.tds_type as tds_type
                from account_tds_line atl
                left join account_invoice ai on ai.id = atl.invoice_id
                left join res_partner rp on rp.id = ai.partner_id
                left join account_account aa on aa.id = atl.account_id
                where aa.tds = True and aa.tds_type in ('payable','receivabale') and ai.state != 'draft' and ai.date > '2023-03-31'

                union all
                (

                select 
                concat(to_char(am.date,'Mon'),'-',to_char(am.date, 'YY')) as month_name,
                atl.partner_id as partner_id,
                rp.pan as pan_no,
                am.fiscalyear_id as fiscal_year,
                am.name as voucher_no,
                am.date as transaction_date,
                am.date as invoice_date,
                '' as invoice_no,
                '' as payment_date,
                atl.base_amount as base_amount,
                atl.ds_amount as tds_amount,
                atl.percentage as tds_rate,
                aa.nature_of_payment as nature_of_payment,
                aa.under_section as under_section,
                am.narration as narration,
                '' as deposit_date,
                '' as bank_name,
                '' as cheque_no,
                '' as challan_no,
                '' as bsr_code,
                '' as tds_expm_cert,

                aa.tds_type as tds_type
                from account_tds_line atl
                left join account_move am on am.id = atl.move_id
                left join account_account aa on aa.id = atl.account_id
                left join res_partner rp on rp.id = atl.partner_id
                where aa.tds = True and aa.tds_type in ('payable','receivabale') and am.move_type in ('receipt','payment','contra','general') and am.state != 'draft' and am.date > '2023-03-31'
                    )) as tds


        )"""
        self.env.cr.execute(query)

    @api.multi
    def _register_search_current_financial_year(self, operator, value):
        start_date, end_date = self.env['hr.leave'].lv_get_current_financial_dates(
        )
        domain = [('transaction_date', '>=', start_date),
                  ('transaction_date', '<=', end_date)]
        return domain
