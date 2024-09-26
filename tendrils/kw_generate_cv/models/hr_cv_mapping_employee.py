from odoo import api, models,fields
from odoo.exceptions import UserError,ValidationError
from odoo import exceptions,_

class HrCvMappingEmployee(models.Model):
    _name       ='hr.cv.mapping.employee'
    _description= 'CV Mapping'


    emp_id = fields.Many2one('hr.cv.mapping', 'Employee Name')
    report_id = fields.Many2one('hr.employee.mis.report', string='Employee')
    emp_code = fields.Char(string="Employee Code", related='report_id.emp_code')
    # name = fields.Char('Emp Name')
    


    @api.multi
    def release_emp(self):
        for rec in self:
            rec.unlink()
   
    @api.multi
    def cv_download(self):
        return {
            'type': 'ir.actions.act_url',
            #'name': 'Download CV',
            'target': 'new',
            'url': f'/report/docx/kw_generate_cv.report_generate_cv_docx/{self.report_id.emp_id.id}'
        }

    


   