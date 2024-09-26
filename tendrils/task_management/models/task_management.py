import pytz
from odoo import models, fields, api,_
from odoo.exceptions import ValidationError,UserError
from datetime import date, datetime, timedelta, time
from odoo.addons.resource.models import resource
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT



class kw_task_management(models.Model):
    _name = "kw_task_management"
    _description = "Ticket"
    _rec_name = "reference_no_txt"
    _order = "id DESC"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _project_id_domain(self):
        project_ids = self.env['project.project'].search(
            ['|', '|', '|', ('resource_id.emp_id', 'in', self.env.user.employee_ids.ids),
             ('reviewer_id', 'in', self.env.user.employee_ids.ids),
             ('emp_id', 'in', self.env.user.employee_ids.ids),
             ('sbu_id.representative_id', 'in', self.env.user.employee_ids.ids)])
        return [('id', 'in', project_ids.ids)]

    project_id = fields.Many2one('project.project', string='Project Name', domain=_project_id_domain)
    project_code = fields.Char(string='Project Code', compute='_compute_project_code')
    module_id = fields.Many2one('kw_project.module', string='Module Name', domain="[('project_id', '=', project_id)]")
    description = fields.Text('Description')
    estimated_hour = fields.Float(string="Effort Hour", track_visibility='always')
    assigned_to = fields.Many2one('hr.employee', string="Assigned To")
    notify_to = fields.Many2many('hr.employee', string="Notify To")
    task_name = fields.Char(string="Task name")
    task_type = fields.Many2one('kw_task_type_master', string="Task Type")
    reference_no = fields.Integer(string='Reference')
    reference_no_txt = fields.Char(string='Reference', default='TXT-000')
    stage = fields.Selection([('Draft', 'Draft'), ('Assigned', 'Assigned'), ('Report', 'Reported'),
                              ('Complete', 'Completed'), ('Reject', 'Rejected'), ('Reopen', 'Reopened')],
                             default='Draft')
    task_raised_by = fields.Many2one('hr.employee', default=lambda self: self.env.user.employee_ids.id,
                                     string="Raised By")
    raised_department_id = fields.Many2one('hr.department', related="task_raised_by.department_id", string="Department")
    can_see_advanced_fields = fields.Boolean(compute="compute_can_see_advanced")
    actual_hour = fields.Float(string="Actual Hour")
    comment = fields.Text(string='Comment')
    assign_task_date = fields.Datetime(string="Assignment Date",required=True)
    project_task_name = fields.Char(string="Project/Task Name", compute="compute_project_with_task")

    start_datetime_task = fields.Datetime(string="Start Date and Time")
    end_datetime_task = fields.Datetime(string="Stop Date and Time")
    duration_of_task = fields.Char(string="Duration OLD")
    task_duration = fields.Float(string="Duration")
    ack_comment = fields.Text(string='Acknowledge Comment')
    reopen_comment = fields.Text(string='Reopen Comment')
    reject_comment = fields.Text(string='Reject Comment')
    extend_effort_comment = fields.Text(string='Extend Hour Comment')
    sr_task_log_ids = fields.One2many(string='field_name', comodel_name='kw_task_management_log',
                                      inverse_name='task_sr_management_id')

    store_pause_time = fields.Datetime(string='Store Pause Time')
    store_resume_end_time = fields.Datetime(string='Store Resume end Time')
    store_stop_time = fields.Datetime(string='Store Stop Time')

    assign_to_report_bool = fields.Boolean(string='Assign To Report')
    reported_start_bool = fields.Boolean(string="Start bool")
    reported_pause_bool = fields.Boolean(string="pause bool")
    reported_resume_bool = fields.Boolean(string="report Resume bool")
    task_raised_by_bool = fields.Boolean(string="Task Raised By Bool", compute='_check_buttons_visible', default=False)
    assign_to_bool = fields.Boolean(string="Assigned To Bool", compute='_check_buttons_visible', default=False)
    extend_effort_hour_bool = fields.Boolean(string="Extend Effort Hour Bool", default=False)
    # assigned_hours = fields.Float(compute = '_compute_remaining_hour', string='Assigned Hours')
    # remaining_hour = fields.Float(compute = '_compute_remaining_hour', string='Remaining Hour')
    sorting_order = fields.Integer(compute='_compute_sorting_order',store=True)
    task_assign_day =fields.Date()
    expected_date_time = fields.Float(string='Expected Date Time',compute = '_compute_remaining_hour')
    actual_ticket_hour = fields.Float(string='Actual Effort Hour')
    extended_hour = fields.Float(string='Extended Hour')

    # resume_pause_bool = fields.Boolean(string="Resume pause bool")
    # is_stop_bool = fields.Boolean(string="Stop bool")

    # @api.onchange('task_raised_by')
    # def _onchange_assigned_to(self):
    #     bss_employee_ids = self.env['hr.employee'].search([('department_id.code', '=', 'BSS')]).ids
    #     if self.task_raised_by.department_id.code == 'BSS':
    #         if bss_employee_ids:
    #             return {'domain': {'assigned_to': [('id', 'in', bss_employee_ids)]}}
    #     elif self.task_raised_by.department_id.code != 'BSS':
    #         other_dept_employee_ids = self.env['hr.employee'].search(
    #             ['|', ('department_id.code', '!=', 'BSS'), ('department_id.code', '=', False)]).ids
    #         if other_dept_employee_ids:
    #             return {'domain': {'assigned_to': [('id', 'in', other_dept_employee_ids)]}}
    #     else:
    #         return {'domain': {'assigned_to': []}}

    @api.depends('assigned_to', 'assign_task_date', 'estimated_hour')
    def _compute_remaining_hour(self):
        assign_date = self.assign_task_date.date() if self.assign_task_date else False
        assigned_to_data = self.search(
            [('assigned_to', '=', self.assigned_to.id), ('task_assign_day', '=', assign_date)])
        if assigned_to_data.exists():
            expected_time_hours = sum(assigned_to_data.mapped('estimated_hour'))

            working_hours_per_day = 8.5 
            self.expected_date_time = expected_time_hours / working_hours_per_day

    @api.depends('stage')
    def _compute_sorting_order(self):
        sorting_order = {'Assigned': 1, 'Report': 2, 'Complete': 3, 'Reject': 4}
        for record in self:
            record.sorting_order = sorting_order.get(record.stage, 5)

    @api.constrains('estimated_hour')
    def _check_estimated_hour(self):
        if not self.estimated_hour:
            raise ValidationError('Please select an Effort Hour.')

    @api.onchange('estimated_hour')
    def _onchange_estimated_hour(self):
        if self.estimated_hour > 26.0:
            raise ValidationError('Estimate hour should be less than or equal to 26 hour.')

    @api.depends('project_id', 'module_id', 'task_name')
    def compute_project_with_task(self):
        for rec in self:
            if not rec.project_id and not rec.project_code and not rec.module_id:
                rec.project_task_name = rec.task_name
            else:
                project_name = rec.project_id.name if rec.project_id else ''
                module_name = rec.module_id.name if rec.module_id else rec.task_name
                rec.project_task_name = f"{project_name}/{module_name}"

    @api.depends('project_id')
    def _compute_project_code(self):
        for rec in self:
            if rec.project_id and rec.project_id.crm_id:
                project_code_record = self.env['crm.lead'].sudo().browse(rec.project_id.crm_id.id)
                if project_code_record.stage_id.code == 'workorder' and project_code_record.code is not False:
                    rec.project_code = project_code_record.code
                elif project_code_record.stage_id.code == 'opportunity' and project_code_record.code is not False:
                    rec.project_code = project_code_record.code
                else:
                    rec.project_code = rec.project_id.code
            else:
                rec.project_code = False

    def _check_buttons_visible(self):
        for record in self:
            login_user_id = self.env.user.employee_ids.id
            task_raised_by_ids = [record.task_raised_by.id] if record.task_raised_by else []
            task_assigned_by_ids = [record.assigned_to.id] if record.assigned_to else []
            data = login_user_id in task_raised_by_ids
            assign_user = login_user_id in task_assigned_by_ids
            if data and record.stage == 'Report':
                record.task_raised_by_bool = True
            if assign_user and record.stage == 'Assigned':
                record.assign_to_bool = True

    @api.model
    def create(self, vals):
        max_reference_no = self.search([('stage', '!=', 'Draft')], order="id desc", limit=1).reference_no
        vals['reference_no'] = max_reference_no + 1
        vals['reference_no_txt'] = 'TKT-' + str(vals['reference_no']).zfill(4)
        vals['stage'] = 'Assigned'
        vals['assign_to_report_bool'] = True
        if 'assign_task_date' in vals:
            vals['task_assign_day'] = datetime.strptime(vals['assign_task_date'], '%Y-%m-%d %H:%M:%S').date()

        res = super(kw_task_management, self).create(vals)

        template_id = self.env.ref('task_management.task_management_assigned_task_email_template')
        assigned_by = self.env.user.employee_ids
        task_assigned_by_name = assigned_by.display_name
        email_from = assigned_by.work_email
        email_to = res.assigned_to.work_email
        assign_task_to = res.assigned_to.name
        email_cc = ','.join(res.notify_to.mapped('work_email'))
        template_id.with_context(email_from=email_from,
                                 email_to=email_to,
                                 email_cc=email_cc,
                                 assign_task_to=assign_task_to,
                                 ticket_no=res.reference_no_txt,
                                 task_assigned_by_name=task_assigned_by_name).sudo().send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        self.env.user.notify_success("Task Assigned Successfully.")

        return res
    
    # @api.multi
    # def unlink(self):
    #     print("Method called =====>>>>>>")
    #     for record in self:
    #         print(record.task_raised_by.id, "============", self.env.user.employee_ids.id, "=======>>>>>>>",record.reported_start_bool)
    #         if record.task_raised_by.id == self.env.user.employee_ids.id and record.reported_start_bool == True:
    #             print(record.task_raised_by.id, "============", self.env.user.employee_ids.id, "=======>>>>>>>",record.reported_start_bool)
    #             msg = _("You cannot delete a record that has already started.")
    #             raise UserError(msg)
    #         elif record.task_raised_by.id != self.env.user.employee_ids.id and record.reported_start_bool == False:
    #             msg = _("You cannot delete this record.....")
    #             raise UserError(msg)
            # else:
            #     msg = _("You cannot delete this record.")
            #     raise UserError(msg)
            # elif record.task_raised_by.id != self.env.user.employee_ids.id or record.reported_start_bool == False:
            #     print(record.task_raised_by.id, "============", self.env.user.employee_ids.id, "=======>>>>>>>",record.reported_start_bool)

            #     print("in elif===============")
            #     msg = _("You cannot delete this record.")
            #     raise UserError(msg)
        # return super(kw_task_management, self).unlink()

    def btn_extend_effort_hour(self):
        view_id = self.env.ref("task_management.extende_effort_hour_wizard_view").id
        action = {
            'name': 'Extend Effort Hour',
            'type': 'ir.actions.act_window',
            'res_model': 'extend_effort_hour',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'default_effort_hour': self.estimated_hour},
        }
        return action

    def btn_acknowledge(self):
        view_id = self.env.ref("task_management.tasks_management_wizard_ack_view").id
        action = {
            'name': 'Acknowledge',
            'type': 'ir.actions.act_window',
            'res_model': 'report_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'target': 'new',
        }
        return action

    def btn_stop(self):
        actual_hour = datetime.now()

        if self.assigned_to == self.env.user.employee_ids and self.stage == "Assigned":
            view_id = self.env.ref("task_management.tasks_management_wizard_view").id
            action = {
                'name': 'Report',
                'type': 'ir.actions.act_window',
                'res_model': 'report_wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view_id,
                'target': 'new',
                'context': {'stage': 'Report',
                            'default_start_time': self.start_datetime_task,
                            'default_resume_time': self.store_resume_end_time}
            }
            return action

    def btn_pause(self):
        actual_hour = datetime.now()

        if self.assigned_to == self.env.user.employee_ids and self.stage == "Assigned":
            view_id = self.env.ref("task_management.tasks_management_wizard_pause_view").id
            action = {
                'name': 'Pause',
                'type': 'ir.actions.act_window',
                'res_model': 'report_wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view_id,
                'target': 'new',
                'context': {'default_start_time': self.start_datetime_task,
                            'default_resume_time': self.store_resume_end_time},
            }
            return action

    def btn_resume(self):
        actual_hour = datetime.now()

        if self.assigned_to == self.env.user.employee_ids and self.stage == "Assigned":
            view_id = self.env.ref("task_management.tasks_management_wizard_resume_view").id
            action = {
                'name': 'Resume',
                'type': 'ir.actions.act_window',
                'res_model': 'report_wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': view_id,
                'target': 'new',
                'context': {'default_pause_time': self.store_pause_time},
            }
            return action

    @api.depends('raised_department_id')
    def compute_can_see_advanced(self):
        for rec in self:
            if rec.raised_department_id and rec.raised_department_id.code in ["BSS"]:
                rec.can_see_advanced_fields = True

    def btn_start(self):
        start_time = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        # kw_server_tz = pytz.timezone(KWANTIFY_SERVER_TIMEZONE or 'UTC')
        # start_time = actual_hour.astimezone(kw_server_tz).strftime("%Y-%m-%d %H:%M:%S")
        # print(start_time,"kw_server_actual_hour=============================")
        # print(kw_server_actual_hourddd,"kw_server_actual_hour=============================")

        if self.assigned_to == self.env.user.employee_ids and self.stage == "Assigned":
            self.write({'start_datetime_task': start_time,
                        'reported_start_bool': True})
            self.env['kw_task_management_log'].create({
                'start_datetime': start_time,
                'action': 'Started',
                'task_sr_management_id': self.id,
            })

    # daily reminder mail for start the task
    def daily_reminder_mail_for_start_task(self):
        all_data = {}
        tasks = self.env['kw_task_management'].search([('stage', 'in', ['Assigned']), ('reported_start_bool', '=', False)])
        template_id = self.env.ref('task_management.task_start_reminder_mail_to_employee_mail_template')
        for rec in tasks:
            if rec.assign_task_date.date() < date.today():
                if rec.assigned_to.work_email not in all_data:
                    all_data[rec.assigned_to.work_email] = {'name': rec.assigned_to.display_name, 'data': []}
                    # print(all_data[rec.assigned_to.work_email],"all_data======>>>>")
                all_data[rec.assigned_to.work_email]['data'].append([rec.assign_task_date + timedelta(hours=5, minutes=30), rec.reference_no_txt])

        for mail in all_data:
            mail_to = mail
            emp_name = all_data[mail]['name']
            template_id.with_context(email_to=mail_to, emp_name=emp_name, data=all_data[mail]['data']).sudo().send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            self.env.user.notify_info("Mail Sent Successfully.")


