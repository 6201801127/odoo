# Commit History
# penalty_type aded for major and minor penalty while closing vigillance 7 June 2021(Gouranga kala)
# complaint_type aded for major and minor penalty while creating vigillance 10 June 2021(Gouranga kala)

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
import re
from datetime import datetime

class MyVigilance(models.Model):
    _name = "my.vigilance"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Vigilance"

    def default_country(self):
        return self.env['res.country'].search([('name', '=', 'India')], limit=1)

    vigilance_sequence = fields.Char('Vigilance number')

    name = fields.Char(string="Case Name",track_visibility='always')
    district = fields.Char(string="District",track_visibility='always')

    state_id = fields.Many2one("res.country.state", string='State', help='Enter State', ondelete='restrict')
    country_id = fields.Many2one('res.country', string='Country', help='Select Country', ondelete='restrict', default=default_country)

    mobile = fields.Char(string="Mobile",track_visibility='always')
    email = fields.Char(string="Email",track_visibility='always')
    description = fields.Text(string="Description",track_visibility='always')
    org_name = fields.Char(string="  Name of Organization(s) where Grievance is pending",track_visibility='always')
    receipt_type = fields.Many2one('vigilance.receipt.type', string="Receipt Type",track_visibility='always')
    # complaint_type = fields.Selection(string="Complaint Type",selection=[('major','Major'),('minor','Minor')])
    penalty_type = fields.Selection(string="Type",selection=[('major','Major'),('minor','Minor')])

    mode_of_complaint = fields.Selection([('oral', 'Oral'), ('written', 'Written')], string='Mode of Complaint', default='oral', track_visibility='always')
    type_of_complaint = fields.Selection([('internal', 'Internal'), ('external', 'External')], string='Type of Complaint', default='internal', track_visibility='always')
    name_of_complaint = fields.Many2many('res.partner', string='Name of Complainant')
    complaint_against = fields.Many2many('hr.employee', string='Complaint Against')
    address = fields.Char(string="Address of the Complainant",track_visibility='always')
    reg_no = fields.Char(string = 'Communication Number',track_visibility='always')
    allegation_in_brief = fields.Text(string = 'Allegation (in brief)',track_visibility='always')
    com_date = fields.Date(string = 'Communication Date',track_visibility='always')
    date_of_receipt = fields.Date(string="Date of Receipt of Complaint", default=fields.Date.today(),track_visibility='always')
    remarks = fields.Text('Remarks (If any)')
    penalty = fields.Many2one('vigilance.penalty', string='Penalty: ')
    state = fields.Selection([('draft', 'Draft'), ('in_progress', 'Forwarded'), ('PI', 'PI'), ('closed', 'Closed')], required=True, string='Status', default='draft', track_visibility='always')

    pi_conducted_by = fields.Selection([('internal_emp', 'Internal Employee'), ('external_emp', 'External Employee')], string='PI conducted by', default='internal_emp', track_visibility='always')
    pi_conducted_ext = fields.Many2one('res.partner', string='Name')
    pi_conducted_int = fields.Many2one('hr.employee', string='Name of the Employee')
    date_pi = fields.Date(string = 'Date of Receipt of PI report',track_visibility='always')
    outcome_pi = fields.Text('Outcome of PI')

    date_co = fields.Date(string = 'Date of receipt of representation of CO',track_visibility='always')
    comm_number_co = fields.Char(string = 'Communication Number(CO)',track_visibility='always')
    comm_date_co = fields.Date(string = 'Communication Date(CO)',track_visibility='always')
    remarks_co = fields.Text('Remarks CO (If any)')

    io_conducted_by = fields.Selection([('internal_emp', 'Internal Employee'), ('external_emp', 'External Employee')], string='IO conducted by', default='internal_emp', track_visibility='always')
    io_conducted_ext = fields.Many2one('res.partner', string='Name of the Inquiring Officer (IO)')
    io_conducted_int = fields.Many2one('hr.employee', string='Name of the Inquiring Officer (IO)')
    address_io = fields.Char('Address of the IO')
    date_io = fields.Date(string = 'Date appointing IO',track_visibility='always')
    order_number_io = fields.Char('Order Number IO')
    po_conducted_int = fields.Many2one('hr.employee', string='Name of the Presenting Officer (PO)')
    date_po = fields.Date(string = 'Date appointing PO',track_visibility='always')
    address_po = fields.Char('Address of the PO')
    order_number_po = fields.Char('Order Number PO')
    remarks_io_po = fields.Text('Remarks IO/PO (If any)')

    date_ir = fields.Date(string='Date  of receipt of inquiry report', track_visibility='always')
    date_fw_ir = fields.Date(string='Date of forwarding of inquiry report to CO', track_visibility='always')
    date_rep_ir = fields.Date(string='Date of receipt of representation from CO on IR', track_visibility='always')
    date_cvc = fields.Date(string='Date of receipt of CVC 2nd  Stage advice', track_visibility='always')
    report_num_ir = fields.Char('Report  No. & Date')
    find_io = fields.Char('Findings of IO (in brief)')
    comm_num_co = fields.Char('Communication No. & Date')
    comm_num_ir = fields.Char('Communication No. & Date')
    stpi_ref = fields.Char('STPI Ref No/Date')

    @api.onchange('type_of_complaint')
    def _onchange_type_of_complaint(self):
        if self.type_of_complaint == 'internal':
            return {'domain': {'name_of_complaint': [('user_ids', '!=', False), ('is_company', '=', False)]}}
        else:
            return {'domain': {'name_of_complaint': [('user_ids', '=', False), ('is_company', '=', False)]}}

    @api.multi
    def Initiation_of_major_pp(self):
        for rec in self:
            return {
                'name': 'Intimation of major',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'vigilance.major.penalty',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'view_id': self.env.ref('my_vigilance.vigilance_initiate_major_form_view').id,
                'context': {
                    'default_vigilance_id': rec.id
                },
            }

    @api.multi
    def Initiation_of_minor_pp(self):
        for rec in self:
            pass
            # rec.write({'state': 'draft'})


    @api.multi
    def issue_of_warning(self):
        for rec in self:
            pass
            # rec.write({'state': 'draft'})


    @api.multi
    def issue_of_warning(self):
        for rec in self:
            pass
            # rec.write({'state': 'draft'})


    @api.multi
    def suspension(self):
        for rec in self:
            pass
            # rec.write({'state': 'draft'})



    @api.multi
    def ignore_pi(self):
        for rec in self:
            pass
            # rec.write({'state': 'draft'})


    @api.multi
    def initiate_pi(self):
        for rec in self:
            pass
            # rec.write({'state': 'draft'})

    @api.multi
    def forward_to_admin(self):
        for rec in self:
            pass
            # rec.write({'state': 'draft'})


    @api.multi
    def button_pi(self):
        for rec in self:
            rec.write({'state': 'PI'})


    @api.multi
    def button_draft(self):
        for rec in self:
            rec.write({'state': 'draft'})

    @api.multi
    def button_in_progress(self):
        for rec in self:
            rec.write({'state': 'in_progress'})

    @api.multi
    def button_re_open(self):
        for rec in self:
            rec.button_in_progress()

    @api.multi
    def button_register_actions(self):
        rc = {
            'name': 'Register actions',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('my_vigilance.view_reason_revert_vigilance_wizard').id,
            'res_model': 'revert.vigilance.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
            }
        }
        return rc

    @api.multi
    def button_create_activities(self):
        self.ensure_one()
        serch_id = self.env['ir.model'].search([('model', '=', 'my.vigilance')])
        compose_form_id = self.env.ref('mail.mail_activity_view_form_popup').id

        ctx = dict(
            default_res_id=self.id,
            default_res_model_id=serch_id.id,
            default_user_id=self.env.user.id,
            date_deadline=datetime.now().date(),
            activity_type_id=4
        )
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.activity',
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


    @api.model
    def create(self, vals):
        res =super(MyVigilance, self).create(vals)
        sequence = ''
        seq = self.env['ir.sequence'].next_by_code('my.vigilance')
        sequence = 'Vigilance - ' + str(seq)
        res.vigilance_sequence = sequence
        return res

    @api.multi
    @api.depends('vigilance_sequence')
    def name_get(self):
        res = []
        for record in self:
            if record.vigilance_sequence:
                name = record.vigilance_sequence
            else:
                name = 'Vigilance'
            res.append((record.id, name))
        return res

    @api.multi
    def button_closed(self):
        for rec in self:
            rc = {
                'name': 'Register actions',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': self.env.ref('my_vigilance.view_reason_revert_vigilance_wizard').id,
                'res_model': 'revert.vigilance.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {
                    'default_res_model': self._name,
                    'default_res_id': self.id,
                }
            }
            return rc

    @api.constrains('email')
    @api.onchange('email')
    def _check_email_address(self):
        for rec in self:
            if rec.email:
                match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',rec.email)
                if match == None:
                    raise ValidationError(_("Please enter correct Email Address..."))

    @api.constrains('mobile')
    @api.onchange('mobile')
    def _check_mobile_number(self):
        for rec in self:
            if rec.mobile:
                for e in rec.mobile:
                    if not e.isdigit():
                        raise ValidationError(_("Please enter correct Mobile number, it must be numeric..."))
                if len(rec.mobile) != 10:
                    raise ValidationError(_("Please enter correct Mobile number, it must be of 10 digits..."))

    @api.constrains('name')
    @api.onchange('name')
    def _check_name_number(self):
        for rec in self:
            if rec.name:
                for e in rec.name:
                    if not e.isalpha():
                        raise ValidationError(_("Please enter correct Name, it must be Character only..."))
                if len(rec.name) > 120:
                    raise ValidationError(_("Please enter correct Name, it must be greater than 120 alphabet..."))

    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id:
            return {'domain': {'state_id': [('country_id', '=', self.country_id.id)]}}
        else:
            return {'domain': {'state_id': []}}

