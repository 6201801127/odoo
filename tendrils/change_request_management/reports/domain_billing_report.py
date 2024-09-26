"""

This module provides models and tools for generating domain billing data reports in Odoo.

Imports:
    - models: For defining Odoo models.
    - fields: For defining fields in Odoo models.
    - api: For defining Odoo API methods.
    - tools: For various tools provided by Odoo.
    - date: For working with date objects.
    - datetime: For working with date and time objects.
    - time: For working with time objects.
    - request: For handling HTTP requests in Odoo.
    - ValidationError: For handling validation errors in Odoo.

"""

from odoo import models, fields, api, tools
from datetime import date, datetime, time
from odoo.http import request
from odoo.exceptions import ValidationError
from odoo.http import request


class CrServerDataReport(models.Model):
    """
    This class represents domain billing data reports in Odoo.

    Attributes:
        _name (str): The technical name of the model.
    """
    _name = 'domain_billing_data_report'
    # _rec_name = 'reference_no'
    _description = 'Domain Billing Report'
    _auto = False

    domain_name = fields.Char(string="Domain Name", )
    project_id = fields.Many2one('project.project', string="Project Name")
    registration_at = fields.Many2one('registration_master_config', string="Registration At")
    bill_no = fields.Char(string='Bill No')
    account_head_id = fields.Many2one('kw_account_head_master', string='Account Head')
    order_date = fields.Date(string='Order Date')
    billed_amount = fields.Float(string='Billed Amount')
    discount = fields.Float(string='Discount')
    approved_amount = fields.Float(string='Approved Amount', compute="calculate_approve_amount", store=True)
    fy_year = fields.Many2one('account.fiscalyear', string='Fiscal Year')

    @api.depends('billed_amount', 'discount')
    def calculate_approve_amount(self):
        for rec in self:
            if rec.billed_amount and rec.discount:
                approved_amount = rec.billed_amount - rec.discount
                rec.approved_amount = approved_amount

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
                SELECT   
                ROW_NUMBER() OVER () AS id,
                cr.domain_name AS domain_name,
                cr.project_id AS project_id,
                cr.registration_at AS registration_at,
                dbi.bill_no AS bill_no,
                dbi.account_head_id AS account_head_id,
                dbi.order_date AS order_date,
                dbi.billed_amount AS billed_amount,
                dbi.discount AS discount,
                dbi.approved_amount AS approved_amount,
                dbi.fy_year AS fy_year
            FROM kw_cr_domain_server_configuration cr
            LEFT JOIN kw_domain_bill AS dbi on dbi.domain_server_bill_id = cr.id
          )"""
        self.env.cr.execute(query)


class DomainBillingFilterWizard(models.TransientModel):
    """
    This class represents a transient model for filtering domain billing data in Odoo.

    Attributes:
        _name (str): The technical name of the model.
        _description (str): The description of the model.
    """
    _name = "domain_billing_filter_wizard"
    _description = "Billing Filter Wizard"

    dt_start = fields.Date(string='From Date', required=True)
    dt_stop = fields.Date(string='To Date', required=True)
    fy_year = fields.Many2one('account.fiscalyear', string='Fiscal Year')
    report_type_selection = fields.Selection(string="Report Type", default='monthly',
                                             selection=[('monthly', 'Monthly'), ('general', 'General')])
    # ('bill_wise', 'Bill Wise'), ('domain_wise', 'Domain Wise'),
    # filter_month = fields.Selection([(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'),
    #                                           (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'),
    #                                           (10, 'October'), (11, 'November'), (12, 'December')],)

    @api.multi
    def action_generate_report(self):
        if self.dt_start > self.dt_stop:
            raise ValidationError("Please select end date after start date.")
        mode = self.report_type_selection
        if mode in ['general', 'bill_wise', 'domain_wise']:
            res_model = 'domain_wise_data_report'
            tree_view_id = self.env.ref('change_request_management.domain_wise_filter_report_tree').id
        elif mode == 'monthly':
            res_model = 'monthly_billing_data_report_new'
            tree_view_id = self.env.ref('change_request_management.monthly_bill_filter_report_tree').id
        request.session['billing_dt_start'] = self.dt_start.strftime("%Y-%m-%d")
        request.session['billing_dt_stop'] = self.dt_stop.strftime("%Y-%m-%d")
        return {
            'name': f'Domain Bill Report ({self.dt_start.strftime("%d-%b-%Y")} - {self.dt_stop.strftime("%d-%b-%Y")})',
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': False,
            'res_model': res_model,
            'type': 'ir.actions.act_window',
            'target': 'main',
            'context': {'dt_start': self.dt_start, 'dt_stop': self.dt_stop, 'report_type': mode},
            'views': [(tree_view_id, 'tree')],
        }

        # action = {
        #     'type': 'ir.actions.act_url',
        #     'url': '/download-report/%s/%s/%s' % (self.dt_start, self.dt_stop, self.report_type_selection),
        #     'target': 'new',
        # }
        # return action


class MonthlyBillDataReport(models.Model):
    """
    This class represents monthly billing reports in Odoo.
    Attributes:
        _name (str): The technical name of the model.
        _description (str): The description of the model.
        _auto (bool): Indicates whether the model is automatically created in the database.
        _order (str): The default sorting order for records.
    """

    _name = "monthly_billing_data_report_new"
    _description = "Monthly Billing Report"
    _auto = False
    _order = "order_date asc"

    account_head_id = fields.Many2one('kw_account_head_master', string='Account Head')
    order_date = fields.Date(string='Order Date')
    approved_amount = fields.Float(string='Approved Amount')

    bill_jan = fields.Float(string='January', digits=(10, 2))
    bill_feb = fields.Float(string='February', digits=(10, 2))
    bill_mar = fields.Float(string='March', digits=(10, 2))
    bill_apr = fields.Float(string='April', digits=(10, 2))
    bill_may = fields.Float(string='May', digits=(10, 2))
    bill_jun = fields.Float(string='June', digits=(10, 2))
    bill_jul = fields.Float(string='July', digits=(10, 2))
    bill_aug = fields.Float(string='August', digits=(10, 2))
    bill_sep = fields.Float(string='September', digits=(10, 2))
    bill_oct = fields.Float(string='October', digits=(10, 2))
    bill_nov = fields.Float(string='November', digits=(10, 2))
    bill_dec = fields.Float(string='December', digits=(10, 2))
    total_bill = fields.Float(string='Total', digits=(10, 2))

    seq_no = fields.Integer(string='Sequence', readonly=True, compute='compute_seq_no')
    fy_year = fields.Many2one('account.fiscalyear', string='Fiscal Year')
    dt_start = fields.Date(string='dt_start', compute='compute_dt_start_date_stop')
    dt_stop = fields.Date(string='dt_stop', compute='compute_dt_start_date_stop')

    @api.depends('account_head_id')
    def compute_seq_no(self):
        for rec in self:
            rec.seq_no = rec.id

    def compute_dt_start_date_stop(self):
        for rec in self:
            rec.dt_start = request.session.get('billing_dt_start', None)
            rec.dt_stop = request.session.get('billing_dt_stop', None)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if self._context.get('dt_start') and self._context.get('dt_stop'):
            dt_start = self._context.get('dt_start')
            dt_stop = self._context.get('dt_stop')
            domain += [('order_date', '>=', dt_start), ('order_date', '<=', dt_stop)]
            # print('dt_stop >> ', dt_start, dt_stop, domain)
        res = super(MonthlyBillDataReport, self).search_read(domain, fields, offset, limit, order)
        return res

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
                    SELECT
                        kdb.id AS id,
                        kdb.account_head_id AS account_head_id,
                        kdb.order_date AS order_date,
                        kdb.fy_year AS fy_year,
						kdb.approved_amount AS approved_amount,
                        CASE WHEN EXTRACT(MONTH FROM kdb.order_date) = 1 THEN kdb.approved_amount ELSE 0 END AS bill_jan,
                        CASE WHEN EXTRACT(MONTH FROM kdb.order_date) = 3 THEN kdb.approved_amount ELSE 0 END AS bill_mar,
                        CASE WHEN EXTRACT(MONTH FROM kdb.order_date) = 4 THEN kdb.approved_amount ELSE 0 END AS bill_apr,
                        CASE WHEN EXTRACT(MONTH FROM kdb.order_date) = 5 THEN kdb.approved_amount ELSE 0 END AS bill_may,
                        CASE WHEN EXTRACT(MONTH FROM kdb.order_date) = 2 THEN kdb.approved_amount ELSE 0 END AS bill_feb,
                        CASE WHEN EXTRACT(MONTH FROM kdb.order_date) = 6 THEN kdb.approved_amount ELSE 0 END AS bill_jun,
                        CASE WHEN EXTRACT(MONTH FROM kdb.order_date) = 7 THEN kdb.approved_amount ELSE 0 END AS bill_jul,
                        CASE WHEN EXTRACT(MONTH FROM kdb.order_date) = 8 THEN kdb.approved_amount ELSE 0 END AS bill_aug,
                        CASE WHEN EXTRACT(MONTH FROM kdb.order_date) = 9 THEN kdb.approved_amount ELSE 0 END AS bill_sep,
                        CASE WHEN EXTRACT(MONTH FROM kdb.order_date) = 10 THEN kdb.approved_amount ELSE 0 END AS bill_oct,
                        CASE WHEN EXTRACT(MONTH FROM kdb.order_date) = 11 THEN kdb.approved_amount ELSE 0 END AS bill_nov,
                        CASE WHEN EXTRACT(MONTH FROM kdb.order_date) = 12 THEN kdb.approved_amount ELSE 0 END AS bill_dec,
                        kdb.approved_amount AS total_bill
                    FROM
                        kw_domain_bill AS kdb
          )"""
        self.env.cr.execute(query)


