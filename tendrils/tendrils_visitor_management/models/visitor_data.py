from datetime import datetime
import re
from odoo import _
from odoo import tools
from ast import literal_eval
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date,datetime,timedelta



class Visitor(models.Model):
    _name = 'visitor_data'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Visitor data'
    _rec_name = 'visitor_name'

    visitor_image = fields.Binary(string='Visitor Photo')
    visit_purpose = fields.Selection([('official', 'Office Work'), ('personal', 'Personal Work'), ('other', 'Other')], default='official', required=True)
    visitor_name = fields.Char(string="Name", required=True, track_visibility="always")
    visitor_phn = fields.Char(string="Phone Number", required=True, track_visibility="always")
    
    visitor_email = fields.Char(string="E-mail", track_visibility="always")
    visitor_gender = fields.Selection([('male', 'Male'), ('female', 'Female')], default='male', string="Gender",
                                required=True)
    visitor_address = fields.Text(string="Address")
    channel = fields.Many2one('mail.channel')

    whom_to_meet = fields.Many2one('hr.employee',string="Whom To Meet",required=True)
    employee_status = fields.Char(related='whom_to_meet.work_phone',string="Employee Status")
    
    asset_opt = fields.Boolean(default=False, string="Do You Have Any Asset")
    asset_no = fields.Char(string='Asset No.')
    asset_srl_no = fields.Char(string='Asset Srl No.')
    asset_type = fields.Char(string='Asset Type')

    submitted = fields.Boolean(string="Submitted", default=False)  
    entry = fields.Boolean(string="Allow", default=False)  
    # not_entry = fields.Boolean(string="Deny", default=False)
    test_css = fields.Html(string='CSS', sanitize=False, compute='_compute_css', store=False)
    in_time = fields.Float("In Time")
    out_time = fields.Float("Out Time")

    @api.depends('submitted')
    def _compute_css(self):
        for rec in self:
            if rec.submitted == False:
                rec.test_css = ''
            else:
                rec.test_css = '<style>.o_form_button_edit {display: none !important;}</style>'


    @api.onchange('whom_to_meet')
    def _onchange_employee_to_get_status(self):
        self.employee_status = ''
        if self.whom_to_meet:
            check_employee = self.env['kw_daily_employee_attendance'].sudo().search([('employee_id','=',self.whom_to_meet.id),('attendance_recorded_date','=',date.today())],limit=1)
            self.employee_status = check_employee.status
            
            
    @api.onchange('visitor_phn')
    def onchange_visitor_phn(self):
        self.visitor_name = False
        self.visitor_email = False
        self.visitor_gender = False
        self.visitor_address = False
        self.visitor_image = False
        self.in_time = False
        self.out_time = False
        if self.visitor_phn:
            existing_visitor = self.env['visitor_data'].search([('visitor_phn', '=', self.visitor_phn)], limit=1)
            if existing_visitor:
                self.visitor_name = existing_visitor.visitor_name
                self.visitor_email = existing_visitor.visitor_email
                self.visitor_gender = existing_visitor.visitor_gender
                self.visitor_address = existing_visitor.visitor_address
                self.visitor_image = existing_visitor.visitor_image
                

    def action_check_in(self):
        if not self.visitor_name or not self.visitor_phn:
            raise ValidationError("First fill up all the required fields.")
        self.submitted = True
        current_time = datetime.now()
        adjusted_time = current_time + timedelta(hours=5, minutes=30)
        hh_mm_float = float(f"{adjusted_time.hour}.{adjusted_time.minute}")
        self.in_time = hh_mm_float
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'visitor_wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_visitor_id': self.id,
            },
        }
    def action_check_out(self):
        current_time = datetime.now()
        adjusted_time = current_time + timedelta(hours=5, minutes=30)
        hh_mm_float = float(f"{adjusted_time.hour}.{adjusted_time.minute}")
        self.out_time = hh_mm_float
        self.entry = True


    

    # ##################Phone number Validations################################

    @api.onchange('visitor_phn')
    def _check_mobile_number(self):
        if self.visitor_phn:
            if len(self.visitor_phn) != 10 or not self.visitor_phn.isdigit():
                raise ValidationError("Incorrect Mobile Number.")


    
    ###################################################################################################

    # appointment count section
    # def visitor_appointment(self):
    #     return {
    #         'name': _('Appointment'),
    #         'domain': [('visitor_name', '=', self.id)],
    #         'view_type': 'form',
    #         'res_model': 'visitor_data',
    #         'view_id': False,
    #         'view_mode': 'tree,form',
    #         'type': 'ir.actions.act_window',
    #     }

    def action_mail(self):
        # print("mail")
        template_id = self.env.ref('visitor_management.email_template').id
        # print(template_id)
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, force_send=True)
        
    # def action_allowed_visitor(self):
    #     self.entry = True
    
    # def action_denied_visitor(self):
    #     self.entry = True
    #     self.not_entry = True


   

    @api.onchange('visitor_email')
    def validate_mail(self):
        if self.visitor_email:
            match = re.match(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.visitor_email)
            if match is None:
                raise ValidationError('Not a valid E-mail ID')




