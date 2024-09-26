from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re
# import datetime
import time
from datetime import date, datetime,timedelta
from ast import literal_eval
import calendar


class KwEmployeeOnboardingChecklist(models.Model):
    _name = 'kw_employee_onboarding_checklist'
    _description = "Onboarding Checklist"
    _rec_name = 'employee_id'
    _order = "write_date desc"

    joining_kit = fields.Selection(string='Joining Kit', selection=[('yes', 'Yes'), ('no', 'No'), ('na', 'NA')],
                                   default='no')
    doc_collection = fields.Selection(string='Documents Collection',
                                      selection=[('yes', 'Yes'), ('no', 'No'), ('na', 'NA')], default='no')
    kw_profile_update = fields.Selection(string='Tendrils Profile Update',
                                         selection=[('yes', 'Yes'), ('no', 'No'), ('na', 'NA')], default='no')
    hard_copy_verification = fields.Selection(string='Hard Copy Verification',
                                              selection=[('yes', 'Yes'), ('no', 'No'), ('na', 'NA')], default='no')
    kw_id_generation = fields.Selection(string='Tendrils ID Generation',
                                        selection=[('yes', 'Yes'), ('no', 'No'), ('na', 'NA')], default='no')
    email_id_creation = fields.Selection(string='Email ID Creation',
                                         selection=[('yes', 'Yes'), ('no', 'No'), ('na', 'NA')], default='no')
    telephone_extention = fields.Selection(string='Telephone Extension',
                                           selection=[('yes', 'Yes'), ('no', 'No'), ('na', 'NA')], default='no')
    health_insurance = fields.Selection(string='Health Insurance',
                                        selection=[('yes', 'Yes'), ('no', 'No'), ('na', 'NA')], default='no')

    family_info = fields.Many2one('kwemp_family_info', 'Dependants info', )

    esi = fields.Selection(string='ESI', selection=[('yes', 'Yes'), ('no', 'No'), ('na', 'NA')], default='no')
    accident_policy = fields.Selection(string='Accident Policy', selection=[('yes', 'Yes'), ('no', 'No'), ('na', 'NA')],
                                       default='yes')
    gratuity = fields.Selection(string='Gratuity', selection=[('yes', 'Yes'), ('no', 'No'), ('na', 'NA')], default='no')
    pf = fields.Selection(string='EPF', selection=[('yes', 'Yes'), ('no', 'No'), ('na', 'NA')], default='no')
    work_station = fields.Selection(string='Work Station', selection=[('yes', 'Yes'), ('no', 'No'), ('na', 'NA')],
                                    default='no')

    offsite = fields.Boolean(string='Offsite')
    work_station_link = fields.Char(string="Workstation link")
    onsite = fields.Boolean(string='Onsite')
    client_loc = fields.Many2one('kw_res_branch', 'Client Location', )
    hr_induction = fields.Selection(string='HR Induction', selection=[('yes', 'Yes'), ('no', 'No')], default='no')
    jd = fields.Selection(string='JD', selection=[('yes', 'Yes'), ('no', 'No')], default='no')
    bond_formality = fields.Selection(string='Bond Formality', selection=[('yes', 'Yes'), ('no', 'No'), ('na', 'NA')],
                                      default='no')
    appointment_letter = fields.Selection(string='Appointment Letter', selection=[('yes', 'Yes'), ('no', 'No')],
                                          default='no')
    id_card = fields.Selection(string='ID Card', selection=[('yes', 'Yes'), ('no', 'No')], default='no')
    criminal_record_verification = fields.Selection(string='Criminal Record Verification',
                                                    selection=[('yes', 'Yes'), ('no', 'No')], default='no')
    background_verification = fields.Selection(string='Background Verification',
                                               selection=[('yes', 'Yes'), ('no', 'No'), ('na', 'NA')], default='no')
    status = fields.Selection([('in-progress', 'In-Progress'), ('complete', 'Completed')], string="Status",
                              compute="compute_state", track_visibility='onchange')
    employee_id = fields.Many2one('hr.employee', string="Employee")
    client_loc_id = fields.Many2one('res.partner', string='Client Location')
    # dependants_info_ids = fields.One2many('kwemp_family_info', 'emp_id', string='Dependants Info', compute='compute_dependants')
    health_self = fields.Boolean(string="Self")
    health_dependants = fields.Boolean(string="Dependants")
    location = fields.Selection(selection=[('onsite', 'Onsite'), ('offsite', 'Offsite'), ('wfa', 'WFA')], string="Location")
    dependantsinfo_ids = fields.Many2many('kwemp_family_info', string='Dependants Info')
    image = fields.Binary(string="Upload Photo", attachment=True,
                          help="Only .jpeg,.png,.jpg format are allowed. Maximum file size is 1 MB", store=True)
    designation_id = fields.Many2one('hr.job', string="Designation")
    department = fields.Char('Department', related='employee_id.department_id.name')

    @api.onchange('health_dependants')
    def compute_dependants(self):
        for rec in self:
            return {'domain': {'dependantsinfo_ids': [('emp_id', '=', self.employee_id.id), ('is_insured', '=', True)]}}

    @api.onchange('work_station')
    def onchange_work_station(self):
        self.location = False

    @api.onchange('health_insurance')
    def onchange_health_insurance(self):
        self.health_self = False
        self.health_dependants = False

    @api.model
    def create(self, values):
        result = super(KwEmployeeOnboardingChecklist, self).create(values)
        lst = []
        if 'active_model' and 'active_id' in self._context:
            if self._context['active_model'] == 'hr.employee':
                employee_id = self._context['active_id']
                employee_rec = self.env['hr.employee'].browse(employee_id)
                if employee_rec and not employee_rec.onboarding_checklist:
                    employee_rec.onboarding_checklist = result.id
        if result.workstation_id:
            lst.append(result.employee_id.id)
            workstation_rec = self.env['kw_workstation_master'].sudo().search([('id', '=', result.workstation_id.id)])
            workstation_emp_lis = workstation_rec.mapped('employee_id.id')
            workstation_emp_lis.append(result.employee_id.id)
            workstation_rec.write({'employee_id': [(6, 0, workstation_emp_lis)]})
        return result

    @api.multi
    def write(self, vals):
        old_rec = self.env['kw_employee_onboarding_checklist'].sudo().search([('id', '=', self.id)])
        old_workstation_id = old_rec.workstation_id.id
        result = super(KwEmployeeOnboardingChecklist, self).write(vals)
        if 'workstation_id' in vals:
            new_rec = self.env['kw_employee_onboarding_checklist'].sudo().search([('id', '=', self.id)])
            new_workstation_id = new_rec.workstation_id.id
            if old_workstation_id != new_workstation_id:
                old_workstation = self.env['kw_workstation_master'].sudo().search([('id', '=', old_workstation_id)])
                new_workstation = self.env['kw_workstation_master'].sudo().search([('id', '=', new_workstation_id)])
                old_work_emp_lis = old_workstation.mapped('employee_id.id')
                if old_rec.employee_id.id in old_work_emp_lis:
                    old_work_emp_lis.remove(old_rec.employee_id.id)
                new_work_emp_lis = new_workstation.mapped('employee_id.id')
                new_work_emp_lis.append(old_rec.employee_id.id)
                old_workstation.write({'employee_id': [(6, 0, old_work_emp_lis)]})
                new_workstation.write({'employee_id': [(6, 0, new_work_emp_lis)]})
        return result

    def compute_state(self):
        for rec in self:
            if rec.joining_kit == 'no' or rec.doc_collection == 'no' or rec.kw_profile_update == 'no' or rec.hard_copy_verification == 'no' or \
                    rec.kw_id_generation == 'no' or rec.email_id_creation == 'no' or rec.telephone_extention == 'no' or rec.esi == 'no' or \
                    rec.accident_policy == 'no' or rec.gratuity == 'no' or rec.health_insurance == 'no' or rec.pf == 'no' or rec.hr_induction == 'no' or \
                    rec.jd == 'no' or rec.bond_formality == 'no' or rec.appointment_letter == 'no' or rec.id_card == 'no' or rec.criminal_record_verification == 'no' or \
                    rec.background_verification == 'no' or rec.work_station == 'no':
                rec.status = 'in-progress'

            else:
                rec.status = 'complete'

    @api.model
    def get_report_data(self, args):
        data = dict()
        join_month = args.get('month', False)
        join_year = args.get('year', False)
        dept_id = args.get('dept_id', False)
        div_id = args.get('div_id', False)
        sec_id = args.get('sec_id', False)
        pra_id = args.get('pra_id', False)
        last_day = calendar.monthrange(int(join_year), int(join_month))[1]
        from_date = f'{join_year}-{join_month}-01'
        to_date = f'{join_year}-{join_month}-{last_day}'
        params = [('employee_id.date_of_joining', '>=', from_date), ('employee_id.date_of_joining', '<=', to_date), ('employee_id.active', '=', True)]

        if pra_id:
            params.extend([('employee_id.practise','=',int(pra_id)), ('employee_id.section','=',int(sec_id)), 
                                        ('employee_id.division','=',int(div_id)), ('employee_id.department_id','=',int(dept_id))])
        if sec_id and pra_id == '0':
            params.extend([('employee_id.section','=',int(sec_id)), 
                                        ('employee_id.division','=',int(div_id)), ('employee_id.department_id','=',int(dept_id))])
        if div_id and sec_id == '0':
            params.extend([('employee_id.division','=',int(div_id)), ('employee_id.department_id','=',int(dept_id))])
        if dept_id and div_id == '0':
            params.extend([('employee_id.department_id','=',int(dept_id))])

        emp_recs = self.env['kw_employee_onboarding_checklist'].sudo().search(params)
        if emp_recs:
            data = {
                'name': {'title0': 'Checklist'},
                'joining_date': {'date0': 'Joining Date'},
                'joining_kit': {'kit0': 'Joining Kit'},
                'doc_collection': {'doc0': 'Doc Collection'},
                'kw_profile_update': {'kw_profile0': 'Kwantify Profile Update'},
                'hard_copy_verification':  {'hard_copy0': 'Hard Copy Verification'},
                'kw_id_generation': {'kw_id_generation0': 'Kwantify ID Generation'},
                'email_id_creation': {'email_id_creation0': 'Email ID Creation'},
                'telephone_extention': {'telephone_extention0': 'Telephone Extention'},
                'health_insurance': {'health_insurance0': 'Health Insurance'},
                'esi': {'esi0': 'ESI'},
                'accident_policy': {'accident_policy0': 'Accident Policy'},
                'gratuity': {'gratuity0': 'Gratuity'},
                'pf': {'pf0': 'EPF'},
                'work_station': {'work_station0': 'Work Station'},
                'hr_induction': {'hr_induction0': 'HR Induction'},
                'jd': {'jd0': 'JD'},
                'bond_formality': {'bond_formality0': 'Bond Formality'},
                'appointment_letter': {'appointment_letter0': 'Appointment Letter'},
                'id_card': {'id_card0': 'ID Card'},
                'criminal_record_verification': {'criminal_record_verification0': 'Criminal Record Verification'},
                'background_verification': {'background_verification0': 'Background Verification'},
                'status': {'status0': 'Status'},
            }
            for index, rec in enumerate(emp_recs, start=1):
                btn_link = f'<a href="/web#id={rec.id}&model=kw_employee_onboarding_checklist&view_type=form" target="_blank"><button type="button" class="btn btn-primary ml-2">Edit</button></a>'
                data['name'][f'title{index}'] = f'{rec.employee_id.name}<br/>{rec.employee_id.emp_code}<br/>{rec.employee_id.job_id.name}{btn_link}'
                data['joining_date'][f'date{index}'] = rec.employee_id.date_of_joining.strftime('%d-%b-%Y')
                data['joining_kit'][f'kit{index}'] = str(rec.joining_kit).capitalize()
                data['doc_collection'][f'doc{index}'] = str(rec.doc_collection).capitalize()
                data['kw_profile_update'][f'kw_profile{index}'] = str(rec.kw_profile_update).capitalize()
                data['hard_copy_verification'][f'hard_copy{index}'] = str(rec.hard_copy_verification).capitalize()
                data['kw_id_generation'][f'kw_id_gen{index}'] = str(rec.kw_id_generation).capitalize()
                data['email_id_creation'][f'email_id{index}'] = str(rec.email_id_creation).capitalize()
                data['telephone_extention'][f'telephone_ext{index}'] = str(rec.telephone_extention).capitalize()
                data['health_insurance'][f'health_ins{index}'] = str(rec.health_insurance).capitalize()
                data['gratuity'][f'gratu{index}'] = str(rec.gratuity).capitalize()
                data['esi'][f'esi{index}'] = str(rec.esi).capitalize()
                data['pf'][f'pf{index}'] = str(rec.pf).capitalize()
                data['accident_policy'][f'accident_policy{index}'] = str(rec.accident_policy).capitalize()
                data['work_station'][f'work_station{index}'] = str(rec.work_station).capitalize()
                data['hr_induction'][f'hr_induction{index}'] = str(rec.hr_induction).capitalize()
                data['jd'][f'jd{index}'] = str(rec.jd).capitalize()
                data['bond_formality'][f'bond_formality{index}'] = str(rec.bond_formality).capitalize()
                data['appointment_letter'][f'appointment_letter{index}'] = str(rec.appointment_letter).capitalize()
                data['id_card'][f'id_card{index}'] = str(rec.id_card).capitalize()
                data['criminal_record_verification'][f'criminal_record_verification{index}'] = str(rec.criminal_record_verification).capitalize()
                data['background_verification'][f'background_verification{index}'] = str(rec.background_verification).capitalize()
                data['status'][f'status{index}'] = rec.status.capitalize()
        return data

    @api.model
    def get_dept_details(self, args):
        dept_type = args.get('type', "department")
        parent_id = args.get('id', False)
        pid = int(parent_id) if int(parent_id) > 0 else None
        dept_rec = []
        result = self.env["hr.department"].sudo().search([("parent_id", "=", pid)])
        if result:
            for rec in result:
                dept_rec.append({"id": rec.id, "name": rec.name})
        return dept_rec

    def get_designation_cc(self):
        get_desig_ids = self.env['ir.config_parameter'].sudo().get_param('kw_employee.employee_creation_inform_ids')
        emails = ''
        if get_desig_ids:
            get_desig_list = literal_eval(get_desig_ids)
            if len(get_desig_list)>0:
                emps = self.env['hr.employee'].sudo().search([('job_id','in', [int(x) for x in get_desig_list]),('work_email','!=',False)])
                emails = ','.join(emps.mapped('work_email')) or ''
        return emails

    def daily_checklist_scheduler(self):
        email_fr = self.env['ir.config_parameter'].sudo().get_param('kw_onboarding.responsible_person')
        emp_id = int(email_fr) if email_fr != 'False' else False
        emp_recs = self.env['kw_employee_onboarding_checklist'].sudo().search([('employee_id.active', '=', True)])
        emp_list = []
        for rec in emp_recs:
            current_date = date.today()
            yesterday = current_date - timedelta(days=1)
            if rec.employee_id.date_of_joining == yesterday:
                if rec.id_card == 'no':
                    emp_list.append(f'{rec.employee_id.emp_code}:{rec.employee_id.name}:{rec.employee_id.job_id.name}')
        if emp_id != False:
            emp = self.env['hr.employee'].sudo().browse(emp_id)
            email_to, email_name = emp.work_email, emp.name

        if len(emp_list) > 0 and emp_id != False:
            template = self.env.ref('kw_employee.checklist_scheduler_email_template')
            template_id = self.env['mail.template'].browse(template.id)
            subject = 'ID Authentication Pending'
            mail_status = template_id.with_context(emp_list=emp_list, subject=subject, email_to=email_to,
                                                   email_name=email_name, email_cc=self.get_designation_cc()) \
                .send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")

    def weekly_checklist_scheduler(self):
        emp_recs = self.env['kw_employee_onboarding_checklist'].sudo().search([('employee_id.active', '=', True)])
        email_fr = self.env['ir.config_parameter'].sudo().get_param('kw_onboarding.responsible_person')
        emp_id = int(email_fr) if email_fr != 'False' else False
        template = self.env.ref('kw_employee.checklist_scheduler_email_template')
        template_id = self.env['mail.template'].browse(template.id)
        emp_profile_list = []
        emp_appointment_list = []
        emp_bck_list = []
        for rec in emp_recs:
            if rec.kw_profile_update == 'no':
                emp_profile_list.append(f'{rec.employee_id.emp_code}:{rec.employee_id.name}:{rec.employee_id.job_id.name}')  
            if rec.appointment_letter == 'no':
                emp_appointment_list.append(f'{rec.employee_id.emp_code}:{rec.employee_id.name}:{rec.employee_id.job_id.name}')
            if rec.background_verification == 'no':
                emp_bck_list.append(f'{rec.employee_id.emp_code}:{rec.employee_id.name}:{rec.employee_id.job_id.name}')
        if emp_id != False:
            emp = self.env['hr.employee'].sudo().browse(emp_id)
            email_to, email_name = emp.work_email, emp.name

        if len(emp_profile_list) > 0 and emp_id != False:
            subject = 'Tendrils Profile Updation Pending'
            mail_status = template_id.with_context(emp_list=emp_profile_list, subject=subject, email_to=email_to,
                                                   email_name=email_name, email_cc=self.get_designation_cc()) \
                .send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        if len(emp_appointment_list) > 0 and emp_id != False:
            subject = 'APL Letter release Pending'
            mail_status = template_id.with_context(emp_list=emp_appointment_list, subject=subject, email_to=email_to,
                                                   email_name=email_name, email_cc=self.get_designation_cc()) \
                .send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        if len(emp_appointment_list) > 0 and emp_id != False:
            subject = 'Background Verification Pending'
            mail_status = template_id.with_context(emp_list=emp_appointment_list, subject=subject, email_to=email_to,
                                                   email_name=email_name, email_cc=self.get_designation_cc()) \
                .send_mail(rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")

    def daily_night_checklist_scheduler(self):
        email_new_joiner_notify = self.env.ref('kw_onboarding.group_kw_new_joinee', False).mapped('users.employee_ids')
        if not email_new_joiner_notify:
            return False
        group_new_offshore_joinee = self.env.ref('kw_onboarding.group_new_offshore_join_notification', False)
        if not group_new_offshore_joinee:
            return False
        
        email_list = email_new_joiner_notify.filtered(lambda r: r.work_email != False and r.active == True).mapped('work_email')
        email = set(email_list)
        email_to = ",".join(email) or ''
        if group_new_offshore_joinee and len(group_new_offshore_joinee.users) > 0:
            hrd_mail = self.env['ir.config_parameter'].sudo().get_param('hrd_mail') or False
            group_new_joinee_offshore_email_list = [hrd_mail] + [user.email for user in group_new_offshore_joinee.users if user.email]
            group_new_joinee_offshore_emails = ','.join(group_new_joinee_offshore_email_list) or ''  

        current_date = datetime.today()
        previous_day = current_date - timedelta(days=1)
        emp_recs = self.env['hr.employee'].sudo().search([('date_of_joining', '=', previous_day),('active','=',True),('department_id.code','!=', 'OFFS')])
        non_offshore_emp_list=[]
        offshore_emp_list =[]
        for rec in emp_recs:
            non_offshore_emp_list.append({'branch': rec.base_branch_id.alias,
                                        'department': rec.department_id.name,
                                        'division': rec.division.name,
                                        'section': rec.section.name,
                                        'pratice': rec.practise.name,
                                        'code': rec.emp_code,
                                        'name': rec.name,
                                        'job_position': rec.job_id.name,
                                        'ra': rec.parent_id.name})
        emp_recs_offs = self.env['hr.employee'].sudo().search([('date_of_joining', '=', previous_day),('active','=',True),('department_id.code','=', 'OFFS')])
        if emp_recs_offs:
            for rec in emp_recs_offs:
                offshore_emp_list.append({'branch': rec.base_branch_id.alias,
                                        'department': rec.department_id.name,
                                        'division': rec.division.name,
                                        'section': rec.section.name,
                                        'pratice': rec.practise.name,
                                        'code': rec.emp_code,
                                        'name': rec.name,
                                        'job_position': rec.job_id.name,
                                        'ra': rec.parent_id.name})
        if non_offshore_emp_list:
            date = previous_day.strftime('%d-%b-%Y')
            template = self.env.ref('kw_employee.new_employee_email_template')
            template_id = self.env['mail.template'].browse(template.id)
            mail_status = template_id.with_context(emp_list=non_offshore_emp_list, date=date, email_to=email_to) \
                .send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        if offshore_emp_list:
            date = previous_day.strftime('%d-%b-%Y')
            template = self.env.ref('kw_employee.new_employee_email_template')
            template_id = self.env['mail.template'].browse(template.id)
            mail_status = template_id.with_context(emp_list=offshore_emp_list, date=date, email_to=group_new_joinee_offshore_emails) \
                .send_mail(self.id, notif_layout="kwantify_theme.csm_mail_notification_light")