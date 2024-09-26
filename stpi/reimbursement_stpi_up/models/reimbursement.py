from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError,UserError
import re
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

class Reimbursement(models.Model):

    _name = "reimbursement"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Reimbursement"
    _order = 'create_date desc'

    @api.model
    def default_get(self, field_list):
        result = super(Reimbursement, self).default_get(field_list)
        ts_user_id = self.env.context.get('user_id', self.env.user.id)
        result['employee_id'] = self.env['hr.employee'].search([('user_id', '=', ts_user_id)], limit=1).id
        return result


    name = fields.Selection([
        ('lunch', 'Lunch Subsidy'),
        ('telephone', 'Telephone Reimbursement'),
        ('mobile', 'Mobile Reimbursement'),
        ('medical', 'Medical Reimbursement'),
        ('tuition_fee', 'Tuition Fee claim'),
        ('briefcase', 'Briefcase Reimbursement'),
        ('quarterly', 'Newspaper Reimbursements'),
    ], string='Reimbursement Type', store=True, track_visibility='always')
    employee_id = fields.Many2one('hr.employee', store=True, track_visibility='always')
    job_id = fields.Many2one('hr.job', string='Functional Designation', store=True, track_visibility='always')
    branch_id = fields.Many2one('res.branch', string='Branch', store=True, track_visibility='always')
    department_id = fields.Many2one('hr.department', string='Department', store=True, track_visibility='always')
    lunch_daily = fields.Char('Lunch Daily: ', track_visibility='always')
    net_amount = fields.Float('Amount you get : ', track_visibility='always')
    lunch_tds_amt = fields.Float('Amount for TDS')
    claimed_amount = fields.Float('Claimed Amount', track_visibility='always')
    Approved_amount = fields.Float('Approved Amount', track_visibility='always')
    from_date = fields.Date('From Date', track_visibility='always')
    to_date = fields.Date('To Date', track_visibility='always')
    working_days = fields.Char(string='Number of days: ', track_visibility='always')
    remarks = fields.Text(string='Remarks: ', track_visibility='always')
    service_provider = fields.Char(string='Service Provider', track_visibility='always')
    phone = fields.Binary(string='Phone Attachment', track_visibility='always')
    bill_no = fields.Char(string='Bill number', track_visibility='always')
    no_of_months = fields.Char(string='No of months', track_visibility='always')
    bill_due_date = fields.Date(string='Bill Due Date', track_visibility='always')
    amount_phone = fields.Float(string='Amount', track_visibility='always')
    total_amount = fields.Float(string='Total Amount', track_visibility='always')
    name_of_child = fields.Char(string='Name of Child', track_visibility='always')
    dob = fields.Date(string='Date of birth', track_visibility='always')
    name_of_school = fields.Char(string='Name of School', track_visibility='always')
    class_current = fields.Char(string='Class in which Studying', track_visibility='always')
    academic_year = fields.Char(string='Academic Year', track_visibility='always')
    brief_amount = fields.Float('Amount', track_visibility='always')
    dis_child = fields.Boolean(
        string='Whether the child for whom Children Education Allowance is applied is a disabled child?', track_visibility='always')
    bc_school = fields.Boolean(string='Whether Bonafide Certificate from School is enclosed', track_visibility='always')
    bc_amount = fields.Boolean(
        string='Whether Bonafide Certificate mentioning the amount of expenditure wrt Hostel is enclosed ', track_visibility='always')
    fee_enclose = fields.Boolean(string='Whether Original Fee Receipts is enclosed', track_visibility='always')
    claim_date_from = fields.Date('Claim Date: From', track_visibility='always')
    claim_date_to = fields.Date('Claim Date: To', track_visibility='always')
    claim_date = fields.Date('Claim Date', track_visibility='always')
    approved_date = fields.Date('Approved On', track_visibility='always')
    rejected_date = fields.Date('Rejected On', track_visibility='always')
    relative_ids = fields.One2many('reimbursement.relatives','reimbursement', string='Details', track_visibility='always')
    reimbursement_sequence = fields.Char('Reimbursement number', track_visibility='always')
    state = fields.Selection([('draft', 'Draft'), ('waiting_for_approval', 'Submitted'), ('forwarded', 'Forwarded'), ('approved', 'Approved'), ('rejected', 'Rejected')
                               ], required=True, default='draft', track_visibility='always', string='Status')


    @api.onchange('employee_id')
    @api.constrains('employee_id')
    def onchange_emp_get_base(self):
        for rec in self:
            rec.job_id = rec.employee_id.job_id.id
            rec.department_id = rec.employee_id.department_id.id
            rec.branch_id = rec.employee_id.branch_id.id

    # @api.constrains('name')
    @api.onchange('name')
    def _onchange_name(self):
        for rec in self:
            if rec.name:
                if rec.name == 'lunch' or rec.name == 'telephone' or rec.name == 'mobile':
                    rec.from_date = datetime.now().date().replace(day=1)
                    rec.to_date = rec.from_date + relativedelta(months=1) - relativedelta(days=1)
                    if rec.employee_id.date_of_join and rec.from_date < rec.employee_id.date_of_join < rec.to_date:
                        rec.from_date = rec.employee_id.date_of_join
                        rec.claim_date_from = rec.from_date + relativedelta(months=1)
                        rec.claim_date_to = rec.claim_date_from + relativedelta(days=6)
                        rec.claim_date = datetime.now().date()
                    else:
                        rec.claim_date_from = rec.from_date + relativedelta(months=1)
                        rec.claim_date_to = rec.claim_date_from + relativedelta(days=6)
                        rec.claim_date = datetime.now().date()
                elif rec.name == 'medical' or rec.name == 'quarterly':
                    rec.from_date = datetime.now().date().replace(day=1)
                    rec.to_date = rec.from_date + relativedelta(months=3) - relativedelta(days=1)
                    if rec.employee_id.date_of_join and rec.from_date < rec.employee_id.date_of_join < rec.to_date:
                        rec.from_date = rec.employee_id.date_of_join
                        rec.claim_date_from = rec.from_date + relativedelta(months=3)
                        rec.claim_date_to = rec.claim_date_from + relativedelta(days=6)
                        rec.claim_date = datetime.now().date()
                    else:
                        rec.claim_date_from = rec.from_date + relativedelta(months=3)
                        rec.claim_date_to = rec.claim_date_from + relativedelta(days=6)
                        rec.claim_date = datetime.now().date()
                elif rec.name == 'tuition_fee':
                    rec.from_date = datetime.now().date().replace(day=1)
                    rec.to_date = rec.from_date + relativedelta(months=12) - relativedelta(days=1)
                    if rec.employee_id.date_of_join and rec.from_date < rec.employee_id.date_of_join < rec.to_date:
                        rec.from_date = rec.employee_id.date_of_join
                        rec.claim_date_from = rec.from_date + relativedelta(months=12)
                        rec.claim_date_to = rec.claim_date_from + relativedelta(days=6)
                        rec.claim_date = datetime.now().date()
                    else:
                        rec.claim_date_from = rec.from_date + relativedelta(months=12)
                        rec.claim_date_to = rec.claim_date_from + relativedelta(days=6)
                        rec.claim_date = datetime.now().date()
                elif rec.name == 'briefcase':
                    rec.from_date = datetime.now().date().replace(day=1)
                    rec.to_date = rec.from_date + relativedelta(months=1) - relativedelta(days=1)
                    if rec.employee_id.date_of_join and rec.from_date < rec.employee_id.date_of_join < rec.to_date:
                        rec.from_date = rec.employee_id.date_of_join
                else:
                    rec.from_date = False
                    rec.to_date = False
                    rec.claim_date_from = False
                    rec.claim_date_to = False
                    rec.claim_date = False

    @api.constrains('name','employee_id','claimed_amount','from_date','to_date')
    @api.onchange('name','employee_id','claimed_amount','from_date','to_date')
    def _onchange_name_employee(self):
        for rec in self:
            if rec.employee_id and rec.name == 'lunch':
                count = 0
                serch_id = self.env['reimbursement.attendence'].search([('employee_id', '=', rec.employee_id.id),('date_related_month', '>=', rec.from_date),('date_related_month', '<', rec.to_date)])
                for i in serch_id:
                    count += i.present_days
                rec.lunch_daily = '75'
                rec.working_days = count
                rec.net_amount = float(count * 75)
                rec.lunch_tds_amt = float(count * 50)
            elif rec.employee_id and rec.name:
                if rec.name == 'telephone' or rec.name == 'mobile':
                    gr_id = self.env['reimbursement.configuration'].search([('name', '=', rec.name),('group_ids.users','=',self.env.user.id)],order='name desc', limit=1)
                    if gr_id:
                        if int(rec.claimed_amount) > int(gr_id.allowed) and gr_id.full == False:
                            rec.Approved_amount = gr_id.allowed
                        else:
                            rec.Approved_amount = int(rec.claimed_amount)
                    else:
                        rec.Approved_amount = 0
                elif rec.name == 'medical':
                    gr_id = self.env['reimbursement.configuration'].search([('name', '=', rec.name),('group_ids.users','=',self.env.user.id)],order='name desc', limit=1)
                    if gr_id:
                        if int(rec.total_amount) > int(gr_id.allowed) and gr_id.full == False:
                            rec.total_amount = gr_id.allowed
                        else:
                            rec.total_amount = int(rec.total_amount)
                    else:
                        rec.total_amount = 0
                elif rec.name == 'briefcase':
                    gr_id = self.env['reimbursement.configuration'].search([('name', '=', rec.name),('group_ids.users','=',self.env.user.id)],order='name desc', limit=1)
                    if gr_id:
                        if int(rec.brief_amount) > int(gr_id.allowed) and gr_id.full == False:
                            rec.brief_amount = gr_id.allowed
                        else:
                            rec.brief_amount = int(rec.brief_amount)
                    else:
                        rec.brief_amount = 0
                elif rec.name == 'quarterly':
                    gr_id = self.env['reimbursement.configuration'].search([('name', '=', rec.name),('group_ids.users','=',self.env.user.id)],order='name desc', limit=1)
                    if gr_id:
                        if int(rec.amount_phone) > int(gr_id.allowed) and gr_id.full == False:
                            rec.amount_phone = gr_id.allowed
                        else:
                            rec.amount_phone = int(rec.amount_phone)
                    else:
                        rec.amount_phone = 0




    @api.multi
    def unlink(self):
        for data in self:
            if data.state not in ('draft', 'rejected'):
                raise UserError(
                    'You cannot delete a Reimbursement which is not in draft or Rejected state')
        return super(Reimbursement, self).unlink()


    @api.constrains('from_date','to_date')
    @api.onchange('from_date','to_date')
    def onchange_date(self):
        for record in self:
            if record.from_date > record.to_date:
                raise ValidationError(
                    _('Start date should be less than or equal to end date, but should not be greater than end date'))
            if record.name == 'lunch' or record.name == 'telephone' or record.name == 'mobile':
                f_date = (record.from_date).replace(day=1)
                t_date = f_date + relativedelta(months=1) - relativedelta(days=1)
                if record.to_date and record.from_date and record.employee_id.date_of_join and (record.to_date - record.employee_id.date_of_join).days < (t_date - f_date).days:
                    record.claim_date_from = f_date + relativedelta(months=1)
                    record.claim_date_to = record.claim_date_from + relativedelta(days=6)
                    record.claim_date = datetime.now().date()
                elif record.to_date and record.from_date and (record.to_date - record.from_date).days < (t_date - f_date).days:
                    raise ValidationError(
                            "You can claim for %s" % record.name + " minimum of  %s" % ((t_date - f_date).days + 1) + " days" )
                else:
                    record.claim_date_from = f_date + relativedelta(months=1)
                    record.claim_date_to = record.claim_date_from + relativedelta(days=6)
                    record.claim_date = datetime.now().date()
            elif record.name == 'medical' or record.name == 'quarterly':
                f_date = datetime.now().date().replace(day=1)
                t_date = f_date + relativedelta(months=3) - relativedelta(days=1)
                if record.to_date and record.from_date and (record.to_date - record.from_date).days < (t_date - f_date).days:
                    raise ValidationError(
                        "You can claim for %s" % record.name + " minimum of  %s" % ((t_date - f_date).days + 1) + " days" )
                record.claim_date_from = record.from_date + relativedelta(months=3)
                record.claim_date_to = record.claim_date_from + relativedelta(days=6)
                record.claim_date = datetime.now().date()
            elif record.name == 'tuition_fee':
                f_date = datetime.now().date().replace(day=1)
                t_date = f_date + relativedelta(months=12) - relativedelta(days=1)
                if record.to_date and record.from_date and (record.to_date - record.from_date).days < (t_date - f_date).days:
                    raise ValidationError(
                        "You can claim for %s" % record.name + " minimum of  %s" % ((t_date - f_date).days + 1) + " days" )
                record.claim_date_from = record.from_date + relativedelta(months=12)
                record.claim_date_to = record.claim_date_from + relativedelta(days=6)
                record.claim_date = datetime.now().date()



    @api.multi
    def button_submit(self):
        for rec in self:
            search_id = self.env['reimbursement'].search([('employee_id', '=', rec.employee_id.id), ('name', '=', rec.name), ('state', 'not in', ['draft','rejected'])])
            index = False
            for emp in search_id:
                if rec.from_date <= emp.from_date or rec.from_date >= emp.to_date:
                    if rec.to_date <= emp.from_date or rec.to_date >= emp.to_date:
                        if not (rec.from_date <= emp.from_date and rec.to_date >= emp.to_date):
                            index = True
                        else:
                            raise ValidationError("This reimbursement is already applied for this duration, please correct the dates")
                    else:
                        raise ValidationError("This reimbursement is already applied for this duration, please correct the dates")
                else:
                    raise ValidationError("This reimbursement is already applied for this duration, please correct the dates")
            else:
                index = True
            if index == True:
                rec.claim_date = datetime.now().date()
                if rec.claim_date_from < rec.claim_date:
                    if rec.name != 'briefcase':
                        if rec.name == 'lunch' and int(rec.net_amount) <= 0:
                            raise ValidationError(
                                "Approved Amount must be greater than zero")
                        elif rec.name == 'telephone' and int(rec.Approved_amount) <= 0:
                            raise ValidationError(
                                "Approved Amount must be greater than zero")
                        elif rec.name == 'mobile' and int(rec.Approved_amount) <= 0:
                            raise ValidationError(
                                "Approved Amount must be greater than zero")
                        elif rec.name == 'medical' and int(rec.total_amount) <= 0:
                            raise ValidationError(
                                "Total Amount must be greater than zero")
                        elif rec.name == 'quarterly' and int(rec.amount_phone) <= 0:
                            raise ValidationError(
                                "Total Amount must be greater than zero")
                        else:
                            if rec.claim_date_from > rec.claim_date or rec.claim_date > rec.claim_date_to:
                                gr_id = self.env['reimbursement.configuration'].search(
                                    [('name', '=', rec.name), ('group_ids.users', '=', self.env.user.id), ('open', '=', True)], order='name desc',
                                    limit=1)
                                if gr_id:
                                    rec.write({'state': 'waiting_for_approval'})
                                else:
                                    raise ValidationError("You can claim for %s" % rec.name + " between  %s" % rec.claim_date_from + " and %s" % rec.claim_date_to)
                            else:
                                rec.write({'state': 'waiting_for_approval'})
                    else:
                        if int(rec.brief_amount) <= 0:
                            raise ValidationError(
                                "Amount must be greater than zero")
                        else:
                            rec.write({'state': 'waiting_for_approval'})
                else:
                    if rec.name != 'briefcase':
                        raise ValidationError(
                            "You are not allowed to take the future reimbursement")
                    else:
                        if int(rec.brief_amount) <= 0:
                            raise ValidationError(
                                "Amount must be greater than zero")
                        else:
                            rec.write({'state': 'waiting_for_approval'})


    @api.model
    def create(self, vals):
        res =super(Reimbursement, self).create(vals)
        sequence = ''
        seq = self.env['ir.sequence'].next_by_code('reimbursement')
        sequence = 'REIMBURSEMENT - ' + str(seq)
        res.reimbursement_sequence = sequence
        return res

    @api.multi
    @api.depends('reimbursement_sequence')
    def name_get(self):
        res = []
        for record in self:
            if record.reimbursement_sequence:
                name = record.reimbursement_sequence
            else:
                name = 'REIMBURSEMENT'
            res.append((record.id, name))
        return res

    @api.multi
    def button_approved(self):
        for rec in self:
            rec.approved_date = datetime.now().date()
            rec.write({'state': 'approved'})

    @api.multi
    def button_reject(self):
        for rec in self:
            rec.write({'state': 'rejected'})


    @api.multi
    def button_reset_to_draft(self):
        for rec in self:
            self.ensure_one()
            compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
            ctx = dict(
                default_composition_mode='comment',
                default_res_id=self.id,

                default_model='reimbursement',
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
            self.rejected_date = datetime.now().date()
            self.write({'state': 'draft'})
            return mw



class ReimbursementConfiguration(models.Model):
    _name = "reimbursement.configuration"
    _description = "Reimbursement Configuration"

    name = fields.Selection([
        ('lunch', 'Lunch Subsidy'),
        ('telephone', 'Telephone Reimbursement'),
        ('mobile', 'Mobile Reimbursement'),
        ('medical', 'Medical Reimbursement'),
        ('tuition_fee', 'Tuition Fee claim'),
        ('briefcase', 'Briefcase Reimbursement'),
        ('quarterly', 'Newspaper Reimbursements'),
    ], string='Reimbursement Type')
    group_ids = fields.Many2many('res.groups', string='Groups')
    full = fields.Boolean('Full')
    allowed = fields.Char('Allowed')
    open = fields.Boolean('Open')

    @api.constrains('full')
    @api.onchange('full')
    def _onchange_full(self):
        for rec in self:
            if rec.full == True:
                rec.allowed = '0'



class ReimbursementTution(models.Model):
    _name = "reimbursement.relatives"
    _description = "Reimbursement Relatives"


    reimbursement = fields.Many2one('reimbursement', string='Reimbursement')
    employee_id = fields.Many2one('hr.employee', string='Employee', related='reimbursement.employee_id')
    family_details = fields.Many2one('employee.relative', string='Family Details', domain="[('employee_id', '=', employee_id),('tuition', '=', True)]")
    name_of_school = fields.Char(string='Name of School')
    class_current = fields.Char(string='Class in which Studying')
    academic_year = fields.Char(string='Academic Year')
    dis_child = fields.Boolean(
        string='Whether the child for whom Children Education Allowance is applied is a disabled child?')
    bc_school = fields.Boolean(string='Whether Bonafide Certificate from School is enclosed')
    bc_amount = fields.Boolean(
        string='Whether Bonafide Certificate mentioning the amount of expenditure wrt Hostel is enclosed ')
    fee_enclose = fields.Boolean(string='Whether Original Fee Receipts is enclosed')