class ScheduledVisitor(models.Model):
    _name = 'scheduled_visitor_data'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Pre-Scheduled Visitors'
    _rec_name = 'visitor_name'

    visitor_image = fields.Binary(string='Visitor Photo')
    visitor_name = fields.Char(string="Name", required=True)
    visitor_phn = fields.Char(string="Phone Number")
    
    visitor_email = fields.Char(string="E-mail")
    organisation_name = fields.Char(string="Organisation",required=True)
    visit_date = fields.Datetime("Date Of Visit",required=True)
    # visit_time = fields.Float("Time Of Visit",required=True)
    # am_pm = fields.Selection([('AM', 'AM'),('PM', 'PM')],default='AM',required=True)
    vehicle_no = fields.Char(string='Vehicle No.')
    vehicle_model = fields.Char(string='Vehicle Model')
    allow_preschedule_visitors =fields.Selection([('yes', 'Yes'), ('no', 'No')], default='no', string="Security Allowed")
    state =fields.Selection([('draft', 'Draft'),('schedule', 'Scheduled'), ('cancel', 'Cancel')], default='draft', string="Status")
    is_scheduled = fields.Boolean(default=False)
    test_css = fields.Html(string='CSS', sanitize=False, compute='_compute_css', store=False)
    # visit_time_full = fields.Char(string='Visit Time', compute='_compute_visit_time_full', store=True)
    remark = fields.Char("Remark")

    # @api.depends('visit_time', 'am_pm')
    # def _compute_visit_time_full(self):
    #     for record in self:
    #         if record.visit_time and record.am_pm:
    #             record.visit_time_full = f"{record.visit_time} {record.am_pm}"
            
    # ##################Phone number Validations################################

    @api.onchange('visit_date')
    def _onchange_visit_date(self):
        if self.visit_date and self.visit_date < datetime.now():
            self.visit_date = False
            return {
                'warning': {
                    'title': "Invalid Visit Date",
                    'message': "The visit date cannot be less than today's date.",
                }
            }

    @api.depends('visitor_phn')
    def check_phn(self):
        for rec in self:
            if rec.visitor_phn > 11:
                raise ValidationError(_("Incorrect"))
        return True

    
    @api.onchange('visitor_email')
    def validate_mail(self):
        if self.visitor_email:
            match = re.match(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.visitor_email)
            if match is None:
                raise ValidationError('Not a valid E-mail ID')

    def schedule_visitor(self):
        activity_type = self.env.ref('tendrils_visitor_management.preschedule_visitor_create_notification')  # Reference to custom activity type
        summary = _("Pre-Schedule Visitor Notification")
        note = _("Pre-schedule visitor: %s from %s on %s") % (
            self.visitor_name,
            self.organisation_name,
            self.visit_date,
            # self.visit_time
        )
        self.is_scheduled = True
        self.state = 'schedule'
        receptionist_group = self.env.ref('tendrils_visitor_management.tendrils_visitor_management_receptionist')
        receptionist_users = receptionist_group.users
        for user in receptionist_users:
            activity = self.env['mail.activity'].create({
                            'activity_type_id': activity_type.id,
                            'summary': summary,
                            'note': note,
                            'res_model_id': self.env['ir.model']._get(self._name).id,
                            'res_id': self.id,
                            'user_id': user.id,
                            'date_deadline': self.visit_date,
                        })
            self.activity_ids |= activity    
    
    def allow_preschedule_visitor(self):
        for rec in self:
            rec.write({'allow_preschedule_visitors': 'yes'})
            rec.activity_ids.unlink()
            # tree_view_id = self.env.ref('tendrils_visitor_management.scheduled_visitor_data_tree_view').id
            return {
                'type': 'ir.actions.act_window',
                'name': "Pre-Scheduled Visitors",
                'res_model': 'scheduled_visitor_data',
                'view_mode': 'tree',
                # 'view_id': tree_view_id,
                'context': {'edit': False},
                'target': 'current',
            }
            
    def re_schedule_visitor(self):
        return {
            'name':f'Re-Schedule Visit for {self.visitor_name}',
            'type': 'ir.actions.act_window',
            'res_model': 'reschedule_visit_wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_update_visit_date': self.visit_date,
                # 'default_update_visit_time': self.visit_time,
                # 'default_update_am_pm': self.am_pm,
                'default_remark': self.remark,
            }
        }
        
    def cancel_schedule_visitor(self):
        self.activity_ids.unlink()
        return {
            'name':f'Cancel Visit for {self.visitor_name}',
            'type': 'ir.actions.act_window',
            'res_model': 'cancel_visit_wizard',
            'view_mode': 'form',
            'target': 'new',
            # 'context': {
            #     'default_remark': self.remark,
            # }
        }
        
    # @api.constrains('visit_time')
    # def _check_visit_time(self):
    #     for record in self:
    #         if record.visit_time == 0.00:
    #             raise ValidationError("The visit time cannot be 00.00.")

    @api.depends('allow_preschedule_visitors')
    def _compute_css(self):
        for rec in self:
            if rec.is_scheduled == False:
                rec.test_css = ''
            else:
                rec.test_css = '<style>.o_form_button_edit {display: none !important;}</style>'


