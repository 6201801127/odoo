from datetime import date
from odoo import models, fields, api,tools,_
from odoo.exceptions import UserError, ValidationError
from kw_utility_tools import kw_validations



class Psychometricfeedback(models.Model):
    _name = "kw_employee_psychometric_feedback"
    _description = "psychometric Feedback"
    _rec_name = "applicant_id"


    applicant_id = fields.Char(string="Applicant's Name")
    applicant_email = fields.Char(string="Email Id")
    applicant_ph_no = fields.Char(string="PH no",size=15)
    
    sl_1 = fields.Integer(string="sl no",default=1.)
    most_1 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Most")
    least_1 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')], required=True,string="Least")
    
    sl_2 = fields.Integer(string="sl no",default=2.)
    most_2 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Most")
    least_2 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Least")

    sl_3 = fields.Integer(string="sl no",default=3.)
    most_3 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')], required=True,string="Most")
    least_3 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Least")

    sl_4 = fields.Integer(string="sl no",default=4.)
    most_4 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Most")
    least_4 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')], required=True,string="Least")
    
    sl_5 = fields.Integer(string="sl no",default=5.)
    most_5 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')], required=True,string="Most")
    least_5 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Least")
    
    sl_6 = fields.Integer(string="sl no",default=6.)
    most_6 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')], required=True,string="Most")
    least_6 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Least")
    
    sl_7 = fields.Integer(string="sl no",default=7.)
    most_7 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Most")
    least_7 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')], required=True,string="Least")
    
    sl_8 = fields.Integer(string="sl no",default=8.)
    most_8 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Most")
    least_8 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Least")

    sl_9 = fields.Integer(string="sl no",default=9.)
    most_9 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Most")
    least_9 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Least")

    sl_10 = fields.Integer(string="sl no",default=10.)
    most_10 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Most")
    least_10 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Least")

    sl_11 = fields.Integer(string="sl no",default=11.)
    most_11 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Most")
    least_11 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')], required=True,string="Least")

    sl_12 = fields.Integer(string="sl no",default=12.)
    most_12 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')], required=True,string="Most")
    least_12 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Least")

    sl_13 = fields.Integer(string="sl no",default=13.)
    most_13 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')], required=True,string="Most")
    least_13 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')], required=True,string="Least")

    sl_14 = fields.Integer(string="sl no",default=14.)
    most_14 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')], required=True,string="Most")
    least_14 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Least")

    sl_15 = fields.Integer(string="sl no",default=15.)
    most_15 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Most")
    least_15 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')], required=True,string="Least")

    sl_16 = fields.Integer(string="sl no",default=16.)
    most_16 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Most")
    least_16 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Least")

    sl_17 = fields.Integer(string="sl no",default=17.)
    most_17 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Most")
    least_17 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Least")

    sl_18 = fields.Integer(string="sl no",default=18.)
    most_18 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Most")
    least_18 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Least")

    sl_19 = fields.Integer(string="sl no",default=19.)
    most_19 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')], required=True,string="Most")
    least_19 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Least")

    sl_20 = fields.Integer(string="sl no",default=20.)
    most_20 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Most")
    least_20 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Least")

    sl_21 = fields.Integer(string="sl no",default=21.)
    most_21 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Most")
    least_21 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Least")

    sl_22 = fields.Integer(string="sl no",default=22.)
    most_22 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')], required=True,string="Most")
    least_22 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Least")

    sl_23 = fields.Integer(string="sl no",default=23.)
    most_23 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Most")
    least_23 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Least")

    sl_24 = fields.Integer(string="sl no",default=24.)
    most_24 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Most")
    least_24 = fields.Selection([('A', 'A'),('B', 'B'),('C', 'C'),('D', 'D')],required=True, string="Least")

    
    status = fields.Selection([
    ('draft', 'Draft'),
    ('submitted', 'Submitted')
    ], default='draft')

    @api.constrains('applicant_email')
    def check_email_from(self):
        for record in self:
            kw_validations.validate_email(record.applicant_email)
    
    @api.constrains('applicant_ph_no')
    def check_partner_phone(self):
        if len(self.applicant_ph_no) > 10 or len(self.applicant_ph_no) <10:
            raise ValidationError("Phone number should be exactly 10 digits.") 
            
    def btn_submit(self):
        if self.most_1 and self.least_1 and self.most_2 and self.least_2 and self.most_3 and self.least_3 and self.most_4 and self.least_4\
            and self.most_5 and self.least_5 and self.most_6 and self.least_6 and self.most_7 and self.least_7 and self.most_8 and self.least_8\
            and self.most_9 and self.least_9 and self.most_10 and self.least_10 and self.most_11 and self.least_11 and self.most_12 and self.least_12\
            and self.most_13 and self.least_13 and self.most_14 and self.least_14 and self.most_15 and self.least_15 and self.most_16 and self.least_16\
            and self.most_17 and self.least_17 and self.most_18 and self.least_18 and self.most_19 and self.least_19 and self.most_20 and self.least_20\
            and self.most_21 and self.least_21 and self.most_22 and self.least_22 and self.most_23 and self.least_23 and self.most_24 and self.least_24:
            self.write({'status':'submitted'}) 
        else:
            raise ValidationError("Please Give the all Most and least Feedback")
        if self.most_1 == self.least_1 or self.most_2 == self.least_2 or self.most_3 == self.least_3 or self.most_4 == self.least_4 or self.most_5 == self.least_5 or self.most_6 == self.least_6\
            or self.most_7 == self.least_7 or self.most_8 == self.least_8 or self.most_9 == self.least_9 or self.most_10 == self.least_10 or self.most_11 == self.least_11 or self.most_12 == self.least_12\
            or self.most_13 == self.least_13 or self.most_14 == self.least_14 or self.most_15 == self.least_15 or self.most_16 == self.least_16 or self.most_17 == self.least_17 or self.most_18 == self.least_18\
            or self.most_19 == self.least_19 or self.most_20 == self.least_20 or self.most_21 == self.least_21 or self.most_22 == self.least_22 or self.most_23 == self.least_23 or  self.most_24 == self.least_24:
            raise ValidationError("Most and Least value should not be Same. ")
        
        
    # @api.multi
    # def write(self, vals):
    #     res = super(Psychometricfeedback, self).write(vals)
    #     if vals.get('most_1') == vals.get('least_1') or vals.get('most_2') == vals.get('least_2') or vals.get('most_3') == vals.get('least_3') or vals.get('most_4') == vals.get('least_4') or vals.get('most_5') == vals.get('least_5')\
    #         or vals.get('most_6') == vals.get('least_6') or vals.get('most_7') == vals.get('least_7') or vals.get('most_8') == vals.get('least_8') or vals.get('most_9') == vals.get('least_9')\
    #         or vals.get('most_10') == vals.get('least_10') or vals.get('most_11') == vals.get('least_11') or vals.get('most_12') == vals.get('least_12') or vals.get('most_13') == vals.get('least_13') or  vals.get('most_14') == vals.get('least_14') or vals.get('most_15') == vals.get('least_15')\
    #         or vals.get('most_16') == vals.get('least_16') or vals.get('most_17') == vals.get('least_17') or vals.get('most_18') == vals.get('least_18') or vals.get('most_19') == vals.get('least_19')  or vals.get('most_20') == vals.get('least_20') or vals.get('most_21') == vals.get('least_21')\
    #         or vals.get('most_22') == vals.get('least_22') or vals.get('most_23') == vals.get('least_23') or vals.get('most_24') == vals.get('least_24') :
    #         print("in write---------------------------------")
    #         raise ValidationError("Most and Least value should not be Same. ")
    #     return res
            
        
    
