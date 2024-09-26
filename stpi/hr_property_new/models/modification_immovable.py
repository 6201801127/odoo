from odoo import api, fields, models, tools, _
from datetime import datetime, date
from odoo.exceptions import ValidationError,UserError


class HRPropertyNew(models.Model):
    _name = "hr.property.modification"
    _description = "HR Property Modification Form"
    _rec_name = 'employee_id'

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)


    employee_id = fields.Many2one('hr.employee', string="Name of the Government servant", default=_default_employee,track_visibility='always')
    designation = fields.Many2one('hr.job',string="Designation: ")

    need_cancel = fields.Boolean(string="Needs Cancellation")
    property_id = fields.Many2one('hr.property.new',string="Immovable Property")


 
    @api.onchange('property_id')
    def get_detail(self):
        if self.property_id:
            self.pay_level_id = self.property_id.pay_level_id.id
            self.purpose = self.property_id.purpose
            self.propert_ad = self.property_id.propert_ad
            self.probable_date = self.property_id.probable_date
            self.mode_of_acquisition = self.property_id.mode_of_acquisition
            self.mode_of_disposal = self.property_id.mode_of_disposal
            self.intimation_type = self.property_id.intimation_type
            self.address_details = self.property_id.address_details
            self.des_property = self.property_id.des_property
            self.free_leas_hold = self.property_id.free_leas_hold
            self.full_part = self.property_id.full_part
            self.owner_property = self.property_id.owner_property
            self.property_price = self.property_id.property_price
            self.copy_attached = self.property_id.copy_attached
            self.disposed_attachment = self.property_id.disposed_attachment
            self.disposed_attachment_name = self.property_id.disposed_attachment_name
            self.party_details = self.property_id.party_details
            self.party_relation =  self.property_id.party_relation
            self.nature_of_dealings = self.property_id.nature_of_dealings
            self.state_relationship = self.property_id.state_relationship
            self.dealings = self.property_id.dealings
            self.transaction = self.property_id.transaction
            self.acquistion_gift = self.property_id.acquistion_gift
            self.party_name = self.property_id.party_name
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

    immov_sequence = fields.Char('Immovable Property Number',track_visibility='always')
    service_belo = fields.Char("Service to which belongs: ",track_visibility='always')
    employee_no = fields.Char(string="Employee No./Code No.: ")

    pay_level_id = fields.Many2one('hr.payslip.paylevel', string='Pay Level	',track_visibility='always')
    scale_pay = fields.Float("Present pay:",track_visibility='always')
    purpose = fields.Char("Purpose of application:",track_visibility='always')
    propert_ad = fields.Selection([('acquired', 'Acquired'), ('disposed', 'Disposed')], string='Whether property is being acquired or disposed of',track_visibility='onchange')
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
            if rec.need_cancel:
                rec.write({'state': 'approved'}) 
                rec.property_id.write({
                'state': 'disposed',
                        })
            else:
                rec.write({'state': 'approved'}) 
                rec.property_id.write({
                'pay_level_id' : rec.pay_level_id.id,
                'purpose' : rec.purpose,
                'propert_ad' : rec.propert_ad,
                'probable_date' : rec.probable_date,
                'mode_of_acquisition' : rec.mode_of_acquisition,
                'mode_of_disposal' : rec.mode_of_disposal,
                'intimation_type' :rec.intimation_type,
                'address_details' : rec.address_details,
                'des_property' : rec.des_property,
                'free_leas_hold' : rec.free_leas_hold,
                'full_part' :rec.full_part,
                'owner_property' : rec.owner_property,
                'property_price' : rec.property_price,
                'copy_attached' : rec.copy_attached,
                'disposed_attachment' : rec.disposed_attachment,
                'disposed_attachment_name' : rec.disposed_attachment_name,
                'party_details' : rec.party_details,
                'party_relation' : rec.party_relation,
                'nature_of_dealings' : rec.nature_of_dealings,
                'state_relationship' : rec.state_relationship,
                'dealings' : rec.dealings,
                'transaction' : rec.transaction,
                'acquistion_gift' : rec.acquistion_gift,
                'party_name' : rec.party_name,
                'rel_fact' : rec.rel_fact,
                'finance_id' : rec.finance_id,       
                        })
            
            
            
        
       
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