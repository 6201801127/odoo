from math import ceil, floor
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
from ast import literal_eval
import datetime,calendar
from datetime import date, datetime, timedelta
from dateutil import relativedelta


class FdTracker(models.Model):
    _name = "fd_tracker"
    _description = "fd_tracker"
    _rec_name = 'acc_number'
    # _order = 'start_date'

    
    serial_no = fields.Char(string="Serial", default='New')   
    acc_number = fields.Char('A/C No')
    bg_number = fields.Char('Bg No')
    start_date = fields.Date('Start Dt.')
    maturity_date = fields.Date('Maturity Dt.')
    principal_amt = fields.Float('Principal')
    rate_of_interest = fields.Float('RoI')
    fd_type = fields.Selection([('cumulative','Cumulative'),('fixed','Fixed')],string="Type")
    maturity_amt = fields.Float('Maturity Amt.')
    state = fields.Selection([('live', 'Live'), ('renewed', 'Renewed'),('closed', 'Closed')],
                             string='Closed/Live', copy=False, default='live')
    recovered_or_renewed_dt = fields.Date('Maturity recd/Renewal Date')
    recovered_or_renewed_amt = fields.Float('Maturity recd/Renewal Amt')
    maturity_interest_net = fields.Float('Maturity Interest (Net)')
    tds = fields.Float('TDS')
    maturity_interest_gross = fields.Float('Maturity Interest (Gross)')
    is_fd_live = fields.Boolean('FD Live', default=False)
    is_fd_renew = fields.Boolean('FD Renew', default=False)
    interest_till = fields.Float('Interest')  
    interest_till_date = fields.Date('Interest Till Date')  
    interest_calculation_log_ids = fields.One2many('interest_calculation_log', 'fd_tracker_id', string='Interest Calculation Log') 
    current_status = fields.Selection([
        ('live', 'Live'),
        ('renewed', 'Renewed'),
        ('closed', 'Closed')
    ], string='Current Status', compute='_compute_current_status', store=True, copy=False)
    bg_tagged_ids = fields.One2many('bg_reference','parent_id',string="BG Tagged")
    lien_amount = fields.Float(string="Lien Amount",compute="_get_lien_amount",store=True)
    free_amount = fields.Float(string="Free Amount",compute="_get_lien_amount",store=True)
    ckeck_thirty_days = fields.Date(string="Check 30 Days",compute="get_thirty_days")
    bank_id = fields.Char(string="Bank")

    start_date_char = fields.Char(string="start_date_char",compute="date_to_char")
    maturity_date_char = fields.Char(string="maturity_date_char",compute="date_to_char")
    recovered_or_renewed_dt_char = fields.Char(string="recovered_or_renewed_dt_char",compute="date_to_char")
    interest_till_date_char = fields.Char(string="interest_till_date_char",compute="date_to_char")

    def date_to_char(self):
        for rec in self:
            rec.start_date_char = rec.start_date.strftime('%d-%m-%y') if rec.start_date else ''
            rec.maturity_date_char = rec.maturity_date.strftime('%d-%m-%y') if rec.maturity_date else ''
            rec.recovered_or_renewed_dt_char = rec.recovered_or_renewed_dt.strftime('%d-%m-%y') if rec.recovered_or_renewed_dt else ''
            rec.interest_till_date_char = rec.interest_till_date.strftime('%d-%m-%y') if rec.interest_till_date else ''
    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            name = str(rec.serial_no +' - '+ rec.acc_number)   
            result.append((rec.id, name))
        return result

    def get_thirty_days(self):
        for rec in self:
            thirty_days = datetime.today() + relativedelta.relativedelta(months=1)
            rec.ckeck_thirty_days = thirty_days.date()

    @api.multi
    @api.onchange('bg_tagged_ids')
    def _get_lien_amount(self):
        for rec in self:
            total_bg_amount = rec.bg_tagged_ids.mapped('bg_lien_amount')
            rec.lien_amount = sum(total_bg_amount) 
            rec.free_amount = rec.principal_amt - rec.lien_amount

    @api.depends('state', 'acc_number')
    def _compute_current_status(self):
        for record in self:
            last_record = self.search([('acc_number', '=', record.acc_number)], order='id desc', limit=1)

            if last_record and record != last_record:
                record.current_status = last_record.state
            elif record.state == 'closed':
                record.current_status = 'closed'
            else:
                record.current_status = 'live'

    # @api.constrains('start_date', 'maturity_date')
    # def validate_date(self):
    #     current_date = datetime.now().date()
    #     for record in self:
    #         if record.maturity_date < current_date:
    #             raise ValidationError("The maturity date should not be less than current date.")
    #         if record.maturity_date < record.start_date:
    #             raise ValidationError("The maturity date should be greater than start date.")


    
    @api.multi
    def action_btn_calculate_interest(self):

        action_id = self.env.ref('kw_accounting.account_fd_calc_interest_action_window').id
        return {
                    'type': 'ir.actions.act_url',
                    'url': f'/web#action={action_id}&model=calc_fd_interest_wizard&view_type=form',
                    'target': 'new',
                }


    # @api.constrains('acc_number')
    # def check_acc_number(self):
    #     for record in self:
    #         if record.acc_number and not self._context.get('renewal'):
    #             existing_records = self.env['fd_tracker'].search([
    #                 ('acc_number', '=', record.acc_number),
    #                 ('state', 'in', ['live', 'renewed']),
    #             ])
    #             if existing_records:
    #                 raise ValidationError('Account number already exists for a live or renewed record.')

    @api.onchange('maturity_interest_net','tds')
    def _onchange_interest_gross(self):
         self.maturity_interest_gross = (self.maturity_interest_net + self.tds) if (self.maturity_interest_net > 0 or self.tds > 0) else 0

    @api.onchange('recovered_or_renewed_amt','principal_amt')
    def _onchange_interest_net(self):
         self.maturity_interest_net = (self.recovered_or_renewed_amt - self.principal_amt) if self.recovered_or_renewed_amt > 0 else 0

    # @api.model
    # def create(self, vals):
    #     seq = self.env['ir.sequence'].next_by_code('serial.sequence') or '/'
    #     vals['serial_no'] = seq
    #     return super(FdTracker, self).create(vals)  
          
    @api.multi
    def make_fd_renewed(self):
        if not self.recovered_or_renewed_dt :
            raise ValidationError("Maturity recd/Renewal Date should not be left empty for renewal.")
        form_view_id = self.env.ref("kw_accounting.renew_date_assign_wizard_form_view").id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Renew Date Assign Wizard',
            'res_model': 'renew_date_assign_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'new',
            'context': {'renewal': True},
        }  
        
  
    @api.multi
    def make_fd_close(self):
        self.state = 'closed'   


    @api.multi
    def fd_expire_reminder_mail(self):
        today = fields.Date.today()
        expiration_date = today + timedelta(days=7)
        expiring_records = self.env['fd_tracker'].sudo().search([
            ('maturity_date', '>=', today),
            ('maturity_date', '<=', expiration_date),
            ('state','not in',('closed','renewed'))
        ])

        expiring_records_list = []

        if expiring_records:
            for record in expiring_records:
                expiring_records_list.append(f"{record.serial_no}:{record.acc_number}:{record.maturity_date}:{record.maturity_amt}:{record.fd_type}:")

        if len(expiring_records) > 0:
            param = self.env['ir.config_parameter'].sudo()
            acc_group = literal_eval(param.get_param('kw_accounting.fd_mail_emp_ids'))
            email_list = []
            if acc_group:
                empls = self.env['hr.employee'].search([('id', 'in', acc_group), ('active', '=', True)])
                email_list = empls.filtered(lambda r: r.work_email != False).mapped('work_email')
            email_to = email_list and ",".join(email_list) or ''
            extra_params = {'expiring_records_list':expiring_records_list,'email_to': email_to}
            self.env['hr.employee'].employee_send_custom_mail(res_id=self.id,
                                                                notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                template_layout='kw_accounting.fd_expire_email_template',
                                                                ctx_params=extra_params,
                                                                description="FD Expire Reminder")
            self.env.user.notify_info(message='Mail sent successfully.')
        