class ReceiptType(models.Model):
    _name = "vigilance.receipt.type"
    _description = "Vigilance Receipt Type"
    name = fields.Char('Name')

class MiniorPenalty(models.Model):
    _name = "vigilance.minor.penalty"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Vigilance Minor Penalty"

    vigilance_id = fields.Many2one('my.vigilance', string='Vigilance')
    dis_auth = fields.Many2one('hr.employee', string='Disciplinary Authority')
    charge_num = fields.Char( string='Chargesheet No.')
    charge_date = fields.Date( string='Chargesheet Date')
    charge_issue_date = fields.Date( string='Date of Issue of Chargesheet')
    charge_in_brief = fields.Text( string='Charges in brief')
    charge_in_brief_up = fields.Binary( string='Charges (Upload)')
    charged_officer = fields.Many2many('hr.employee', string='Name of the Charged Officer(s)', related="vigilance_id.complaint_against")
    remarks = fields.Text('Remarks (if any)')

class MajorrPenalty(models.Model):
    _name = "vigilance.major.penalty"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Vigilance Major Penalty"

    vigilance_id = fields.Many2one('my.vigilance', string='Vigilance')
    dis_auth = fields.Many2one('hr.employee', string='Disciplinary Authority')
    charge_num = fields.Char( string='Chargesheet No.')
    charge_date = fields.Date( string='Chargesheet Date')
    charge_issue_date = fields.Date( string='Date of Issue of Chargesheet')
    charge_in_brief = fields.Text( string='Charges in brief')
    charge_in_brief_up = fields.Binary( string='Charges (Upload)')
    charged_officer = fields.Many2many('hr.employee', string='Name of the Charged Officer(s)', related="vigilance_id.complaint_against")
    remarks = fields.Text('Remarks (if any)')

