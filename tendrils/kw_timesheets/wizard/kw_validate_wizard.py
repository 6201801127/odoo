from odoo import api, models, fields


class kw_validate_wizard(models.TransientModel):
    _name = 'kw_validate_wizard'
    _description = 'Validation wizard'

    def _get_default_timesheet_confirm(self):
        res = self.env['kw_weekly_timesheet_report'].browse(self.env.context.get('active_ids'))
        return res

    timesheet_report_id = fields.Many2many('kw_weekly_timesheet_report', readonly=1, default=_get_default_timesheet_confirm)

    @api.multi
    def button_validate(self):
        # date_format = "%Y-%m-%d"
        for rec in self.timesheet_report_id:
            
            domain = []
            
            if not self.env.user.has_group('hr_timesheet.group_timesheet_manager'):
                current_employee = self.env['hr.employee'].search([('user_id','=',self._uid)],limit=1)
                project_work = self.env['kw_project_category_master'].search([('mapped_to','=','Project')],limit=1)
                
                domain = ['&',('employee_id', '=', rec.employee_id.id),
                                    '|','|',('project_id.emp_id','=',current_employee.id),
                                            '&',('employee_id.parent_id','=',current_employee.id),('prject_category_id','!=',project_work.id),
                                            '&',('project_id.reviewer_id','=',current_employee.id),('project_id.emp_id','=',rec.employee_id.id)]


            # date_list = []
            # start_date = str(rec.week_start_date)
            # end_date = str(rec.week_end_date)
            # start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            # end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            # step = datetime.timedelta(days=1)
            # while start <= end:
            #     date_list.append(start.date())
            #     start += step

            # analytic_id = self.env['account.analytic.line'].sudo().search([('employee_id', '=', rec.employee_id.id), ('date', 'in', date_list)])
            timesheets = self.env['account.analytic.line']
            if domain:
                timesheets = self.env['account.analytic.line'].search(domain)

                timesheets = self.env['account.analytic.line'].search([('id','in',timesheets.ids),('employee_id', '=', rec.employee_id.id), ('date', '>=', rec.week_start_date),('date', '<=', rec.week_end_date),('validated','=',False)])
            else:
                timesheets = self.env['account.analytic.line'].search([('employee_id', '=', rec.employee_id.id), ('date', '>=', rec.week_start_date),('date', '<=', rec.week_end_date)])
            
            # print("timesheet data are-->",timesheets)
            for record in timesheets:
                record.write({'validated': True})
                
            if timesheets:
                self.env.user.notify_success(f"{len(timesheets)} timesheet(s) have been validated.")
                template = self.env.ref('kw_timesheets.kw_timesheet_ra_pm_reviewer_validate_mail_template')
                template.with_context(timesheet_records=timesheets).send_mail(timesheets[0].id,notif_layout="kwantify_theme.csm_mail_notification_light")
            else:
                self.env.user.notify_warning("No timesheets to validate.")
                
                # record.mapped('employee_id').sudo().write({'timesheet_validated': rec.week_end_date})

            # if len(date_list) > 0:
            #     """ Mail send after RA approval """
            #     extra_params = {'list_date': date_list,
            #                     'start_date': start_date,
            #                     'end_date': end_date,
            #                     'remark_get': ''}
            #     self.env['account.analytic.line'].timesheet_send_custom_mail(res_id=rec.employee_id.id,
            #                                                                  notif_layout='kwantify_theme.csm_mail_notification_light',
            #                                                                  template_layout='kw_timesheets.kw_timesheet_ra_validate_mail_template',
            #                                                                  ctx_params=extra_params,
            #                                                                  description="Timesheet")
