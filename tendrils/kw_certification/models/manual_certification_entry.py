from datetime import date
from kw_utility_tools import kw_validations
import datetime
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class KwManualCertification(models.Model):
    _name = 'kw_manual_certification'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Manual Certification Entry"
    _rec_name = 'raised_by_id'


    date_of_raised = fields.Datetime(string='Date', default=fields.Datetime.now, readonly=True,track_visibility='always')
    department_id = fields.Many2one('hr.department', track_visibility='always')
    raised_by_id = fields.Many2one('hr.employee', string="Raised By",default=lambda self:  self.env.user.employee_ids, store=True)
    require_department_id = fields.Many2one('hr.department', string='For Department', track_visibility='always', domain="[('dept_type','=',1)]")
    certification_type_id = fields.Many2one('kwmaster_stream_name', string='Certification Name', track_visibility='always', domain="[('course_id.code', '=', 'cert')]")
    technology_id = fields.Many2one('kw_certification_technology_master', string='Technology',track_visibility='always')
    assigned_emp_data = fields.One2many('assign_employee','manual_certification_entry_id')
    state = fields.Selection(string="Status",
                             selection=[('Draft', 'Draft'),
                                        ('Submit', 'Submit')
                                        ], default="Draft", track_visibility='always')
    show_button = fields.Boolean(compute='_compute_show_button', string='Show Button')


    @api.depends('state')
    def _compute_show_button(self):
        current_record = self.env.context.get('active_id')
        certification = self.env['kw_manual_certification'].browse(current_record)
        return certification.state == 'Submit'

    def btn_submit(self):
        for record in self:
            if not record.assigned_emp_data:
                raise ValidationError('You must add atleast one employee.')
            else:
                self.state = 'Submit'

    @api.onchange('raised_by_id', 'certification_type_id')
    def _change_employee(self):
        self.department_id = self.raised_by_id.department_id.id if self.raised_by_id.department_id else False
        if self.certification_type_id:
            data = self.env['kw_certification_budget_master'].sudo().search([('certificate_id', '=',
                                                                self.certification_type_id.id)])
            if data:
                self.cert_budget = data.mapped('budget')[0]
            else:
                raise ValidationError(f'Certification {self.certification_type_id.name} budget is not set.')            


class ManualCertificationAddWizard(models.TransientModel):
    _name = 'manual_certification_add_wizard'
    _description = 'Manual Certification Add Wizard'
    
    def get_emp_id(self):
        emp_list = []
        current_record_id = self._context.get('current_record')
        data = self.env['kw_manual_certification'].sudo().search([('id', '=', current_record_id), ('state', '=', 'Submit')])
        for rec in data:
            emp_id = []
            for recc in rec.assigned_emp_data:
                if recc.status_certification == 'Accepted' and recc.certificate_upload == None:
                    emp_id.append(recc.employee_id.id)
            emp_list = [('id','in',emp_id)]
        return emp_list

    def get_emp_ids(self):
        emp_domain = []
        current_record_id = self._context.get('current_record')
        if current_record_id:
            data = self.env['kw_manual_certification'].sudo().search([('id', '=', current_record_id), ('state', '=', 'Submit')])
            for rec in data:
                emp_id = []
                for recc in rec.assigned_emp_data:
                    if recc.status_certification == 'Uploaded' and recc.certificate_upload is not None:
                        emp_id.append(recc.employee_id.id)
                emp_domain = [('id', 'in', emp_id)]
        return emp_domain
    
    
    manual_certification_record_id = fields.Many2one('kw_manual_certification')
    assign_emp_record_id = fields.Many2one('assign_employee')
    certificate_upload = fields.Binary(string='Document')
    employee_id = fields.Many2one('hr.employee',string="Employee Name", domain=get_emp_id)
    emp_id = fields.Many2many('hr.employee',string="Employee Name", domain=get_emp_ids)
    course_type = fields.Selection(string="Type", selection=[('1', 'Educational'), ('2', 'Professional Qualification'),
                                                             ('3', 'Training And Certification')], default='3')
    course_id = fields.Many2one('kwmaster_course_name', string="Course Name", domain="[('code', '=', 'cert')]", default=lambda self: self._default_course_id(), readonly=True)
    university_name = fields.Many2one('kwmaster_institute_name', string="University/Institution")
    stream_id = fields.Many2one('kwmaster_stream_name', string="Certification", compute="_compute_certification_type_id", store=True)
    division = fields.Char(string="Division / Grade", size=6)
    marks_obtained = fields.Float(string="% of marks obtained")
    doc_file_name = fields.Char(string="Document Name")
    passing_year = fields.Selection(string="Passing Year", selection='_get_year_list')


    @api.depends('employee_id')
    def _compute_certification_type_id(self):
        self.stream_id = self.manual_certification_record_id.certification_type_id.id  


    def _default_course_id(self):
        cert_course = self.env['kwmaster_course_name'].search([('code', '=', 'cert')], limit=1)
        return cert_course.id if cert_course else False

    @api.model
    def _get_year_list(self):
        current_year = date.today().year
        return [(str(i), i) for i in range(current_year, 1953, -1)]


    def btn_submit_upload_manual(self):
        if self.assign_emp_record_id:
            self.assign_emp_record_id.write({'status_certification' : 'Uploaded','certificate_upload':self.certificate_upload})
            employee_data = self.env['hr.employee'].search([('id', '=', self.assign_emp_record_id.employee_id.id)])
            skill_id = []
            for rec in employee_data.educational_details_ids:
                skill_id.append(rec.stream_id.id)
            if self.stream_id.id in skill_id:
                raise ValidationError(f'{self.stream_id.name} certification has already been updated against {self.employee_id.name}.')
            else:
                employee_data.write(
                            {'educational_details_ids':[[0,0,{
                                'course_type':self.course_type,
                                'course_id':self.course_id.id,
                                'stream_id':self.stream_id.id,
                                'university_name':self.university_name.id,
                                'division':self.division,
                                'marks_obtained':self.marks_obtained,
                                'uploaded_doc':self.certificate_upload,
                                'passing_year':self.passing_year
                            }]]
                             })
              



            
    
