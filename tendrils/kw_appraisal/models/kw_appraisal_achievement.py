from odoo import models, fields, api
from odoo.exceptions import  ValidationError
from datetime import datetime,date


class kw_appraisal_achievement(models.Model):
    _name           = 'kw_appraisal_achievement'
    _description    = 'Appraisal achievement'
    _rec_name       = 'appraisal_period'


    def _get_financial_year(self):
        """ Current financial year logic """
        current_date = date.today()
        year_of_date= current_date.year
        financial_year_start_date = datetime.strptime(str(year_of_date)+"-04-01","%Y-%m-%d").date()
        final_date = ''
        if current_date < financial_year_start_date:
            start_date = str(financial_year_start_date.year-1)
            end_date = str(financial_year_start_date.year)[-2:]
            final_date = start_date+'-'+ end_date
        else:
            start_date = str(financial_year_start_date.year)
            end_date = str(financial_year_start_date.year+1)[-2:]
            final_date = start_date+'-'+ end_date
        return final_date

    appraisal_period    = fields.Char(string='Financial Year',default=_get_financial_year)
    employee_id         = fields.Many2one('hr.employee',string='Employee',default=lambda self: self.env.user.employee_ids)
    ra_id               = fields.Many2one('hr.employee',related='employee_id.parent_id',string='Reporting Authority')
    emp_deg             = fields.Many2one('hr.job','Designation', related='employee_id.job_id')
    emp_dept            = fields.Many2one('hr.department','Department', related='employee_id.department_id')
    achievement_pages   = fields.One2many('kw_appraisal_achievement_pages','achievement_id',string='Achievement Lists')
    
    image = fields.Binary("Photo", related='employee_id.image',
                          help="This field holds the image used as photo for the employee, limited to 1024x1024px.")

    @api.constrains('appraisal_period','employee_id','achievement_pages')
    def _validate_appraisal_period(self):
        record = self.env['kw_appraisal_achievement'].search([]) - self
        for info in record:
            if info.employee_id.id == self.employee_id.id and info.appraisal_period.lower() == self.appraisal_period.lower():
                raise ValidationError(f'Exist! Already an achievement exist for {self.employee_id.name} in FY {self.appraisal_period}.')
            elif not self.achievement_pages:
                raise ValidationError(f'Achievement list can not be left blank for FY {self.appraisal_period}.')


class kw_appraisal_achievement_pages(models.Model):
    _name           = 'kw_appraisal_achievement_pages'
    _description    = 'Appraisal achievement Pages'
    
    achievement_id  = fields.Many2one('kw_appraisal_achievement',string='Achievement Name')
    situation       = fields.Text(string='S (Situation)',required=True)
    task            = fields.Text(string='T (Task)',required=True)
    action   = fields.Text(string='A (Action)',required=True)
    result   = fields.Text(string='R (Result)',required=True)