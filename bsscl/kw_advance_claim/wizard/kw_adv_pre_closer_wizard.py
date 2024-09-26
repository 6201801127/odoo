from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kw_adv_pre_closer_wizard(models.TransientModel):
    _name = 'kw_advance_pre_closer_wizard'
    _description = ' Pre Closure Wizard'

    @api.depends('total_installment')
    def _get_installment_data(self):
        pass
        # paid_count, left_count ,paid_amount ,left_amount= 0,0,0,0
        # if self.salary_adv_id.deduction_line_ids:
        #     for line_id in self.salary_adv_id.deduction_line_ids:
        #         if line_id.status == 'paid' and line_id.principal_amt != 0:
        #             paid_count += 1
        #             paid_amount += line_id.principal_amt
        #         if line_id.status == 'draft' and line_id.principal_amt != 0    :
        #             left_count += 1
        #             left_amount += line_id.principal_amt
        # self.paid_installment = paid_count
        # self.left_installment = left_count
        # self.left_amount = left_amount
        # self.paid_amount = paid_amount


    # total_installment = fields.Integer(string="Total Installment", related='salary_adv_id.total_install')
    total_amount = fields.Float(string="Total Amount", related='salary_adv_id.adv_amnt')
    paid_installment = fields.Integer(string="Paid Installment")
    paid_amount = fields.Float(string="Paid Amount")
    left_installment = fields.Integer(string="Remaining Installment", store=True)
    left_amount = fields.Float(string="Remaining Amount")
    closer_type = fields.Selection(string='Closure Type',selection=[('partial', 'Partial'), ('full', 'Full')])
    salary_adv_id = fields.Many2one('kw_advance_apply_salary_advance', string="salary Adv Id", default=lambda self: self.env.context.get('current_rec_id'))
    no_of_month = fields.Integer(string='No of Installment(s)')
    partial_amount = fields.Float(string='Paying')
    payment_ref = fields.Text("Payment Ref")

    
    def pre_closer_btn(self):
        if self.closer_type:
            self.salary_adv_id.sudo().write({
                'closer_type':self.closer_type,
                'total_month_count': self.no_of_month if self.no_of_month else self.left_installment,
            })
            self.salary_adv_id.calculate_emi()
    
    @api.onchange('no_of_month')
    def onchange_no_of_month(self):
        if self.no_of_month > 0:
            self.partial_amount = self.no_of_month * self.salary_adv_id.install_amnt
        if self.closer_type == 'partial' and self.no_of_month >= self.left_installment:
            raise ValidationError('Total no of Installment(s) should be less than Remaining installment')
    
    @api.onchange('closer_type')
    def onchange_closure_type(self):
        if self.closer_type == 'full':
            self.no_of_month = 0
            self.partial_amount = self.left_installment * self.salary_adv_id.install_amnt
            self.no_of_month = self.left_installment
        if self.closer_type == 'partial':
            self.partial_amount = 0
            self.no_of_month = 0