from odoo import models, fields, api

class kw_employee_covid_data(models.Model):
    _name               = 'kw_employee_covid_data'
    _description        = 'Employee Covid Data'
    _rec_name           = 'employee_id'
    _order              = 'id desc'


    employee_id         = fields.Many2one('hr.employee', string='Employee',  track_visibility='onchange')
    department_id       = fields.Many2one('hr.department', compute='get_dept_data', string='Department', track_visibility='onchange', store=True)
    division            = fields.Many2one('hr.department', compute='get_dept_data', string="Division", track_visibility='onchange', store=True)
    section             = fields.Many2one('hr.department', compute='get_dept_data', string="Practice", track_visibility='onchange', store=True)
    practise            = fields.Many2one('hr.department', compute='get_dept_data', string="Section", store=True)

    date                = fields.Date('Date', track_visibility='onchange')
    due_date            = fields.Date('Date', track_visibility='onchange')
    dose_1_document     = fields.Binary(string='Dose 1 Document', track_visibility='onchange')
    dose_2_document     = fields.Binary(string='Dose 2 Document', track_visibility='onchange')
    dose_1_file_name    = fields.Char("Dose 1 File Name", track_visibility='onchange')
    dose_2_file_name    = fields.Char("Dose 2 File Name", track_visibility='onchange')
    dose                = fields.Selection([('first_dose','1st Dose'),('second_dose','2nd Dose'),('no_dose_taken','No Dose Taken')],string='Dose',default='no_dose_taken',  track_visibility='onchange')
    remark              = fields.Char(string='Remark', track_visibility='onchange')

    @api.depends('employee_id')
    def get_dept_data(self):
        for rec in self:
            if rec.employee_id:
                rec.department_id = rec.employee_id.department_id
                rec.division = rec.employee_id.division
                rec.section = rec.employee_id.section
                rec.practise = rec.employee_id.practise