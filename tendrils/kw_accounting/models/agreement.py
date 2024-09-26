from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta


due_day_selection = [
    ('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10'),('11','11'),('12','12'),('13','13'),('14','14'),('15','15'),('16','16'),
    ('17','17'),('18','18'),('19','19'),('20','20'),('21','21'),('22','22'),('23','23'),('24','24'),('25','25'),('26','26'),('27','27'),('28','28'),('29','29'),('30','30'),('31','31')]
period_selection = [('monthly','Monthly'),('quarterly','Quarterly')]
frequency_selection = [('at_the_beginning','At the Beginning'),('at_the_end','At the End')]

class RentAgreement(models.Model):
    _name = 'rent_agreement'
    _description = 'Rent Agreement'
    _rec_name = 'purpose'

    account_code = fields.Char(string="Account Code")
    location = fields.Char(string="Location")
    purpose = fields.Selection([('office_rent','Office Rent'),('electricity','Electricity'),('maintainance_charges','Maintainance Charges'),('vehicle_rent','Vehicle Rent'),('others','Others')],string="Purpose") 
    period_start = fields.Date(string="Period From",compute="get_min_max_date",store=True)
    period_end = fields.Date(string="Period Till",compute="get_min_max_date",store=True)
    monthly_amount = fields.Float(string="Monthly Amt.",compute="get_min_max_date",store=True)
    security_deposit_paid = fields.Float(string="Security Deposit Paid")
    security_deposit_account_code = fields.Many2one('account.account',string="Security Deposit Account")
    due_date = fields.Selection(due_day_selection,string="Due Date")
    period = fields.Selection(period_selection,string="Period")
    frequency = fields.Selection(frequency_selection,string="Frequency")
    status = fields.Selection([('open','Open'),('renewed','Renewed'),('closed','Closed')],string="Status")
    remarks = fields.Text(string="Remarks")
    partner_id = fields.Many2one('res.partner','Vendor')
    agreement_copy = fields.Binary(string="Agreement Copy",attachment=True)
    agreement_copy_file_name = fields.Char(string="Agreement Copy File Name")
    security_deposit_code = fields.Char(related="security_deposit_account_code.code",string='Security Deposit Account Code')
    security_amount = fields.Float(string="Closing Balance",compute="get_security_amount")
    rent_agreement_lines = fields.One2many('rent_agreement_log', 'rent_agreement_id', string="Rent Agreement Log", index=True)
    address = fields.Text(string="Address")
    expense_type = fields.Selection([('project','Project'),('treasury','Treasury'),('capital','Capital')],string="Expense Type")
    
    @api.multi
    @api.depends('rent_agreement_lines')
    def get_min_max_date(self):
        for rec in self:
            if len(rec.rent_agreement_lines) > 0:
                rec.monthly_amount = rec.rent_agreement_lines[0].agreement_amount
                self.period_start = min(rec.rent_agreement_lines.mapped('from_date'))
                self.period_end = max(rec.rent_agreement_lines.mapped('to_date'))
                

    @api.constrains('rent_agreement_lines')
    def rent_date_validate(self):
        for rec in self:
            if len(rec.rent_agreement_lines) == 0:
                raise ValidationError("Please fill rent schedule")
                    
    @api.multi
    def get_security_amount(self):
        for rec in self:
            security_line_ids = self.env['account.move.line'].search([('account_id','=',rec.security_deposit_account_code.id)])
            rec.security_amount = sum(security_line_ids.mapped('debit')) - sum(security_line_ids.mapped('credit'))

class AgreementLog(models.Model):
    _name = 'rent_agreement_log'
    _description = "Rent Agreement Log"

    @api.model
    def _get_date(self):
        agreement_id = self.search([('rent_agreement_id','=',self._context.get('default_rent_agreement_id'))],order="id desc",limit=1)
        from_date = (agreement_id.to_date + relativedelta(days=1)) if agreement_id else None

        return from_date

    rent_agreement_id = fields.Many2one('rent_agreement', string="Rent Agreement")
    from_date = fields.Date(string="From Date",default=_get_date)
    to_date = fields.Date(string="To Date")
    agreement_amount = fields.Float(string="Amount")

    @api.constrains('from_date', 'to_date')
    def rent_date_validate(self):
        agreement_id = self.search([('rent_agreement_id','=',self.rent_agreement_id.id)],order="id desc",limit=2)
        x = False
        if len(agreement_id) >= 2:
            x = agreement_id[1]

        for rec in self:
            if rec.from_date > rec.to_date:
                raise ValidationError("From Date should be less than To Date.")
            if x and rec.from_date != (x.to_date + relativedelta(days=1)):
                raise ValidationError("Rent Period is not continuous.")