from odoo import api, fields, models, tools, _
from datetime import datetime, date
from odoo.exceptions import ValidationError,UserError


class HRPropertyNew(models.Model):
    _name = "hr.property.new"
    _description = "HR Property Form-I"
    _rec_name = 'employee_id'

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)


    employee_id = fields.Many2one('hr.employee', string="Name of the Government servant", default=_default_employee,track_visibility='always')
    designation = fields.Many2one('hr.job',string="Designation: ")

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

    immov_sequence = fields.Char('Immovable Property Number',track_visibility='always')
    service_belo = fields.Char("Service to which belongs: ",track_visibility='always')
    employee_no = fields.Char(string="Employee No./Code No.: ")

    pay_level_id = fields.Many2one('hr.payslip.paylevel', string='Pay Level	',track_visibility='always')
    scale_pay = fields.Float("Present pay:",track_visibility='always')
    purpose = fields.Char("Purpose of application:",track_visibility='always')
    propert_ad = fields.Selection([('acquired', 'Acquired'), ('disposed', 'Disposed')], string='Whether property is being acquired or disposed of',track_visibility='onchange')
    select_id = fields.Many2one('hr.property.new',string='Select Immovable Property Sequence' ,domain="[('propert_ad','=','acquired')]")


    probable_date = fields.Date(string='Probable date of acquistion or disposal of property',track_visibility='onchange')
    mode_of_acquisition = fields.Selection(
        [('purchase', 'Purchase'), ('gift', 'Gift'), ('Motagage', 'Motagage'), ('Lease', 'Lease'),
         ('Other', 'Other')
         ], string='Mode of Acquisition', track_visibility='onchange')

    mode_of_disposal = fields.Selection([('sales','Sales'), ('gift', 'Gift'), ('Motagage', 'Motagage'), ('Lease', 'Lease'),
         ('Other', 'Other')
         ], string='Mode of Disposal', track_visibility='onchange')

    intimation_type = fields.Selection([('prior','Prior'),('post','Post')],string="Intimation Type", track_visibility='onchange')

    #Description of Property
    address_details = fields.Char("Full details about location")
    des_property = fields.Char(string="Description of the Property")
    free_leas_hold = fields.Char("Whether freehold or leasehold")
    full_part = fields.Char("Whether the applicants interest in the property is in full or part")
    owner_property = fields.Char("Ownership of the property")
    property_price = fields.Float("Sale/Purchase price of the property")

    # acquisition_source = fields.Selection(
    #     [('p_s', 'Personal Savings'), ('others', 'Others')
    #      ], string='In case of acquistion, source or sources from which financed/propsed to be financed',
    #     track_visibility='onchange')
    copy_attached = fields.Selection([('yes','Yes'),('no','No')],string='In the case of disposal of property, was requisite sanction/intimation obtained/given forits acquisition (A copy of the sanction/acknowledgement should be attached):')
    disposed_attachment = fields.Binary("Upload Attachment")
    disposed_attachment_name = fields.Char('Disposed Attachment Name')
    #. Details of the Parties with whom transaction is proposed to be made:

    party_details = fields.Char('Name and address of the party whith whom transaction is proposed to be made')
    party_relation = fields.Selection([('yes','Yes'),('no','No')],string='Is the party related to the applicant? If so, state the relationship.')
    nature_of_dealings = fields.Text(string="Nature of Dealings")
    state_relationship = fields.Char(string="State relationship")
    dealings = fields.Selection([('yesp','Yes'),('no','No')],string="Did the applicant have any official dealing with the parties?")
    transaction = fields.Char(string="How was transaction arranged?")

    acquistion_gift = fields.Selection([('yes','Yes'),('no','No')],string="In the case of acquistion by gifts, whether sanction is also required under rule 13 of CCS Rules. 1964",track_visibility='onchange')
    party_name = fields.Char('Party Name')
    rel_fact = fields.Char(string="Any other relevant fact which the appliciant may like to mention",track_visibility='onchange')

    state = fields.Selection(
        [('draft', 'Draft'), ('submitted', 'Waiting for Approval'), ('approved', 'Approved'), ('rejected', 'Rejected'),('disposed','Disposed')
         ], required=True, default='draft', string='Status', track_visibility='onchange')

    finance_id = fields.One2many('hr.property.finance','property_id',string="In case of acquistion, source or sources from which financed/propsed to be financed")

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
        res =super(HRPropertyNew, self).create(vals)
        seq = self.env['ir.sequence'].next_by_code('hr.property.new')
        sequence = 'IMMOV' + seq
        res.immov_sequence = sequence
        if res.propert_ad == 'disposed':
            res.write({'state': 'approved'})
            res.select_id.write({'state': 'disposed'})
        return res

    @api.multi
    @api.depends('immov_sequence')
    def name_get(self):
        res = []
        for record in self:
            if record.immov_sequence:
                name = record.immov_sequence
            else:
                name = 'IMMOV'
            res.append((record.id, name))
        return res

    @api.onchange('select_id')
    def get_detail(self):
        if self.select_id:
            self.pay_level_id = self.select_id.pay_level_id.id
            self.purpose = self.select_id.purpose
            self.probable_date = self.select_id.probable_date
            self.mode_of_acquisition = self.select_id.mode_of_acquisition
            self.mode_of_disposal = self.select_id.mode_of_disposal
            self.intimation_type = self.select_id.intimation_type
            self.address_details = self.select_id.address_details
            self.des_property = self.select_id.des_property
            self.free_leas_hold = self.select_id.free_leas_hold
            self.full_part = self.select_id.full_part
            self.owner_property = self.select_id.owner_property
            self.property_price = self.select_id.property_price
            self.copy_attached = self.select_id.copy_attached
            self.disposed_attachment = self.select_id.disposed_attachment
            self.disposed_attachment_name = self.select_id.disposed_attachment_name
            self.party_details = self.select_id.party_details
            self.party_relation =  self.select_id.party_relation
            self.nature_of_dealings = self.select_id.nature_of_dealings
            self.state_relationship = self.select_id.state_relationship
            self.dealings = self.select_id.dealings
            self.transaction = self.select_id.transaction
            self.acquistion_gift = self.select_id.acquistion_gift
            self.party_name = self.select_id.party_name
            self.rel_fact = self.select_id.rel_fact
            self.finance_id = self.select_id.finance_id

class HRPropertyFinance(models.Model):
    _name = "hr.property.finance"
    _description = "HR Property Form-I Finance"

    property_id = fields.Many2one('hr.property.new',string="Property")
    mode_of_finance = fields.Selection([('p_s', 'Personal Savings'), ('loan','Loan'), ('bank','Bank'), ('others', 'Others')],string="Mode of Finance")
    description = fields.Text('Description')
    amount = fields.Float(string="Amount")
    finance_attachment = fields.Binary(string='Document')
    document_filename = fields.Char(string="Document Filename")