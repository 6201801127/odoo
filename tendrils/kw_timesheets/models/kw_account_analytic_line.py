import pytz
import calendar
import json, requests
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.addons.resource.models import resource
# from odoo.tools.profiler import profile

# class kw_crm_lead(models.Model):
#     _inherit = "crm.lead"


#     @api.multi
#     def name_get(self):
#         result = []
#         for record in self:
#             if record.code:
#                 result.append((record.id, f'{record.code}'))
#             else:
#                 result.append((record.id, f'{record.name}'))
#         return result


class kw_account_analytic_line(models.Model):
    _inherit = "account.analytic.line"
    _description = "Timesheet"

    name = fields.Text('Description', required=True)
    sync_status = fields.Boolean(string='Sync Status', default=False)
    sbu_id = fields.Char(related='project_id.sbu_id.name', string='Sbu Name', store=True)
    emp_category_id = fields.Char(related='employee_id.emp_category.name', string='Employee Category', store=True)
    project_code = fields.Char(related='project_id.crm_id.code', string='Project Code')
    pending_at = fields.Char(compute='_compute_pending_at', string='Pending At')
    parent_task_id = fields.Many2one('project.task',string="Activity")
    approved_by = fields.Char('Timesheet Approved By')
   
    @api.multi
    def _compute_pending_at(self):
        project_work = self.env['kw_project_category_master'].search([('mapped_to', '=', 'Project')], limit=1)
        for record in self:
            record.pending_at = record.employee_id.parent_id and record.employee_id.parent_id.name or ''
            if record.prject_category_id == project_work:
                # employee is tech lead
                if record.employee_id.emp_category.code == 'TTL':
                    # employee not pm not pr
                    if record.project_id.emp_id != record.employee_id and \
                            record.project_id.reviewer_id != record.employee_id:
                        record.pending_at = record.project_id.emp_id and record.project_id.emp_id.name or ''
                    # employee pm not pr
                    if record.project_id.emp_id == record.employee_id and \
                            record.project_id.reviewer_id != record.employee_id:
                        record.pending_at = record.project_id.reviewer_id and record.project_id.reviewer_id.name or ''
                # employee not tech lead
                elif record.employee_id.emp_category.code != 'TTL':
                    # task has team lead
                    if record.task_id.tl_employee_id:
                        if record.project_id.emp_id != record.employee_id and \
                                record.task_id.tl_employee_id != record.employee_id and \
                                record.project_id.reviewer_id != record.employee_id:
                            record.pending_at = record.task_id.tl_employee_id and record.task_id.tl_employee_id.name or ''
                        elif record.project_id.emp_id != record.employee_id and \
                                record.task_id.tl_employee_id == record.employee_id and \
                                record.project_id.reviewer_id != record.employee_id:
                            record.pending_at = record.project_id.emp_id and record.project_id.emp_id.name or ''
                        elif record.project_id.emp_id == record.employee_id and \
                                record.project_id.reviewer_id != record.employee_id:
                            record.pending_at = record.project_id.reviewer_id and record.project_id.reviewer_id.name or ''
                    # task has no team lead
                    if not record.task_id.tl_employee_id:
                        if record.project_id.emp_id != record.employee_id and \
                                record.project_id.reviewer_id != record.employee_id:
                            record.pending_at = record.project_id.emp_id and record.project_id.emp_id.name or ''
                        if record.project_id.emp_id == record.employee_id and \
                                record.project_id.reviewer_id != record.employee_id:
                            record.pending_at = record.project_id.reviewer_id and record.project_id.reviewer_id.name or ''
                if record.project_id.emp_id == record.employee_id and not record.project_id.reviewer_id:
                    record.pending_at = record.employee_id.parent_id and record.employee_id.parent_id.name or ''

    # #send custom email by changing the model description
    def timesheet_send_custom_mail(self, res_id, force_send=False, raise_exception=False, email_values=None,
                                   notif_layout=False, template_layout=False, ctx_params=None, description=False):
        template = self.env.ref(template_layout)
        if template:
            # template.with_context(extra_params).send_mail(emp_rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")

            values = template.with_context(ctx_params).generate_email(res_id)
            values['recipient_ids'] = [(4, pid) for pid in values.get('partner_ids', list())]
            values.update(email_values or {})

            # add a protection against void email_from
            if 'email_from' in values and not values.get('email_from'):
                values.pop('email_from')
            # encapsulate body
            if notif_layout and values['body_html']:
                try:
                    notif_template = self.env.ref(notif_layout, raise_if_not_found=True)
                except ValueError:
                    pass
                else:
                    record = self.env[template.model].browse(res_id)
                    template_ctx = {
                        'message': self.env['mail.message'].sudo().new(dict(body=values['body_html'], record_name=record.display_name)),
                        'model_description': description if description else self.env['ir.model']._get(record._name).display_name,
                        'company': 'company_id' in record and record['company_id'] or self.env.user.company_id,
                    }
                    body = notif_template.render(template_ctx, engine='ir.qweb', minimal_qcontext=True)
                    values['body_html'] = self.env['mail.thread']._replace_local_links(body)

            mail = self.env['mail.mail'].create(values)

            if force_send:
                mail.send(raise_exception=raise_exception)

            mail.model = False
            return mail.id

    def get_previous_week_sunday_date(self):
        today = datetime.now()
        monday = today - timedelta(days = today.weekday())
        return monday.date()

    """ Timesheet add for Past week restriction """
    @api.constrains('date')
    def _check_previous_date_entry(self):
        config_check = self.env['ir.config_parameter'].sudo().get_param('kw_timesheets.validation_check')
        current_date = date.today()
        current_month_1st_date = current_date.replace(day=1)

        current_month_25th_date = current_date.replace(day=25)
        previous_month_1st_date = current_month_1st_date - relativedelta(months=1)
        previous_month_25th_date = current_month_25th_date - relativedelta(months=1)

        prvs_week_sunday_date = self.get_previous_week_sunday_date()
        emp_id = self.env['hr.employee'].sudo().search([('id', '=', self.employee_id.id)])

        if config_check and self.env.user.employee_ids.id != self.employee_id.parent_id.id:
            if self.date < prvs_week_sunday_date and emp_id.allow_backdate == False:
                raise ValidationError('You are not allowed to add timesheet for past week.')

        if previous_month_1st_date <= self.date < current_month_1st_date:
            if current_month_1st_date <= current_date <= current_month_25th_date:
                if not (previous_month_1st_date <= self.date <= current_month_25th_date):
                    raise ValidationError("You can add timesheet data after 25th of this month")

        if not (current_month_1st_date <= current_date <= current_month_25th_date):
            if previous_month_1st_date <= self.date < current_month_1st_date:
                if self.date <= previous_month_25th_date:
                    raise ValidationError("You can't add Timesheet data for previous month")

        if self.date < previous_month_1st_date:
            raise ValidationError("You can't add Timesheet for two months before.")

    # start : one day validation check (In general settings -> timesheets check one day restriction check)
    @api.constrains('date','prject_category_id','project_id','crm_lead_id','task_id','name','unit_amount','task_status')
    def validate_one_day_restriction_check(self):
        current_date = date.today()
        current_employee = self.env['hr.employee'].search([('user_id','=',self._uid)],limit=1)
        one_day_restriction = self.env['ir.config_parameter'].sudo().get_param('kw_timesheets.one_day_restriction_check')

        if one_day_restriction:
            current_week_monday = current_date - timedelta(days=current_date.weekday())

            current_week_friday = current_week_monday + timedelta(days=4)
            current_week_saturday = current_week_monday + timedelta(days=5)
            current_week_sunday = current_week_saturday + timedelta(days=1)

            previous_week_friday = current_week_friday - timedelta(weeks=1)

            if current_date == current_week_monday: # Monday (Check timesheet for friday)
                timesheet_date = previous_week_friday
            elif current_date in [current_week_saturday,current_week_sunday]: #Saturday and Sunday
                timesheet_date = current_week_friday
            else:
                timesheet_date = current_date - timedelta(days=1)

            for timesheet in self:
                if timesheet.employee_id == current_employee and timesheet.date < timesheet_date:
                    raise ValidationError("You are not allowed to update timesheet after one day.")
        for timesheet in self:
            if timesheet.validated:
                raise ValidationError("Timesheet can't be modified after validated.")
            if timesheet.task_id.task_status == 'Completed':
                raise ValidationError("You can't add timesheet as this task is Completed.")
    # end : one day validation check (In general settings -> timesheets check one day restriction check)

    @api.multi
    def write(self, vals):
        config_check = self.env['ir.config_parameter'].sudo().get_param('kw_timesheets.validation_check')
        # prvs_week_sunday_date = date.today() + relativedelta(weeks=2, days=1, weekday=-1)
        # today = date.today()
        # idx = (today.weekday() + 1) % 7
        # prvs_pre_week_sunday_date = today - timedelta(7 + idx)
        year = datetime.today().year
        month = datetime.today().month
        # prvs_month = month - 1
        # dt_26th_prvs_month = datetime.strptime('{}-{}-{:2}'.format(year, prvs_month, 26), '%Y-%m-%d')
        prvs_week_sunday_date = self.get_previous_week_sunday_date()
        for rec in self:
            emp_id = self.env['hr.employee'].sudo().search([('id', '=', rec.employee_id.id)])
            if config_check:
                if rec.date < prvs_week_sunday_date and emp_id.allow_backdate == False:
                    if self._context.get('uid') == rec.employee_id.user_id.id:
                        raise ValidationError('You are not allowed to update timesheet for past week.')
            # if config_check and self.env.user.employee_ids.id == self.employee_id.parent_id.id:
            #     if rec.date < prvs_pre_week_sunday_date and emp_id.allow_backdate == False:
            #             raise ValidationError('You are not allowed to edit timesheet for past week.')
            # if self.date < dt_26th_prvs_month.date():
            #     raise ValidationError('You are not allowed to edit timesheet after 25th of previous month.')
            vals['sync_status'] = False
        res = super(kw_account_analytic_line, self).write(vals)
        return res

    @api.multi
    def unlink(self):
        config_check = self.env['ir.config_parameter'].sudo().get_param('kw_timesheets.validation_check')
        # prvs_week_sunday_date = date.today() + relativedelta(weeks=2, days=1, weekday=-1)
        # today = date.today()
        # idx = (today.weekday() + 1) % 7
        # prvs_week_sunday_date = today - timedelta(7 + idx)
        prvs_week_sunday_date = self.get_previous_week_sunday_date()
        if config_check and not self.user_has_groups('hr_timesheet.group_timesheet_manager'):
            for rec in self:
                if rec.date < prvs_week_sunday_date:
                    raise ValidationError(f'You are not allowed to delete timesheet for past week for date {rec.date}.')
        return super(kw_account_analytic_line, self).unlink()

    @api.constrains('name')
    def _check_field_size(self):
        if len(self.name) < 10:
            raise ValidationError('You have to enter minimum 10 character description.')
        if len(self.name) > 300:
            raise ValidationError('You cannot enter more than 300 character in description.')

    # @api.model
    # def _get_project_id(self):
    #     query_lst2 = []
    #     print('printing context+++++++++++++++++++++++++++++++++++++++++++++',self.env.context.get('tree_view_ref'))
    #     # prj_category_id = self.env['project.task'].sudo().search([])
    #     if self.env.user.employee_ids.id:
    #         query = f'''select department_id,division,section,practise from hr_employee
    #                     where id = {self.env.user.employee_ids.id}
    #                     '''
    #         self._cr.execute(query)
    #         query_result = self._cr.fetchall()
    #         query_lst = query_result[0]
    #         print('india maal====================',query_lst)
    #         if query_lst:
    #             fil_res = tuple(filter(lambda x : x != None, query_lst))

    #         if fil_res:
    #             query1 = f'select distinct project_task_id from hr_department_project_task_rel where hr_department_id in {fil_res}'
    #             self._cr.execute(query1)
    #             query_result1 = type(self._cr.dictfetchall())
    #             print('japanese maal====================',query_result1)
    #             query_lst1 = query_result1[0]

    #         if query_lst1:
    #             query2 = f'select prject_category_id from project_task where id in {query_lst1}'
    #             self._cr.execute(query1)
    #             query_result2 = self._cr.fetchall()
    #             query_lst2 = list(query_result1[0])
    #             print('chinese maal==================',query_lst2)


    #     return [('id', 'in', query_lst2)]

    # @profile
    # @api.model
    # def _get_project_id(self):
    #     # department = self.env['hr.department']
    #     # department |= self.env.user.employee_ids.department_id
    #     # department |= self.env.user.employee_ids.division
    #     # department |= self.env.user.employee_ids.section
    #     # department |= self.env.user.employee_ids.practise
    #     # emp_dept = self.env['hr.employee'].sudo().search([('id','=',self.env.user.employee_ids.id)]).mapped('department_id').mapped('division')
    #     query_lst = []
    #     if self.env.user.employee_ids.id:
    #         query = f'''select department_id,division,section,practise from hr_employee
    #                     where id = {self.env.user.employee_ids.id}
    #                     '''
    #         self._cr.execute(query)
    #         query_result = self._cr.fetchall()
    #         query_lst = list(query_result[0])

    #     ##Not Required kindly consult with module owner before any modification done ##
    #     # department |= self.env.user.employee_ids.additional_department
    #     # department |= self.env.user.employee_ids.additional_division
    #     # department |= self.env.user.employee_ids.additional_section
    #     # department |= self.env.user.employee_ids.additional_practice

    #     prj_category_id = self.env['project.task'].sudo().search([('mapped_to', 'in', query_lst)]).mapped(
    #         'prject_category_id')

    #     return [('id', 'in', prj_category_id.ids)]

    
    @api.model
    def _get_project_id(self):
        dom_list = []
        dep_list = []
        if self.env.user.employee_ids.id:
            query = f'''select department_id,division,section,practise from hr_employee
                        where id = {self.env.user.employee_ids.id}
                        '''
            self._cr.execute(query)
            query_result = self._cr.fetchall()
            query_lst = query_result[0]
            fil_res = str(tuple(filter(lambda x : x != None, query_lst))).replace(",)",")")
            # print('check all filters===========',query_result,query_lst,fil_res)
            # query_result = self._cr.dictfetchall()
            # for dep in query_result:
            #     dept = dep['department_id']
            if fil_res:
                query1 = f'with a as (select project_task_id from hr_department_project_task_rel where hr_department_id in {fil_res}) select distinct prject_category_id from project_task p join a on a.project_task_id = p.id where prject_category_id is not null'
                self._cr.execute(query1)
                query_result1 = self._cr.dictfetchall()
                if query_result1:
                    for x in query_result1:
                        dom_list.append(x['prject_category_id'])

        return [('id', 'in', dom_list)]
    


    effective_hours = fields.Float(string='Effective Hours', related='task_id.effective_hours')
    task_planned_hours = fields.Float(string='Task Planned Hours', related='task_id.planned_hours')
    task_start_date = fields.Date(string='Task Start Date', related='task_id.planning_start_date')
    task_end_date = fields.Date(string='Task End Date', related='task_id.planning_end_date')
    prject_category_id = fields.Many2one('kw_project_category_master', string='Category Name',domain=_get_project_id)
    # get_project_category = fields.Many2many('kw_project_category_master',string='Get Category Id',compute='_get_category_id')
    hide_tagged_to = fields.Boolean(string='Hide tagged To', default=False)
    show_oppertunity_mapped = fields.Boolean(string='Show Opportunity Mapped', default=False)
    project_manager_id = fields.Many2one("hr.employee","Project Manager",related="project_id.emp_id")
    crm_lead_id = fields.Many2one('crm.lead', string='Opportunity/Work Order')
    module_id = fields.Many2one('kw_project.module', string='Module Name')
    work_hours=fields.Float("Attendance Hours", compute='get_employee_work_hour')
    #indexing in addons field
    project_id = fields.Many2one('project.project', 'Project', domain=[('allow_timesheets', '=', True)])
    employee_id = fields.Many2one('hr.employee', "Employee")

    is_project_activity = fields.Boolean("Project Work ?",compute="_compute_if_project_activity")
    is_opportunity_activity = fields.Boolean("Opportunity Work ?",compute="_compute_if_project_activity")
    is_admin_activity = fields.Boolean("Administrative Work ?",compute="_compute_if_project_activity")
    active = fields.Boolean("Active",default=True)
    job_id = fields.Many2one("hr.job","Designation",related="employee_id.job_id")
    task_status = fields.Selection([('inprogress','In-Progress'),('completed','Completed')],default="inprogress",string="Task Status")

    @api.depends('employee_id','date')
    def get_employee_work_hour(self):
        for rec in self:
            emp_work_hr = self.env['kw_daily_employee_attendance'].sudo().search(
                [('attendance_recorded_date', '=', rec.date),
                ('employee_id', '=', rec.employee_id.id)],limit=1)
            rec.work_hours = emp_work_hr.worked_hours

    # @profile
    # def _get_category_id(self):
    #     dept_id = self.env['hr.department'].sudo().browse(self.env.user.employee_ids.department_id.id)
    #     print('dekhiba kan hauchi',dept_id)
    #     dom_list = []
    #     if dept_id:
    #         query1 = f'with a as (select project_task_id from hr_department_project_task_rel where hr_department_id = {dept_id.id}) select distinct prject_category_id from project_task p join a on a.project_task_id = p.id where prject_category_id is not null'
    #         print(query1)
    #         self._cr.execute(query1)
    #         query_result1 = self._cr.dictfetchall()
    #         if query_result1:
    #             for x in query_result1:
    #                 dom_list.append(x['prject_category_id'])

       
    #     print(dom_list,self.get_project_category,'============klity===============')
    #     self.get_project_category = [[6,0,dom_list]]
    #     print(dom_list,self.get_project_category,'============love===============')



    @api.model
    def read_grid(self, row_fields, col_field, cell_field, domain=None, range=None):
        current_employee = self.env['hr.employee'].search([('user_id','=',self._uid)],limit=1)
        project_work = self.env['kw_project_category_master'].search([('mapped_to','=','Project')],limit=1)
        # user_is_timesheet_manager = self.env.user.has_group('hr_timesheet.group_timesheet_manager')
        if self._context.get('filter_project_timesheet'):
            employee_projects = self.env['project.project'].search([('emp_id','=',current_employee.id)])
            domain += [('project_id', '!=', False),('project_id','in',employee_projects.ids)]

        if self._context.get('filter_ra_pm_reviewer_timesheet'):
            query = f'''select ana.id from account_analytic_line ana
                        join project_project pj on pj.id = ana.project_id
                        where pj.emp_id = ana.employee_id and pj.reviewer_id = {current_employee.id}::integer
                        '''
            self._cr.execute(query)
            query_result = self._cr.fetchall()
            pm_reviewer_timesheet_ids = [id_tuple[0] for id_tuple in query_result]

            query = f'''select ana.id from account_analytic_line ana
                        join project_task pt on pt.id = ana.task_id
                        where pt.tl_employee_id = ana.employee_id
                        '''
            self._cr.execute(query)
            query_result = self._cr.fetchall()
            pm_timesheet_ids = [id_tuple[0] for id_tuple in query_result]

            query = f'''select ana.id from account_analytic_line ana
                        join project_project pj on pj.id = ana.project_id
                        where pj.reviewer_id = ana.employee_id
                        '''
            self._cr.execute(query)
            query_result = self._cr.fetchall()
            project_ra_timesheet_ids = [id_tuple[0] for id_tuple in query_result]

            query = f'''select ana.id from account_analytic_line ana
                        join project_project pj on pj.id = ana.project_id
                        where pj.emp_id = ana.employee_id'''

            self._cr.execute(query)
            query_result = self._cr.fetchall()
            no_reviewer_ra_timesheet_ids = [id_tuple[0] for id_tuple in query_result]

            # if not user_is_timesheet_manager:
            domain += ['&', '&', ('employee_id', '!=', current_employee.id), ('validated', '!=', True),
                     '|', '|', '|','|',
                         '&', '&', '&', '&', ('task_id.tl_employee_id', '=', current_employee.id),
                         ('prject_category_id', '=', project_work.id),
                         '|', '|', ('employee_id.emp_category.code', '!=', 'TTL'),
                              ('employee_id.emp_category.code', '=', None), ('employee_id.emp_category', '=', False),
                         ('id', 'not in', no_reviewer_ra_timesheet_ids),
                         ('id', 'not in', project_ra_timesheet_ids),

                         '&', ('project_id.emp_id', '=', current_employee.id),
                         '|', '|', ('id', 'in', pm_timesheet_ids), ('task_id.tl_employee_id', '=', False),
                         ('employee_id.emp_category.code', '=', 'TTL'),

                         '&', ('employee_id.parent_id', '=', current_employee.id),
                         '|', '|', ('prject_category_id', '!=', project_work.id),
                              '&', ('prject_category_id', '=', project_work.id), ('id', 'in', project_ra_timesheet_ids),
                              '&', '&', ('prject_category_id', '=', project_work.id), ('project_id.reviewer_id', '=', False),
                                   ('id', 'in', no_reviewer_ra_timesheet_ids),

                        ('employee_id.coach_id', '=', current_employee.id),

                         ('id', 'in', pm_reviewer_timesheet_ids)]
        return super(kw_account_analytic_line, self).read_grid(row_fields, col_field, cell_field, domain=domain, range=range)
   
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        current_employee = self.env['hr.employee'].search([('user_id','=',self._uid)],limit=1)
        project_work = self.env['kw_project_category_master'].search([('mapped_to','=','Project')],limit=1)
        # user_is_timesheet_manager = self.env.user.has_group('hr_timesheet.group_timesheet_manager')
        if self._context.get('filter_project_timesheet'):
            employee_projects = self.env['project.project'].search([('emp_id','=',current_employee.id)])
            args += [('project_id', '!=', False),('project_id','in',employee_projects.ids)]

        if self._context.get('filter_ra_pm_reviewer_timesheet'):
            query = f'''select ana.id from account_analytic_line ana
                        join project_project pj on pj.id = ana.project_id
                        where pj.emp_id = ana.employee_id and pj.reviewer_id = {current_employee.id}::integer
                        '''
            self._cr.execute(query)
            query_result = self._cr.fetchall()
            pm_reviewer_timesheet_ids = [id_tuple[0] for id_tuple in query_result]

            query = f'''select ana.id from account_analytic_line ana
                        join project_task pt on pt.id = ana.task_id
						join project_project pj on pj.id = ana.project_id
                        where pt.tl_employee_id = ana.employee_id and pt.task_status != 'completed'
						and pj.emp_id = {current_employee.id}::integer
                        '''
            self._cr.execute(query)
            query_result = self._cr.fetchall()
            pm_timesheet_ids = [id_tuple[0] for id_tuple in query_result]

            query = f'''select ana.id from account_analytic_line ana
                        join project_project pj on pj.id = ana.project_id
                        where pj.reviewer_id = ana.employee_id
                        '''
            self._cr.execute(query)
            query_result = self._cr.fetchall()
            project_ra_timesheet_ids = [id_tuple[0] for id_tuple in query_result]

            query = f'''select ana.id from account_analytic_line ana
                        join project_project pj on pj.id = ana.project_id
                        where pj.emp_id = ana.employee_id'''

            self._cr.execute(query)
            query_result = self._cr.fetchall()
            no_reviewer_ra_timesheet_ids = [id_tuple[0] for id_tuple in query_result]

            # if not user_is_timesheet_manager:
            args += ['&', '&', ('employee_id', '!=', current_employee.id), ('validated', '!=', True),
                     '|', '|', '|', '|',

                         '&', '&', '&', '&', ('task_id.tl_employee_id', '=', current_employee.id),
                         ('prject_category_id', '=', project_work.id),
                         '|', '|', ('employee_id.emp_category.code', '!=', 'TTL'),
                              ('employee_id.emp_category.code', '=', None), ('employee_id.emp_category', '=', False),
                         ('id', 'not in', no_reviewer_ra_timesheet_ids),
                         ('id', 'not in', project_ra_timesheet_ids),

                         '&', ('project_id.emp_id', '=', current_employee.id),
                         '|', '|', ('id', 'in', pm_timesheet_ids), ('task_id.tl_employee_id', '=', False),
                         ('employee_id.emp_category.code', '=', 'TTL'),


                         '&', ('employee_id.parent_id', '=', current_employee.id),
                         '|', '|', ('prject_category_id', '!=', project_work.id),
                              '&', ('prject_category_id', '=', project_work.id), ('id', 'in', project_ra_timesheet_ids),
                              '&', '&', ('prject_category_id', '=', project_work.id), ('project_id.reviewer_id', '=', False),
                                   ('id', 'in', no_reviewer_ra_timesheet_ids),

                        ('employee_id.coach_id', '=', current_employee.id),

                        
                         ('id', 'in', pm_reviewer_timesheet_ids)]

        return super(kw_account_analytic_line, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1)
        project_work = self.env['kw_project_category_master'].search([('mapped_to', '=', 'Project')], limit=1)
        # user_is_timesheet_manager = self.env.user.has_group('hr_timesheet.group_timesheet_manager')
        if self._context.get('filter_project_timesheet'):
            employee_projects = self.env['project.project'].search([('emp_id', '=', current_employee.id)])
            domain += [('project_id', '!=', False), ('project_id', 'in', employee_projects.ids)]

        if self._context.get('filter_ra_pm_reviewer_timesheet'):
            query = f'''select ana.id from account_analytic_line ana
                        join project_project pj on pj.id = ana.project_id
                        where pj.emp_id = ana.employee_id and pj.reviewer_id = {current_employee.id}::integer
                        '''
            self._cr.execute(query)
            query_result = self._cr.fetchall()
            pm_reviewer_timesheet_ids = [id_tuple[0] for id_tuple in query_result]

            query = f'''select ana.id from account_analytic_line ana
                        join project_task pt on pt.id = ana.task_id
                        where pt.tl_employee_id = ana.employee_id
                        '''
            self._cr.execute(query)
            query_result = self._cr.fetchall()
            pm_timesheet_ids = [id_tuple[0] for id_tuple in query_result]

            query = f'''select ana.id from account_analytic_line ana
                        join project_project pj on pj.id = ana.project_id
                        where pj.reviewer_id = ana.employee_id
                        '''
            self._cr.execute(query)
            query_result = self._cr.fetchall()
            project_ra_timesheet_ids = [id_tuple[0] for id_tuple in query_result]

            query = f'''select ana.id from account_analytic_line ana
                        join project_project pj on pj.id = ana.project_id
                        where pj.emp_id = ana.employee_id'''

            self._cr.execute(query)
            query_result = self._cr.fetchall()
            no_reviewer_ra_timesheet_ids = [id_tuple[0] for id_tuple in query_result]

            # if not user_is_timesheet_manager:
            domain += ['&', '&', ('employee_id', '!=', current_employee.id), ('validated', '!=', True),
                     '|', '|', '|','|',
                         '&', '&', '&', '&', ('task_id.tl_employee_id', '=', current_employee.id),
                         ('prject_category_id', '=', project_work.id),
                         '|', '|', ('employee_id.emp_category.code', '!=', 'TTL'),
                              ('employee_id.emp_category.code', '=', None), ('employee_id.emp_category', '=', False),
                         ('id', 'not in', no_reviewer_ra_timesheet_ids),
                         ('id', 'not in', project_ra_timesheet_ids),

                         '&', ('project_id.emp_id', '=', current_employee.id),
                         '|', '|', ('id', 'in', pm_timesheet_ids), ('task_id.tl_employee_id', '=', False),
                         ('employee_id.emp_category.code', '=', 'TTL'),

                         '&', ('employee_id.parent_id', '=', current_employee.id),
                         '|', '|', ('prject_category_id', '!=', project_work.id),
                              '&', ('prject_category_id', '=', project_work.id), ('id', 'in', project_ra_timesheet_ids),
                              '&', '&', ('prject_category_id', '=', project_work.id), ('project_id.reviewer_id', '=', False),
                                   ('id', 'in', no_reviewer_ra_timesheet_ids),

                        ('employee_id.coach_id', '=', current_employee.id),


                         ('id', 'in', pm_reviewer_timesheet_ids)]
        return super(kw_account_analytic_line, self).read_group(domain, fields, groupby, offset=offset, limit=limit,orderby=orderby, lazy=lazy)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1)
        project_work = self.env['kw_project_category_master'].search([('mapped_to', '=', 'Project')], limit=1)
        # user_is_timesheet_manager = self.env.user.has_group('hr_timesheet.group_timesheet_manager')
        if self._context.get('filter_project_timesheet'):
            employee_projects = self.env['project.project'].search([('emp_id', '=', current_employee.id)])
            domain += [('project_id', '!=', False), ('project_id', 'in', employee_projects.ids)]

        if self._context.get('filter_ra_pm_reviewer_timesheet'):
            query = f'''select ana.id from account_analytic_line ana
                        join project_project pj on pj.id = ana.project_id
                        where pj.emp_id = ana.employee_id and pj.reviewer_id = {current_employee.id}::integer
                        '''
            self._cr.execute(query)
            query_result = self._cr.fetchall()
            pm_reviewer_timesheet_ids = [id_tuple[0] for id_tuple in query_result]

            query = f'''select ana.id from account_analytic_line ana
                        join project_task pt on pt.id = ana.task_id
                        where pt.tl_employee_id = ana.employee_id
                        '''
            self._cr.execute(query)
            query_result = self._cr.fetchall()
            pm_timesheet_ids = [id_tuple[0] for id_tuple in query_result]

            query = f'''select ana.id from account_analytic_line ana
                        join project_project pj on pj.id = ana.project_id
                        where pj.reviewer_id = ana.employee_id
                        '''
            self._cr.execute(query)
            query_result = self._cr.fetchall()
            project_ra_timesheet_ids = [id_tuple[0] for id_tuple in query_result]

            query = f'''select ana.id from account_analytic_line ana
                        join project_project pj on pj.id = ana.project_id
                        where pj.emp_id = ana.employee_id'''

            self._cr.execute(query)
            query_result = self._cr.fetchall()
            no_reviewer_ra_timesheet_ids = [id_tuple[0] for id_tuple in query_result]

            # if not user_is_timesheet_manager:
            domain += ['&', '&', ('employee_id', '!=', current_employee.id), ('validated', '!=', True),
                     '|', '|', '|','|',
                         '&', '&', '&', '&', ('task_id.tl_employee_id', '=', current_employee.id),
                         ('prject_category_id', '=', project_work.id),
                         '|', '|', ('employee_id.emp_category.code', '!=', 'TTL'),
                              ('employee_id.emp_category.code', '=', None), ('employee_id.emp_category', '=', False),
                         ('id', 'not in', no_reviewer_ra_timesheet_ids),
                         ('id', 'not in', project_ra_timesheet_ids),

                         '&', ('project_id.emp_id', '=', current_employee.id),
                         '|', '|', ('id', 'in', pm_timesheet_ids), ('task_id.tl_employee_id', '=', False),
                         ('employee_id.emp_category.code', '=', 'TTL'),

                         '&', ('employee_id.parent_id', '=', current_employee.id),
                         '|', '|', ('prject_category_id', '!=', project_work.id),
                              '&', ('prject_category_id', '=', project_work.id), ('id', 'in', project_ra_timesheet_ids),
                              '&', '&', ('prject_category_id', '=', project_work.id), ('project_id.reviewer_id', '=', False),
                                   ('id', 'in', no_reviewer_ra_timesheet_ids),

                        ('employee_id.coach_id', '=', current_employee.id),

                         ('id', 'in', pm_reviewer_timesheet_ids)]
        return super(kw_account_analytic_line,self).search_read(domain, fields, offset, limit, order)

    @api.multi
    def action_validate_timesheet(self):
        return {'type': 'ir.actions.act_window',
                'name': 'Validate Timesheet',
                'res_model': 'kw_timesheets_validate_wizard',
                'view_mode': 'form',
                'target':'new',
                }

   

    @api.model
    def check_pending_timesheet(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        if not current_employee or (not current_employee.enable_timesheet):
            return False, False
        else:
            current_date = date.today()

            current_week_monday = current_date - timedelta(days=current_date.weekday())
            current_week_friday = current_week_monday + timedelta(days=4)
            current_week_saturday = current_week_monday + timedelta(days=5)
            current_week_sunday = current_week_saturday + timedelta(days=1)

            previous_week_friday = current_week_friday - timedelta(weeks=1)
            employee_timesheet = False
            timesheet_date = False
            if current_date == current_week_monday:  # Monday (Check timesheet for friday)
                timesheet_date = previous_week_friday
            elif current_date in [current_week_saturday, current_week_sunday]:
                timesheet_date = current_week_friday
            else:
                timesheet_date = current_date - timedelta(days=1)
            # check whether employee was on leave or shift has holidays
            employee_shift = current_employee.resource_calendar_id
            if not employee_shift:
                employee_timesheet = self.env['account.analytic.line'].search(
                    [('date', '=', timesheet_date), ('employee_id', '=', current_employee.id)])
                if not employee_timesheet:
                    menu_id = self.env.ref('hr_timesheet.timesheet_menu_root').sudo().id
                    action_id = self.env.ref('hr_timesheet.act_hr_timesheet_line').sudo().id
                    return f'/web#action={action_id}&model=account.analytic.line&view_type=grid&menu_id={menu_id}',timesheet_date.strftime('%d-%b-%Y')
                else:
                    return False,False
            else:
                employee_shift_holiday = employee_shift.public_holidays.filtered(lambda r:r.date == timesheet_date)
                employee_on_leave = self.env['kw_daily_employee_attendance'].search(
                    [('attendance_recorded_date', '=', timesheet_date), ('leave_day_value', '=', 1),
                     ('employee_id', '=', current_employee.id)])
                if employee_on_leave or employee_shift_holiday:
                    return False, False
                else:
                    employee_timesheet = self.env['account.analytic.line'].search(
                        [('date', '=', timesheet_date), ('employee_id', '=', current_employee.id)])
                    if not employee_timesheet:
                        menu_id = self.env.ref('hr_timesheet.timesheet_menu_root').sudo().id
                        action_id = self.env.ref('hr_timesheet.act_hr_timesheet_line').sudo().id
                        return f'/web#action={action_id}&model=account.analytic.line&view_type=grid&menu_id={menu_id}',timesheet_date.strftime('%d-%b-%Y')
                    else:
                        return False,False

    @api.model
    def check_ra_pm_reviewer_pending_validatations(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        if not current_employee:
            return False, False  # ,False
        else:
            current_date = date.today()

            current_week_monday = current_date - timedelta(days=current_date.weekday())
            current_week_friday = current_week_monday + timedelta(days=4)
            current_week_saturday = current_week_monday + timedelta(days=5)
            current_week_sunday = current_week_saturday + timedelta(days=1)

            previous_week_friday = current_week_friday - timedelta(weeks=1)
            timesheet_date = False

            if current_date == current_week_monday:  # Monday (Check timesheet for friday)
                timesheet_date = previous_week_friday
            elif current_date in [current_week_saturday, current_week_sunday]:
                timesheet_date = current_week_friday
            else:
                timesheet_date = current_date - timedelta(days=1)

            query = f'''select ana.id from account_analytic_line ana
                        join project_project pj on pj.id = ana.project_id
                        where pj.emp_id = ana.employee_id and pj.reviewer_id = {current_employee.id}::integer
                        '''
            self._cr.execute(query)
            query_result = self._cr.fetchall()
            pm_reviewer_timesheet_ids = [id_tuple[0] for id_tuple in query_result]

            query = f'''select ana.id from account_analytic_line ana
                        join project_task pt on pt.id = ana.task_id
                        where pt.tl_employee_id = ana.employee_id
                        '''
            self._cr.execute(query)
            query_result = self._cr.fetchall()
            pm_timesheet_ids = [id_tuple[0] for id_tuple in query_result]

            query = f'''select ana.id from account_analytic_line ana
                        join project_project pj on pj.id = ana.project_id
                        where pj.reviewer_id = ana.employee_id
                        '''
            self._cr.execute(query)
            query_result = self._cr.fetchall()
            project_ra_timesheet_ids = [id_tuple[0] for id_tuple in query_result]

            query = f'''select ana.id from account_analytic_line ana
                        join project_project pj on pj.id = ana.project_id
                        where pj.emp_id = ana.employee_id'''

            self._cr.execute(query)
            query_result = self._cr.fetchall()
            no_reviewer_ra_timesheet_ids = [id_tuple[0] for id_tuple in query_result]

            project_work = self.env['kw_project_category_master'].search([('mapped_to', '=', 'Project')], limit=1)

            domain = ['&','&','&',('date','=',timesheet_date),('employee_id','!=',current_employee.id),('validated','!=',True),
                       '|', '|', '|',
                         '&', '&', '&', '&', ('task_id.tl_employee_id', '=', current_employee.id),
                         ('prject_category_id', '=', project_work.id),
                         '|', '|', ('employee_id.emp_category.code', '!=', 'TTL'),
                              ('employee_id.emp_category.code', '=', None), ('employee_id.emp_category', '=', False),
                         ('id', 'not in', no_reviewer_ra_timesheet_ids),
                         ('id', 'not in', project_ra_timesheet_ids),

                         '&', ('project_id.emp_id', '=', current_employee.id),
                         '|', '|', ('id', 'in', pm_timesheet_ids), ('task_id.tl_employee_id', '=', False),
                         ('employee_id.emp_category.code', '=', 'TTL'),

                         '&', ('employee_id.parent_id', '=', current_employee.id),
                         '|', '|', ('prject_category_id', '!=', project_work.id),
                              '&', ('prject_category_id', '=', project_work.id), ('id', 'in', project_ra_timesheet_ids),
                              '&', '&', ('prject_category_id', '=', project_work.id), ('project_id.reviewer_id', '=', False),
                                   ('id', 'in', no_reviewer_ra_timesheet_ids),


                         ('id', 'in', pm_reviewer_timesheet_ids)]

            to_validate_timesheets = self.env['account.analytic.line'].search(domain,limit=1)
            if to_validate_timesheets:
                menu_id = self.env.ref('hr_timesheet.timesheet_menu_root').sudo().id
                action_id = self.env.ref('kw_timesheets.kw_timesheets_validate_window_action').sudo().id
                # data = f'/web#action={action_id}&model=account.analytic.line&view_type=list&menu_id={menu_id}',timesheet_date.strftime('%d-%b-%Y')
                # return data
                return f'/web#action={action_id}&model=account.analytic.line&view_type=list&menu_id={menu_id}',timesheet_date.strftime('%d-%b-%Y')
            else:
                return False,False#,False

    @api.model
    def remind_one_day_timesheeet_to_employees(self):
        valid_timesheet_employees = self.env['hr.employee'].search(
            [('enable_timesheet', '=', True), ('active', '=', True)])

        current_date = date.today()
        current_week_monday = current_date - timedelta(days=current_date.weekday())

        current_week_friday = current_week_monday + timedelta(days=4)
        current_week_saturday = current_week_monday + timedelta(days=5)
        current_week_sunday = current_week_saturday + timedelta(days=1)

        previous_week_friday = current_week_friday - timedelta(weeks=1)

        if current_date == current_week_monday: # Monday (Check timesheet for friday)
            timesheet_date = previous_week_friday
        elif current_date in [current_week_saturday,current_week_sunday]: # Saturday and Sunday
            timesheet_date = current_week_friday
        else:
            timesheet_date = current_date - timedelta(days=1)

        already_filled_employees = self.env['account.analytic.line'].search(
            [('date', '=', timesheet_date), ('employee_id', 'in', valid_timesheet_employees.ids)]).mapped('employee_id')
        valid_timesheet_employees -= already_filled_employees

        employee_shifts = valid_timesheet_employees.mapped('resource_calendar_id')
        holiday_shift = employee_shifts.filtered(
            lambda r: r.public_holidays.filtered(lambda r: r.date == timesheet_date))
        valid_timesheet_employees -= valid_timesheet_employees.filtered(
            lambda r: r.resource_calendar_id in holiday_shift)
        leave_employees = self.env['kw_daily_employee_attendance'].search(
            [('attendance_recorded_date', '=', timesheet_date), ('leave_day_value', '=', 1),
             ('employee_id', 'in', valid_timesheet_employees.ids)]).mapped('employee_id')
        valid_timesheet_employees -= leave_employees
        for employee in valid_timesheet_employees:
            # employee_timesheet = self.env['account.analytic.line'].search([('date','=',timesheet_date),('employee_id','=',employee.id)])
            # if not employee_timesheet:
            self.timesheet_send_custom_mail(res_id=employee.id,
                                            notif_layout='kwantify_theme.csm_mail_notification_light',
                                            template_layout="kw_timesheets.timesheet_one_day_reminder_to_employee_mail_template",
                                            ctx_params={'timesheet_date': timesheet_date.strftime("%d-%b-%Y")},
                                            description="Timesheet")

    @api.model
    def remind_one_day_timesheeet_to_ra_pm_reviewer(self):
        project_work = self.env['kw_project_category_master'].search([('mapped_to','=','Project')],limit=1)
        current_date = date.today()

        current_week_monday = current_date - timedelta(days=current_date.weekday())

        current_week_friday = current_week_monday + timedelta(days=4)
        current_week_saturday = current_week_monday + timedelta(days=5)
        current_week_sunday = current_week_saturday + timedelta(days=1)

        previous_week_friday = current_week_friday - timedelta(weeks=1)

        if current_date == current_week_monday: # Monday (Check timesheet for friday)
            timesheet_date = previous_week_friday
        elif current_date in [current_week_saturday,current_week_sunday]:
            timesheet_date = current_week_friday
        else:
            timesheet_date = current_date - timedelta(days=1)

        query = f'''with employee as(select case
                                when ana.prject_category_id = {project_work.id} and pj.emp_id = ana.employee_id then pj.reviewer_id
                                when ana.prject_category_id = {project_work.id} then pj.emp_id
                                when ana.prject_category_id != {project_work.id} then emp.parent_id
                            end as validate_employee

                        from account_analytic_line ana
                        join project_project pj on ana.project_id = pj.id
                        join hr_employee emp on ana.employee_id = emp.id

                        where ana.date = '{timesheet_date.strftime("%Y-%m-%d")}' and ana.validated = false
                        group by validate_employee)
                        select validate_employee from employee join hr_employee a on employee.validate_employee = a.id
                        where a.parent_id is not null
                    '''
        self._cr.execute(query)
        query_result = self._cr.fetchall()

        timesheet_pending_employee_ids = [id_tuple[0] for id_tuple in query_result]

        for emp_id in timesheet_pending_employee_ids:
            self.timesheet_send_custom_mail(res_id=emp_id,
                                            notif_layout='kwantify_theme.csm_mail_notification_light',
                                            template_layout="kw_timesheets.timesheet_one_day_reminder_to_ra_pm_reviewer_template",
                                            ctx_params={'timesheet_date':timesheet_date.strftime("%d-%b-%Y")},
                                            description="Timesheet")

    @api.depends('prject_category_id')
    def _compute_if_project_activity(self):
        for analytic_line in self:
            if analytic_line.prject_category_id:

                if analytic_line.prject_category_id.mapped_to == 'Project':
                    analytic_line.is_project_activity = True

                if analytic_line.prject_category_id.mapped_to == 'Opportunity':
                    analytic_line.is_opportunity_activity = True

                if analytic_line.prject_category_id.mapped_to == 'Support':
                    analytic_line.is_admin_activity = True

    @api.onchange('prject_category_id')
    def onchange_prj_category_id(self):
        if not self.prject_category_id:
            self.date = date.today()
        self.project_id = False
        self.module_id = False
        self.task_id = False
        self.parent_task_id = False
        self.crm_lead_id = False

        current_employee = self.env['hr.employee'].search([('user_id','=',self._uid)],limit=1)
        department = self.env['hr.department']
        department |= current_employee.department_id
        department |= current_employee.division
        department |= current_employee.section
        department |= current_employee.practise

        # project_list = []

        project_domain = [('id','=',0)]
        task_domain = [('id','=',0)]
        parent_task_domain = [('id','=',0)]
        # if not self.prject_category_id:
        #     project_rec = False
        # else:

        if self.prject_category_id:
            if self.prject_category_id.mapped_to == 'Project':
                project_rec = self.env['project.project'].sudo().search(
                    ['&',('prject_category_id', 'in', self.prject_category_id.ids),
                        '|',
                            ('resource_id.emp_id','in',self.env.user.employee_ids.ids),
                            '&',('emp_id','!=',False),('emp_id','=',current_employee.id)])

                self.show_oppertunity_mapped = False
                self.hide_tagged_to = False
                project_domain = [('id', 'in', project_rec.ids)]

                # parent_tasks = self.env['project.task'].sudo().search(
                #     ['&', '&', ('mapped_to', 'in', department.ids), ('project_id', 'in', project_rec.ids),
                #      ('prject_category_id', '=', self.prject_category_id.id),('assigned_employee_id.user_id','=',self.env.user.id)])
                # parent_task_domain = [('id', 'in', parent_tasks.mapped('parent_id.id'))]
                # # tasks = self.env['project.task'].sudo().search(
                # #     ['&', '&', ('mapped_to', 'in', department.ids), ('project_id', 'in', project_rec.ids),
                # #      ('prject_category_id', '=', self.prject_category_id.id)])
                # task_domain = [('parent_id', 'in', parent_tasks.mapped('parent_id.id')),('task_status','not in',['Completed'])]

            if self.prject_category_id.mapped_to == 'Opportunity':
                project_rec = self.env['project.project'].sudo().search(
                    [('prject_category_id', 'in', self.prject_category_id.ids)])
                project_domain = [('id', 'in', project_rec.ids)]
                if project_rec:
                    self.show_oppertunity_mapped = True
                    self.hide_tagged_to = True
                    self.project_id = project_rec[0].id

                    tasks = self.env['project.task'].sudo().search(
                        [('mapped_to', 'in', department.ids), ('project_id', 'in', project_rec.ids),
                         ('prject_category_id', '=', self.prject_category_id.id)])
                    task_domain = [('id', 'in', tasks.ids)]

            if self.prject_category_id.mapped_to == 'Support':
                project_rec = self.env['project.project'].sudo().search([('prject_category_id', 'in', self.prject_category_id.ids)])
                project_domain = [('id', 'in', project_rec.ids)]
                if project_rec:
                    self.hide_tagged_to = True
                    self.show_oppertunity_mapped = False
                    self.project_id = project_rec[0].id

                    tasks = self.env['project.task'].sudo().search(
                        [('mapped_to', 'in', department.ids), ('project_id', 'in', project_rec.ids),
                         ('prject_category_id', '=', self.prject_category_id.id)])
                    task_domain = [('id', 'in', tasks.ids)]
        domain = {'domain': {'project_id': project_domain,'parent_task_id':parent_task_domain,'task_id':task_domain}}
        return domain

        # if project_rec:
        #     for rec in project_rec:
        #         project_list.append(rec.id)

        #     if self.prject_category_id.mapped_to == 'Support':
        #         self.project_id = project_list[0] if len(project_list) > 0 else False
        #         self.hide_tagged_to = True
        #         self.show_oppertunity_mapped = False
        #     elif self.prject_category_id.mapped_to == 'Opportunity':
        #         self.project_id = project_list[0] if len(project_list) > 0 else False
        #         self.show_oppertunity_mapped = True
        #         self.hide_tagged_to = True
        #     else:
        #         self.show_oppertunity_mapped = False
        #         self.hide_tagged_to = False

    @api.onchange('project_id', 'date')
    def set_module_data(self):
        self.module_id = False
        self.task_id = False
        self.parent_task_id = False
        module_domain = [('id','=',0)]
        task_domain = [('id','=',0)]
        parent_task_domain = [('id','=',0)]

        if self.project_id:
            module_domain = [('project_id','=',self.project_id.id)]
            current_date = datetime.now().date()
            current_employee = self.env['hr.employee'].search([('user_id','=',self._uid)],limit=1)
            department = self.env['hr.department']
            department |= current_employee.department_id
            department |= current_employee.division
            department |= current_employee.section
            department |= current_employee.practise

            if self.prject_category_id.mapped_to == 'Project':
                tasks = self.env['project.task'].sudo().search([('mapped_to', 'in', department.ids),
                                                                ('project_id', '=', self.project_id.id),
                                                                ('prject_category_id', '=', self.prject_category_id.id),
                                                                ('assigned_employee_id.user_id','=',self.env.user.id),('task_status','not in',['Completed'])])
            else:
                tasks = self.env['project.task'].sudo().search([('mapped_to', 'in', department.ids),
                                                                ('project_id', '=', self.project_id.id),
                                                                ('prject_category_id', '=', self.prject_category_id.id)])
            task_domain = [('id','in',tasks.ids)]
            # print(task_domain)
            parent_task_domain = [('id','in',tasks.mapped('parent_id').ids)]
            # print(parent_task_domain)
        return {
            'domain':{'module_id':module_domain,'task_id':task_domain,'parent_task_id':parent_task_domain}
        }

    @api.onchange('module_id', 'date')
    def get_module_domain(self):
        self.parent_task_id = False
        self.task_id = False
        # current_employee = self.env['hr.employee'].search([('user_id','=',self._uid)],limit=1)
        # department = self.env['hr.department']
        # current_date = datetime.now().date()
        # department |= current_employee.department_id
        # department |= current_employee.division
        # department |= current_employee.section
        # department |= current_employee.practise

        # domain = [('id','=',0)]
        # if self.prject_category_id.mapped_to == 'Project':
        #     domain = [('prject_category_id', '=', self.prject_category_id.id),
        #               ('mapped_to', 'in', department.ids)]
        # if self.prject_category_id.mapped_to != 'Project':
        #     domain = [('prject_category_id', '=', self.prject_category_id.id),
        #               ('mapped_to', 'in', department.ids)]

        # if self.project_id:
        #     domain.append(('project_id', '=', self.project_id.id))

        # # if self.module_id:
        # #     domain.append(('module_id','=',self.module_id.id))
        #             #   ('prject_category_id', '=', self.prject_category_id.id),
        #             #   ('mapped_to', 'in', department.ids),
        #             #   ]
        # return {
        #     'domain':{'task_id':domain}
        # }

    @api.onchange('parent_task_id', 'date')
    def get_task_domain(self):
        self.task_id = False
        module_domain = [('id','=',0)]
        task_domain = [('id','=',0)]

        if self.project_id:
            module_domain = [('project_id','=',self.project_id.id)]
            current_date = datetime.now().date()
            current_employee = self.env['hr.employee'].search([('user_id','=',self._uid)],limit=1)
            department = self.env['hr.department']
            department |= current_employee.department_id
            department |= current_employee.division
            department |= current_employee.section
            department |= current_employee.practise

            if self.prject_category_id.mapped_to == 'Project':
                tasks = self.env['project.task'].sudo().search([('mapped_to', 'in', department.ids),
                                                                ('project_id', '=', self.project_id.id),
                                                                ('prject_category_id', '=', self.prject_category_id.id),
                                                                ('parent_id','=',self.parent_task_id.id),
                                                                ('assigned_employee_id.user_id','=',self.env.user.id),('task_status','not in',['Completed'])])
            else:
                tasks = self.env['project.task'].sudo().search([('mapped_to', 'in', department.ids),
                                                                ('project_id', '=', self.project_id.id),
                                                                ('prject_category_id', '=', self.prject_category_id.id)])
            task_domain = [('id','in',tasks.ids)]
        return {
            'domain':{'module_id':module_domain,'task_id':task_domain}
        }

        
    # @api.onchange('project_id', 'prject_category_id')
    # def onchange_project_id(self):
    #     department = self.env['hr.department']
    #     department |= self.env.user.employee_ids.department_id
    #     department |= self.env.user.employee_ids.division
    #     department |= self.env.user.employee_ids.section
    #     department |= self.env.user.employee_ids.practise

    #     project_rec = self.env['project.task'].sudo().search(
    #         ['&',
    #          '&', ('mapped_to', 'in', department.ids), ('project_id', '=', self.project_id.id),
    #          ('prject_category_id', '=', self.prject_category_id.id)])
    #     return {'domain': {'task_id': [('id', 'in', project_rec.ids)]}}

    @api.constrains('unit_amount')
    def _check_hour(self):
        for rec in self:
            date_records = self.env['account.analytic.line'].sudo().search(
                [('date', '=', rec.date), ('employee_id', '=', self.env.user.employee_ids.id)]).mapped('unit_amount')
            if sum(date_records) > 24:
                raise ValidationError('You are not allowed to enter more than 24 hours for a day in duration field.')
            if rec.date > date.today():
                raise ValidationError("You are not allowed to add a task for future date.")
            if rec.unit_amount <= 0:
                raise ValidationError("Time Spent should be more than zero.")

    @api.constrains('date','unit_amount')
    def validate_current_date_timesheet(self):
        current_date = date.today()
        current_time = datetime.now()
        daily_employee_attendance = self.env['kw_daily_employee_attendance']
        for timesheet in self:
            if timesheet.date == current_date:
                employee = timesheet.employee_id

                employee_timezone = pytz.timezone(employee.tz or employee.resource_calendar_id.tz or 'UTC')
                current_time_as_emp_timezone = current_time.astimezone(employee_timezone).replace(tzinfo=None)

                employee_shift_in_float_time = daily_employee_attendance._get_employee_shift(employee, current_date)[4]
                employee_shift_in_date_time = datetime.combine(current_date, resource.float_to_time(employee_shift_in_float_time))

                if employee_shift_in_date_time > current_time_as_emp_timezone:
                    raise ValidationError("You are not allowed to enter your timesheet before shift in time.")

                current_date_timesheet = self.search([('date','=',current_date),('employee_id','=',employee.id)]) - timesheet
                total_timesheet_time = sum(current_date_timesheet.mapped('unit_amount')) or 0.0

                max_available_hours = (current_time_as_emp_timezone - employee_shift_in_date_time).seconds / 3600
                availability_time = max_available_hours - total_timesheet_time
                expected_login_time = current_time_as_emp_timezone - timedelta(hours=total_timesheet_time+timesheet.unit_amount)
                if availability_time < timesheet.unit_amount:
                    formatted_hour = '{0:02.0f}:{1:02.0f}'.format(*divmod(availability_time * 60, 60))
                    # raise ValidationError(f"You can't enter timesheet more than {formatted_hour} Hour(s) as per your shift in time and Timesheets.")
                    raise ValidationError(f"""It’s just {'{0:02.0f}:{1:02.0f}'.format(*divmod(max_available_hours * 60, 60))} hrs from your shift start time.\n
                                        Really! Have you logged in at {expected_login_time.strftime('%I:%M %p')}?""")
            if timesheet.prject_category_id.mapped_to == 'Project':
                task_timesheet = self.env['account.analytic.line'].sudo().search(
                    [('task_id', '=', timesheet.task_id.id)]) - self
                total_time_spent = sum(task_timesheet.mapped('unit_amount'))
                # remaining_hours = timesheet.task_id.planning_hour - total_time_spent
                remaining_hours = timesheet.task_id.parent_id.planned_hours - total_time_spent
                if remaining_hours <= 0.0:
                    raise ValidationError(f'Cannot fill timesheet for {timesheet.task_id.name} activity as planned hours is over.')
                else:
                    new_remaining_hours = remaining_hours - timesheet.unit_amount
                    if new_remaining_hours < 0.0:
                        raise ValidationError(f'Only {round(remaining_hours, 2)} hours are left for selected {timesheet.task_id.name}.\n'
                                              f'Cannot fill more than {round(remaining_hours, 2)} hours')

    # def get_current_week(self, date):
    #     one_day = timedelta(days=1)
    #     date = date
    #     day_idx = (date.weekday()) % 7
    #     sunday = date - timedelta(days=day_idx)
    #     date = sunday
    #     for n in range(7):
    #         yield date
    #         date += one_day

    """Timesheet : Timesheet Auto Validate Scheduler
    it will execute in last Day of the month"""

    # @api.model
    # def action_timesheet_auto_validate_scheduler(self):
    #     year = datetime.today().year
    #     month = datetime.today().month
    #     day = datetime.today().day
    #     dt_today = str(year) + str(month) + str(day)
    #     last_sunday = max(week[-1] for week in calendar.monthcalendar(year, month))
    #     dt_last_sunday = str(year) + str(month) + str(last_sunday)
    #     days_in_month = calendar.monthrange(year, month)[1]

    #     notif_layout = "kwantify_theme.csm_mail_notification_light"
    #     if day == days_in_month:
    #         """find 26th of next month on last day of month"""f
    #         prvs_month = month - 1 or 12
    #         current_month = month
    #         next_year = year if month < 12 else year + 1
    #         dt_26th_prvs_month = datetime.strptime('{}-{}-{:2}'.format(next_year, prvs_month, 26), '%Y-%m-%d')
    #         dt_25th_current_month = datetime.strptime('{}-{}-{:2}'.format(next_year, current_month, 25), '%Y-%m-%d')

    #     """find last sunday of next month"""
    #     next_month = month  if month < 12 else 1
    #     next_year = year if month < 12 else year + 1
    #     last_sunday_next_month = max(week[-1] for week in calendar.monthcalendar(next_year, next_month))

    #     dt_last_sunday_next_month = datetime.strptime(
    #         '{}-{}-{:2} {}:{}:{}'.format(next_year, next_month, last_sunday_next_month, 5, 0, 0),
    #         '%Y-%m-%d %H:%M:%S')  # it is in UTC
    #     last_day_in_month = calendar.monthrange(year, month)[1]

    #     """ Auto validate on last day of the month """
    #     if day == last_day_in_month:
    #         analytic_rec = self.env['account.analytic.line'].sudo().search(
    #             [('validated', '=', False), ('date', '<=', dt_25th_current_month)])
    #         analytic_rec.write({"validated": True})

    #         """ Mail send after auto validate """
    #         employee_list = analytic_rec.mapped('employee_id')
    #         for emp in employee_list:
    #             timesheet_dates = set(analytic_rec.filtered(lambda r: r.employee_id == emp).mapped('date'))
    #             extra_params = {'prvs_mnth_26': dt_26th_prvs_month,
    #                             'current_mnth_25': dt_25th_current_month,
    #                             'to_mail': emp.work_email,
    #                             'emp_name': emp.name}
    #             self.env['account.analytic.line'].timesheet_send_custom_mail(res_id=emp.id,
    #                                                                          notif_layout='kwantify_theme.csm_mail_notification_light',
    #                                                                          template_layout="kw_timesheets.kw_timesheet_auto_validate_mail_template",
    #                                                                          ctx_params=extra_params,
    #                                                                          description="Timesheet")

    #         """update cron next execution time"""
    #         # validate_scheduler = self.env.ref('kw_timesheets.auto_validate_scheduler_for_timesheet')
    #         # validate_scheduler.sudo().write({'nextcall': dt_last_sunday_next_month})

    """Timesheet : Timesheet Paycut and EL reminder mail scheduler
    It will execute from 26th to month end"""

    @api.model
    def action_timesheet_el_paycut_mail_scheduler(self):
        year = datetime.today().year
        month = datetime.today().month
        day = datetime.today().day
        # today = str(year) + str(month) + str(day)
        """monthrange(year, month) :- This function returns two integers,
        first, the starting day number of week(0 as monday) ,
        second, the number of days in the month"""
        days_in_month = calendar.monthrange(year, month)[1]

        if 26 <= day <= days_in_month:
            timesheet_payroll_ids = self.env['kw_timesheet_payroll_report'].sudo().search(
                ['&', ('attendance_year', '=', year), ('attendance_month', '=', str(month).zfill(2)), '|',
                 ('timesheet_el_days', '>', 0), ('timesheet_paycut_days', '>', 0),
                 ('employee_id.enable_timesheet', '=', True)])
            # timesheet_payroll_ids = self.env['kw_timesheet_payroll_report'].sudo().search(
            #     ['&',('attendance_year', '=', year), ('attendance_month', '=', str(month).zfill(2))])
            # emps = timesheet_payroll_ids.filtered(lambda x: (x.timesheet_el_days > 0 or x.timesheet_paycut_days > 0) and x.employee_id.enable_timesheet).sorted(key=lambda r:r.employee_id.name)
            el_template_id = self.env.ref('kw_timesheets.kw_timesheet_reminder_payroll_el_paycut_mail_template')
            # trim_required_effort_hour, trim_num_actual_effort, trim_total_effort_hr, trim_timesheet_el_days, trim_timesheet_paycut_days = '', '', '', '', ''

            formatNumber = lambda n: n if n % 1 else int(n)
            emp_list = []
            for emp in timesheet_payroll_ids:
                trim_required_effort_hour = formatNumber(emp.required_effort_hour)
                trim_num_actual_effort = float("%.0f" %emp.num_actual_effort)
                trim_total_effort_hr = float("%.0f" %emp.total_effort)
                trim_timesheet_el_days = formatNumber(emp.timesheet_el_days)
                trim_timesheet_paycut_days = formatNumber(emp.timesheet_paycut_days)
                if trim_total_effort_hr < 0:
                    emp_list.append(f'{emp.employee_id.emp_code}:{emp.employee_id.name}:{trim_required_effort_hour}:{trim_num_actual_effort}:{trim_total_effort_hr}:{trim_timesheet_el_days}:{trim_timesheet_paycut_days}')

                    el_template_id.with_context(trim_required_effort_hour=trim_required_effort_hour,
                                                trim_num_actual_effort=trim_num_actual_effort,
                                                trim_total_effort_hr=abs(trim_total_effort_hr),
                                                trim_timesheet_el_days=trim_timesheet_el_days,
                                                trim_timesheet_paycut_days=trim_timesheet_paycut_days,
                                                db_month=calendar.month_name[month]).send_mail(emp.id,
                                                                                           notif_layout="kwantify_theme.csm_mail_notification_light")

            if emp_list:
                el_hr_template_id = self.env.ref('kw_timesheets.kw_timesheet_hr_reminder_el_paycut_mail_template')
                el_hr_template_id.with_context(emp_list=emp_list, db_month=calendar.month_name[month]).send_mail(emp.id, notif_layout="kwantify_theme.csm_mail_notification_light")

            self.env.user.notify_success("Mail sent successfully.")

    """ Timesheet : Reminder Email to Employee
    it will execute every Thursday, Friday, Saturday and Sunday"""

    # @api.model
    # def action_timesheet_reminder_to_employee(self):
    #     dt_weekday = datetime.today().weekday()
    #     if dt_weekday in [3, 4, 5, 6]:
    #         current_week_date_list = []
    #         dt_list = []
    #         current_date = date.today()

    #         for d in self.get_current_week(datetime.today()):
    #             current_week_date_list.append(d)

    #         attendance_records = self.env['kw_daily_employee_attendance'].sudo().search(
    #             [('check_in', '!=', False), ('day_status', 'in', ['0', '3']), ('is_valid_working_day', '=', True),
    #              ('attendance_recorded_date', 'in', current_week_date_list),
    #              ('attendance_recorded_date', '!=', current_date), ('leave_day_value', '<', 1)])

    #         attendance_employee = attendance_records.filtered(lambda r: r.employee_id.enable_timesheet).mapped('employee_id')

    #         timesheet_records = self.env['account.analytic.line'].sudo().search(
    #             [('employee_id', 'in', attendance_employee.ids),
    #              ('date', 'in', current_week_date_list), ('date', '!=', current_date)])
    #         timesheet_emp_rec_id = timesheet_records[0].id
    #         for employee in attendance_employee:
    #             # if employee.employement_type.code == 'P':
    #             if employee.enable_timesheet:
    #                 attdance_dates = set(attendance_records.filtered(lambda r: r.employee_id == employee).mapped('attendance_recorded_date'))
    #                 timesheet_emp_rec = timesheet_records.filtered(lambda r: r.employee_id == employee)
    #                 timesheet_dates = set(timesheet_records.filtered(lambda r: r.employee_id == employee).mapped('date'))

    #                 not_filled_date = attdance_dates - timesheet_dates
    #                 dt_list.clear()
    #                 for dt in not_filled_date:
    #                     dt_list.append(dt.strftime("%d-%B-%Y"))
    #                 dt_list.sort(key=lambda date: datetime.strptime(date, "%d-%B-%Y"))
    #                 if len(dt_list) > 0:
    #                     extra_params = {'to_mail': employee.work_email,
    #                                     'emp_name': employee.name,
    #                                     'list_date': dt_list}

    #                     self.env['account.analytic.line'].timesheet_send_custom_mail(res_id=timesheet_emp_rec_id,
    #                                                                                  notif_layout='kwantify_theme.csm_mail_notification_light',
    #                                                                                  template_layout="kw_timesheets.kw_timesheet_reminder_mail_to_employee_mail_template",
    #                                                                                  ctx_params=extra_params,
    #                                                                                  description="Timesheet")

    #     self.env.user.notify_success("Mail sent successfully.")

    # """ Timesheet : Reminder Email to RA """

    # @api.model
    # def action_timesheet_reminder_to_ra_scheduler(self):
    #     dt_weekday = datetime.today().weekday()

    #     if dt_weekday in [0]:
    #         users = self.env.ref('kw_employee.group_hr_ra').users.ids

    #         emp_recs = self.env['hr.employee'].sudo().search([('user_id', 'in', users), ('enable_timesheet', '=', True)])

    #         for emp_rec in emp_recs:
    #             if emp_rec:
    #                 extra_params = {
    #                     'to_mail': emp_rec.work_email,
    #                     'emp_name': emp_rec.name
    #                 }
    #                 self.env['account.analytic.line'].timesheet_send_custom_mail(res_id=emp_rec.id,
    #                                                                              notif_layout='kwantify_theme.csm_mail_notification_light',
    #                                                                              template_layout="kw_timesheets.kw_timesheet_reminder_mail_to_ra_mail_template",
    #                                                                              ctx_params=extra_params,
    #                                                                              description="Timesheet")
    #         # today = datetime.today()
    #         # next_monday = (today + timedelta(days=-today.weekday(), weeks=1)).replace(hour=10, minute=15)
    #         # validate_scheduler = self.env.ref('kw_timesheets.reminder_to_ra_for_timesheet')
    #         # validate_scheduler.sudo().write({'nextcall': next_monday})

    #     self.env.user.notify_success("Mail sent successfully.")
    ''' Synchronization of Timesheet data to kwantify v5 '''
    @api.model
    def create(self, vals):
        res = super(kw_account_analytic_line, self).create(vals)
        if res.prject_category_id.mapped_to == 'Project':
            if res.task_status == 'completed':
                res.task_id.write({'task_status':'Completed'})
            else:
                res.task_id.write({'task_status':'In Progress'})
        else:
            res.task_id.write({'task_status':'In Progress'})
        return res
    
    
    @api.model
    def syncTimesheetData(self):
        header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        parameterurl = self.env['ir.config_parameter'].sudo().get_param('kwantify_common_api')
        analytic_records = self.env['account.analytic.line'].sudo().search(
            [('sync_status', '=', False), ('validated', '=', True)])
        if not analytic_records:
            return True
        TimeSheetData = []

        # for _ in range(int((len(analytic_records)/100) + 1)):
        #     analytic_records_limit = self.env['account.analytic.line'].sudo().search([('sync_status', '=', False),('validated','=',True)], limit=100)
        for record in analytic_records:
            analytic_dict = {"ActivityId": record.task_id.kw_id,
                             "EmployeeId": record.employee_id.kw_id,
                             "Date": str(record.date),
                             "EffortHour": record.unit_amount,
                             "Description": str(record.name),
                             "ProjectId": record.project_id.kw_id,
                             "AutoId": record.id
                             }

            TimeSheetData.append(analytic_dict)

        timesheet_dict = {"TimeSheetData": TimeSheetData}

        timesheeturl = parameterurl + '/TimeSheet_ProjectTaskUpdate'

        resp = requests.post(timesheeturl, headers=header, data=json.dumps(timesheet_dict))

        j_data = json.dumps(resp.json())
        json_record = json.loads(j_data)

        if json_record[0]['outMSg'] == "SUCCESS":
            query = f"UPDATE account_analytic_line SET sync_status=true WHERE id in ({analytic_records.ids});"
            self._cr.execute(query)
            # analytic_records.write({'sync_status': True})

            self.env.user.notify_success(message='Timesheet data synced successfully')

        self.env['kw_kwantify_integration_log'].sudo().create({'name': 'Timesheet Sync Data',
                                                               'new_record_log': timesheet_dict,
                                                               'request_params': timesheeturl,
                                                               'response_result': resp.json()
                                                               })