class FdInterestCalc(models.TransientModel):
    _name = "calc_fd_interest_wizard"
    _description = "calc_fd_interest_wizard"
    _rec_name = 'calculate_interest_till_date'

    calculate_interest_till_date = fields.Date('Calculate Interest Till')    

    @api.multi
    def calculate_fd_interest(self):
        fd_records = self.env['fd_tracker'].sudo().search([('state', 'not in', ('closed', 'renewed'))])
        
        for record in fd_records:
            
            if record.start_date and self.calculate_interest_till_date:
                current_fiscal_year_id = self.env['account.fiscalyear'].sudo().search([
                    ('date_start', '<=', self.calculate_interest_till_date),
                    ('date_stop', '>=', self.calculate_interest_till_date)
                ], limit=1)

                if record.start_date > current_fiscal_year_id.date_start:
                    delta = self.calculate_interest_till_date - record.start_date
                    number_of_days = delta.days + 1
                    roi = record.rate_of_interest / 100
                    current_year = datetime.today().year
                    number_of_dayss = 366 if calendar.isleap(int(current_year)) else 365
                    interest = round((record.principal_amt * roi/number_of_dayss) * number_of_days)  # Round down to the nearest integer

                elif record.start_date < current_fiscal_year_id.date_start:
                    delta = self.calculate_interest_till_date - current_fiscal_year_id.date_start
                    number_of_days = delta.days + 1
                    roi = record.rate_of_interest / 100
                    current_year = datetime.today().year
                    number_of_dayss = 366 if calendar.isleap(int(current_year)) else 365
                    interest = round((record.principal_amt * roi/number_of_dayss) * number_of_days)  # Round down to the nearest integer
                    
                existing_log = self.env['interest_calculation_log'].search([
                    ('fd_tracker_id', '=', record.id),
                    ('calculation_date', '=', self.calculate_interest_till_date),
                ])
                
                if existing_log:
                    existing_log.write({'calculated_on': date.today(),
                                        'calculated_interest': interest})
                else:
                    self.env['interest_calculation_log'].create({
                        'calculated_on': date.today(),
                        'start_date': record.start_date,
                        'calculation_date': self.calculate_interest_till_date,
                        'calculated_interest': interest,
                        'fd_tracker_id': record.id,
                    })
                    
                record.write({'interest_till': interest,
                              'interest_till_date': self.calculate_interest_till_date})
        return {
            'name': _("FD Interest as on %s") % self.calculate_interest_till_date.strftime("%d-%b-%Y"),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'views': [[self.env.ref('kw_accounting.interest_calculation_log_tree').id, 'tree']],
            'res_model': 'interest_calculation_log',
            'domain': [('fd_tracker_id', '!=', False),('calculation_date','=',self.calculate_interest_till_date)],
            
        }        
        