class BillWiseDataReport(models.Model):
    """
    This class represents bill-wise reports in Odoo.

    Attributes:
        _name (str): The technical name of the model.
        _description (str): The description of the model.
        _auto (bool): Indicates whether the model is automatically created in the database.
        _order (str): The default sorting order for records.
    """
    _name = "bill_wise_data_report"
    _description = "Domain Bill Wise Report"
    _auto = False
    _order = "domain_name asc, account_head_id asc"

    domain_name = fields.Char(string="Domain Name", )
    bill_no = fields.Char(string='Bill No')
    account_head_id = fields.Many2one('kw_account_head_master', string='Account Head')
    order_date = fields.Date(string='Order Date')
    billed_amount = fields.Float(string='Billed Amount', digits=(10, 2))
    discount = fields.Float(string='Discount', digits=(10, 2))
    approved_amount = fields.Float(string='Approved Amount', compute="calculate_approve_amount", store=True,
                                   digits=(10, 2))
    seq_ = fields.Integer(string='Sequence', readonly=True, compute='compute_seq_')
    fy_year = fields.Many2one('account.fiscalyear', string='Fiscal Year')

    @api.depends('domain_name', 'account_head_id')
    def compute_seq_(self):
        for rec in self:
            rec.seq_ = rec.id

    @api.depends('billed_amount', 'discount')
    def calculate_approve_amount(self):
        for rec in self:
            if rec.billed_amount and rec.discount:
                approved_amount = rec.billed_amount - rec.discount
                rec.approved_amount = approved_amount

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if self._context.get('dt_start') and self._context.get('dt_stop'):
            dt_start = self._context.get('dt_start')
            dt_stop = self._context.get('dt_stop')
            domain += [('order_date', '>=', dt_start), ('order_date', '<=', dt_stop)]
            # print('dt_stop >> ', dt_start, dt_stop, domain)
        res = super(BillWiseDataReport, self).search_read(domain, fields, offset, limit, order)
        return res

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
                WITH ranked_data AS (
                    SELECT
                        ROW_NUMBER() OVER () AS id,
                        domain_name,
                        account_head_id,
                        bill_no,
                        order_date,
                        billed_amount,
                        discount,
                        approved_amount,
                        fy_year,
                        ROW_NUMBER() OVER (PARTITION BY domain_name, account_head_id ORDER BY id) AS account_head_rank
                    FROM
                        domain_billing_data_report
                )
                SELECT
                    id,
                     domain_name,
                     account_head_id,
                    bill_no,
                    order_date,
                    billed_amount,
                    discount,
                    approved_amount,
                    fy_year
                FROM
                    ranked_data
          )"""
        self.env.cr.execute(query)


class DomainWiseDataReport(models.Model):
    """
    This class represents domain-wise reports in Odoo.

    Attributes:
        _name (str): The technical name of the model.
        _description (str): The description of the model.
        _auto (bool): Indicates whether the model is automatically created in the database.
        _order (str): The default sorting order for records.
    """
    _name = 'domain_wise_data_report'
    _description = 'Domain Wise Report'
    _auto = False
    _order = "order_date ASC"

    domain_name = fields.Char(string="Domain Name", )
    bill_no = fields.Char(string='Bill No')
    account_head_id = fields.Many2one('kw_account_head_master', string='Account Head')
    order_date = fields.Date(string='Order Date')
    billed_amount = fields.Float(string='Billed Amount', digits=(10, 2))
    discount = fields.Float(string='Discount', digits=(10, 2))
    approved_amount = fields.Float(string='Approved Amount', compute="calculate_approve_amount", store=True,
                                   digits=(10, 2))
    # seq = fields.Integer(string='Sequence')
    # total_billed_amount = fields.Float(string='Total Billed Amount', compute='_compute_domain_totals', store=True, digits=(10, 2))
    # total_discount = fields.Float(string='Total Discount', compute='_compute_domain_totals', store=True, digits=(10, 2))
    # total_approved_amount = fields.Float(string='Total Approved Amount', compute='_compute_domain_totals', store=True, digits=(10, 2))
    dt_start = fields.Date(string='dt_start', compute='compute_dt_start_date_stop')
    dt_stop = fields.Date(string='dt_stop', compute='compute_dt_start_date_stop')

    def compute_dt_start_date_stop(self):
        for rec in self:
            rec.dt_start = request.session.get('billing_dt_start', None)
            rec.dt_stop = request.session.get('billing_dt_stop', None)

    @api.depends('domain_name')
    def compute_seq(self):
        for rec in self:
            rec.seq = rec.id

    @api.depends('billed_amount', 'discount')
    def calculate_approve_amount(self):
        for rec in self:
            if rec.billed_amount and rec.discount:
                approved_amount = rec.billed_amount - rec.discount
                rec.approved_amount = approved_amount

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if self._context.get('dt_start') and self._context.get('dt_stop'):
            dt_start = self._context.get('dt_start')
            dt_stop = self._context.get('dt_stop')
            domain += [('order_date', '>=', dt_start), ('order_date', '<=', dt_stop)]
        res = super(DomainWiseDataReport, self).search_read(domain, fields, offset, limit, order)
        return res

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f"""CREATE or REPLACE VIEW {self._table} as (
          WITH DomainBillingCTE AS (
        SELECT
            DENSE_RANK() OVER (ORDER BY domain_name) AS seq,
            id AS id,
            domain_name,
            bill_no,
            account_head_id,
            order_date,
            billed_amount,
            discount,
            approved_amount,
            SUM(billed_amount) OVER (PARTITION BY domain_name) AS total_billed_amount,
            SUM(discount) OVER (PARTITION BY domain_name) AS total_discount,
            SUM(approved_amount) OVER (PARTITION BY domain_name) AS total_approved_amount
        FROM
            domain_billing_data_report
    )
    SELECT
        seq,
        id,
        domain_name,
        bill_no,
        account_head_id,
        order_date,
        billed_amount,
        discount,
        approved_amount,
        total_billed_amount,
        total_discount,
        total_approved_amount
    FROM
        DomainBillingCTE

        )"""
        self.env.cr.execute(query)
