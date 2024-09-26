# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import ValidationError, AccessError
from datetime import date,datetime
from dateutil.relativedelta import relativedelta
from odoo.addons.web_grid.models.models import END_OF


class ValidationWizard(models.TransientModel):
    _name = 'timesheet.validation'
    _description = 'Timesheet Validation'

    validation_date = fields.Date('Validate up to')
    validation_line_ids = fields.One2many('timesheet.validation.line', 'validation_id')
    remark = fields.Text("Remark")

    def action_validate(self):
        anchor = date.today() + relativedelta(weeks=-1, days=1, weekday=-1)
        dt_list = []
        
        if self.validation_date > anchor:
            raise ValidationError('You can not validate task for current week.')
        else:
            emp_ids = self.validation_line_ids.filtered('validate').mapped('employee_id')
            start_date = self._context.get('grid_anchor')
            end_date = self._context.get('week_end_date')
            # print(start_date,end_date,type(start_date),type(end_date))
            analytic_recs = self.env['account.analytic.line'].sudo().search(
                [('employee_id', 'in', emp_ids.ids), ('date', '>=', start_date), ('date', '<=', end_date)])
            analytic_recs.write({'validated': True, 'remark': self.remark})

            emp_list = []
            
            employee_id = set(analytic_recs.mapped('employee_id'))
            for emp in employee_id:
                emp_list.append(emp.id)
            dates = set(analytic_recs.mapped('date'))

            dt_list.clear()
            for dt in dates:
                dt_list.append(dt.strftime("%d-%B-%Y"))
            dt_list.sort()
            if len(dt_list) > 0:
                """ Mail send after RA approval """
                extra_params = {'list_date': dt_list,
                                'start_date': start_date,
                                'end_date': end_date,
                                'remark_get': self.remark}
                self.env['account.analytic.line'].timesheet_send_custom_mail(res_id=emp_list[0],
                                                                             notif_layout='kwantify_theme.csm_mail_notification_light',
                                                                             template_layout='kw_timesheets.kw_timesheet_ra_validate_mail_template',
                                                                             ctx_params=extra_params,
                                                                             description="Timesheet")
            # emp_ids.sudo().write({'timesheet_validated': self.validation_date})
            action_id = self.env.ref('kw_timesheets.action_kw_weekly_timesheet_report_act_window').id
            # return {'type': 'ir.actions.act_window_close'}
            return {'type': 'ir.actions.act_url',
            'url': f'/web#action={action_id}&model=kw_weekly_timesheet_report&view_type=list',
            'target': 'self',}


class ValidationWizardLine(models.TransientModel):
    _name = 'timesheet.validation.line'
    _description = 'Timesheet Validation Line'

    validation_id = fields.Many2one('timesheet.validation', required=True, ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, ondelete='cascade')
    validate = fields.Boolean(default=True, help="Validate this employee's timesheet up to the chosen date")
