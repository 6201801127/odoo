from odoo import models, fields, _, api
from odoo.exceptions import ValidationError

class TourSettlement(models.Model):
    _name = 'tour.settlement'
    _description = 'Tour Settlement'
    _rec_name = 'tour_id'

    tour_id = fields.Many2one(comodel_name="bsscl.tour", string="Tour")
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee Name / कर्मचारी का नाम",)
    originating_place_id = fields.Many2one(comodel_name="res.country.state", string="Originating Place / उद्गम स्थल")
    date_of_travel = fields.Date(string="Date Of Travel / यात्रा की तिथि")
    return_date = fields.Date(string="Return Date / वापसी दिनांक")
    travel_arrangement = fields.Selection(string="Travel Arrangement / यात्रा व्यवस्था",
        selection=[('Self', 'Self / खुद'), ('Company', 'Company / कंपनी')], required=True,
        default="Company")
    purpose_of_travel = fields.Text(string="Purpose Of Travel / यात्रा का उद्देश्य")
    travel_expense_details_ids = fields.One2many(comodel_name="bsscl.tour.travel.expense.details",inverse_name="tour_settlement_id", string="Travel Expense / यात्रा खर्च")
    medical_exp_ids = fields.One2many(comodel_name="bsscl.medical.expense", inverse_name="settlement_id", string="Medical Expense / चिकित्सा खर्च")
    telephone_bill_exp_ids = fields.One2many(comodel_name="bsscl.telephone.expense", inverse_name="settlement_id")
    tour_details_ids = fields.One2many(comodel_name="bsscl.tour.details", inverse_name="settlement_id", string="Tour Details / भ्रमण विवरण")
    state = fields.Selection([('1','Draft'),('2','Applied'),('3','Approved'),('4','Grant'),('5','Payment Done'),('6','Canceled')], string="State")
    travel_booking_ids = fields.One2many(comodel_name="travel.booking", inverse_name="settlement_id" , string="Travel Booking Details")
    currency_id = fields.Many2one('res.currency', string="Currency", required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id,
                                  track_visibility='onchange')
    amount_total = fields.Float(string="Total", compute="_compute_amount_total")

    @api.depends('travel_booking_ids.travel_cost')
    def _compute_amount_total(self):
        for rec in self:
            if rec.travel_booking_ids:
                total_sum = 0
                for record in rec.travel_booking_ids:
                    if record.travel_cost:
                        total_sum += record.travel_cost
                        rec.amount_total = total_sum
                    else:
                        rec.amount_total = 0.0
            else:
                rec.amount_total = 0.0

    @api.onchange('tour_id')
    def _onchange_tour_id(self):
        for rec in self:
            if rec.tour_id:
                rec.employee_id = rec.tour_id.employee_id
                rec.originating_place_id = rec.tour_id.originating_place_id
                rec.date_of_travel = rec.tour_id.date_of_travel
                rec.return_date = rec.tour_id.return_date
                rec.travel_arrangement = rec.tour_id.travel_arrangement
                rec.purpose_of_travel = rec.tour_id.purpose_of_travel
                if rec.tour_id.travel_expense_details_ids.tour_id == rec.tour_id:
                    rec.travel_expense_details_ids = rec.tour_id.travel_expense_details_ids
                    rec.tour_details_ids = rec.tour_id.tour_details_ids
                    rec.medical_exp_ids = rec.tour_id.medical_exp_ids
                    rec.telephone_bill_exp_ids = rec.tour_id.telephone_bill_exp_ids
            else:
                return False
            
    @api.model
    def create(self,vals):
        res =super(TourSettlement, self).create(vals)
        print("=============Vals=========================",vals)
        res.state = '1'
        return res

    def apply_tour_settlement(self):
        for rec in self:
            rec.state = '2'

    def approved_tour_settlement(self):
        for rec in self:
            if not rec.travel_booking_ids:
                raise ValidationError("Booking details missing please provide travel booking details before settlement approved.")
            rec.tour_id.travel_booking_ids = rec.travel_booking_ids
            rec.state = '3'
    
    def grant_tour_settlement(self):
        for rec in self:
            rec.state = '4'

    def payment_done_tour_settlement(self):
        for rec in self:
            rec.state = '5'

    def settlement_cancel(self):
        for rec in self:
            rec.state = '6'