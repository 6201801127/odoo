#*******************************************************************************************************************
#  File Name             :   kw_emp_history.py
#  Description           :   This model is used to Keep Employee changes history. 
#  Created by            :   Asish ku Nayak
#  Created On            :   17-08-2020
#  Modified by           :
#  Modified On           :
#  Modification History  :
# *******************************************************************************************************************


from odoo import models, fields, api
from datetime import datetime as dt

class kw_emp_history(models.Model):
    _name = 'kw_emp_history'
    # _rec_name = 'emp_id'
    _description = 'Maintains Employee History.'
    _order = 'end_date desc'


    emp_id = fields.Many2one('hr.employee',string="Name")
    emp_code = fields.Char(string='Employee Code')
    dept_id = fields.Many2one('hr.department', string="Department")
    division = fields.Many2one('hr.department',string='Division')
    section = fields.Many2one('hr.department',string='Practice')
    practice = fields.Many2one('hr.department',string='Section')
    deg_ig = fields.Many2one('hr.job',string='Designation')
    grade_id = fields.Many2one('kwemp_grade_master',string="Grade")
    band_id = fields.Many2one('kwemp_band_master',string="Band")
    name = fields.Char(string="Grade & Band")
    job_location_id = fields.Many2one('res.partner', string="Job Location Id")
    job_location_city = fields.Char(string="Job Location")
    
    work_location_id = fields.Many2one('kw_res_branch', string="Job Location Id")
    office_type = fields.Many2one('kw_res_branch', string="Office Type")
    start_date = fields.Char(string="Start Date")
    end_date = fields.Char(string="End Date",default='Till Date')
    duration = fields.Char(string="Duration", compute="_compute_duration")

    @api.model
    def _compute_duration(self):
        for record in self:
            if record.end_date != 'Till Date':
                start_date = dt.strptime(record.start_date, '%d-%B-%Y')
                end_date = dt.strptime(record.end_date, '%d-%B-%Y')
                calc_duration = end_date-start_date
                record.duration = str(calc_duration.days) + 'day(s)'


    @api.model
    def create(self, vals):
        if vals.get('grade_id'):
            grade = self.env['kwemp_grade_master'].search([('id','=',vals.get('grade_id'))]).name
            if grade:
                vals['name'] = grade
        if vals.get('band_id'):
            band = self.env['kwemp_band_master'].search([('id','=',vals.get('band_id'))]).name
            if vals.get('name'):
                vals['name'] = vals.get('name')+'-'+band
            else:
                vals['name'] = band
        record = super(kw_emp_history, self).create(vals)
        if record:
            self.env.user.notify_success(message='Employee History created successfully.')
        else:
            self.env.user.notify_danger(message='Employee History creation failed.')
        return record
