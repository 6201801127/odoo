# -*- coding: utf-8 -*-

from odoo import models, fields, api


class kw_face_matched_log(models.Model):
    _name       = 'kw_face_matched_log'
    _description = 'Facereader Matched Log'  
    _rec_name   = 'employee_id'
    
       
    match_date_time = fields.Datetime(
       string='Matched Time',
       default=fields.Datetime.now,
    )

    employee_code  = fields.Char(
        string='Employee Code',inverse="_inverse_emp_code"
    ) 
   
    employee_id = fields.Many2one(
        string='Employee',
        comodel_name='hr.employee',
        ondelete='restrict',
    )

    
    job_id = fields.Many2one(
        string='Designation',
        related='employee_id.job_id',readonly=True       
    )

    department_id = fields.Many2one(
        string='Department',
        related='employee_id.department_id',readonly=True       
    )


    @api.multi
    def _inverse_emp_code(self):
        # print("inside matched log")
        for record in self:
            if not record.employee_id and record.employee_code:

                # print(record.employee_code)
                emp_rec             = self.env['hr.employee'].search([('emp_code','=',record.employee_code)],limit=1)
                # print(emp_rec)
                record.employee_id  = emp_rec.id

    

   