class VisitorWizard(models.TransientModel):
    _name = 'visitor_wizard'
    _description = 'Visitor Wizard'

    visitor_id = fields.Many2one('visitor_data', string='Visitor', required=True)


    def action_send_visitor_mail(self):
        email_cc_ids = self.env['ir.config_parameter'].sudo().search([('key', '=', 'Visitor Management Employees E-MAIL')]).value
        email_cc_ids_list = [int(x) for x in re.findall(r'\d+', email_cc_ids)]
            
        sender_emp = self.env['hr.employee'].sudo().search([('id','in',email_cc_ids_list)])
        email_cc = sender_emp.mapped('work_email')
        email_cc_str = ', '.join(email_cc)
        
        visitor = self.visitor_id
        param = self.env['ir.config_parameter'].sudo()
        template = self.env.ref('tendrils_visitor_management.visitor_management_email_template')
        # email_from = self.env.user.employee_ids.work_email
        v_name = visitor.visitor_name
        v_number = visitor.visitor_phn
        v_purpose = visitor.visit_purpose
        email_to = visitor.whom_to_meet.work_email
        email_to_name = visitor.whom_to_meet.name


        if template:
            extra_params = {
                        # 'email_from': email_from,
                        'email_to': email_to,
                        'v_name':v_name,
                        'v_number':v_number,
                        'email_cc':email_cc_str,
                        'v_purpose':v_purpose,
                        'email_to_name':email_to_name
                    }

            self.env['hr.contract'].contact_send_custom_mail(
                res_id=self.id,
                force_send=True,
                notif_layout='kwantify_theme.csm_mail_notification_light',
                template_layout='tendrils_visitor_management.visitor_management_email_template',
                ctx_params=extra_params,
                description="VMS | A vistor has come to visit you"
            )

            self.env.user.notify_success("Mail Sent successfully.")

