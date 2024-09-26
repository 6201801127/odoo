from odoo import api, fields, models, _
from odoo.exceptions import UserError

class TourClaimWizard(models.TransientModel):
    _name = 'tour.claim.wizard'
    _description = "Tour Claim Wizard"

    # @api.depends('unpaid_detail_of_journey','unpaid_detail_of_journey.paid')
    # def get_loan_close_lines(self):
    #         temp = 0.0
    #         for line in self.unpaid_detail_of_journey:
    #             if line.paid:
    #                 temp += line.amount
    #                 # print("amount===============>>>>",temp,line.amount)
    #         self.loan_amount = temp

    claim_id = fields.Many2one('employee.tour.claim', string="Claim Ref.")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    unpaid_detail_of_journey = fields.One2many('tour.wizard.line','un_claim_id', string="Details of Journey", index=True)
    remarks = fields.Char(string='Remarks')


    @api.multi
    def confirm_loan_payment(self):
        self.claim_id.detail_of_journey.unlink()
        self.claim_id.detail_of_journey_lodging.unlink()
        self.claim_id.detail_of_journey_leave.unlink()
        for i in self.unpaid_detail_of_journey:
            if i.done:
                self.env['tour.claim.journey'].create({
                    'tour_sequence': i.tour_sequence,
                    'departure_date': i.departure_date,
                    'departure_time': i.departure_time,
                    'arrival_date': i.arrival_date,
                    'arrival_time': i.arrival_time,
                    'from_l': i.from_l.id,
                    'to_l': i.to_l.id,
                    'travel_mode': i.travel_mode.id,
                    'mode_detail': i.mode_detail,
                    'travel_entitled': i.travel_entitled,
                    'boarding': i.boarding,
                    'lodging': i.lodging,
                    'conveyance': i.conveyance,
                    'employee_journey': self.claim_id.id,
                    })
                self.env['tour.claim.journey.lodging'].create({
                    'tour_sequence': i.tour_sequence,
                    'employee_journey': self.claim_id.id,
                    })
                self.env['employee.leave.taken'].create({
                    'tour_sequence': i.tour_sequence,
                    'employee_journey': self.claim_id.id,
                    'employee_id': self.claim_id.employee_id.id,
                    'departure_date': i.departure_date,
                    'arrival_date': i.arrival_date,
                    'from_l': i.from_l.id,
                    'to_l': i.to_l.id,
                    })


class TourWizardLine(models.TransientModel):
    _name = "tour.wizard.line"
    _description = "Tour Wizard Line"

    done = fields.Boolean('Check')
    un_claim_id = fields.Many2one('tour.claim.wizard', string='Claim')
    tour_sequence = fields.Char('Tour number')
    employee_journey = fields.Many2one('employee.tour.claim')
    departure_date = fields.Date('Departure Date')
    arrival_date = fields.Date('Arrival Date')
    from_l = fields.Many2one('res.city', string='From City')
    to_l = fields.Many2one('res.city', string='To City')
    departure_time = fields.Float('Departure Time')
    arrival_time = fields.Float('Arrival Time')
    travel_mode = fields.Many2one('travel.mode', string='Mode of Travel')
    mode_detail = fields.Char('Flight/Train No.')
    travel_entitled = fields.Boolean('Is Travel Mode Entitled?')
    boarding = fields.Boolean('Boarding required?')
    lodging = fields.Boolean('Lodging required?')
    conveyance = fields.Boolean('Local Conveyance required?')
