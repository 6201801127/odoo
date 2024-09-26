from odoo import api, fields, models, tools, _
from datetime import datetime, date
from odoo.exceptions import ValidationError,UserError


class HREmployeeProperty(models.Model):
    _name = "hr.employee.property.modification"
    _description = "HR Property Modification"
    _rec_name = 'employee_id'

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)


    employee_id = fields.Many2one('hr.employee', string="Name of the Government servant", default=_default_employee,track_visibility='always')
    designation = fields.Many2one('hr.job',string="Designation: ")

    need_cancel = fields.Boolean(string="Needs Cancellation")
    property_id = fields.Many2one('hr.employee.property',string="Select Movable Property")

    @api.onchange('property_id')
    def get_detail(self):
        if self.property_id:
            self.employee_id = self.property_id.employee_id.id
            self.designation = self.property_id.designation.id
            self.mov_sequence = self.property_id.mov_sequence
            self.service_belo = self.property_id.service_belo
            self.employee_no = self.property_id.employee_no
            self.pay_level_id = self.property_id.pay_level_id.id
            self.scale_pay = self.property_id.scale_pay
            self.purpose = self.property_id.purpose
            self.propert_ad = self.property_id.propert_ad
            self.acq_date = self.property_id.acq_date
            self.details_property = self.property_id.details_property
            self.mode_of_acquisition = self.property_id.mode_of_acquisition
            self.full_part = self.property_id.full_part
            self.owner_property = self.property_id.owner_property
            self.property_price = self.property_id.property_price
            self.copy_attached = self.property_id.copy_attached
            self.disposed_attachment = self.property_id.disposed_attachment
            self.disposed_attachment_name = self.property_id.disposed_attachment_name
            self.address_details = self.property_id.address_details
            self.party_relation = self.property_id.party_relation
            self.state_relationship = self.property_id.state_relationship
            self.dealings = self.property_id.dealings
            self.official_party = self.property_id.official_party
            self.transaction = self.property_id.transaction
            self.acquistion_gift = self.property_id.acquistion_gift
            self.rel_fact = self.property_id.rel_fact
            self.finance_id = self.property_id.finance_id
          



    @api.onchange('employee_id')
    @api.constrains('employee_id')
    def get_designation(self):
        for rec in self:
            rec.designation = rec.employee_id.job_id.id
            rec.employee_no = rec.employee_id.identify_id
            emp_contract = self.env['hr.contract'].search(
                [('employee_id', '=', rec.employee_id.id), ('state', '=', 'open')], limit=1)
            if emp_contract:
                for contract in emp_contract:
                    rec.scale_pay = contract.wage
                    rec.pay_level_id = contract.pay_level_id.id

    mov_sequence = fields.Char('Movable Property Number',track_visibility='always')
    service_belo = fields.Char("Service to which belongs: ",track_visibility='always')
    employee_no = fields.Char(string="Employee No./Code No.: ")

    pay_level_id = fields.Many2one('hr.payslip.paylevel', string='Pay Level	',track_visibility='always')
    scale_pay = fields.Float("Present pay:",track_visibility='always')

    purpose = fields.Char("Purpose of application:", track_visibility='always')

    #Description of Movable Property
    propert_ad = fields.Selection([('acquisition', 'Acquisition'), ('disposal', 'Disposal')], string='Acquisition or disposal',track_visibility='onchange')
    acq_date = fields.Date(string="Date of acquisition or disposal")
    details_property = fields.Char(string="Details of Property" )
    mode_of_acquisition = fields.Selection(
        [('pursale', 'Purchase/Sale'), ('gift', 'Gift'), ('Motagage', 'Motagage'), ('Lease', 'Lease'),
         ('Other', 'Other')
         ], string='Mode of acquistion', track_visibility='onchange')
    full_part = fields.Char("Whether the applicants interest in the property is in full or part")
    owner_property = fields.Char("Ownership of the property")
    property_price = fields.Float("Sale/Purchase price of the property")

    # acquisition_source = fields.Selection(
    #     [('p_s', 'Personal Savings'), ('others', 'Others')
    #      ], string='In case of acquistion, source or sources from which financed/propsed to be financed',
    #     track_visibility='onchange')
    copy_attached = fields.Selection([('yes','Yes'),('no','No')],'In the case of disposal of property, was requisite sanction/intimation obtained/given for its acquisition (A copy of the sanction/acknowledgement should be attached)')
    disposed_attachment = fields.Binary("Upload Attachment")
    disposed_attachment_name = fields.Char('Disposed Attachment Name')
    #Details of the Parties with whom transaction is proposed to be made! has been made:

    address_details = fields.Char("Name and address of the parties. ")
    party_relation = fields.Selection([('yes','Yes'),('no','No')],'Is the party related to the applicant? If so, state the relationship.')
    state_relationship = fields.Char(string="state relationship")
    dealings = fields.Selection([('yes','Yes'),('no','No')],string="Did the applicant have any official dealing with the parties?")
    official_party = fields.Char(string="Nature of official dealing with the party")
    transaction = fields.Char(string="How was transaction arranged?")

    acquistion_gift = fields.Selection([('yes','Yes'),('no','No')],string="In the case of acquistion by gifts, whether sanction is also required under rule 13 of CCS Rules. 1964",track_visibility='onchange')
    rel_fact = fields.Char(string="Any other relevant fact which the appliciant may like to mention",track_visibility='onchange')

    state = fields.Selection(
        [('draft', 'Draft'), ('submitted', 'Waiting for Approval'), ('approved', 'Approved'), ('rejected', 'Rejected'),('disposal', 'Disposal')
         ], required=True, default='draft', string='Status', track_visibility='onchange')

    finance_id = fields.One2many('movable.property.finance','property_id',string="In case of acquistion, source or sources from which financed/propsed to be financed")

    @api.multi
    def button_reset_to_draft(self):
        for rec in self:
            rec.write({'state': 'draft'})


    @api.multi
    def button_to_approve(self):
        for rec in self:
            total_amount = 0
            for finance in rec.finance_id:
                total_amount += finance.amount
            if total_amount != rec.property_price:
                raise ValidationError("Total financed amount and Property Price should be same.")
            else:
                rec.write({'state': 'submitted'})
            if rec.need_cancel:
                rec.write({'state': 'approved'}) 
                rec.property_id.write({
                'state': 'disposal',
                        })

    @api.multi
    def button_approved(self):
        for rec in self:
            rec.write({'state': 'approved'})

    @api.multi
    def button_reject(self):
        for rec in self:
            rec.write({'state': 'rejected'})

    @api.model
    def create(self, vals):
        res =super(HREmployeeProperty, self).create(vals)
        seq = self.env['ir.sequence'].next_by_code('hr.employee.property')
        sequence = 'MOV' + seq
        res.mov_sequence = sequence
        return res

    @api.multi
    @api.depends('mov_sequence')
    def name_get(self):
        res = []
        for record in self:
            if record.mov_sequence:
                name = record.mov_sequence
            else:
                name = 'MOV'
            res.append((record.id, name))
        return res