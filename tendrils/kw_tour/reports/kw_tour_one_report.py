from odoo import models, fields, api
from odoo import tools
from odoo.exceptions import ValidationError


class TourAllOneReport(models.Model):
    _name = 'kw_tour_one_report'
    _description = 'Tour All One Report'
    _auto = False

    tour_id = fields.Many2one("kw_tour", "Tour")
    settlement_id = fields.Many2one("kw_tour_settlement", "Settlement ID")
    tour_type_id = fields.Many2one("kw_tour_type_new", "Tour Type")
    applied_date = fields.Date("Applied Dt.")
    employee_id = fields.Many2one("hr.employee", string="Employee Name")
    department = fields.Char(related='employee_id.department_id.name', string='Department Name')
    department_id = fields.Many2one("hr.department", string='Department Name')
    division = fields.Char(related='employee_id.division.name', string='Division')
    company_id = fields.Many2one("res.company", string='Company Name')
    section = fields.Char(related='employee_id.section.name', string='Section')
    project_id = fields.Many2one('crm.lead', string='Project/ OPP')
    date_of_travel = fields.Date("Dt. of Tvl.")
    date_of_return = fields.Date("Dt. of Return")
    purpose = fields.Char("Purpose")
    budget_head_id = fields.Many2one('kw_tour_budget_head', string='Budget Head')
    tour_code = fields.Char(string='Tour Ref. No.')
    project_type = fields.Char(string='Project Type')
    advance_domestic = fields.Float("Adv. Amt. (Dom. Cur.)")
    advance_international = fields.Float("Adv. Amt. (Oth. Cur.)")
    place_of_travel = fields.Char("Place Of Travel")
    pending_at = fields.Char("Action To Be Taken By")
    domestic_currency_id = fields.Many2one("res.currency", "Domestic currency")
    usd_currency_id = fields.Many2one("res.currency", "USD currency")
    state = fields.Char("Status")
    tour_state = fields.Char("Tour State")
    action_taken_by = fields.Char("Action To Be Taken By", compute="get_pending_at")
    # action_taken_by1 = fields.Char("Action To Be Taken By", compute="get_pending_at", store=True)
    fiscal_year_id = fields.Many2one('account.fiscalyear', "Fiscal Year")
    ta_inr = fields.Float("TA Amt. (Dom. Cur.)")
    ta_usd = fields.Float("TA Amt. (Oth. Cur.)")
    da_inr = fields.Float("DA Amt. (Dom. Cur.)")
    da_usd = fields.Float("DA Amt. (Oth. Cur.)")
    hra_inr = fields.Float("HRA Amt. (Dom. Cur.)")
    hra_usd = fields.Float("HRA Amt. (Oth. Cur.)")
    ticket_inr = fields.Float("Ticket Cost (Dom. Cur.)")
    ticket_usd = fields.Float("Ticket Cost (Oth. Cur.)")

    misc_inr = fields.Float("Misc. Amt. (Dom. Cur.)")
    misc_usd = fields.Float("Misc. Amt.(Oth. Cur.)")
    hardship_inr = fields.Float("Hardship Amount(INR)")
    hardship_usd = fields.Float("Hardship Amount(USD)")
    visa_inr = fields.Float("VISA Amount(INR)")
    visa_usd = fields.Float("VISA Amount(USD)")
    vaccine_inr = fields.Float("Vaccine Amount(INR)")
    vaccine_usd = fields.Float("Vaccine Amount(USD)")
    rtpcr_inr = fields.Float("RTPCR Amount(INR)")
    rtpcr_usd = fields.Float("RTPCR Amount(USD)")
    add_exp_inr = fields.Float("RTPCR Amount(INR)")
    add_exp_usd = fields.Float("RTPCR Amount(USD)")

    amount_total_inr = fields.Float("Total Amt. (Dom. Cur.)", compute='_compute_total_inr')
    amount_total_usd = fields.Float("Total Amt. (Oth. Cur.)", compute='_compute_total_usd')
    others_total_inr = fields.Float("Others Amt. (Dom. Cur.)", compute='_compute_other_total_inr')
    others_total_usd = fields.Float("Others Amt. (Oth. Cur.)", compute='_compute_other_total_usd')

    # tour_settlement_id = fields.Many2one("", "Settelment ID")

    @api.multi
    def get_pending_at(self):
        for rec in self:
            if rec.tour_state not in ('Draft'):
                if rec.tour_id and rec.settlement_id:
                    if rec.settlement_id.state in ('Approved', 'Granted'):
                        pending_at = rec.settlement_id.pending_at
                        rec.action_taken_by = pending_at.split(",")[0]
                    else:
                        rec.action_taken_by = rec.settlement_id.pending_at if rec.settlement_id.pending_at else "NA"
                else:
                    if rec.tour_id.state == 'Traveldesk Approved':
                        pending_at = rec.tour_id.pending_at
                        rec.action_taken_by = pending_at.split(",")[0]
                    else:
                        rec.action_taken_by = rec.tour_id.pending_at if rec.tour_id.pending_at else "NA"

   
    @api.multi
    def _compute_total_inr(self):
        for rec in self:
            rec.amount_total_inr = rec.ta_inr + rec.da_inr + rec.hra_inr + rec.ticket_inr + rec.misc_inr + rec.hardship_inr + rec.visa_inr + rec.vaccine_inr + rec.rtpcr_inr + rec.add_exp_inr

    @api.multi
    def _compute_total_usd(self):
        for rec in self:
            rec.amount_total_usd = rec.ta_usd + rec.da_usd + rec.hra_usd + rec.ticket_usd + rec.misc_usd + rec.hardship_usd + rec.visa_usd + rec.vaccine_usd + rec.rtpcr_usd + rec.add_exp_usd

    @api.multi
    def _compute_other_total_inr(self):
        for rec in self:
            rec.others_total_inr = rec.misc_inr + rec.hardship_inr + rec.visa_inr + rec.vaccine_inr + rec.rtpcr_inr + rec.add_exp_inr

    @api.multi
    def _compute_other_total_usd(self):
        for rec in self:
            rec.others_total_usd = rec.misc_usd + rec.hardship_usd + rec.visa_usd + rec.vaccine_usd + rec.rtpcr_usd + rec.add_exp_usd

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    ROW_NUMBER() OVER (ORDER BY t.id DESC, ts.id DESC) AS id,
                    (SELECT id FROM res_company
                     WHERE id = (SELECT company_id FROM hr_employee WHERE id = t.employee_id)
                    ) AS company_id,
                    (SELECT id FROM hr_department
                     WHERE id = (SELECT department_id FROM hr_employee WHERE id = t.employee_id)
                    ) AS department_id,
                    t.id AS tour_id,
                    ts.id AS settlement_id,
                    t.code AS tour_code,
                    t.employee_id,
                    t.tour_type_new AS tour_type_id,
                    t.project_type,
                    t.project_id,
                    t.purpose,
                    t.date_travel AS date_of_travel,
                    DATE(t.create_date) AS applied_date,
                    t.date_return AS date_of_return,
                    t.disbursed_inr AS advance_domestic,
                    ts.pending_at,
                    t.disbursed_usd AS advance_international,
                    ts.domestic_currency_id AS domestic_currency_id,
                    ts.usd_currency_id AS usd_currency_id,
                    t.budget_head_id,
                    t.settlement_id AS tour_settlement_id,
                    (
                        SELECT COALESCE(
                            INITCAP(SPLIT_PART(
                                (SELECT name FROM kw_tour_city
                                 WHERE id = (SELECT from_city_id
                                             FROM kw_tour_details
                                             WHERE tour_id = ktd.tour_id
                                             ORDER BY id ASC
                                             LIMIT 1)
                                ), ' ', 1)
                            ), '') || ', ' ||
                            COALESCE(
                                STRING_AGG(c.name, ',' ORDER BY ktd.id ASC),
                                ''
                            ) AS place_of_travel
                        FROM kw_tour_details ktd
                        JOIN kw_tour_city c ON ktd.to_city_id = c.id
                        WHERE ktd.tour_id = t.id
                        GROUP BY ktd.tour_id
                    ) AS place_of_travel,
                    ts.tour_id AS tour_id_settlement,
                    COALESCE(
                        (SELECT SUM(amount_inr)
                         FROM kw_tour_settlement_total_expense
                         WHERE settlement_id = ts.id
                         AND expense_id = (SELECT id FROM kw_tour_expense_type WHERE code = 'ta')
                        ), 0
                    ) AS ta_inr,
                    COALESCE(
                        (SELECT SUM(amount_usd)
                         FROM kw_tour_settlement_total_expense
                         WHERE settlement_id = ts.id
                         AND expense_id = (SELECT id FROM kw_tour_expense_type WHERE code = 'ta')
                        ), 0
                    ) AS ta_usd,
                    COALESCE(
                        (SELECT SUM(amount_inr)
                         FROM kw_tour_settlement_total_expense
                         WHERE settlement_id = ts.id
                         AND expense_id = (SELECT id FROM kw_tour_expense_type WHERE code = 'da')
                        ), 0
                    ) AS da_inr,
                    COALESCE(
                        (SELECT SUM(amount_usd)
                         FROM kw_tour_settlement_total_expense
                         WHERE settlement_id = ts.id
                         AND expense_id = (SELECT id FROM kw_tour_expense_type WHERE code = 'da')
                        ), 0
                    ) AS da_usd,
                    COALESCE(
                        (SELECT SUM(amount_inr)
                         FROM kw_tour_settlement_total_expense
                         WHERE settlement_id = ts.id
                         AND expense_id = (SELECT id FROM kw_tour_expense_type WHERE code = 'hra')
                        ), 0
                    ) AS hra_inr,
                    COALESCE(
                        (SELECT SUM(amount_usd)
                         FROM kw_tour_settlement_total_expense
                         WHERE settlement_id = ts.id
                         AND expense_id = (SELECT id FROM kw_tour_expense_type WHERE code = 'hra')
                        ), 0
                    ) AS hra_usd,
                    COALESCE(
                        (SELECT SUM(amount_inr)
                         FROM kw_tour_settlement_total_expense
                         WHERE settlement_id = ts.id
                         AND expense_id = (SELECT id FROM kw_tour_expense_type WHERE code = 'ticket cost')
                        ), (SELECT SUM(cost)
                            FROM kw_tour_travel_ticket
                            WHERE tour_id = t.id
                            AND currency_id != 2
                        )
                    ) AS ticket_inr,
                    COALESCE(
                        (SELECT SUM(amount_usd)
                         FROM kw_tour_settlement_total_expense
                         WHERE settlement_id = ts.id
                         AND expense_id = (SELECT id FROM kw_tour_expense_type WHERE code = 'ticket cost')
                        ), (SELECT SUM(cost)
                            FROM kw_tour_travel_ticket
                            WHERE tour_id = t.id
                            AND currency_id = 2
                        )
                    ) AS ticket_usd,
                    COALESCE(
                        (SELECT SUM(amount_inr)
                         FROM kw_tour_settlement_total_expense
                         WHERE settlement_id = ts.id
                         AND expense_id = (SELECT id FROM kw_tour_expense_type WHERE code = 'misc')
                        ), 0
                    ) AS misc_inr,
                    COALESCE(
                        (SELECT SUM(amount_usd)
                         FROM kw_tour_settlement_total_expense
                         WHERE settlement_id = ts.id
                         AND expense_id = (SELECT id FROM kw_tour_expense_type WHERE code = 'misc')
                        ), 0
                    ) AS misc_usd,
                    COALESCE(
                        (SELECT SUM(amount_inr)
                         FROM kw_tour_settlement_total_expense
                         WHERE settlement_id = ts.id
                         AND expense_id = (SELECT id FROM kw_tour_expense_type WHERE code = 'hardship allowance')
                        ), 0
                    ) AS hardship_inr,
                    COALESCE(
                        (SELECT SUM(amount_usd)
                         FROM kw_tour_settlement_total_expense
                         WHERE settlement_id = ts.id
                         AND expense_id = (SELECT id FROM kw_tour_expense_type WHERE code = 'hardship allowance')
                        ), 0
                    ) AS hardship_usd,
                    COALESCE(
                        (SELECT SUM(amount_inr)
                         FROM kw_tour_settlement_total_expense
                         WHERE settlement_id = ts.id
                         AND travel_prerequisite_id = (SELECT id FROM kw_tour_travel_prerequisite WHERE name = 'Visa')
                        ), 0
                    ) AS visa_inr,
                    COALESCE(
                        (SELECT SUM(amount_usd)
                         FROM kw_tour_settlement_total_expense
                         WHERE settlement_id = ts.id
                         AND travel_prerequisite_id = (SELECT id FROM kw_tour_travel_prerequisite WHERE name = 'Visa')
                        ), 0
                    ) AS visa_usd,
                    COALESCE(
                        (SELECT SUM(amount_inr)
                         FROM kw_tour_settlement_total_expense
                        WHERE settlement_id = ts.id
                         AND travel_prerequisite_id = (SELECT id FROM kw_tour_travel_prerequisite WHERE name = 'Vaccine')
                        ), 0
                    ) AS vaccine_inr,
                    COALESCE(
                        (SELECT SUM(amount_usd)
                         FROM kw_tour_settlement_total_expense
                         WHERE settlement_id = ts.id
                         AND travel_prerequisite_id = (SELECT id FROM kw_tour_travel_prerequisite WHERE name = 'Vaccine')
                        ), 0
                    ) AS vaccine_usd,
                    COALESCE(
                        (SELECT SUM(amount_inr)
                         FROM kw_tour_settlement_total_expense
                         WHERE settlement_id = ts.id
                         AND travel_prerequisite_id = (SELECT id FROM kw_tour_travel_prerequisite WHERE name = 'RTPCR Test')
                        ), 0
                    ) AS rtpcr_inr,
                    COALESCE(
                        (SELECT SUM(amount_usd)
                         FROM kw_tour_settlement_total_expense
                         WHERE settlement_id = ts.id
                         AND travel_prerequisite_id = (SELECT id FROM kw_tour_travel_prerequisite WHERE name = 'RTPCR Test')
                        ), 0
                    ) AS rtpcr_usd,
                    COALESCE(
                        (SELECT SUM(amount_inr)
                         FROM kw_tour_settlement_total_expense
                         WHERE settlement_id = ts.id
                         AND expense_id = (SELECT id FROM kw_tour_expense_type WHERE code = 'aex')
                        ), 0
                    ) AS add_exp_inr,
                    COALESCE(
                        (SELECT SUM(amount_usd)
                         FROM kw_tour_settlement_total_expense
                         WHERE settlement_id = ts.id
                         AND expense_id = (SELECT id FROM kw_tour_expense_type WHERE code = 'aex')
                        ), 0
                    ) AS add_exp_usd,
                    (SELECT id FROM account_fiscalyear
                     WHERE (SELECT date_travel FROM kw_tour WHERE id = t.id) BETWEEN date_start AND date_stop
                    ) AS fiscal_year_id,
                    CASE
                        WHEN CURRENT_DATE BETWEEN t.date_travel AND t.date_return THEN 'Tour going on'
                        WHEN t.date_travel > CURRENT_DATE THEN 'Tour yet to start'
                        WHEN t.state = 'Applied' AND ts.tour_id IS NULL THEN 'With RA for tour approval'
                        WHEN t.state = 'Approved' AND ts.tour_id IS NULL THEN 'With travel desk'
                        WHEN t.state = 'Traveldesk Approved' AND ts.tour_id IS NULL THEN 'With Finance for advance'
                        WHEN t.state = 'Finance Approved' AND ts.tour_id IS NULL THEN 'With employee for settlement'
                        WHEN t.state = 'Cancelled' AND ts.tour_id IS NULL THEN 'Cancelled Tour'
                        WHEN t.state = 'Rejected' AND ts.tour_id IS NULL THEN 'Rejected Tour'
                        WHEN t.state = 'Finance Approved' AND ts.state = 'Applied' THEN 'With RA for settlement approval'
                        WHEN t.state = 'Finance Approved' AND ts.state = 'Approved' THEN 'Settlement pending with Finance'
                        WHEN t.state = 'Finance Approved' AND ts.state = 'Granted' THEN 'With Finance for settlement'
                        WHEN t.state = 'Finance Approved' AND ts.state = 'Payment Done' THEN 'Settled and Paid'
                        WHEN t.state = 'Finance Approved' AND ts.state = 'Rejected' THEN 'Rejected'
                        WHEN t.date_return < CURRENT_DATE AND ts.tour_id IS NULL AND t.state = 'Finance Approved' THEN 'With employee for settlement'
                        ELSE '--'
                    END AS state,
                    COALESCE(ts.state, t.state) AS tour_state
                FROM
                    kw_tour t
                JOIN
                    kw_tour_details d ON t.id = d.tour_id
                LEFT JOIN
                    kw_tour_settlement ts ON t.id = ts.tour_id
                WHERE
                    t.state NOT IN ('Draft')
                GROUP BY
                    t.id, ts.id, t.settlement_id, t.code, t.employee_id,
                    t.tour_type_id, t.project_type, t.project_id, t.purpose,
                    t.date_travel, t.date_return, t.state, ts.tour_id, ts.state,
                    ts.domestic_currency_id, ts.usd_currency_id
            )
        """)

    @api.multi
    def action_settlement_details(self):
        settelment_form_view_id = self.env.ref('kw_tour.view_kw_tour_settlement_form_only').id
        tour_form_view_id = self.env.ref('kw_tour.view_kw_tour_view_all_form').id
        if self.settlement_id and self.tour_state not in ('Draft'):
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'kw_tour_settlement',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': settelment_form_view_id,
                'res_id': self.settlement_id.id,
                'target': 'self',
            }
        elif self.tour_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'kw_tour',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': tour_form_view_id,
                'res_id': self.tour_id.id,
                'target': 'self',
            }
        else:
            raise ValidationError("No data Found.")

    @api.multi
    def print_settlement_feedback(self):
        for record in self:
            if not record.settlement_id:
                raise ValidationError("Settlement is required to print the PDF.")
            return self.env.ref('kw_tour.kw_tour_settlement_claim_report').report_action(record)
        # return self.env.ref('kw_tour.kw_tour_settlement_claim_report').report_action(self)
