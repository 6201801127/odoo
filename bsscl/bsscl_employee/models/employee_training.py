from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class EmployeeTraining(models.Model):
    _name='employee.training'
    _description ='Employee Training'

    # def default_employee(self):
    #     print("------------------context", self._context.get('active_id'))
    #     if 'params' in self._context.keys():
    #         return self._context.get('params')['id']
    #     else:
    #         return False

    # employee_id = fields.Many2one('hr.employee', string='employee', default=lambda self: self.default_employee())
    
    employee_id = fields.Many2one('hr.employee', string='employee')
    course = fields.Char('Course Title')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    location = fields.Text('Location')
    trainer_name = fields.Char('Trainer Name')
    training_type = fields.Selection([('internal','Internal'),
                                      ('external','External'),
                                      ('professional','Professional'),
                                      ('functional','Functional'),
                                      ('technical','Technical'),
                                      ('certification', 'Certification'),
                                      ],string='Training Type')
    organization_name = fields.Text('Organization Name')
    cert_file_data = fields.Binary('Certificate upload',attachment=True)
    cert_file_name = fields.Char('Certificate Name')
    skills = fields.Many2one('hr.skill', string = 'Skills')


    @api.constrains('start_date','end_date')
    @api.onchange('start_date','end_date')
    def onchange_date(self):
        for record in self:
            if record.start_date and record.end_date and record.start_date > record.end_date:
                raise ValidationError(
                    _('Start date should be less than or equal to end date, but should not be greater than end date'))
