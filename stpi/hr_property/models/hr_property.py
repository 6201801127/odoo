from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
import re

class HrProperty(models.Model):
    _name = "hr.property"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "HR Property"


    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)


    employee_id = fields.Many2one('hr.employee', string="Name of the officer", default=_default_employee,track_visibility='always')
    designation = fields.Many2one('hr.job', string="Present Post Held", compute='compute_des_dep', store=True,track_visibility='always')
    department = fields.Many2one('hr.department', string="Department", compute='compute_des_dep', store=True,track_visibility='always')
    branch_id = fields.Many2one('res.branch', string="Center", compute='compute_des_dep', store=True,track_visibility='always')
    present_pay=fields.Float(string="Present Pay", compute='_compute_present_pay',track_visibility='always')
    date_range = fields.Many2one('date.range',string='Date Range')
    dist_name = fields.Char(string="Name of the Distt. Subdivision, Tehsil & Vill. In which the property is situated.",track_visibility='onchange')
    house_build = fields.Char(string="Housing and Building",track_visibility='onchange')
    other_lands = fields.Char(string="Other Lands",track_visibility='onchange')
    present_value = fields.Float(string="Present value ",track_visibility='onchange')
    state_relation = fields.Char(string="If not in own name, state in whose name held of his/ her relationship to Govt. Servant",track_visibility='onchange')
    how_acquired = fields.Char(string="How acquired whether by purchase, lease**, mortgage, inheritance, gift or otherwise with date of acquisition and name with detail of person from whom acquired ",track_visibility='onchange')
    annual_income = fields.Float(string="Annual Income from the Property",track_visibility='onchange')

    application_purpose = fields.Selection(
        [('sanction', 'Sanction for Transaction'), ('intimation', 'Intimation of Transaction')
         ], string='Purpose of application:',track_visibility='onchange')
    propert_ad = fields.Selection([('acquired', 'Acquired'), ('disposed', 'Disposed')
                               ], string='Whether property is being acquired or disposed of',track_visibility='onchange')
    probable_date = fields.Date(string='Probable date of acquistion or disposal of property',track_visibility='onchange')
    actual_date = fields.Date(string='Actual date of transaction',track_visibility='onchange')
    make_model = fields.Char(string='Make Model',track_visibility='onchange')
    des_property = fields.Char(string="Description of the Property",track_visibility='onchange')

    mode_of_acquisition = fields.Selection(
        [('pursale', 'Purchase/Sale'), ('gift', 'Gift'),('Motagage', 'Motagage'), ('Lease', 'Lease'), ('Other', 'Other')
         ], string='Mode of acquistion',track_visibility='onchange')

    sapur_pro = fields.Char(string="Sale/Purchase price of the property",track_visibility='onchange')
    acquisition_source = fields.Selection(
        [('p_s', 'Personal Savings'), ('others', 'Others')
         ], string='In case of acquistion, source or sources from which financed/propsed to be financed',track_visibility='onchange')
    other_source = fields.Char('Other Source',track_visibility='onchange')
    party_transaction = fields.Char('Name of the Party with whom transation is proposed to be made',track_visibility='onchange')
    address_party = fields.Char('Address of the party with whom transation is proposed to be made',track_visibility='onchange')
    party_relation = fields.Boolean('Is the party related to the applicant?',track_visibility='onchange')
    relationi_party_state = fields.Char(string=" state relationship",track_visibility='onchange')
    app_deal = fields.Boolean(string="Did the applicant have any dealings with the party in his official capacity at any time, or is the applicant likely to have any dealings with him in the near future ?",track_visibility='onchange')
    nature_deal = fields.Char(string="Nature of official dealings with the party.",track_visibility='onchange')
    tran_arr = fields.Char(string="How was transaction arranged?",track_visibility='onchange')
    acquistion_gift = fields.Boolean(string="In the case of acquistion by gifts, whether sanction is also required under rule 13 of CCS Rules. 1964",track_visibility='onchange')
    other_factss = fields.Char(string="Any other facts needs to be mentioned?",track_visibility='onchange')



    immov_appl_purpose = fields.Selection(
        [('sanction', 'Sanction for transaction'), ('prior', 'Prior Intimation of transaction')
         ], string='Purpose of application',track_visibility='onchange')
    immov_propert_ad = fields.Selection([('acquired', 'Acquired'), ('disposed', 'Disposed')
                                   ], string='Whether property is being acquired or disposed of',track_visibility='onchange')
    im_probable_date = fields.Date(string='Probable date of acquistion or disposal of property',track_visibility='onchange')
    im_mode_of_acquisition = fields.Selection(
        [('pursale', 'Purchase/Sale'), ('gift', 'Gift'), ('Motagage', 'Motagage'), ('Lease', 'Lease'),
         ('Other', 'Other')
         ], string='Mode of acquistion',track_visibility='onchange')
    im_address_details = fields.Char('Full Details about location viz, Municipal No, Street, Village/Taluka/District and state in which situated',track_visibility='onchange')
    im_pro_des = fields.Char('Description of property in the case of cultivable land, dry or irrigated land',track_visibility='onchange')
    im_free_leas = fields.Char('Whether freehold or leasehold',track_visibility='onchange')
    im_full_half = fields.Char('Whether the applicants interest in the property is in full or part (in case of partial interest, the extent of such interest must be indicated)',track_visibility='onchange')
    im_tran_not_ex = fields.Char('In case the transaction is not exclusively in the same name of the government servant, particulars of ownership and share of each member.',track_visibility='onchange')
    im_property_price = fields.Float('Sale / Puchase price of the property (Market value in csase of gift)',track_visibility='onchange')
    im_acquisition_source = fields.Selection(
        [('p_s', 'Personal Savings'), ('others', 'Others')
         ], string='In case of acquistion, source or sources from which financed/propsed to be financed',track_visibility='onchange')
    im_other_source = fields.Char('Other Source',track_visibility='onchange')
    copy_attached = fields.Char('In case of disposal of property, was requisite sanction / intimation obtained / Given for its acqisition? ( A copy of the sanction/acknowledgement should be attached)',track_visibility='onchange')
    im_details_party = fields.Char('Name and address of the party whith whom transaction is proposed to be made',track_visibility='onchange')
    im_party_relation = fields.Boolean('Is the party related to the applicant?',track_visibility='onchange')
    im_relationi_party_state = fields.Char(string="state relationship",track_visibility='onchange')
    im_app_deal = fields.Char(string="Did the applicant have any dealings with the party in his official capacity at any time, or is the applicant likely to have any delaings with him in the near future?",track_visibility='onchange')
    im_tran_arr = fields.Char(string="How was transaction arranged?",track_visibility='onchange')
    im_acq_gift = fields.Char(string="In case of acquisition by gift, whether sancation is also required under Rule 13 of the CCS (Conduct) Rules, 1964",track_visibility='onchange')
    im_other_rel_fact = fields.Char(string="Any other relevant fact which the appliciant may like to mention",track_visibility='onchange')



    each_transaction_details = fields.Char(string="Details of each transaction made in shares, securities, debatunres, mutual funds scheme, during the calender years",track_visibility='onchange')
    party_particulars = fields.Char(string="Particluars of the party, firm with whom transaction is made",track_visibility='onchange')
    party_relate_app = fields.Char(string="Is party related to the applicant ?",track_visibility='onchange')
    applicant_dealing = fields.Char(string="Did the applicant have any dealings with the party in his official capacity at any time or is the applicant likely to have any dealings with him in near future ?",track_visibility='onchange')
    invest_acquisition_source = fields.Selection(
        [('p_s', 'Personal Savings'), ('others', 'Others')
         ], string='In case of acquistion, source or sources from which financed/propsed to be financed',track_visibility='onchange')
    invest_other_source = fields.Char('Other Source',track_visibility='onchange')
    invest_other_rel_fact = fields.Char(string="Any other relevant fact which the appliciant may like to mention",track_visibility='onchange')

    state = fields.Selection(
        [('draft', 'Draft'), ('submitted', 'Waiting for Approval'), ('approved', 'Approved'), ('rejected', 'Rejected')
         ], required=True, default='draft', string='Status',track_visibility='onchange')




    @api.multi
    def button_to_approve(self):
        for rec in self:
            rec.write({'state': 'submitted'})

    @api.multi
    def button_reject(self):
        for rec in self:
            rec.write({'state': 'rejected'})


    @api.multi
    def unlink(self):
        for tour in self:
            if tour.state != 'draft':
                raise UserError(
                    'You cannot delete a Property which is not in draft state')
        return super(HrProperty, self).unlink()



    @api.multi
    def button_reset_to_draft(self):
        self.ensure_one()
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        ctx = dict(
            default_composition_mode='comment',
            default_res_id=self.id,

            default_model='hr.property',
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

    @api.multi
    def button_approved(self):
        for rec in self:
            rec.write({'state': 'approved'})

    @api.depends('employee_id')
    def compute_des_dep(self):
        for rec in self:
            rec.designation = rec.employee_id.job_id.id
            rec.department = rec.employee_id.department_id.id
            rec.branch_id = rec.employee_id.branch_id.id


    @api.depends('employee_id')
    def _compute_present_pay(self):
        for rec in self:
            contract_obj = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)], limit=1)
            if contract_obj:
                for contract in contract_obj:
                    rec.present_pay = contract.wage


    @api.multi
    @api.depends('employee_id')
    def name_get(self):
        res = []
        for record in self:
            if record.employee_id:
                name = 'HR Property - ' + str(record.employee_id.name)
            else:
                name = 'HR Property'
            res.append((record.id, name))
        return res