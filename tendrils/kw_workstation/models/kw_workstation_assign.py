
import datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar



class kw_workstation_assign(models.Model):
    _name = 'kw_workstation_assign'
    _description = "Workstation Assign"
    _order = "assign_date DESC"

    assign_date = fields.Date(string="Assign Date", required=True)
    workstation_id = fields.Many2one('kw_workstation_master', string="Workstation", required=True, domain=[('is_hybrid', '=', True)])
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True,)
    employee_code = fields.Char(string="Name", related="employee_id.emp_code")
    employee_name = fields.Char(string="Name", related="employee_id.name")
    active = fields.Boolean('Active', default=True)
    assign_year = fields.Date(string="Assign Year", compute="_compute_month")
    assign_month = fields.Date(string="Assign Month", compute="_compute_month")
    assign_day = fields.Date(string="Assign Day", compute="_compute_month")
    
    @api.depends('assign_date')
    def _compute_month(self):
        for rec in self:
            if rec.assign_date:
                rec.assign_day = datetime.datetime.strptime(str(rec.assign_date), "%Y-%m-%d").strftime("%d")
                rec.assign_month = datetime.datetime.strptime(str(rec.assign_date), "%Y-%m-%d").strftime("%b")
                rec.assign_year = datetime.datetime.strptime(str(rec.assign_date), "%Y-%m-%d").strftime("%Y")

    @api.onchange('workstation_id')
    def onchange_workstation(self):
        record_workstation = self.env['kw_workstation_master'].sudo().search(
            [('name', '=', self.workstation_id.name)]).mapped('employee_id').ids
        return {'domain': {'employee_id': [('id', 'in', record_workstation)]}}

    @api.model
    def create(self, vals):
        new_record = super(kw_workstation_assign, self).create(vals)
        self.env.user.notify_success(message='Workstation Assign created successfully.')
        return new_record

    @api.multi
    def write(self, vals):
        res = super(kw_workstation_assign, self).write(vals)
        self.env.user.notify_success(message='Workstation Assign updated successfully.')
        return res

    @api.constrains('assign_date', 'workstation_id')
    def check_constraints(self):
        for rec in self:
            record = self.env['kw_workstation_assign'].search(
                [('workstation_id', '=', rec.workstation_id.id), ('assign_date', '=', rec.assign_date)]) - self
            # [('employee_id', '=', rec.employee_id.id), ('assign_date', '=', rec.assign_date)]) - self
            if record.exists():
                raise ValidationError("Record already exists!")
    
    def workstation_assign_emp_cron(self):
        from datetime import datetime, timedelta
        import calendar
        from dateutil.relativedelta import relativedelta
        
        if self._context.get('assign'):
            assign_date_str = self._context.get('assign_date')
            dt = datetime.strptime(assign_date_str, '%Y-%m-%d %H:%M:%S')
        else:
            dt = datetime.now()
        workstations = self.env['kw_workstation_master'].search([('is_hybrid', '=', True)])
        if workstations and (dt.day > 26 or dt.day < 5):
            if dt.month == 12 and dt.day > 25:
                dt = dt + relativedelta(months=1)
                month_add = 0
            else:
                month_add = 1 if dt.day > 25 else 0
            input_date = datetime(year=dt.year, month=dt.month + month_add, day=1, tzinfo=dt.tzinfo)
            year = input_date.year
            month = input_date.month

            first_date_of_month = input_date.replace(day=1)
            last_day = calendar.monthrange(year, month)[1]
            last_day_of_month = input_date.replace(day=last_day)

            current_month_last_date = dt.replace(day=calendar.monthrange(dt.year, dt.month)[1])
            st_date = current_month_last_date - timedelta(days=2)
            last_3_dates_of_month = [(st_date + timedelta(days=x)).date() for x in range((current_month_last_date - st_date).days + 1)]

            firstweekday = 0
            calendar_data = calendar.Calendar(firstweekday)
            week_assignments = {}

            for weekstart in filter(lambda d: d.weekday() == firstweekday, calendar_data.itermonthdates(year, month)):
                week_end = weekstart + timedelta(days=4)
                if weekstart < week_end < first_date_of_month.date():
                    continue
                week_assignments[(weekstart, week_end)] = []

                for workstation in workstations:
                    workstation_id = workstation.id
                    last_friday_date = weekstart - timedelta(4)
                    assigned_employee = self.env['kw_workstation_assign'].search(
                        [('workstation_id', '=', workstation.id), ('assign_date', '=', last_friday_date)])
                    if assigned_employee.exists():
                        employee_id = workstation.employee_id - assigned_employee.employee_id
                    else:
                        employee_id = workstation.employee_id[0] if workstation.employee_id else False
                    if employee_id is not False:
                        if  len(employee_id) > 1:
                            employee_id = employee_id[0]
                        for i in range(0, 5):
                            assign_date = weekstart + timedelta(i)
                            assigned_exists = self.env['kw_workstation_assign'].search(
                                [('workstation_id', '=', workstation.id), ('assign_date', '=', assign_date)])
                            if not assigned_exists.exists():
                                employee_data = {'employee_id': employee_id.id,
                                                 'workstation_id': workstation_id,
                                                 'assign_date': assign_date.strftime("%d-%b-%Y")}
                                self.env['kw_workstation_assign'].sudo().create(employee_data)

            today = input_date
            assigns_data = self.env['kw_workstation_assign'].sudo().search([('assign_date', '>=', first_date_of_month), ('assign_date', '<=', last_day_of_month)])
            assigns = assigns_data.mapped('employee_id')
            employee_workstations = {}

            for assign in assigns_data:
                employee_id = assign.employee_id.id
                workstation = assign.workstation_id.name
                assign_date = assign.assign_date
                weekstart = None
                week_end = None
                for ws, we in week_assignments.keys():
                    if ws <= assign_date <= we:
                        weekstart = ws
                        week_end = we
                        break

                if weekstart and week_end:
                    week_assignments[(weekstart, week_end)].append((assign_date, employee_id))

                if employee_id not in employee_workstations:
                    employee_workstations[employee_id] = set()
                employee_workstations[employee_id].add(workstation)

            employee_workstations = {key: list(value) for key, value in employee_workstations.items()}

            employee_ids_week_ranges = {}
            week_assignments_sorted = {}

            for week_start_end, assignments in week_assignments.items():
                week_start, week_end = week_start_end
                week_start_str = week_start.strftime('%d-%b') if week_start >= first_date_of_month.date() else first_date_of_month.strftime('%d-%b')
                week_end_str = week_end.strftime('%d-%b')
                week_range = f"{week_start_str} to {week_end_str}"

                for assign_date, employee_id in sorted(assignments, key=lambda x: x[0]):
                    if employee_id not in employee_ids_week_ranges:
                        employee_ids_week_ranges[employee_id] = set()
                    employee_ids_week_ranges[employee_id].add(week_range)

                    if employee_id not in week_assignments_sorted:
                        week_assignments_sorted[employee_id] = []
                    week_assignments_sorted[employee_id].append((assign_date, employee_id))

            week_ranges_str = week_dates = {}
            for employee_id, week_ranges in employee_ids_week_ranges.items():
                week_dates[employee_id] = sorted(week_ranges)

            # Determine WFH dates
            wfh_dates = {}
            for employee_id in employee_ids_week_ranges.keys():
                wfh_dates[employee_id] = []
                for week_start_end in week_assignments.keys():
                    week_start, week_end = week_start_end
                    week_range = f"{week_start.strftime('%d-%b')} to {week_end.strftime('%d-%b')}"
                    if week_range not in employee_ids_week_ranges[employee_id]:
                        wfh_dates[employee_id].append(week_range)

            print("week_dates >>>>>>>================= ", week_dates)
            print("wfh_dates >>>>>>>================== ", wfh_dates)

            emp_emails = [rec.work_email for rec in assigns]
            mail_to = ','.join(set(emp_emails))

            cc_notify = self.env.ref('kw_workstation.group_ws_cc_notify').users
            mail_cc = ','.join(cc_notify.mapped("email")) if cc_notify else ''

            month_name = today.strftime("%B %Y")
            template = self.env.ref('kw_workstation.ws_assignment_schedule_mail')
            if template:
                template.with_context(month_name=month_name,
                                    mail_to=mail_to,
                                    cc_mail=mail_cc,
                                    records=assigns,
                                    date=week_dates,
                                    wfh_dates=wfh_dates,
                                    employee_workstations=employee_workstations).sudo().send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")

                self.env.user.notify_success("Mail sent Successfully.")
        return True


    def weekly_workstation_attendance_mode_change(self):
        attn_mode_biometric = self.env['kw_attendance_mode_master'].sudo().search([('alias', '=', 'bio_metric')])
        attn_mode_portal = self.env['kw_attendance_mode_master'].sudo().search([('alias', '=', 'portal')])
        tomorrow = datetime.datetime.now().date() + timedelta(days=1)
        # next_friday = tomorrow + timedelta(days=4)
        workstations = self.env['kw_workstation_assign'].search([('assign_date', '=', tomorrow),])
        # print("workstations >>> ", workstations)
        if workstations:
            # ws_tagged_employees_list = self.env['kw_workstation_master'].search([('id', 'in', workstations.mapped("workstation_id.id"))]).mapped('employee_id')
            ws_tagged_employees_list = self.env['kw_workstation_master'].browse(workstations.mapped("workstation_id.id")).mapped('employee_id')
            # print("ws_tagged_employees_list >>> ", ws_tagged_employees_list)

            wfo_employee_list = workstations.mapped('employee_id')  # bio-metric
            wfh_employee_list = ws_tagged_employees_list - wfo_employee_list  # portal

            for bio_rec in wfo_employee_list:
                check_exist = bio_rec.attendance_mode_ids

                if check_exist.exists():
                    if attn_mode_biometric in check_exist:
                        pass
                    else:
                        query = f"UPDATE hr_employee_kw_attendance_mode_master_rel SET kw_attendance_mode_master_id={attn_mode_biometric.id} WHERE hr_employee_id={bio_rec.id};"
                        self._cr.execute(query)
                else:
                    query = f"INSERT INTO hr_employee_kw_attendance_mode_master_rel (hr_employee_id, kw_attendance_mode_master_id) VALUES ({bio_rec.id}, {attn_mode_biometric.id}) ON CONFLICT DO NOTHING;"
                    self._cr.execute(query)

            for portal_rec in wfh_employee_list:
                check_exist = portal_rec.attendance_mode_ids
                if check_exist.exists():
                    if attn_mode_portal in check_exist:
                        pass
                    else:
                        query = f"UPDATE hr_employee_kw_attendance_mode_master_rel SET kw_attendance_mode_master_id={attn_mode_portal.id} WHERE hr_employee_id={portal_rec.id};"
                        self._cr.execute(query)
                else:
                    query = f"INSERT INTO hr_employee_kw_attendance_mode_master_rel (hr_employee_id, kw_attendance_mode_master_id) VALUES ({portal_rec.id}, {attn_mode_portal.id}) ON CONFLICT DO NOTHING;"
                    self._cr.execute(query)

        # print("Executed successfully.")
        
        
class WorkstationAssignWizard(models.TransientModel):
   
    _name = "workstation_assign_wizard"
    _description = "Workstation Assign"
    
    
    
    date_of_assign = fields.Datetime(string="Date")
    
    
    def assign_workstation(self):
        self.env['kw_workstation_assign'].workstation_assign_emp_cron()
    
    