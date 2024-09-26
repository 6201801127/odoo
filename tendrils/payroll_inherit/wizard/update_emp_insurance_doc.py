import math, random, string
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError



class UpdateInsuranceDoc(models.TransientModel):
    _name = 'update_emp_insurance_doc'
    _description = 'Update Insurance Document'
    
    def get_employee(self):
        if self.env.context.get('employee_id'):
            return  self.env.context.get('employee_id')
    
    employee_id = fields.Many2one('hr.employee',default=get_employee)
    insurance_doc = fields.Binary(string='Insurance Document')
    file_name_insurance = fields.Char(string="File Name") 
    validity_date = fields.Date() 
    enable_insurance = fields.Selection([('Yes', 'Yes'), ('No', 'No')])
    
    def update_emp_doc(self):
        if self.employee_id and (self.insurance_doc or self.validity_date):
            if self.insurance_doc:
                self.employee_id.uplod_insurance_doc = self.insurance_doc
                self.employee_id.file_name_insurance = self.file_name_insurance
            if self.validity_date:
                self.employee_id.insurance_validate_date = self.validity_date
            # if self.enable_insurance:
            #     self.employee_id.personal_insurance = self.enable_insurance
        else:
            raise ValidationError('Please update the details')
            
            