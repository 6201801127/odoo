from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError,UserError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import re

class EmployeeTourCancel(models.Model):
    _name = 'employee.tour.cancel'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Tour Cancel'

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    @api.multi
    @api.depends('tour_request_id')
    def _compute_approved_amount(self):
        total_cancel = 0.0
        total_cl_journey = 0.0
        for record in self:
            record.advance_requested = record.tour_request_id.advance_requested
            # for line in record.detail_of_journey:
            #     if line:
            #         total_cl_journey += line.amount_claimed
            # print('================', total_claimed)
            # print('================', record.other_details)
            # print('================', total_cl_journey)
            # record.total_claimed_amount = total_claimed + record.other_details + total_cl_journey
            # print('================', record.total_claimed_amount)
            record.balance_left = record.amount_to_be_return - record.advance_requested 

    employee_id = fields.Many2one('hr.employee', string='Requested By', default=_default_employee,track_visibility='always')
    designation = fields.Many2one('hr.job', string="Designation", compute='compute_des_dep',track_visibility='always')
    branch_id = fields.Many2one('res.branch', 'Branch', compute='compute_des_dep',track_visibility='always', store=True)
    department = fields.Many2one('hr.department', string="Department", compute='compute_des_dep', store=True,track_visibility='always')
    tour_request_id = fields.Many2one('tour.request', string='Select Tour', store=True,track_visibility='always')
    state = fields.Selection(
        [('draft', 'Draft'), ('submitted', 'Waiting for Approval'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('paid', 'Paid')
         ], required=True, default='draft', string='Status',track_visibility='always')
    detail_of_journey = fields.One2many('tour.cancel.journey','employee_journey',track_visibility='always')
    advance_requested = fields.Float(string="Advance Requested", readonly=True, compute='_compute_approved_amount',track_visibility='always')
    amount_to_be_return = fields.Float(string="Amount to be Return", readonly=True, track_visibility='always')
    balance_left = fields.Float(string="Balance left", readonly=True, compute='_compute_approved_amount',track_visibility='always')
    bank_document = fields.Binary(string="Bank and Cheque Details",attachment=True)
    bank_document_filename = fields.Char(string="Bank Document File Name")
    remarks = fields.Text('Remarks')

    @api.depends('employee_id')
    def compute_des_dep(self):
        for rec in self:
            rec.designation = rec.employee_id.job_id.id
            rec.department = rec.employee_id.department_id.id
            rec.branch_id = rec.employee_id.branch_id.id
    
    @api.onchange('tour_request_id')
    def get_journey_details_tour(self,working_list=None):
        for rec in self:
            detail_of_journey = []
            for i in rec.tour_request_id.employee_journey:
                detail_of_journey.append((0, 0, {
                    'employee_journey': rec.id,
                    'departure_date': i.departure_date,
                    'departure_time': i.departure_time,
                    'arrival_date': i.arrival_date,
                    'arrival_time': i.arrival_time,
                    'from_l': i.from_l.id,
                    'to_l': i.to_l.id,
                }))
            else:
                rec.detail_of_journey = working_list
            rec.detail_of_journey = detail_of_journey

    @api.multi
    @api.depends('employee_id')
    def name_get(self):
        res = []
        name = ''
        for record in self:
            if record.employee_id:
                name = str(record.employee_id.name) + ' - Tour Cancel'
            else:
                name = 'Tour Cancel'
            res.append((record.id, name))
        return res

class TourCancelJourney(models.Model):
    _name = "tour.cancel.journey"
    _description = "Tour Cancel Journey Details"


    employee_journey = fields.Many2one('employee.tour.cancel', string='Tour cancel')
    departure_date = fields.Date('Departure Date')
    arrival_date = fields.Date('Arrival Date')
    from_l = fields.Many2one('res.city', string='From City')
    to_l = fields.Many2one('res.city', string='To City')
    departure_time = fields.Float('Departure Time')
    arrival_time = fields.Float('Arrival Time')
    amount_claimed = fields.Float('Amount Claimed')
    distance = fields.Float('Distance')
    document = fields.Binary(string='Document', attachment=True)
    document_filename = fields.Char(string="Document Filename")
    arranged_by = fields.Selection([('self', 'Self'), ('company', 'Office')], string='Arranged By')
    state = fields.Selection(
        [('draft', 'Draft'), ('submitted', 'Waiting for Approval'), ('approved', 'Approved'),
         ('rejected', 'Rejected'), ('paid', 'Paid')
         ], related='employee_journey.state')


    @api.onchange('arranged_by')
    @api.constrains('arranged_by')
    def arranged_by_claim(self):
        for rec in self:
            if rec.arranged_by == 'company':
                rec.amount_claimed = 0.00