class Suspension(models.Model):
    _name = "vigilance.suspension"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Vigilance Suspension"

    vigilance_id = fields.Many2one('my.vigilance', string='Vigilance')
    order_num = fields.Char( string='Order No.')
    order_date = fields.Date( string='Order Date')
    rate_sus = fields.Char( string='Rate of subsistance allowance under FR-53')
    reason_suspension = fields.Text('Reason of suspension (in brief)')
    period_of_suspension = fields.Integer('Period of suspension')

    suspension_src = fields.Char( string='Suspension Review Committee (SRC)')
    recomendation_src = fields.Char( string='Recommendations of the SRC')
    decision_da = fields.Char( string='Decision of the Disciplinary Authority')
    period_extn_sus = fields.Integer('Period of extension of suspension')
    order_num_ep = fields.Char( string='Order No. extending period of suspension')
    order_date_ep = fields.Date( string='Order Date extending period of suspension')
    rate_sub_a = fields.Char( string='Rate of subsistance allowance ')
    order_num_rsa = fields.Char( string='Order No.  regarding subsistance allowance')
    order_date_rsa = fields.Date( string='Order Date  regarding subsistance allowance')

    order_rs = fields.Char( string='Order No.  of revocation of suspension')
    order_date_rs = fields.Date( string='Order Date  of revocation of suspension')

