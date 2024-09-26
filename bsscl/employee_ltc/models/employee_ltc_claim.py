from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime, date

class EmployeeLtcClaim(models.Model):
    _name = 'employee.ltc.claim'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description='Claim Submission'

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    
    @api.depends('ltc_availed_for_m2o')
    def _compute_approved_amount(self):
        total_claimed = 0.0
        fair_paid = 0
        total_cl_journey = 0.0
        for record in self:
            for line in record.detail_of_journey:
                if line:
                    fair_paid += int(line.fair_paid)
            for line in record.detail_of_journey_gov:
                if line:
                    fair_paid += int(line.fair_paid)
            record.total_claimed_amount = fair_paid
            record.advance_requested = round(record.ltc_availed_for_m2o.single_fare_approved)
            record.balance_left = record.total_claimed_amount - record.advance_requested - record.amount_paid



    employee_id = fields.Many2one('hr.employee', default=_default_employee,track_visibility='always')
    branch_id = fields.Many2one('res.branch', string='Branch', store=True)
    job_id = fields.Many2one('hr.job', string='Functional Designation', store=True)
    department_id = fields.Many2one('hr.department', string='Department', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id)
    # amount_claimed = fields.Char('Advance Withdrawn')
    place_of_trvel=fields.Selection([('hometown', 'Hometown'), ('india', 'Anywhere in India'), ('conversion', 'Conversion of Hometown')], default='hometown', string='Place of Travel',track_visibility='always', compute='_compute_fetch_ltc_details')
    ltc_availed_for_m2o = fields.Many2one('employee.ltc.advance',track_visibility='always')
    ltc_availed_for = fields.Char(compute='_compute_fetch_ltc_details',track_visibility='always')
    leave_period = fields.Char('Leave Period', compute='_compute_fetch_ltc_details',track_visibility='always')
    place_of_visit = fields.Char('Place of Visit',track_visibility='always', compute='_compute_fetch_ltc_details')
    relative_claim_ids = fields.One2many('family.claim.ltc','relative_claim_id',track_visibility='always')
    detail_of_journey = fields.One2many('employee.ltc.journey','relate_to_ltc', track_visibility='always')
    detail_of_journey_gov = fields.One2many('employee.ltc.journey.gov','relate_to_ltc',track_visibility='always')
    detail_of_journey_train = fields.One2many('employee.ltc.journey.train','relate_to_ltc', track_visibility='always')
    remarks = fields.Char(string='Remarks')
    total_claimed_amount = fields.Float('Total Claimed Amount', compute='_compute_approved_amount')
    advance_requested = fields.Float('Advance Requested', compute='_compute_approved_amount')
    amount_paid = fields.Float('Amount Paid')
    balance_left = fields.Float('Balance Left', compute='_compute_approved_amount')
    state = fields.Selection(
        [('draft', 'Draft'), ('to_approve', 'To Approve'), ('approved', 'Approved'), ('settled', 'Settled'), ('rejected', 'Rejected')
         ], required=True, default='draft',track_visibility='always', string='Status')
    bank_document = fields.Binary(string="Payment Details",help='Bank and Cheque DetailsTechnical Field',attachment=True)
    bank_document_filename = fields.Char(string="Bank Document File Name")
    remarks = fields.Text('Remarks')
    check_self = fields.Boolean('check_self',compute='_compute_self_name')

    @api.constrains('ltc_availed_for_m2o')
    def validate_duplicate_claim(self):
        for claim in self:
            if claim.search([('state','!=','rejected'),('ltc_availed_for_m2o','=',claim.ltc_availed_for_m2o.id)]) - claim:
                raise ValidationError("You can't claim a LTC twice.")
                
    @api.onchange('employee_id')
    @api.constrains('employee_id')
    def onchange_emp_get_base(self):
        for rec in self:
            rec.job_id = rec.employee_id.job_id.id
            rec.department_id = rec.employee_id.department_id.id
            rec.branch_id = rec.employee_id.branch_id.id

    
    def button_to_approve(self):
        for rec in self:
            if len(rec.detail_of_journey) == 0:
                raise ValidationError("Please Enter Your Details of Journey.")
            else:
                rec.write({'state': 'to_approve'})

     # (wagisha) check RA of an employee
    @api.depends('employee_id')
    def _compute_self_name(self):
        for rec in self:
            if rec.employee_id.parent_id.user_id.id == self.env.user.id:
                rec.check_self= True
            else :
                rec.check_self= False
    
    def button_approved(self):
        for rec in self:
            rec.write({'state': 'approved'})

    
    def button_reject(self):
        for rec in self:
            rec.write({'state': 'rejected'})

    
    def button_reset_to_draft(self):
        for rec in self:
            rec.write({'state': 'draft'})

    
    def open_ltc_claim_wizard(self):
        form_view_id = self.env.ref("employee_ltc.view_ltc_wizard_form").id 
        action= {
            'name':'Alert',
            'type': 'ir.actions.act_window',
            'res_model': 'employee.ltc.claim',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'view_id': form_view_id,
            'target': 'new',
        }
        return action

    
    def button_settled(self):
        for rec in self:
            if rec.balance_left == 0:
                pass
            elif rec.balance_left < 0 or rec.balance_left > 0:
                if not rec.bank_document:
                    raise ValidationError('Please fill the Payment Details.')
                if rec.amount_paid == 0:
                    raise ValidationError('Please enter the paid amount.')
            rec.write({'state': 'settled'})
    
    @api.depends('ltc_availed_for_m2o')
    def _compute_fetch_ltc_details(self):
        for rec in self:
            if rec.employee_id:
                # ltc_ad = self.env['employee.ltc.advance'].search([('employee_id','=',rec.employee_id.id)],order='ltc_sequence desc', limit=1)
                # rec.amount_claimed = rec.ltc_availed_for_m2o.amount
                rec.leave_period = rec.ltc_availed_for_m2o.leave_period
                rec.ltc_availed_for = rec.ltc_availed_for_m2o.ltc_sequence
                rec.place_of_trvel = rec.ltc_availed_for_m2o.place_of_trvel
                rec.place_of_visit = rec.ltc_availed_for_m2o.hometown_address

    
    @api.depends(' ','employee_id')
    def name_get(self):
        res = []
        name = ''
        for record in self:
            if record.ltc_availed_for and record.employee_id:
                name = str(record.employee_id.name) + ' - ' + str(record.ltc_availed_for) + ' - LTC Claim'
            else:
                name = 'LTC Claim'
            res.append((record.id, name))
        return res



    @api.onchange('ltc_availed_for_m2o')
    @api.constrains('ltc_availed_for_m2o')
    def get_journey_details_ltc(self,working_list=None):
        for rec in self:
            relative_claim_ids = []
            for i in rec.ltc_availed_for_m2o.relative_ids:
                relative_claim_ids.append((0, 0, {
                    'relative_claim_id': rec.id,
                    'relative_id': i.relative_id.id,
                    'name': i.name.id,
                    'relation': i.relation,
                    'age': i.age,
                }))
            else:
                rec.relative_claim_ids = working_list
            rec.relative_claim_ids = relative_claim_ids



