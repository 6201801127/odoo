from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError,UserError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import re

class TourRequest(models.Model):
    _name = "tour.request"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Tour Request"


    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)


    employee_id = fields.Many2one('hr.employee', string="Requested By", default=_default_employee,track_visibility='always')
    date = fields.Date(string='Requested Date', default=fields.Date.today())
    designation = fields.Many2one('hr.job', string="Designation", compute='compute_des_dep')
    branch_id= fields.Many2one('res.branch', string="Branch", compute='compute_des_dep', store=True)
    department = fields.Many2one('hr.department', string="Department", compute='compute_des_dep')
    purpose = fields.Char(string="Purpose",track_visibility='always')
    employee_journey = fields.One2many('tour.request.journey','employee_journey', string="Employee Journey")
    tour_sequence = fields.Char('Tour number',track_visibility='always')
    claimed = fields.Boolean('Claimed')
    advance_requested = fields.Float(' Advance Amount (Rs.)')
    vehicle_required = fields.Selection([('yes', 'Yes'), ('no', 'No')],string='Vehicle Required?',track_visibility='always')
    vehicle_address = fields.Char('Address')
    vehicle_phone = fields.Char("Phone Number")
    vehicle_date_from = fields.Date('Date')
    vehicle_day1 = fields.Selection([('full', 'Full'), ('half', 'Half')],string='Day:')
    vehicle_date_to = fields.Date('Returning Date')
    vehicle_day2 = fields.Selection([('full', 'Full'), ('half', 'Half')])
    vehicle_remarks = fields.Text('Remarks')


    state = fields.Selection([('draft', 'Draft'), ('waiting_for_approval', 'Waiting for Approval'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('cancelled', 'Cancelled')
                               ], required=True, string='Status', default='draft',track_visibility='always')


    def onchange_tour_request_state(self):
        group_id = self.env.ref('tour_request.group_tour_claim_approvere')
        resUsers = self.env['res.users'].sudo().search([]).filtered(lambda r: group_id.id in r.groups_id.ids and self.branch_id.id in r.branch_ids.ids).mapped('partner_id')
        if resUsers:
            employee_partner = self.employee_id.user_id.partner_id
            if employee_partner:
                resUsers += employee_partner
            message = "Tour Request of %s is move to %s"%(self.employee_id.name, dict(self._fields['state'].selection).get(self.state))
            self.env['mail.message'].create({'message_type':"notification",
                "subtype_id": self.env.ref("mail.mt_comment").id,
                'body': message,
                'subject': "Tour request",
                'needaction_partner_ids': [(4, p.id, None) for p in resUsers],
                'model': self._name,
                'res_id': self.id,
                })
            self.env['mail.thread'].message_post(
                body=message,
                partner_ids=[(4, p.id, None) for p in resUsers],
                subtype='mail.mt_comment',
                notif_layout='mail.mail_notification_light',
            )

    @api.multi
    def button_to_approve(self):
        for rec in self:
            rec.onchange_tour_request_state()
            rec.write({'state': 'waiting_for_approval'})

    @api.multi
    def button_cancel(self):
        for rec in self:
            rec.onchange_tour_request_state()
            rec.write({'state': 'cancelled'})
    #
    # @api.multi
    # def button_forwarded(self):
    #     for rec in self:
    #         rec.write({'state': 'forwarded'})

    @api.multi
    def button_approved(self):
        for rec in self:
            rec.onchange_tour_request_state()
            rec.write({'state': 'approved'})

    # @api.multi
    # def button_processed(self):
    #     for rec in self:
    #         rec.write({'state': 'processed'})

    @api.multi
    def button_reject(self):
        for rec in self:
            rec.onchange_tour_request_state()
            rec.write({'state': 'rejected'})

    @api.multi
    def button_reschedule(self):
        for rec in self:
            rec.onchange_tour_request_state()
            rec.write({'state': 'draft'})


    @api.multi
    def unlink(self):
        for tour in self:
            if tour.state != 'draft':
                raise UserError(
                    'You cannot delete a Tour Request which is not in draft state')
        return super(TourRequest, self).unlink()

    @api.multi
    def button_reset_to_draft(self):
        self.ensure_one()
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        ctx = dict(
            default_composition_mode='comment',
            default_res_id=self.id,

            default_model='tour.request',
            default_is_log='True',
            custom_layout='mail.mail_notification_light'
        )
        mw = {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
        self.write({'state': 'draft'})
        return mw

    @api.depends('employee_id')
    def compute_des_dep(self):
        for rec in self:
            rec.designation = rec.employee_id.job_id.id
            rec.department = rec.employee_id.department_id.id
            rec.branch_id = rec.employee_id.branch_id.id

    @api.multi
    @api.depends('employee_id')
    def name_get(self):
        res = []
        name = ''
        for record in self:
            if record.employee_id:
                name = record.employee_id.name + ' - Tour Request'
            else:
                name = 'Tour Request'
            res.append((record.id, name))
        return res


    @api.model
    def create(self, vals):
        res =super(TourRequest, self).create(vals)
        sequence = ''
        seq = self.env['ir.sequence'].next_by_code('tour.request')
        sequence = 'Tour Request - ' + seq
        res.tour_sequence = sequence
        res.onchange_tour_request_state()
        return res

    @api.multi
    @api.depends('tour_sequence')
    def name_get(self):
        res = []
        for record in self:
            if record.tour_sequence:
                name = record.tour_sequence
            else:
                name = 'Tour Request'
            res.append((record.id, name))
        return res


class TourRequestJourney(models.Model):

    _name = "tour.request.journey"
    _description = "Tour Request Journey Details"

    employee_id = fields.Many2one('hr.employee', string="Employee", related='employee_journey.employee_id')
    employee_journey = fields.Many2one('tour.request')
    tour_sequence = fields.Char(related='employee_journey.tour_sequence', string='Tour Sequence')

    travel_mode = fields.Many2one('travel.mode', string='Requested Mode of Travel')
    mode_detail = fields.Char('Flight / Train / Others Number')
    mode_of_travlel = fields.Selection([('air', 'By Air'), ('train', 'By Train'), ('road', 'By Road'), ('sea', 'By Sea')], string='Mode of Travel')
    coc_air = fields.Selection([('first', 'First Class'), ('business', 'Business Class'), ('economy', 'Economy Class')], string='Class of Accomodation')
    coc_train = fields.Selection([('ac1', 'AC 1-Tier'), ('ac2', 'AC 2-Tier'), ('ac3', 'AC 3-Tier'), ('1st', 'First Class'), ('ac_chair', 'A.C Chair Class'), ('sleeper', 'Sleeper'), ('2nd_sit', 'Second Sitting')], string='Class of Accomodation')
    coc_bus = fields.Selection([('ac', 'AC'), ('n_ac', 'Non AC'), ('seater', 'Seater'), ('semi_sleep', 'Semi Sleeper'), ('sleeper', 'Sleeper')], string='Class of Accomodation')
    coc_sea = fields.Selection([('higher', 'Higher Class'), ('lower', 'Lower Class')], string='Class of Accomodation')
    departure_date = fields.Date('Departure Date')
    departure_time = fields.Float('Departure Time')
    arrival_time = fields.Float('Arrival Time')
    arrival_date = fields.Date('Arrival Date')
    from_l = fields.Many2one('res.city', string='From City')
    to_l = fields.Many2one('res.city', string='To City')
    travel_entitled = fields.Boolean('Is Travel Mode Entitled?')
    boarding = fields.Boolean('Boarding required?')
    lodging = fields.Boolean('Lodging required?')
    conveyance = fields.Boolean('Local Conveyance required?')
    exceptional_reason = fields.Text('Exceptional Reason')

    @api.constrains('departure_date','arrival_date')
    def dep_less_arrival(self):
        for rec in self:
            if rec.arrival_date < rec.departure_date:
                raise UserError(
                    'Arrival date must be greater than departure date')

    @api.onchange('travel_mode')
    def travel_mode_entitled(self):
        employee_contract_id = self.env['hr.contract'].search([('employee_id','=',self.env.user.employee_ids.id),('state','=','open')],limit=1)
        if self.travel_mode.id in employee_contract_id.pay_level_id.tour_travel_modes.ids:
            self.travel_entitled = True
        else: 
            self.travel_entitled = False

#
#
# class EmployeeTourClaim(models.Model):
#     _name = 'employee.tour.claim'
#     _description = 'Tour Claim'
#
#
#
#
#     def _default_employee(self):
#         return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
#
#     @api.multi
#     @api.depends('detail_of_journey','employee_id')
#     def _compute_approved_amount(self):
#         total_claimed = 0.0
#         advance_requested = 0.0
#         for record in self:
#             tour_req = self.env['tour.request'].search([('employee_id', '=', record.employee_id.id),('state', '=', 'approved')])
#             for i in tour_req:
#                 if i:
#                     advance_requested += i.advance_requested
#             for line in record.detail_of_journey_lodging:
#                 if line:
#                     total_claimed += ((line.daily_lodging_charge + line.daily_boarding_charge + line.daily_boarding_lodginf_charge)*line.no_of_days + line.other_details)
#             record.total_claimed_amount = total_claimed
#             record.advance_requested = advance_requested
#             record.balance_left = record.total_claimed_amount - record.advance_requested - record.amount_paid
#
#
#     employee_id = fields.Many2one('hr.employee', string='Employee', default=_default_employee)
#     designation = fields.Many2one('hr.job', string="Designation", compute='compute_des_dep')
#     department = fields.Many2one('hr.department', string="Department", compute='compute_des_dep', store=True)
#     detail_of_journey = fields.One2many('tour.claim.journey','employee_journey')
#     detail_of_journey_lodging = fields.One2many('tour.claim.journey.lodging','employee_journey')
#     detail_of_journey_leave = fields.One2many('employee.leave.taken','employee_journey')
#     advance_requested = fields.Float(string="Advance Requested", readonly=True, compute='_compute_approved_amount')
#     balance_left = fields.Float(string="Balance left", readonly=True, compute='_compute_approved_amount')
#     tour_sequence = fields.Char(string="tour sequence")
#     total_claimed_amount = fields.Float(string="Total Claimed Amount", compute='_compute_approved_amount')
#     amount_paid = fields.Float(string="Amount Paid")
#     from_date_camp = fields.Date(string='From Date')
#     to_date_camp = fields.Date(string='To Date')
#     leave_taken = fields.Many2one('hr.leave', string='Date of absence from place of halt ',
#                                    )
#
#     state = fields.Selection(
#         [('draft', 'Draft'), ('submitted', 'Waiting for Approval'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('paid', 'Paid')
#          ], required=True, default='draft', string='Status')
#     action_app = fields.Boolean('Action Approve bool', invisible=1)
#     action_clos = fields.Boolean('Action Paid Close bool', invisible=1)
#
#     @api.depends('employee_id')
#     def compute_des_dep(self):
#         for rec in self:
#             rec.designation = rec.employee_id.job_id.id
#             rec.department = rec.employee_id.department_id.id
#
#     @api.multi
#     def button_submit(self):
#         for rec in self:
#             rec.write({'state': 'submitted'})
#
#     @api.multi
#     def button_reject(self):
#         for rec in self:
#             rec.write({'state': 'rejected'})
#
#
#     @api.multi
#     def unlink(self):
#         for tour in self:
#             if tour.state != 'draft':
#                 raise UserError(
#                     'You cannot delete a Tour Claim which is not in draft state')
#         return super(EmployeeTourClaim, self).unlink()
#
#
#
#     @api.multi
#     def button_reset_to_draft(self):
#         self.ensure_one()
#         compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
#         ctx = dict(
#             default_composition_mode='comment',
#             default_res_id=self.id,
#
#             default_model='employee.tour.claim',
#             default_is_log='True',
#             custom_layout='mail.mail_notification_light'
#         )
#         mw = {
#             'type': 'ir.actions.act_window',
#             'view_type': 'form',
#             'view_mode': 'form',
#             'res_model': 'mail.compose.message',
#             'view_id': compose_form_id,
#             'target': 'new',
#             'context': ctx,
#         }
#         self.write({'state': 'draft'})
#         return mw
#
#     @api.multi
#     def button_approved(self):
#         for rec in self:
#             rec.write({'state': 'approved'})
#
#
#     @api.multi
#     def button_pay(self):
#         for rec in self:
#             rec.amount_paid = rec.total_claimed_amount - rec.advance_requested
#             tour_req = self.env['tour.request.journey'].search(
#                 [('employee_id', '=', rec.employee_id.id), ('employee_journey.state', '=', 'approved'),
#                  ('employee_journey.claimed', '=', False)], order='tour_sequence desc')
#             for tour in tour_req:
#                 tour.employee_journey.claimed = True
#             rec.write({'state': 'paid'})
#     #
#     # @api.multi
#     # def get_journey_details(self):
#     #     detail_of_journey = []
#     #     for rec in self:
#     #         rec.detail_of_journey.unlink()
#     #         if rec.employee_id:
#     #             tour_req = self.env['tour.request.journey'].search([('employee_id', '=', rec.employee_id.id),('employee_journey.state', '=', 'approved'),('claimed', '=', False)], order='tour_sequence desc')
#     #             for i in tour_req:
#     #                 detail_of_journey.append((0, 0, {
#     #                     'tour_sequence': i.tour_sequence,
#     #                     'departure_date': i.departure_date,
#     #                     'departure_time': i.departure_time,
#     #                     'arrival_date': i.arrival_date,
#     #                     'arrival_time': i.arrival_time,
#     #                     'from_l': i.from_l,
#     #                     'to_l': i.to_l,
#     #                     'travel_mode': i.travel_mode,
#     #                     'mode_detail': i.mode_detail,
#     #                     'travel_entitled': i.travel_entitled,
#     #                     'boarding': i.boarding,
#     #                     'lodging': i.lodging,
#     #                     'conveyance': i.conveyance,
#     #                     'employee_journey': self.id
#     #                 }))
#     #             self.detail_of_journey = detail_of_journey
#
#     @api.multi
#     def get_journey_details(self):
#         ctx = self._context.copy()
#         view = self.env.ref('tour_request.form_view_tour_claim_wizard')
#         # tour_req = self.detail_of_journey.search([('paid', '=', False), ('claim_id', '=', self.id)])
#         tour_req = self.env['tour.request.journey'].search(
#             [('employee_id', '=', self.employee_id.id), ('employee_journey.state', '=', 'approved'),
#              ('employee_journey.claimed', '=', False)], order='tour_sequence desc')
#
#         wiz = self.env['tour.claim.wizard'].create({
#             'employee_id': self.employee_id.id,
#             'claim_id': self.id,
#         })
#         for i in tour_req:
#             self.env['tour.wizard.line'].create({
#                         'tour_sequence': i.tour_sequence,
#                         'departure_date': i.departure_date,
#                         'departure_time': i.departure_time,
#                         'arrival_date': i.arrival_date,
#                         'arrival_time': i.arrival_time,
#                         'from_l': i.from_l.id,
#                         'to_l': i.to_l.id,
#                         'travel_mode': i.travel_mode.id,
#                         'mode_detail': i.mode_detail,
#                         'travel_entitled': i.travel_entitled,
#                         'boarding': i.boarding,
#                         'lodging': i.lodging,
#                         'conveyance': i.conveyance,
#                         'employee_journey': self.id,
#                         'un_claim_id': wiz.id
#
#             })
#         return {
#             'name': 'Tour Claim',
#             'type': 'ir.actions.act_window',
#             'view_type': 'form',
#             'view_mode': 'form',
#             'res_model': 'tour.claim.wizard',
#             'views': [(view.id, 'form')],
#             'view_id': view.id,
#             'res_id': wiz.id,
#             'target': 'new',
#         }
#
#     @api.multi
#     @api.depends('employee_id')
#     def name_get(self):
#         res = []
#         name = ''
#         for record in self:
#             if record.employee_id:
#                 name = str(record.employee_id.name) + ' - Tour Claim'
#             else:
#                 name = 'Tour Claim'
#             res.append((record.id, name))
#         return res
#
#
# class TourClaimJourney(models.Model):
#
#     _name = "tour.claim.journey"
#     _description = "Tour Claim Journey Details"
#
#
#     #
#     # @api.multi
#     # @api.depends('daily_lodging_charge','daily_boarding_charge','daily_boarding_lodginf_charge','no_of_days')
#     # def _Compute_total_amount_paid(self):
#     #     for rec in self:
#     #         rec.total_amount_paid = (rec.daily_lodging_charge + rec.daily_boarding_charge + rec.daily_boarding_lodginf_charge)*rec.no_of_days
#
#
#     tour_sequence = fields.Char('Tour number')
#     employee_journey = fields.Many2one('employee.tour.claim', invisible=1)
#     departure_date = fields.Date('Departure Date')
#     arrival_date = fields.Date('Arrival Date')
#     from_l = fields.Many2one('res.city', string='From City')
#     to_l = fields.Many2one('res.city', string='To City')
#     departure_time = fields.Float('Departure Time')
#     arrival_time = fields.Float('Arrival Time')
#     amount_claimed = fields.Float('Amount Claimed')
#     distance = fields.Float('Distance')
#     approved_approved = fields.Float('Approved Amount')
#     travel_mode = fields.Many2one('travel.mode', string='Mode of Travel')
#     mode_detail = fields.Char('Flight/Train No.')
#     travel_entitled = fields.Boolean('Is Travel Mode Entitled?')
#     boarding = fields.Boolean('Boarding required?')
#     lodging = fields.Boolean('Lodging required?')
#     conveyance = fields.Boolean('Local Conveyance required?')
#     # arranged_by = fields.Selection([('self', 'Self'), ('company', 'Company')], string='Arranged By')
#     # from_date = fields.Date('From Date')
#     # to_date = fields.Date('To Date')
#     # no_of_days = fields.Float('No. of days', compute='compute_no_of_days', store=True)
#     # name_of_hotel = fields.Char('Name of Hotel/Guest House')
#     # daily_lodging_charge = fields.Float('Daily Lodging Charges')
#     # daily_boarding_charge = fields.Float('Daily Boarding Charges')
#     # daily_boarding_lodginf_charge = fields.Float('Daily Lodging and Boarding Charges')
#     # total_amount_paid = fields.Float('Total Amount Paid', compute='_Compute_total_amount_paid')
#     # other_details = fields.Float('Details of other reimbursable expenses ')
#
#     state = fields.Selection(
#         [('draft', 'Draft'), ('submitted', 'Waiting for Approval'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('paid', 'Paid')
#          ], related='employee_journey.state')
#
#
#     #
#     # @api.constrains('from_date','to_date')
#     # def compute_no_of_days(self):
#     #     for rec in self:
#     #         rec.no_of_days = (rec.to_date - rec.from_date).days
#     #
#     #
#
#
# class EmployeeLeaveTaken(models.Model):
#     _name = 'employee.leave.taken'
#     _description = 'Leave Taken'
#
#
#     tour_sequence = fields.Char('Tour number')
#     employee_journey = fields.Many2one('employee.tour.claim', invisible=1)
#     employee_id = fields.Many2one('hr.employee', string='Employee')
#     departure_date = fields.Date('Departure Date')
#     arrival_date = fields.Date('Arrival Date')
#     from_l = fields.Many2one('res.city', string='From City')
#     to_l = fields.Many2one('res.city', string='To City')
#     from_date_camp = fields.Date(string='From Date', compute='compute_get_leave_details')
#     to_date_camp = fields.Date(string='To Date', compute='compute_get_leave_details')
#     leave_taken = fields.Many2one('hr.leave', string='Date of absence from place of halt ',
#                                   domain="[('state','=','approved'),('employee_id','=',employee_id),('request_date_from','<=',departure_date),('request_date_to','>=',arrival_date)]"
#                                    )
#
#     state = fields.Selection(
#         [('draft', 'Draft'), ('submitted', 'Waiting for Approval'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('paid', 'Paid')
#          ], required=True, default='draft', string='Status')
#
#
#
#     @api.depends('leave_taken')
#     def compute_get_leave_details(self):
#         for line in self:
#             if line.leave_taken:
#                 line.from_date_camp = line.leave_taken.request_date_from
#                 line.to_date_camp = line.leave_taken.request_date_to
#
#
#
# class JourneyLodgingBoarding(models.Model):
#
#     _name = "tour.claim.journey.lodging"
#     _description = "Tour Claim Journey Details Lodging Boarding"
#
#
#
#     @api.multi
#     @api.depends('daily_lodging_charge','daily_boarding_charge','daily_boarding_lodginf_charge','no_of_days')
#     def _Compute_total_amount_paid(self):
#         for rec in self:
#             rec.total_amount_paid = (rec.daily_lodging_charge + rec.daily_boarding_charge + rec.daily_boarding_lodginf_charge)*rec.no_of_days
#
#
#     tour_sequence = fields.Char('Tour number')
#     employee_journey = fields.Many2one('employee.tour.claim', invisible=1)
#     arranged_by = fields.Selection([('self', 'Self'), ('company', 'Company')], string='Arranged By')
#     from_date = fields.Date('From Date')
#     to_date = fields.Date('To Date')
#     no_of_days = fields.Float('No. of days', compute='compute_no_of_days', store=True)
#     name_of_hotel = fields.Char('Name of Hotel/Guest House')
#     daily_lodging_charge = fields.Float('Daily Lodging Charges')
#     daily_boarding_charge = fields.Float('Daily Boarding Charges')
#     daily_boarding_lodginf_charge = fields.Float('Daily Lodging and Boarding Charges')
#     total_amount_paid = fields.Float('Total Amount Paid', compute='_Compute_total_amount_paid')
#     other_details = fields.Float('Details of other reimbursable expenses ')
#
#     state = fields.Selection(
#         [('draft', 'Draft'), ('submitted', 'Waiting for Approval'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('paid', 'Paid')
#          ], related='employee_journey.state')
#
#
#
#     @api.constrains('from_date','to_date')
#     def compute_no_of_days(self):
#         for rec in self:
#             rec.no_of_days = (rec.to_date - rec.from_date).days
#
#
#
#



class TravelMode(models.Model):

    _name = "travel.mode"
    _description = "Travel Mode"

    name = fields.Char('Name')

class HrPaySlip(models.Model):
    _inherit='hr.payslip.paylevel'

    tour_travel_modes = fields.Many2many('travel.mode',string="Travel Modes")
    tour_advance_cost = fields.Float('Tour Advance Amount')