class Appeal(models.Model):
    _name = "vigilance.appeal"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Vigilance Appeal"

    vigilance_id = fields.Many2one('my.vigilance', string='Vigilance')
    appeal_auth = fields.Many2one('hr.employee', string='Appellate Authority')
    date_app = fields.Date(string = 'Date of appeal',track_visibility='always')
    comm_number = fields.Char(string = 'Communication Number',track_visibility='always')
    order_number = fields.Char(string = 'Order Number',track_visibility='always')
    comm_date = fields.Date(string = 'Communication Date',track_visibility='always')
    dis_date = fields.Date(track_visibility='always')
    decision_da = fields.Char( string='Decision of the Appellate Authority')
    remarks = fields.Text('Remarks (If any)')

    revision_number = fields.Char('Revision Number')
    revision_order_number = fields.Char('Revision Order no.')
    decision_revision = fields.Text('Decision of the Revisionary Authority')
    date_ra = fields.Date(string='Date of Revision application (if any)', track_visibility='always')
    date_dis_ra = fields.Date(string='Date disposing  Revision application', track_visibility='always')
    remarks_revise = fields.Text('Remarks(If any)')

    review_number = fields.Char('Review Number')
    review_order_number = fields.Char('Review Order no.')
    decision_review = fields.Text('Decision of the reviewary Authority')
    date_rev = fields.Date(string='Date of review application (if any)', track_visibility='always')
    date_dis_rev = fields.Date(string='Date disposing  review application', track_visibility='always')
    remarks_review = fields.Text('Remarks(If any)')

class DisAuth(models.Model):
    _name = "vigilance.disciplinary"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Vigilance disciplinary"

    vigilance_id = fields.Many2one('my.vigilance', string='Vigilance')
    date_app = fields.Date(string = 'Date of penalty imposed',track_visibility='always')
    pen_detail = fields.Char(string = 'Detail of penalty imposed',track_visibility='always')
    order_number = fields.Char(string = 'Order Number',track_visibility='always')

    remarks = fields.Text('Remarks (If any)')

class CvC(models.Model):
    _name = "vigilance.cvc"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Vigilance cvc"

    vigilance_id = fields.Many2one('my.vigilance', string='Vigilance')
    cvc_stage = fields.Selection([('first', 'First'), ('second', 'Second')], string='CVC Stage', default='first', track_visibility='always')

    stpi_refdate_cvci = fields.Date(string = 'STPI Reference Date',track_visibility='always')
    stpi_refno_cvci = fields.Char(string = 'STPI Reference No',track_visibility='always')
    stpi_omdate_cvci = fields.Date(string = 'CVC OM Date',track_visibility='always')
    stpi_omno_cvci = fields.Char(string = 'CVC OM No.',track_visibility='always')
    stpi_recdate_cvci = fields.Date(string = 'Date of receipt of CVC 1st Stage advice',track_visibility='always')
    rec_cvc_i = fields.Char(string = 'Recommendations of CVC',track_visibility='always')
    remarks_cvci = fields.Text('Remarks (If any)')

    stpi_refdate_cvcii = fields.Date(string = 'STPI Reference Date',track_visibility='always')
    stpi_refno_cvcii = fields.Char(string = 'STPI Reference No',track_visibility='always')
    stpi_omdate_cvcii = fields.Date(string = 'CVC OM Date',track_visibility='always')
    stpi_omno_cvcii = fields.Char(string = 'CVC OM No.',track_visibility='always')
    stpi_recdate_cvcii = fields.Date(string = 'Date of receipt of CVC 2nd  Stage advice',track_visibility='always')
    rec_cvc_ii = fields.Char(string = 'Recommendations of CVC',track_visibility='always')
    remarks_cvcii = fields.Text('Remarks (If any)')

class Penalty(models.Model):
    _name = "vigilance.penalty"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Vigilance penalty"

    name = fields.Char('Penalty')
    type = fields.Selection(string="Type",selection=[('major','Major'),('minor','Minor')])