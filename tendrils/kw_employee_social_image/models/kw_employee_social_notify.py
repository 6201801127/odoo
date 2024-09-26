from odoo import api, models, fields
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError
import requests, json
from datetime import datetime


class kw_employee_social_notify(models.Model):
    _name = 'kw_employee_social_notify'
    _description = 'Employee Candid Image notify'
    _rec_name = 'search_option'

    name = fields.Char("Name")
    department_ids = fields.Many2many('hr.department', 'social_image_deptartment', 'social_id', 'dept_id',
                                      string='Department')
    division = fields.Many2many('hr.department', 'social_image_division', 'social_id', 'div_id', string='Division')
    section = fields.Many2many('hr.department', 'social_image_section', 'social_id', 'section_id', string='Practice')
    practice = fields.Many2many('hr.department', 'social_image_practice', 'social_id', 'practise_id', string='Section')
    searched_user = fields.Many2many('hr.employee', string='Employee')
    search_option = fields.Selection([('by_user', 'By User'), ('by_hierarchy', 'By Hierarchy')], string='Search Option', default='by_user')
    location_type = fields.Selection([('all', 'All'), ('location_specific', 'Location Specific')], default='all')
    location_ids = fields.Many2many('kw_res_branch', string='Location')
    from_date = fields.Date(string='From Date', default=fields.Date.today())
    to_date = fields.Date(string='To Date')

    @api.onchange('department_ids')
    def onchange_department(self):
        dept_child = self.mapped("department_ids.child_ids")
        self.division &= dept_child
        return {'domain': {'division': [('id', 'in', dept_child.ids)]}}

    @api.onchange('division')
    def onchange_division(self):
        division_child = self.mapped("division.child_ids")
        self.section &= division_child
        return {'domain': {'section': [('id', 'in', division_child.ids)]}}

    @api.onchange('section')
    def onchange_section(self):
        section_child = self.mapped("section.child_ids")
        self.practice &= section_child
        return {'domain': {'practice': [('id', 'in', section_child.ids)]}}

    @api.onchange('search_option', 'location_type')
    def set_default(self):
        if self.search_option == 'by_user':
            self.department_ids = False
            self.division = False
            self.section = False
            self.practice = False

        if self.location_type == 'all':
            self.location_ids = False

    @api.constrains('from_date')
    def date_validation_date(self):
        if self.from_date and self.from_date < date.today():
            raise ValidationError("You can not choose back date .")

    @api.constrains('to_date')
    def date_validation_to_date(self):
        if self.from_date and self.to_date and self.from_date > self.to_date:
            raise ValidationError("From date can not be greater than to date .")

    @api.onchange('from_date', 'to_date', 'department_ids', 'division', 'section', 'practice', 'location_ids')
    def onchange_searched_user(self):
        emp_ids = self.filter_employee(self)
        return {'domain': {'searched_user': [('id', 'in', emp_ids.ids)]}}

    @api.model
    def create(self, vals):
        res = super(kw_employee_social_notify, self).create(vals)
        if self.env.context.get('customview'):
            for rec in res:
                emp_ids = False
                if not rec.searched_user:
                    emp_ids = self.filter_employee(rec)
                else:
                    emp_ids = rec.searched_user
                for record in emp_ids:
                    template = self.env.ref("kw_employee_social_image.notification_mail_template_social_image")
                    if template:
                        template.with_context(
                            mail_from=self.env.user.employee_ids[
                                0].work_email if self.env.user.employee_ids else 'tendrils@csm.tech',
                            emp_name=record.name,
                            mail_to=record.work_email).send_mail(res.id,
                                                                 notif_layout='kwantify_theme.csm_mail_notification_light')
                self.env.user.notify_success("Mail sent successfully.")
        return res

    def sync_now(self):
        log = self.env["log_sync_social_image"].sudo()
        last_sync = log.search([], limit=1, order="id desc")
        last_sync_date = last_sync.create_date if last_sync else date.today()
        # print("last_sync_date >> ", last_sync_date)

        """sync social images"""
        records = self.env["kw_employee_social_image"].search([('is_sync', '=', False)], limit=25)
        if records:
            try:
                payload = {"method": "employee_sync",
                           "data": [{"employee_id": emp.emp_id.id,
                                     "name": emp.emp_id.name,
                                     "email": emp.emp_id.work_email,
                                     "updated_on": emp.write_date.strftime('%Y-%m-%d'),
                                     "image": emp.social_image.decode('UTF-8')} for emp in records if not emp.is_sync and emp.social_image]
                           }
                # print("payload >> ", payload)
                data = json.dumps(payload)

                sync_url = self.env["ir.config_parameter"].sudo().get_param("social_picture_sync_url")
                if not sync_url:
                    # sync_url = "http://192.168.103.229/CSM/api/consoleServices"
                    sync_url = self.env["ir.config_parameter"].sudo().get_param("kwantify_console_service_sync_url")
                # print("sync_url >> ", sync_url)
                response_obj = requests.post(sync_url, headers={"Content-Type": "application/json"}, data=data,
                                             timeout=30)
                content = response_obj.content
                resp = json.loads(content.decode("utf-8"))
                # print("resp >> ", resp)

                if resp['status'] == '200':
                    records.write({'is_sync': True})
                    self._log(log, "Employee Image Sync", data, "Success")
                    self.env.user.notify_success(message='Employee Image sync successful.')
                elif resp['status'] == '422':
                    self._log(log, "Employee Image Sync", data, "API: Empty Employee details")
                    self.env.user.notify_danger(message='Empty Employee details.')
                elif resp['status'] == '500':
                    self._log(log, "Employee Image Sync", data, "API Error")
                    self.env.user.notify_danger(message='Something went wrong.')
            except Exception as e:
                # print("Error : no response from career server", e)
                self._log(log, "Employee Image Sync", data, "Failed")
                self.env.user.notify_danger(message='An error occurred while master sync.')
        else:
            self.env.user.notify_info(message='All images synced. No new images found')

        """# Ex employee Sync"""
        records = self.env['hr.employee'].sudo().search([('last_working_day', '>=', last_sync_date),
                                                         '|', ('active', '=', True), ('active', '=', False)])
        if records:
            try:
                payload_ex = {
                    "method": "ex_employee_sync",
                    "ex_employees": [{"id": emp.id} for emp in records]
                }
                # print("payload_ex >> ", payload_ex)
                data = json.dumps(payload_ex)

                sync_url = self.env["ir.config_parameter"].sudo().get_param("social_picture_sync_url")
                if not sync_url:
                    # sync_url = "http://192.168.103.229/CSM/api/consoleServices"
                    sync_url = self.env["ir.config_parameter"].sudo().get_param("kwantify_console_service_sync_url")

                # print("sync_url >> ", sync_url)
                response_obj = requests.post(sync_url, headers={"Content-Type": "application/json"}, data=data, timeout=30)
                content = response_obj.content
                resp = json.loads(content.decode("utf-8"))
                # print('resp >> ', resp)

                if resp['status'] == '200':
                    self.env.user.notify_success(message='Employee sync successful.')
                    self._log(log, "Ex Employee Sync", data, "Success")
                elif resp['status'] == '500':
                    self.env.user.notify_danger(message='Something went wrong in API.')
                    self._log(log, "Ex Employee Sync", data, "API Error")
            except Exception as e:
                # print("Error : no response from career server", e)
                self.env.user.notify_danger(message='An error occurred while employee sync.')
                self._log(log, "Ex Employee Sync", data, "Failed")
        else:
            self.env.user.notify_info(message='All ex-employees synced. No new employees found')

    def _log(self, log, name, payload, status):
        return log.create({"name": name, "payload": payload, 'status': status, })

    def notify(self):
        res = self.env['ir.actions.act_window'].for_xml_id('kw_employee_social_image', 'kw_employee_social_notify_action_window')
        return res

    def profile_picture(self):
        res = self.env['ir.actions.act_window'].for_xml_id('kw_employee_social_image', 'kw_employee_social_image_action_window')
        return res

    def sync_log(self):
        res = self.env['ir.actions.act_window'].for_xml_id('kw_employee_social_image', 'log_sync_social_image_action_window')
        return res

    # @api.model
    # def check_profile_picture(self, user_id):
    #     user = user_id
    #     profile_url = False
    #     employee_id = self.env['hr.employee'].sudo().search([('user_id', '=', user)], limit=1)
    #     if employee_id:
    #         curr_date = date.today()
    #         notify = self.env['kw_employee_social_notify'].sudo().search([('searched_user', '=', employee_id.id), ('from_date', ">=", curr_date), ('to_date', "<=", curr_date)])

    #         if notify:
    #             survey_id = self.env.ref('kw_employee_social_image.profile_picture_upload_form')
    #             profile_url = f"/profile-picture/{slug(notify)}/{slug(employee_id)}/{slug(survey_id)}"
    #             return profile_url
    #     return profile_url

    def filter_employee(self, new_Record):
        domain = []
        if new_Record.search_option == 'by_hierarchy':
            if new_Record.department_ids:
                domain.append(('department_id', 'in', new_Record.department_ids.ids))
            if new_Record.division:
                domain.append(('division', 'in', new_Record.division.ids))
            if new_Record.section:
                domain.append(('section', 'in', new_Record.section.ids))
            if new_Record.practice:
                domain.append(('practise', 'in', new_Record.practice.ids))
        if new_Record.location_ids:
            domain.append(('job_branch_id', 'in', new_Record.location_ids.ids))

        emp_ids = self.env['hr.employee'].sudo().search(domain)

        return emp_ids
