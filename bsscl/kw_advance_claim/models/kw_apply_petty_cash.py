from odoo import models, fields, api
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError
import re
from ast import literal_eval

state_selection = [('draft', 'New'), ('applied', 'Applied'),
                   ('approve', 'Approved'), ('hold', 'Hold'), ('grant', 'Grant'),
                    ('release', 'Release'),('cancel', 'Cancelled'), ('reject', 'Rejected')]


class kw_adv_apply_petty_cash(models.Model):
    _name = 'kw_advance_apply_petty_cash'
    _description = "Petty Cash"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"

    @api.depends('name')
    
    def _compute_btn_access(self):
        self.hide_btn_cancel = False
        self.show_ra_button = False
        self.show_accounts_button = False
        for record in self:
            if self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_user'):
                if self.env.user.employee_ids and not self.env.user.employee_ids.child_ids:
                    record.hide_btn_cancel = True
                if record.state == 'applied' and record.env.uid == record.action_to_be_taken_by.user_id.id \
                        and self.env.user.has_group('bsscl_employee.group_hr_ra'):
                    record.show_ra_button = True
                if record.state == 'forward' and record.env.uid == record.action_to_be_taken_by.user_id.id \
                        and self.env.user.has_group('bsscl_employee.group_hr_ra'):
                    record.show_ra_button = True
                if record.state == 'hold' and record.env.uid == record.action_to_be_taken_by.user_id.id \
                        and self.env.user.has_group('bsscl_employee.group_hr_ra'):
                    record.show_ra_button = True

                if record.state == 'approve' and self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_account'):
                    record.show_accounts_button = True
                if record.state == 'hold' and self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_account'):
                    record.show_accounts_button = True
                if record.state == 'grant' and self.env.user.has_group('kw_advance_claim.group_kw_advance_claim_account'):
                    record.show_accounts_button = True



    
    def _compute_claim_btn(self):
        for record in self:
            if record.state != 'cancel' or record.state != 'reject':
                record.hide_claim_settlement_button = True
            if record.state == 'cancel' or record.state == 'reject':
                record.hide_claim_settlement_button = False

    @api.depends('state')
    
    def _get_settlement_user_id(self):
        self.check_settlement_user = ''
        for record in self:
            if record.env.user.employee_ids.id == record.user_emp_id.id:
                record.check_settlement_user = True


    @api.onchange('write_uid')
    def _compute_approved_by(self):
        for rec in self:
            if rec.write_uid:
                rec.approved_by = rec.write_uid.employee_ids.id

    @api.onchange('claim_id')
    def _compute_on_claim(self):
        for rec in self:
            if rec.claim_id:
                rec.hide_btm_claim = True
            else:
                rec.hide_btm_claim = False

    # Form fields
    petty_cash_type = fields.Selection(string="Petty Cash Type", selection=[('others', 'Others')], required=True,
                                       default='others', track_visibility='onchange')
    code = fields.Char(string="Reference No.", default="New", readonly="1", track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', string="Currency", required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id,
                                  track_visibility='onchange')
    advance_amt = fields.Float(string="Advance Amount", required=True, track_visibility='onchange')
    advance_amt_required = fields.Float(string="Advance Amount Required")
    req_date = fields.Date(string='Required Date', required=True, track_visibility='onchange')
    description = fields.Text(string="Description", required=True, track_visibility='onchange')
    forward = fields.Boolean(string="Forward")
    user_emp_id = fields.Many2one('hr.employee', string="Employee Name", track_visibility='onchange')
    remark = fields.Text(string="Remark", track_visibility='onchange')
    amnt_paid = fields.Integer(string="Amount to be Paid", track_visibility='onchange')
    # state
    state = fields.Selection(string='Status', selection=state_selection, default='draft', track_visibility='onchange')
    payment_date = fields.Date(string="Disburse Date", track_visibility='onchange')
    department_id = fields.Many2one('hr.department', string="Department", related='user_emp_id.department_id',
                                    store=True, track_visibility='onchange')
    # division = fields.Many2one('hr.department', string="Division", related='user_emp_id.division', store=True,
    #                            track_visibility='onchange')
    # section = fields.Many2one('hr.department', string="Section", related='user_emp_id.section', store=True,
    #                           track_visibility='onchange')
    # practise = fields.Many2one('hr.department', string="Practice", related='user_emp_id.practise', store=True,
    #                            track_visibility='onchange')
    job_id = fields.Many2one('hr.job', string="Designation", related='user_emp_id.job_id', store=True,
                             track_visibility='onchange')
    mail_sent = fields.Boolean(string="Send Mail", default=False)
    # # remark action on button
    accounts_remark = fields.Text(string="Remarks")
    approved_on = fields.Date(string="Approved On")
    approved_by = fields.Many2one('hr.employee', string="Approved By", compute=_compute_approved_by)
    active = fields.Boolean(string="Active", default=True)
    emp_id = fields.Many2one('hr.employee', string="Forwarded To")
    forward_remark = fields.Char(string="Forwarded Remark")
    forwarded_by = fields.Char(string="Forwarded By")
    email_from = fields.Char("Email", size=128, help="These people will receive email.")
    action_by = fields.Char(string='Action by')
    claim_ids = fields.One2many('kw_advance_claim_settlement', 'petty_cash_id', string="Claim ID")
    claim_id = fields.Many2one('kw_advance_claim_settlement', string='Calim id')
    eligible_amount = fields.Char(string="Elgible Amount")
    # buttons hide/show
    hide_btn_cancel = fields.Boolean(compute='_compute_btn_access')
    show_ra_button = fields.Boolean(compute='_compute_btn_access')
    show_apply_btn = fields.Boolean(string="Show Apply Button")
    show_accounts_button = fields.Boolean(compute='_compute_btn_access')
    hide_claim_settlement_button = fields.Boolean(compute='_compute_claim_btn')
    # action to be taken by
    action_to_be_taken_by = fields.Many2one('hr.employee', string="Action to be taken by")
    action_taken_by = fields.Many2one('hr.employee', string="Action taken by")
    pending_status = fields.Selection(string='Pending At',
                                      selection=[('ra', 'Pending at RA'), ('accounts', 'Pending at Accounts')],
                                      track_visibility='onchange')
    settlement_status = fields.Selection(string='Settlement Status',
                                         selection=[('notsettle', 'Not Settled'), ('settle', 'Settled')],
                                         default='notsettle', track_visibility='onchange')
    check_settlement_user = fields.Boolean(string='Check Settlement User', compute='_get_settlement_user_id',
                                           default=False)
    claim_type_id = fields.Many2one('kw_advance_claim_type', required=False, string="Claim Type",
                                    track_visibility='onchange')
    category_id = fields.Many2one('kw_advance_claim_category', string="Category", required=True,
                                  track_visibility='onchange',domain=[('category','=','advance')])
    name = fields.Char(string="Ref No", required=True, default="New", readonly="1", track_visibility='onchange')
    hide_btm_claim = fields.Boolean(compute=_compute_on_claim, default=False)
    # center = fields.Many2one("res.branch",string="Center",related='user_emp_id.current_office_id',
    #                                 store=True, track_visibility='onchange')


    @api.onchange('advance_amt')
    def onchange_advance_amt(self):
        if self._origin.advance_amt_required and self._origin.advance_amt_required < self.advance_amt:
            raise ValidationError("Advance amount can not be greater than applied amount.")




    @api.onchange('category_id')
    def _onchange_category_id(self):
        lst = []
        self.claim_type_id = False
        for record in self:
            claim_type_record = self.env['kw_advance_claim_type'].sudo().search(
                [('claim_category_id', '=', record.category_id.id)])
            if claim_type_record:
                for rec in claim_type_record:
                    lst.append(rec.id)
        return {'domain': {'claim_type_id': [('id', 'in', lst)]}}

    @api.onchange('petty_cash_type')
    def get_user_employee_id(self):
        if self.petty_cash_type == 'others' or self.petty_cash_type == 'project':
            self.user_emp_id = self.env.user.employee_ids.id

    #(wagisha) for Description validation               
    @api.constrains('description')
    @api.onchange('description')          
    def _check_description_validation(self):
        for rec in self:
            if rec.description:
                if not (re.match(r'^[A-Za-z]{1}[A-Za-z\s]*$', rec.description)):
                    raise ValidationError("Description should be in alphanumeric only")
                if len(rec.description)>500:
                    raise ValidationError("Description should not be greater than 500")
                
    #(wagisha) for Amount validation               
    @api.constrains('advance_amt')
    @api.onchange('advance_amt')          
    def _check_advance_amt_validation(self):
        for rec in self:
            if rec.advance_amt and rec.advance_amt < 1:
                raise ValidationError("Advance amount should not be less than 1")
            if self.advance_amt > 20000:
                raise ValidationError("Advance amount should not be greater than 20000")
                
    @api.model
    def create(self, vals):
        vals['user_emp_id'] = self.env.user.employee_ids.id
        vals['show_apply_btn'] = True
        if vals.get('advance_amt') <= 0.00:
            raise ValidationError("Please add advance amount.")
        if vals.get('advance_amt') > 20000.00:
            raise ValidationError("Advance amount should not be greater than 20,000")
        vals['advance_amt_required'] = vals['advance_amt']
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('kw_apply_petty_cash') or '/'
        result = super(kw_adv_apply_petty_cash, self).create(vals)
        print(result, self.id, '*******&&&&&')
        # self.env.user.notify_success("Petty Cash applied successfully.")
        """ send mail user to RA"""
        if result.mail_sent == True:
            status = "Applied"
            dept_head_mail = result.user_emp_id.department_id.manager_id.work_email
            result.write({'state': 'applied', 'action_to_be_taken_by': result.user_emp_id.parent_id.id, 'pending_status': 'ra'})
            template_id = self.env.ref('kw_advance_claim.kw_petty_cash_apply_mail_template').id

            # template_id = self.env.ref("ssi_maintenance.maintenance_email_notification_template").id

            template = self.env['mail.template'].browse(template_id)

            template.with_context(vals).send_mail(result.id, force_send=True)
            # template_id = self.env.ref('kw_advance_claim.kw_petty_cash_apply_mail_template')
            template.with_context(work_email=dept_head_mail, status=status).send_mail(result.id,
                                                                                         notif_layout="kwantify_theme.csm_mail_notification_light")
        return result

    @api.constrains('req_date')
    def sal_adv_date_validation(self):
        for record in self:
            req_date = datetime.now().date()
            current_year = date.today().year
            if record.req_date < datetime.now().date():
                raise ValidationError("You cannot apply for a previous date.")
            if record.req_date.year > current_year:
                raise ValidationError("You cannot apply for a future year.")

    
    def take_action_button(self):
        view_id = self.env.ref('kw_advance_claim.kw_adv_apply_petty_cash_takeaction_form').id
        target_id = self.id
        action = self.env.ref('kw_advance_claim.kw_adv_apply_petty_cash_takeaction_form_refresh').read()[0]
        action['res_id'] = target_id
        return action
        # return {
        #     'name': 'Take Action',
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'kw_advance_apply_petty_cash',
        #     'res_id': target_id,
        #     'view_type': 'form',
        #     'view_mode': 'tree,form',
        #     'views': [(view_id, 'form')],
        #     'target': 'self',
        #     'view_id': view_id,
        # }

    
    def petty_cash_take_action_button(self):
        view_id = self.env.ref('kw_advance_claim.kw_adv_apply_petty_cash_takeaction_account_form').id
        target_id = self.id
        return {
            'name': 'Take Action',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_advance_apply_petty_cash',
            'res_id': target_id,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(view_id, 'form')],
            'target': 'self',
            'view_id': view_id,
        }

    def get_claim_record(self):
        view_id = self.env.ref('kw_advance_claim.kw_adv_claim_settlement_redirect_form').id
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Claim Settlement',
            'view_mode': 'tree,form',
            'views': [(view_id, 'form')],
            'res_model': 'kw_advance_claim_settlement',
            'target': 'self',
            'view_id': view_id,
            'context': {'default_petty_cash_id': self.id,
                        'default_empl_id': self.user_emp_id.id,
                        'default_applied_date': self.create_date,
                        'default_currency_id': self.currency_id.id,
                        'default_petty_cash_type': self.petty_cash_type,
                        'default_advance_amt': self.advance_amt,
                        'default_advance_taken': 'yes'
                        }
        }
        return action

    
    def get_emp_email(self):
        emp_name = self.env['hr.employee'].sudo().search([('user_id', '=', self.create_uid.id)], limit=1)
        if emp_name:
            return emp_name.work_email
        else:
            return ""

    def get_ra_email(self):
        emp_id = self.env['hr.employee'].sudo().search([('user_id', '=', self.create_uid.id)], limit=1)
        ra_email = ''
        if emp_id:
            ra_email = emp_id.parent_id.work_email if emp_id.parent_id else ""
        return ra_email

    def get_emp_name(self):
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.create_uid.id)], limit=1)
        username = employee and employee.name or self.create_uid.name
        return username

    @api.model
    def default_get(self, fields):
        res = super(kw_adv_apply_petty_cash, self).default_get(fields)
        if self.env.user:
            if self.env.user.employee_ids:
                empl_id = self.env.user.employee_ids.id
        return res

    
    def get_cc_email(self):
        param = self.env['ir.config_parameter'].sudo()
        cc_group = literal_eval(param.get_param('kw_advance_claim.notification_cc_ids'))
        email_list = []
        if cc_group:
            all_jobs = self.env['hr.job'].browse(cc_group)
            email_list += self.env['hr.employee'].search([('job_id', 'in', all_jobs.ids)]).mapped('work_email')
            # if empls:
            #     email_list = [emp.work_email for emp in empls if emp.work_email]
        return ",".join(email_list)

    
    def users_status_cc(self):
        emp_cc_mail_list = []
        param = self.env['ir.config_parameter'].sudo()
        emp_cc_mail_list += self.user_emp_id.department_id.manager_id.mapped('work_email')
        cc_hr_mails = param.get_param('kw_advance_claim.individual_hr_email')
        if cc_hr_mails and cc_hr_mails != "False":
            emp_cc_mail_list += cc_hr_mails.split(',')
        return ','.join(set(emp_cc_mail_list))

    
    def users_grant_cc(self):
        unique_mail_list = []
        unique_mail_list += self.user_emp_id.department_id.manager_id.mapped('work_email')
        unique_mail_list += self.user_emp_id.parent_id.mapped('work_email')
        param = self.env['ir.config_parameter'].sudo()
        cc_notify = param.get_param('kw_advance_claim.individual_hr_email')
        cc_group = literal_eval(param.get_param('kw_advance_claim.notification_cc_ids'))
        if cc_group:
            all_jobs = self.env['hr.job'].browse(cc_group)
            unique_mail_list += self.env['hr.employee'].search([('job_id', 'in', all_jobs.ids), ('work_email', '!=', False)]).mapped('work_email')
            # if empls:
            #     unique_mail_list += [emp.work_email for emp in empls if emp.work_email]
        if cc_notify and cc_notify != "False":
            unique_mail_list.append(cc_notify)
        return ','.join(set(unique_mail_list))

    
    def get_records(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('kw_advance_claim.kw_adv_claim_settlement_report_action')
        # meetingtype = self.env['calendar.event.type'].search([('code', '=', 'interview')], limit=1)
        res['domain'] = [('petty_cash_id', '=', self.id)]
        return res