class FamilyDetails(models.Model):
    _name = 'family.claim.ltc'
    _description = "LTC Family Details Claim"



    relative_id = fields.Many2one('employee.ltc.advance', string='Relative ID')
    relative_claim_id = fields.Many2one('employee.ltc.claim', string='Relative ClaIm ID')
    name = fields.Many2one('employee.relative','Name')
    relation = fields.Char(string='Relation')
    age = fields.Float(string='Age')



class JourneyDetails(models.Model):
    _name = 'employee.ltc.journey'
    _description = "Employee LTC Journey"

    employee_id = fields.Many2one('hr.employee', string='Employee')
    relate_to_ltc = fields.Many2one('employee.ltc.claim')
    departure_timings = fields.Datetime('Date & Time of Departure')
    arrival_timings = fields.Datetime('Date & Time of Arrival')
    from_l = fields.Many2one('res.city', string='From City')
    to_l = fields.Many2one('res.city', string='To City')
    distance = fields.Char('Distance(in Kms.)')
    travel_mode = fields.Many2many('travel.mode.ltc', string='Mode of Travel')
    ticket_no = fields.Char('Ticket Number')
    fair_paid = fields.Float('Fair')
    ticket_attach = fields.Binary('Attachment',attachment=True)
    ticket_attach_filename = fields.Char('Attachment Filename')


class JourneyDetailsGov(models.Model):
    _name = 'employee.ltc.journey.gov'
    _description = "Employee LTC Journey Gov"

    employee_id = fields.Many2one('hr.employee', string='Employee')
    relate_to_ltc = fields.Many2one('employee.ltc.claim')
    travel_mode = fields.Many2many('travel.mode.ltc', string='Mode of Travel')
    from_l = fields.Many2one('res.city', string='From City')
    to_l = fields.Many2one('res.city', string='To City')
    fair_paid = fields.Float('Fair')

class JourneyDetailsconnected(models.Model):
    _name = 'employee.ltc.journey.train'
    _description = "Employee LTC Journey Train"

    employee_id = fields.Many2one('hr.employee', string='Employee')
    relate_to_ltc = fields.Many2one('employee.ltc.claim')
    travel_mode = fields.Many2many('travel.mode.ltc', string='Mode of Travel')
    from_l = fields.Many2one('res.city', string='From City')
    to_l = fields.Many2one('res.city', string='To City')
    remarks = fields.Char('Remarks')


class TravelMode(models.Model):

    _name = "travel.mode.ltc"
    _description = "Travel Mode LTC"

    name = fields.Char('Name')