class PresecheduleVisitorsReport(models.Model):
    _name           = "preschedule_visitors_report"
    _description  = "Tendrils Pre-Schedule Visitors report"
    _auto             = False


    vtr_name = fields.Char(string="Visitor Name")
    vtr_phn = fields.Char(string="Phone Number")
    
    vtr_email = fields.Char(string="E-mail")
    vtr_organisation = fields.Char(string="Organisation")
    visit_date = fields.Datetime("Date Of Visit")
    # visit_time = fields.Char("Time Of Visit")
    vehicle_no = fields.Char(string='Vehicle No.')
    vehicle_model = fields.Char(string='Vehicle Model.')
    state = fields.Selection([('draft', 'Draft'),('schedule', 'Scheduled'), ('cancel', 'Cancel')], default='draft', string="Status")


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(""" CREATE or REPLACE VIEW %s as (
        select row_number() over(order by svtr.visitor_name,svtr.organisation_name) as id,
            svtr.visitor_name as vtr_name,
			svtr.visitor_phn as vtr_phn,
            svtr.visitor_email as vtr_email,
			svtr.organisation_name as vtr_organisation,
            svtr.visit_date as visit_date,
            svtr.vehicle_no as vehicle_no,
            svtr.vehicle_model as vehicle_model,
            svtr.state as state
            

            from scheduled_visitor_data as svtr
          
        )""" % (self._table))

class UnsecheduleVisitorsReport(models.Model):
    _name           = "un_schedule_visitors_report"
    _description  = "Tendrils Un-Schedule Visitors report"
    _auto             = False


    v_purpose = fields.Selection([('official', 'Office Work'), ('personal', 'Personal Work'), ('other', 'Other')],string="Visit Purpose", required=True)
    v_name = fields.Char(string="Visitor Name")
    v_phn = fields.Char(string="Phone Number")
    v_email = fields.Char(string="E-mail")
    v_address = fields.Text(string="Address")
    to_meet = fields.Many2one('hr.employee',string="Whom To Meet")
    
    v_asset_no = fields.Char(string='Asset No.')
    v_asset_srl_no = fields.Char(string='Asset Srl No.')
    v_asset_type = fields.Char(string='Asset Type')


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(""" CREATE or REPLACE VIEW %s as (
        select row_number() over(order by vtr.visitor_name,vtr.whom_to_meet) as id,
            vtr.visitor_name as v_name,
			vtr.visit_purpose as v_purpose,
			vtr.visitor_phn as v_phn,
            vtr.visitor_email as v_email,
			vtr.visitor_address as v_address,
            vtr.whom_to_meet as to_meet,
            vtr.asset_no as v_asset_no,
            vtr.asset_srl_no as v_asset_srl_no,
            vtr.asset_type as v_asset_type
            from visitor_data as vtr
        )""" % (self._table))       



class RescheduleVisitWizard(models.TransientModel):
    _name = 'reschedule_visit_wizard'
    _description = 'Wizard to Reschedule Visit'

    update_visit_date = fields.Datetime("Date Of Visit", required=True)
    remark = fields.Char("Remark", required=True)
    vehicle_no = fields.Char(string='Vehicle No.')
    vehicle_model = fields.Char(string='Vehicle Model')
    
    
    def action_reschedule(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            visit = self.env['scheduled_visitor_data'].browse(active_id)
            visit.write({
                'visit_date': self.update_visit_date,
                'remark': self.remark,
                'vehicle_no': self.vehicle_no,
                'vehicle_model': self.vehicle_model,
                'state': 'schedule',
                'is_scheduled': True,
            })
            
            
            
class CancelVisitWizard(models.TransientModel):
    _name = 'cancel_visit_wizard'
    _description = 'Wizard to Cancel Visit'

    remark = fields.Char("Remark", required=True)
    
    
    def action_cancel(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            visit = self.env['scheduled_visitor_data'].browse(active_id)
            visit.write({
                'remark': self.remark,
                'state': 'cancel',
            })