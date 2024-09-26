from odoo import models , fields, _ , api 
from odoo.exceptions import ValidationError
from odoo.osv import expression
from datetime import date
from dateutil.relativedelta import relativedelta


class Contract(models.Model):
    _inherit = 'hr.contract'

    employee_type = fields.Selection([('regular', 'Regular Employee'),
                                      ('contractual_with_agency', 'Contractual with Agency'),
                                      ('contractual_with_bsscl', 'Contractual with BSSCL')], string='Employment Type',
                                      tracking=True, store=True)
    mode_of_promotion = fields.Selection([('test_period','Probation'),
                                            ('contract','Contract'),
                                            ('deputation','Deputation'),
                                            ('employment','Regular')],string="Mode of Promotion",tracking=True)
    trail_date_end = fields.Date(string="End of Probation Period")
    pf_tax = fields.Float(string="Professional Tax", help="professional tax as per bihar state government", compute='_compute_pf_tax')

    @api.depends('wage')
    def _compute_pf_tax(self):
        if self.wage:
            if 0.0 < self.wage <= 25000.00:
                self.pf_tax = 0.0
            elif 25000.00 < self.wage <= 41666.00:
                self.pf_tax = 83.33
            elif 41666.00 < self.wage <= 83333.00:
                self.pf_tax = 166.67
            elif self.wage > 83333.00:
                self.pf_tax = 208.33
            else:
                self.pf_tax = 0.0
        else:
            self.pf_tax = 0.0





    @api.constrains('employee_id', 'state', 'kanban_state', 'date_start', 'date_end')
    def _check_current_contract(self):
        """ Two contracts in state [incoming | open | close] cannot overlap """
        for contract in self.filtered(lambda c: (c.state not in ['draft','cancel'] or c.state == 'draft' and c.kanban_state == 'done') and c.employee_id):
            domain = [
                ('id', '!=', contract.id),
                ('employee_id', '=', contract.employee_id.id),
                '|',
                    ('state', 'in', ['open', 'close']),
                    '&',
                        ('state', '=', 'draft'),
                        ('kanban_state', '=', 'done') # replaces incoming
            ]

            if not contract.date_end:
                start_domain = []
                end_domain = ['|', ('date_end', '>=', contract.date_start), ('date_end', '=', False)]
            else:
                start_domain = [('date_start', '<=', contract.date_end)]
                end_domain = ['|', ('date_end', '>', contract.date_start), ('date_end', '=', False)]

            domain = expression.AND([domain, start_domain, end_domain])
            # if self.search_count(domain):
            #     raise ValidationError(_('An employee can only have one contract at the same time. (Excluding Draft and Cancelled contracts)'))
    
    @api.constrains('date_start', 'date_end')
    @api.onchange('date_start', 'date_end')
    def _check_dates(self):
        if self.date_start:
            if self.date_start < date.today():
                raise ValidationError('Contract start date should not less than today date. / अनुबंध की प्रारंभ तिथि आज की तिथि से कम नहीं होनी चाहिए।')
        if self.filtered(lambda c: c.date_end and c.date_start > c.date_end):
            raise ValidationError(_('Contract end date must be greater than contract start date. / अनुबंध की समाप्ति तिथि अनुबंध की प्रारंभ तिथि से अधिक होनी चाहिए।'))

    @api.constrains('trail_date_end')
    @api.onchange('trail_date_end')
    def _check_trail_date(self):
        if self.date_start:
            if self.trail_date_end:
                if self.trail_date_end < self.date_start:
                    raise ValidationError('Probation end date should not less than contract start date. / परिवीक्षा समाप्ति तिथि अनुबंध प्रारंभ तिथि से कम नहीं होनी चाहिए।')


    @api.constrains('wage','hra', 'da', 'travel_allowance', 'meal_allowance', 'medical_allowance', 'other_allowance')
    def _check_sum_allowances(self):
        total_sum_all = 0
        for rec in self:
            total_sum_all = rec.hra + rec.da + rec.travel_allowance + rec.meal_allowance + rec.medical_allowance + rec.other_allowance
            print("total_sum_alltotal_sum_alltotal_sum_all", total_sum_all, rec.wage)
            if rec.wage != total_sum_all:
                raise ValidationError(_('The sum allowances is not equal to wages.Please check and verify.'))