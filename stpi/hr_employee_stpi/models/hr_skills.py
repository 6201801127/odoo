from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning


class ResumeLine(models.Model):
    _inherit = 'hr.resume.line'


    @api.constrains('date_start', 'date_end')
    @api.onchange('date_start', 'date_end')
    def onchange_date(self):
        for record in self:
            if record.date_start and record.date_end and record.date_start > record.date_end:
                raise ValidationError(
                    _('Start date should be less than or equal to end date, but should not be greater than end date'))
    #
    # @api.constrains('date_start', 'date_end')
    # @api.onchange('date_start', 'date_end')
    # def onchange_date(self):
    #     for record in self:
    #         search_id = self.env['hr.resume.line'].search([('resume_employee_id', '=', record.resume_employee_id.id)])
    #         if record.date_start and record.date_end and record.date_start > record.date_end:
    #             raise ValidationError(
    #                 _('Start date should be less than or equal to end date, but should not be greater than end date'))
    #         for emp in search_id:
    #             print('=================emp============',emp)
    #             if emp.date_start and emp.date_end:
    #                 if record.date_start and record.date_end and record.date_start <= emp.date_start or record.date_start >= emp.date_end:
    #                     if record.date_start and record.date_end and record.date_end <= emp.date_start or record.date_end >= emp.date_end:
    #                         if record.date_start and record.date_end and (
    #                                 record.date_start <= emp.date_start and record.date_end >= emp.date_end):
    #                             raise ValidationError("You are not allowed to enter this date3")
    #                     else:
    #                         raise ValidationError("You are not allowed to enter this date2")
    #                 else:
    #                     raise ValidationError("You are not allowed to enter this date1")