class InterestCalculationLog(models.Model):
    _name = "interest_calculation_log"
    _description = "Interest Calculation Log"

    start_date = fields.Date('Start Date', required=True, readonly=True)
    calculation_date = fields.Date('Calculation Till Date', required=True, readonly=True)
    calculated_on = fields.Date('Calculated On', required=True, readonly=True)
    calculated_interest = fields.Float('Calculated Interest',readonly=True)
    fd_tracker_id = fields.Many2one('fd_tracker', string='FD Tracker Record', required=True, ondelete='cascade')    
    
    
class FdReportWizard(models.TransientModel):
    _name = "fd_report_wizard"
    _description = "fd_report_wizard"
    # _rec_name = ''

    date_from = fields.Date('Date From', required=True)
    date_to = fields.Date('Date To', required=True)
    specify_date = fields.Selection([('issue_date','Issue Date'),('maturity_date','Maturity Date')],string='Specify Date Type',default=False,required=True)

    @api.constrains('specify_date')
    def _check_duplicate_department_id(self):
        for record in self:
            if not record.specify_date:
                raise ValidationError("Specify the date type!")

    def find_related_fd_report(self):
        domain = []

        if self.date_from and self.date_to:
            if self.specify_date == 'issue_date':
                domain.append(('start_date', '>=', self.date_from))
                domain.append(('start_date', '<=', self.date_to))
            elif self.specify_date == 'maturity_date':
                domain.append('|')
                domain.append(('recovered_or_renewed_dt', '=', False))
                domain.append('&')
                domain.append(('recovered_or_renewed_dt', '>=', self.date_from))
                domain.append(('recovered_or_renewed_dt', '<=', self.date_to))
                domain.append('|')
                domain.append(('maturity_date', '>=', self.date_from))
                domain.append(('maturity_date', '<=', self.date_to))

        fd_reports = self.env['fd_tracker'].search(domain)

        view_id = self.env.ref('kw_accounting.fd_tracker_report_tree').id
        return {
            'name': 'FD Report',
            'type': 'ir.actions.act_window',
            'view_id': view_id,
            'res_model': 'fd_tracker',
            'view_mode': 'tree',
            'domain': domain,
        }
    # def find_related_fd_report(self):
    #     domain = [('start_date', '>=', self.date_from)]

    #     if self.specify_date == 'maturity_date':
    #         if 'recovered_or_renewed_dt' in self.env['fd_tracker']._fields:
    #             domain.append('|')
    #             domain += [
    #                 '&',
    #                 ('maturity_date', '>=', self.date_from),
    #                 ('maturity_date', '<=', self.date_from),
    #             ]
    #             domain += [
    #                 '&',
    #                 ('recovered_or_renewed_dt', '>=', self.date_from),
    #                 ('recovered_or_renewed_dt', '<=', self.date_from),
    #                 ('recovered_or_renewed_dt', '!=', False),
    #             ]
    #         else:
    #             domain.append(('maturity_date', '<=', self.date_from))

    #     fd_reports = self.env['fd_tracker'].search(domain)

    #     for fd_report in fd_reports:
    #         print("Found FD Report:", fd_report.serial_no)

    #     view_id = self.env.ref('kw_accounting.fd_tracker_report_tree').id
    #     return {
    #         'name': 'FD Report',
    #         'type': 'ir.actions.act_window',
    #         'view_id': view_id,
    #         'res_model': 'fd_tracker',
    #         'view_mode': 'tree',
    #         'domain': [('id', 'in', fd_reports.ids)],
    #     }

class BGReference(models.Model):
    _name = 'bg_reference'
    _description = 'bg Reference'

    parent_id = fields.Many2one('fd_tracker',string="FD No")
    fd_line_id = fields.Many2one('fd_reference',string="FD Reference") 
    bg_id = fields.Many2one('bg_tracker',related="fd_line_id.parent_id",string="BG No.")
    bg_lien_amount= fields.Float(string="BG Lien Amount",related="fd_line_id.bg_amount")

    @api.model
    def fd_bg_report(self,**args):
        pass
