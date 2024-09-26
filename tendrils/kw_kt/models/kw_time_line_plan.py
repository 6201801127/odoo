from odoo import models, fields, api
import pytz
from datetime import datetime, timedelta, date, time
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from kw_utility_tools import kw_validations
import pytz


class kw_time_line_plan(models.Model):
    _name = "kw_time_line_plan"
    _description = "KT Plan"
    _rec_name = 'project_id'

    @api.model
    def _get_time_list(self):
        dt = datetime.now()
        start_loop = dt.replace(hour=7, minute=45, second=0, microsecond=0)
        end_loop = dt.replace(hour=22, minute=0, second=0, microsecond=0)
        time_list = []
        while start_loop < end_loop:
            start_loop = (start_loop + relativedelta(minutes=+15))
            time_list.append((start_loop.strftime('%H:%M:%S'),
                              start_loop.strftime('%I:%M %p')))
        return time_list

    @api.multi
    def unlink(self):
        # print('UNLINK')
        for rec in self:
            if rec.kt_status == 'Approved':
                raise ValidationError('You cannot delete record')
        return super(kw_time_line_plan, self).unlink()

    # @api.model
    # def _domain_get_ids(self,config=False):
    #     if self._context.get('default_kt_view_id',False):
    #         kt_view_rec = self.env['kw_kt_view'].browse(int(self._context.get('default_kt_view_id')))
    #         emp_record = kt_view_rec.applicant_id

    #     elif 'active_id' and 'active_model' in self._context and self._context['active_model']=="kw_kt_view":
    #         print("active model and active id are",self._context['active_id'],self._context['active_model'])
    #         kw_kt_view_id = self._context.get('active_id',False)
    #         rec = self.env['kw_kt_view'].browse(int(kw_kt_view_id))
    #         emp_record = self.env['hr.employee'].sudo().search([('user_id', '=', rec.create_uid.id)]) 
    #     else:
    #         emp_record = self.env.user.employee_ids

    #     kt_rec = self.env['kw_kt_view'].sudo().search([('applicant_id','=',emp_record.id),('state','=','Applied')])
    #     kt_plan_record = self.env['kw_kt_plan_config'].sudo().search([('applicant_id','=',emp_record.id),('kt_view_id','=',kt_rec.id)])
    #     if config:
    #         result = kt_plan_record
    #     else:
    #         project_ids =  kt_plan_record.tag_kt_ids.mapped('project_id')
    #         result = [('id', 'in', project_ids.ids)]
    #     return result

    project_id = fields.Many2one('project.project', string="Project Name")

    employee_ids = fields.Many2many('hr.employee', 'kw_timeline_plan_employee_rel', string="Attendees",
                                    ondelete='cascade', required=True, domain="[('user_id','!=',uid)]")
    kt_date = fields.Date(string='Scheduled Date', required=True)
    start_time = fields.Selection(string='Start Time', selection='_get_time_list', required=True)
    end_time = fields.Selection(string='End Time', selection='_get_time_list', required=True)
    kt_view_id = fields.Many2one('kw_kt_view', string="KT view id", ondelete='cascade')
    document_attach = fields.Binary(string="Document", attachment=True)
    doc_file_name = fields.Char(string="Document Name")
    description = fields.Text(string='Description')
    # prj_document_ids = fields.One2many('kw_project_document','time_line_plan_id', string="Project Document")
    kt_status = fields.Char(string="KT Status", compute="_kt_status")
    # kt_doc = fields.Char(string="KT DOC",compute = "_kt_doc")
    # is_prj_document_submit = fields.Boolean(string="Is Project Document Submit",compute="_compute_prj_document")
    code = fields.Char(string="Reference No.", default="New", readonly="1")
    status = fields.Selection(string="Status", selection=[('pending', 'Pending'), ('completed', 'Completed')],
                              required=True, default="pending")
    kt_type = fields.Selection(string="Type",
                               selection=[('project', 'Current Project'), ('other_project', 'Other Project'),
                                          ('others', 'Administrative Activities')], required=True,
                               default='project')
    activities = fields.Char(string="Activities")
    check_state = fields.Boolean(string="Check State", default=False)
    check_document = fields.Boolean(string="Check Document", compute='check_compute_document', default=False)

    @api.multi
    def check_compute_document(self):
        for record in self:
            if record.kt_view_id:
                if record.status == 'pending' and record.kt_view_id.state in ['Draft', 'Applied']:
                    record.check_document = True
                    # print(" record.check_documen", record.check_document)
                else:
                    record.check_document = False
            else:
                record.check_document = True

    @api.onchange('kt_type')
    def onchange_kt_type(self):
        self.activities = False
        self.project_id = False
        return_ids = False
        if self.kt_type == 'project':
            project_records = self.env['kw_project_resource_tagging']
            if self.env.user.has_group('kw_employee.group_hr_ra') \
                    and self.kt_view_id \
                    and self.kt_view_id.applicant_id.id != self.env.user.employee_ids.id:
                filter_domain = [('emp_id', '=', self.kt_view_id.applicant_id.id)]
            else:
                filter_domain = [('emp_id', '=', self.env.user.employee_ids.id)]

            project_ids = project_records.sudo().search(filter_domain)
            return_ids = project_ids.filtered(lambda r: r.project_id != False).mapped('project_id')
            return {'domain': {'project_id': [('id', 'in', return_ids.ids)]}}
        if self.kt_type == 'other_project':
            prj_list = []
            query = f"select a.project_id from kw_time_line_plan a join kw_timeline_plan_employee_rel b on a.id=b.kw_time_line_plan_id where b.hr_employee_id = {self.env.user.employee_ids.id} union select id from kw_project_resource_tagging where emp_id = {self.env.user.employee_ids.id}"
            # query = f"select a.project_id from kw_time_line_plan a join kw_timeline_plan_employee_rel b on a.id=b.kw_time_line_plan_id where b.hr_employee_id = {20} union select project_id from kw_project_resource_tagging where emp_id = {20}"
            self._cr.execute(query)
            kt_project_data =  self._cr.fetchall()
            prj_list = [project[0] for project in kt_project_data]
            # print("prj_list=",prj_list)
            return {'domain': {'project_id': [('id', 'in', prj_list)]}}

    @api.model
    def create(self, values):
        values['code'] = self.env['ir.sequence'].next_by_code('kt_seq') or 'New'
        new_record = super(kw_time_line_plan, self).create(values)
        if new_record.kt_view_id.state =='Approved' or new_record.kt_view_id.state =='Scheduled':
            raise ValidationError("You can not add a new KT as it is already approved")
        return new_record


    # @api.onchange('kt_date')
    # def onchange_kt_date(self):
    #     # print('kt date==========',self.kt_date)
    #     # print('current date==========',date.today())
    #     if self.kt_date and self.kt_date < date.today():
    #         raise ValidationError("You can not choose back date .")

    @api.onchange('status')
    def onchange_status(self):
        if self.status == 'completed' and not self.document_attach:
            raise ValidationError("You can not complete KT before uploading document .")

    # @api.constrains('status', 'kt_date', 'end_time', 'document_attach', 'start_time')
    # def val_status(self):
    #     user_tz = pytz.timezone(self.env.user.tz) if self.env.user.tz else pytz.utc
    #     curr_datetime = datetime.now(tz=user_tz).replace(tzinfo=None)
    #     curr_time = curr_datetime.strftime("%H:%M:%S")
    #     for rec in self:
    #         date_time = datetime.strptime(rec.kt_date.strftime("%Y-%m-%d") + ' ' + rec.end_time, "%Y-%m-%d %H:%M:%S")
    #         if rec.kt_date == date.today():
    #             if self.kt_view_id.state != 'Approved' :
    #                 if rec.end_time < curr_time or rec.start_time < curr_time:
    #                     raise ValidationError("You can not choose back Time .")
    #         if rec.status == 'completed' and curr_datetime < date_time:
    #             raise ValidationError("You can not complete KT before KT date .")
    #         elif rec.status == 'completed' and not rec.document_attach:
    #             raise ValidationError("You can not complete KT before uploading document .")

    @api.constrains('document_attach', )
    def onchange_document_attach(self):
        for rec in self:
            doc = rec.document_attach
            rec.status = 'completed' if doc else 'pending'

        # max_date_time = max_date_records.mapped(lambda r:datetime.strptime(r.kt_date.strftime("%Y-%m-%d") + ' ' + r.end_time, "%Y-%m-%d %H:%M:%S"))
        # if kt.state == 'Approved' and curr_datetime > max_date_time: 

    # @api.depends('description')
    # @api.multi
    # def _compute_prj_document(self):
    #     for record in self:
    #         if record.prj_document_ids:
    #             print("PRJ DOCUMENT IDS===========",record.prj_document_ids)
    #             record.is_prj_document_submit = True

    @api.constrains('start_time', 'end_time')
    def val_time(self):
        for rec in self:
            if rec.start_time == rec.end_time:
                raise ValidationError("Start Time and End Time can not be same")
            if rec.start_time > rec.end_time:
                raise ValidationError("Start Time can not be greater than End Time")

    @api.multi
    def _kt_status(self):
        for record in self:
            if record.kt_view_id.state == "Applied":
                record.kt_status = 'Applied'
            if record.kt_view_id.state == "Approved":
                record.kt_status = 'Approved'
                # for rec in record.employee_ids:
                #     template_id = self.env.ref('kw_kt.kw_kt_ra_approved_mail_template')
                #     template_id.with_context(mailto=rec.work_email,mailcc=rec.parent_id.work_email,emp_name=rec.name,applicant=record.kt_view_id.applicant_id.name).send_mail(record.id, notif_layout='kwantify_theme.csm_mail_notification_light')

            # if record.kt_view_id.kt_end == "upload":
            #     record.kt_status = 'Upload'
            # for rec in record.employee_ids:
            #     template_id = self.env.ref('kw_kt.kw_kt_ra_approved_mail_template')
            #     template_id.with_context(mailto=rec.work_email,emp_name=rec.name,applicant=record.kt_view_id.applicant_id.name).send_mail(record.id, notif_layout='kwantify_theme.csm_mail_notification_light')

            #     template_id = self.env.ref('kw_kt.kw_kt_ra_approved_ra_mail_template')
            #     template_id.with_context(mailto=rec.parent_id.work_email,emp_name=rec.parent_id.name,receiver=rec.name).send_mail(record.id, notif_layout='kwantify_theme.csm_mail_notification_light')
            #     self.env.user.notify_success("Mail sent successfully.")
            elif record.kt_view_id.state == 'Scheduled':
                record.kt_status = 'Scheduled'
            elif record.kt_view_id.state == 'Completed':
                record.kt_status = 'Completed'

    """ Method for final submission """

    @api.multi
    def btn_document_final_submit(self):
        for record in self:
            if record.prj_document_ids:
                record.kt_view_id.state = 'Completed'
            else:
                raise ValidationError("Please upload KT documents")

    @api.model
    def default_get(self, fields):
        res = super(kw_time_line_plan, self).default_get(fields)
        kt_view_id = False
        res['check_document'] = True
        if self._context.get('default_kt_view_id', False):
            kt_view_id = self._context['default_kt_view_id']
        else:
            kt_view_record = self.env['kw_kt_view'].sudo().search(
                [('applicant_id', '=', self.env.user.employee_ids.id), ('state', '=', 'Applied')])
            kt_view_id = kt_view_record and kt_view_record.id or False
        res['kt_view_id'] = kt_view_id
        return res

    # @api.constrains('document_attach')
    # def validate_document_attach(self):
    #     allowed_file_list = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
    #     for record in self:
    #         kw_validations.validate_file_mimetype(record.document_attach, allowed_file_list)
    #         kw_validations.validate_file_size(record.document_attach, 4)
