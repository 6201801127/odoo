from datetime import date
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re



class remarkwizard(models.TransientModel):
    _name = 'employee_nominate_wizard'


    def get_employee_id(self):
        emp = self.env['hr.employee'].sudo().search([])
        # print("--------------",self._context)
        domain = [('id', 'in', [])]
        if self._context.get('button') == 'special_nominate':
            domain = [('id', 'in', emp.ids)]
        else:
            certification_id = self._context.get('current_record')
            certification = self.env['kw_certification'].sudo().browse(certification_id)
            emp_domain = []
            for rec in emp:
                edu = []
                for recc in rec.educational_details_ids:
                    edu.append(recc.stream_id.id)
                match = re.search(r'(\d+)\s*Years?\s+and\s+(\d+)\s*Months?', rec.total_experience_display)
                years = int(match.group(1)) if match else 0
                common_elements = [x for x in edu if x in certification.qualification_ids.ids]
                if common_elements and  certification.year_of_experience <= years and certification.year_of_experience_max >= years and certification.require_department_id.id == rec.department_id.id:
                    emp_domain.append(rec.id)
            domain = [('id', 'in', emp_domain)]
        # print("domain=====",domain)
        return domain
    
    
    
    employee_ids=fields.Many2many('hr.employee','kw_employee_certification_rel','employee_id','cert_id',string='Employee',
                                  domain=get_employee_id)
    certification_emp_id = fields.Many2one('kw_certification', string="Employee rec",
                                      default=lambda self: self._context.get('current_record'))

        
    def update_employee_for_nominate(self):
            data = []
            for rec in self.certification_emp_id.assigned_emp_data.mapped('employee_id'):
                data.append(rec.id)
            for rec in self.employee_ids.ids:
                # if rec not in data:
                emp_data = {
                    'certification_master_id':self.certification_emp_id.id,
                    'employee_id': rec,
                }
                self.certification_emp_id.assigned_emp_data.create(emp_data)
            dataa = []
            if self.certification_emp_id.assigned_emp_data:
                for rec in self.certification_emp_id.assigned_emp_data:
                    if rec.status_certification in ['Accepted', 'Pending']:
                        dataa.append(rec.id)
            if len(dataa) > self.certification_emp_id.no_of_candidate:
                raise ValidationError('Warning! You cannot add extra nominates.')