class kw_sr_task_log(models.Model):
    _name = "kw_task_management_log"
    _description = "Task Log"

    start_datetime = fields.Datetime(string="Start Date and Time")
    end_datetime = fields.Datetime(string="Stop Date and Time")
    duration_of_task = fields.Char(string="Duration OLD")
    task_duration = fields.Float(string="Duration(HH:MM)")
    task_sr_management_id = fields.Many2one('kw_task_management', string="Task Management")
    action = fields.Char(string='Action')
    stage_comments = fields.Text(string='Comments')

    @api.multi
    def write(self, vals):
        response = super(kw_sr_task_log, self).write(vals)
        for rec in self:
            if rec.start_datetime and rec.end_datetime and rec.action != 'Stopped':
                duration = self._duration(rec.start_datetime, rec.end_datetime)
                # print('duration >>>>>>>>>>>>>> >>>> ',  duration)
                qry = f'UPDATE kw_task_management_log SET task_duration={duration} WHERE id={rec.id};'
                self._cr.execute(qry)
        return response

    def _duration(self, start_date, stop_date):
        ten_hours = 10 * 60
        dt_format = "%Y-%m-%d %H:%M:%S"
        employee_rec = self.env.user.employee_ids
        timezone = pytz.timezone(employee_rec.tz or employee_rec.resource_calendar_id.tz or 'UTC')
        start_date = datetime.strptime(str(start_date).split('.')[0], dt_format).astimezone(timezone).replace(tzinfo=None)
        stop_date = datetime.strptime(str(stop_date).split('.')[0], dt_format).astimezone(timezone).replace(tzinfo=None)
        duration_minutes = (stop_date - start_date).total_seconds() // 60
        day_count = (stop_date - start_date).days + 1
        duration = ''
        attendance = self.env['kw_daily_employee_attendance']
        # print('ten hours >>>> ', ten_hours, employee_rec, duration_minutes, day_count, start_date, stop_date)
        if start_date.hour < 12:
            # print(start_date.hour,"=========",start_date.hour<12)
            if ten_hours < duration_minutes and day_count == 1:
                raise ValidationError("You can't take action today.")
      

        if ten_hours < duration_minutes:
            duration_minutes = 0
            cnt = 0
            attendance_dates = []
            # check in between days and check if in leave or holiday
            if day_count > 2:
                dates = [d.date() for d in (start_date + timedelta(n) for n in range(1, day_count - 1))]
                attendance_data = attendance.search([
                    ('employee_id', '=', employee_rec.id),
                    ('attendance_recorded_date', 'in', dates),
                ])
                # print('dates >>>> ', dates, attendance_data)
                
                for attendance_rec in attendance_data:
                    # 4, 5 = Week Off  2 = Holiday
                    if (attendance_rec.day_status not in ['2', '4', '5']
                            and attendance_rec.status not in ['Week Off', 'Holiday', 'On Leave']):
                        cnt += 1
                        attendance_dates.append(attendance_rec.attendance_recorded_date)
                duration_minutes = 8.5 * 60 * cnt
            # print('attendance_dates >> ', attendance_dates, cnt)
            # print('duration_minutes 1 >>> ', duration_minutes, cnt)
            # check shift
            # dates = [d.date() for d in (start_date + timedelta(n) for n in range(day_count)) if d <= stop_date]
            employee_shift = employee_rec.resource_calendar_id
            # timezone = pytz.timezone(employee_rec.tz or employee_shift.tz or 'UTC')
            # start_date = start_date.astimezone(timezone).replace(tzinfo=None)
            # stop_date = stop_date.astimezone(timezone).replace(tzinfo=None)

            roaster_shift = attendance._get_employee_roaster_shift(employee_rec.id, start_date)
            if roaster_shift:
                employee_shift = roaster_shift.shift_id

            flexi_shift = attendance._get_employee_flexi_shift(employee_rec.id, start_date)
            if flexi_shift:
                employee_shift = flexi_shift
            st_min = int(((employee_shift.second_half_hour_to - int(employee_shift.second_half_hour_to)) * 100) * 0.6)
            st_time = f'{int(employee_shift.second_half_hour_to)}:{st_min}:00'
            st_date = datetime.strptime(str(start_date.date()) + f' {st_time}', dt_format)
            if st_date > start_date:
                duration_minutes += (st_date - start_date).total_seconds() // 60
            # print('duration_minutes 2 >>> ', duration_minutes)
            # print('employee_shift 1 >>>> ', st_date, start_date)
            # print('first_half_hour_from 1 >>>> ', start_date, employee_shift.second_half_hour_to)

            roaster_shift = attendance._get_employee_roaster_shift(employee_rec.id, stop_date)
            if roaster_shift:
                employee_shift = roaster_shift.shift_id

            flexi_shift = attendance._get_employee_flexi_shift(employee_rec.id, stop_date)
            if flexi_shift:
                employee_shift = flexi_shift

            en_min = int(((employee_shift.first_half_hour_from - int(employee_shift.first_half_hour_from)) * 100) * 0.6)
            en_time = f'{int(employee_shift.first_half_hour_from)}:{en_min}:00'
            en_date = datetime.strptime(str(stop_date.date()) + f' {en_time}', dt_format)
            if stop_date > en_date:
                duration_minutes += (stop_date - en_date).total_seconds() // 60
            # print('employee_shiftee_shift 2 >>>> ', en_date, stop_date)
            # print('first_half_hour_from 2 >>>> ', employee_shift.first_half_hour_from, stop_date)
            # print('duration_minutes 3 >>> ', duration_minutes)

        hr_string = str(int(duration_minutes // 60))
        mm_string = str(int(((duration_minutes % 60) / 60) * 100)).zfill(2)
        duration = f'{hr_string}.{mm_string}'
        # print('durationation >>> ', duration_minutes, duration, hr_string, mm_string)
        # aaaay

        return duration


class KwTaskTypeMaster(models.Model):
    _name = 'kw_task_type_master'
    _description = 'Task Type Master'

    name = fields.Char(string='Task Name', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('task_type_name_uniq', 'unique(name)', 'Name already exists.'),
        ('code_uniq', 'unique(code)', 'Code already exist.'),
    ]


class CrconfigurationUser(models.Model):
    """
    Model class for Configuration User Access in Task Management.
    """
    _name = 'task_management_user_access'
    _description = 'Configuration User Access'

    emp_id = fields.Many2one('hr.employee', string='Employee')

    @api.multi
    def give_config_user_group_access(self):
        """
        Method to grant access to the configuration User group.
        """
        configuration_group = self.env.ref('task_management.group_task_management_user')

        configuration_access_records = self.env['task_management_user_access'].sudo().search([])
        users = configuration_access_records.mapped('emp_id.user_id')

        users_to_add = users - configuration_group.users
        for user in users_to_add:
            configuration_group.sudo().write({'users': [(4, user.id)]})

        users_to_remove = configuration_group.users - users
        for user in users_to_remove:
            configuration_group.sudo().write({'users': [(3, user.id)]})

        self.env.user.notify_success("Users Synced Successfully.")
