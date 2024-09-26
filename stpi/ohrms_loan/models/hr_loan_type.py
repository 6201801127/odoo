from odoo import fields,models,api
from odoo.exceptions import ValidationError


class LoanType(models.Model):

    _name='loan.type'
    _description ='Loan Type'
    _rec_name ='type_emp'

    type_emp=fields.Char(string='Name')
    interest=fields.Float(string='Interest Rate%')
    category_ids = fields.Many2many('hr.employee.category', string='Tags')
    max_emi=fields.Integer(string="Max No.EMI")
    filter_domain = fields.Char(string="Domain")

    threshold_emi = fields.Integer(string='Threshold EMI')
    threshold_below_emi = fields.Integer(string='Interest EMI Below Threshold')
    threshold_above_emi = fields.Integer(string='Interest EMI Equal to/Above Threshold')
    apply_day_threshold = fields.Integer('Apply Day Threshold', 
                                help='If the loan is applied on same day of the month or before\
                                EMI will start from same month else from next month.')
    close_day_threshold = fields.Integer('Close Day Threshold', 
                                help='If the loan is closed on same day of the month or before\
                                interest will not be calculated for current month.')


    @api.constrains('type_emp','interest','apply_day_threshold','close_day_threshold')
    def check_name(self):
        if self.search([('type_emp','=',self.type_emp.strip()), ('interest', '=', self.interest)]) - self:
            raise ValidationError("Name must be unique")
        if self.apply_day_threshold > 31 or self.apply_day_threshold < 1:
            raise ValidationError("Apply Day Threshold must be between 1 and 31")
        if self.close_day_threshold > 31 or self.close_day_threshold < 1:
            raise ValidationError("Close Day Threshold must be between 1 and 31")
