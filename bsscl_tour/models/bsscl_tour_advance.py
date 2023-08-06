from odoo import models, fields, _, api

class TourAdvance(models.Model):
    _name = 'tour.advance'
    _description = 'Tour Advance'
    _rec_name = 'tour_id'

    tour_id = fields.Many2one(comodel_name="bsscl.tour", string="Tour")
    currency_id = fields.Many2one('res.currency', string="Currency", required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id,
                                  track_visibility='onchange')
    advance_amount = fields.Float(string="Advance Amount") 
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee Name / कर्मचारी का नाम",)
    originating_place_id = fields.Many2one(comodel_name="res.country.state", string="Originating Place / उद्गम स्थल")
    date_of_travel = fields.Date(string="Date Of Travel / यात्रा की तिथि")
    return_date = fields.Date(string="Return Date / वापसी दिनांक")
    travel_arrangement = fields.Selection(string="Travel Arrangement / यात्रा व्यवस्था",
        selection=[('Self', 'Self / खुद'), ('Company', 'Company / कंपनी')], required=True,
        default="Company")
    purpose_of_travel = fields.Text(string="Purpose Of Travel / यात्रा का उद्देश्य")
    travel_expense_details_ids = fields.One2many(comodel_name="bsscl.tour.travel.expense.details",inverse_name="tour_id", string="Travel Expense / यात्रा खर्च")
    medical_exp_ids = fields.One2many(comodel_name="bsscl.medical.expense", inverse_name="tour_id", string="Medical Expense / चिकित्सा खर्च")
    telephone_bill_exp_ids = fields.One2many(comodel_name="bsscl.telephone.expense", inverse_name="tour_id")
    tour_details_ids = fields.One2many(comodel_name="bsscl.tour.details", inverse_name="tour_id", string="Tour Details / भ्रमण विवरण")
    state = fields.Selection([('1','Draft'),('2','Applied'),('3','Approved'),('4','Canceled')], string="State")

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
                for record in rec.tour_id.travel_expense_details_ids:
                    print("============rec.travel_expense_details_ids======================",rec.travel_expense_details_ids.ids)
                    rec.travel_expense_details_ids.write({
                        'expense_type_id': record.expense_type_id,
                        'currency_id': record.currency_id,
                        'amount': record.amount,
                    })
            else:
                return False
    
    @api.model
    def create(self,vals):
        res =super(TourAdvance, self).create(vals)
        print("=============Vals=========================",vals)
        res.state = '1'
        return res

    def apply_advance_request(self):
        for rec in self:
            rec.state = '2'

    def approved_advance_request(self):
        for rec in self:
            rec.tour_id.advance_amount = rec.advance_amount
            rec.state = '3' 
        
    def advance_request_cancel(self):
        for rec in self:
            rec.state = '4'
    