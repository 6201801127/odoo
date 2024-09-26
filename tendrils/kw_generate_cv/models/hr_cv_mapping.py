# -*- coding: utf-8 -*-
from odoo import models, fields, api, http
from datetime import datetime, date
from odoo.exceptions import ValidationError



class HrEmployeeCvMapping(models.Model):
    _name = 'hr.cv.mapping'
    _description = 'CV MAPPING'
    _rec_name = 'sequence'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    def _default_financial_yr(self):
        fiscal_years = self.env['account.fiscalyear'].search([])
        for rec in fiscal_years:
                current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        return current_fiscal

    financial_year_id = fields.Many2one('account.fiscalyear', 'Financial Year', track_visibility='always',
                           default=_default_financial_yr, required=True)
    account_holder = fields.Many2one('hr.employee', string="Account Holder", required=True)
    location = fields.Selection(selection=[('on site', 'On Site'),('off site', 'Off Site')], string="Work Location")
    qualification_details = fields.Many2many('kwmaster_stream_name','cv_mapping_edu_qual_master_rel','cv_id','edu_qual_id', string="Qualification", domain="[('course_id','in',[3,4])]", required=True )
    min_exp_year = fields.Selection(string='Min. Experience(yrs)', selection='_get_year_list', default="0", required=True)
    max_exp_year = fields.Selection(string='Max. Experience(yrs)', selection='_get_year_list', default="0", required=True)
    engagement = fields.Selection(selection=[('partly', 'Partly Engaged'),('fully', 'Fully Engaged')], string="Engagement Type")
    no_of_engaged_month = fields.Integer(string="No. of Engaged Month", required=True)
    type_project = fields.Selection(string='Project Type',
                                    selection=[('work', 'Work Order'), ('opportunity', 'Opportunity')], default='work',
                                    help="Set recruitment process is work order.")
    project = fields.Many2one('crm.lead', string='Project Name',track_visibility='onchange', required=True)
    job_id = fields.Many2one('hr.job',string="Designation", required=True)
    professional_qualification = fields.Many2many('kwmaster_stream_name', 'cv_mapping_pro_qual_master_rel','cv_id','pro_qual_id',string="Certification", domain="[('course_id','in',[5,6])]")
    no_of_resources = fields.Integer(string="No. of Resources", required=True)
    effective_from_date = fields.Date(string="Effective From Date", required=True)
    effective_to_date = fields.Date(string="Effective To Date", required=True)
    project_excecution_location = fields.Char(string="Resource Deployement Location", required=True)
    requested_by = fields.Many2one('hr.employee', string="Request Raised By", default=lambda self:  self.env.user.employee_ids)
    employee_ids=fields.Many2many("hr.employee",string="employee")
    tagged_employee_ids = fields.One2many("hr.cv.mapping.employee", 'emp_id', string="Tagged Employee")
    result_employee_ids = fields.One2many("cv.mapping.result.employee", 'employee_id', string="Tagged Employee")
    # result_employee_ids = fields.Many2many(
    #     comodel_name='hr.employee.mis.report',
    #     column1 ='mapped_id',
    #     column2 ='employee_id',
    #     relation='hr_employee_mis_cv_mapping_rel',
    #     string='Found List')
    state = fields.Selection(
        [('draft', 'Draft'), 
        ('applied', 'Applied'), 
        ('tagged', 'Tagged'), 
        ('approve', 'Approved'), 
        ('reject', 'Rejected'),
        ('cancel', 'Cancelled')], string='Status', default='draft', readonly=True)
    sequence = fields.Char(string="Request Code", readonly=True,default='New')   
    res_tagged = fields.Boolean(compute='compute_req_approved',store=True) 
    mapped_ids = fields.One2many('cv_mapping_log', 'reg_id', string='Approval Details')
    


    
    @api.model
    def _get_year_list(self):
        years = 30
        return [(str(i), i) for i in range(years + 1)]

    @api.constrains('no_of_engaged_month','no_of_resources','min_exp_year','max_exp_year')
    def _check_validation(self):
        for rec in self:
            if rec.no_of_engaged_month == 0:
                raise ValidationError("Engagement month can not be zero")    
            if rec.no_of_resources == 0:
                raise ValidationError("Number of resource can not be zero")
            if int(rec.min_exp_year) >= int(rec.max_exp_year):
                raise ValidationError("Minimum experience should be less than maximum experience")


    @api.constrains('effective_from_date', 'effective_to_date', 'no_of_engaged_month')
    def _check_num_months(self):
        for record in self:
            # Calculate the number of months between the effective_from_date and effective_to_date fields
            num_months = (record.effective_to_date.year - record.effective_from_date.year) * 12 + record.effective_to_date.month - record.effective_from_date.month
            if num_months != record.no_of_engaged_month:
                raise ValidationError('The number of months must be between the effective from date and effective to date.')

    def check_data(self):
        domain = []
        mis_employee = []
        final_emp_list = []
        qual_emp=[]
        tag_emp_list=[]
        result_emp=[]
        # if self.job_id: 
        #     domain+=[('job_id', '=', self.job_id.id)]
        if int(self.min_exp_year) >= 0 and int(self.max_exp_year) > 0:
            domain+=[('total_experience_in_year', '>=', int(self.min_exp_year)), 
            ('total_experience_in_year', '<', int(self.max_exp_year)+1),('emp_id.company_id','=',1)]
        res = self.env['hr.employee.mis.report'].search(domain)
        for emp in res:
            mis_employee.append(emp.emp_id.id)
        

        if (self.qualification_details and not self.professional_qualification) or (self.professional_qualification and not self.qualification_details):
            if self.qualification_details:
                kw= self.env['kwemp_educational_qualification'].search([('course_type', 'in' , ['1', '2']),
                                                                    ('stream_id', 'in' , self.qualification_details.ids)])
                                                           
            elif self.professional_qualification:
                kw= self.env['kwemp_educational_qualification'].search([('course_type', 'in' , ['3']),
                                                                        ('stream_id', 'in' , self.professional_qualification.ids)])
            

            for edu in kw:
                mis_employee.append(edu.emp_id.id) 
            visited = set()
            duplicate = {x for x in mis_employee if x in visited or (visited.add(x) or False)}

        else:
            if self.qualification_details and self.professional_qualification:
                kw= self.env['kwemp_educational_qualification'].search([('stream_id', 'in' , self.qualification_details.ids),
                ('emp_id', 'in', mis_employee)])
                for emp in kw:
                    qual_emp.append(emp.emp_id.id)
                kw2= self.env['kwemp_educational_qualification'].search([('stream_id', 'in' , self.professional_qualification.ids),
                ('emp_id', 'in', mis_employee)])
                for emp in kw2:
                    # print("empempemp,,,,,,,,", emp)
                    qual_emp.append(emp.emp_id.id)
            visited = set()
            duplicate = {x for x in qual_emp if x in visited or (visited.add(x) or False)}
        for emp_id in duplicate:
            final_emp = self.env['hr.employee.mis.report'].search([('emp_id','=', emp_id)])
            for emp in final_emp:
                final_emp_list.append(emp.id)

        
        for emp in self.tagged_employee_ids:
            tag_emp_list.append(emp.report_id.id)

        s = set(tag_emp_list)
        temp3 = [x for x in final_emp_list if x not in s]


        ''' Filter CV as per date condition ( Employees who are tagged within certain dates, will not be available again '''
        
        # emp_tag_rec = self.env['hr.cv.mapping'].sudo().search(
        #     ['&','|','|','|',
        #     '&',('effective_from_date', '<', self.effective_from_date),('effective_to_date', '>', self.effective_to_date ),
        #     '&','&',('effective_from_date', '<', self.effective_from_date),('effective_to_date', '>', self.effective_from_date),('effective_to_date', '<', self.effective_to_date ),
        #     '&',('effective_from_date', '>', self.effective_from_date),('effective_to_date', '<', self.effective_to_date ),
        #     '&','&',('effective_from_date', '>', self.effective_from_date),('effective_from_date', '<', self.effective_to_date),('effective_to_date', '>', self.effective_to_date ),
        #     ('tagged_employee_ids.report_id.id', 'in', temp3 )
        #     ])

        
        # tag_list = []
        # tag_list = emp_tag_rec.mapped('tagged_employee_ids.report_id.id')


        # s = set(tag_list)
        # temp4 = [x for x in temp3 if x not in s]
        # print(temp4)

        # if temp3:
        #     self.result_employee_ids = [(6, 0, temp3)] #mapped(lambda x : x.emp_id)
        # else:
        #     self.result_employee_ids = [(6, 0, [])]

        if temp3 or temp3==[]:
            self.env['cv.mapping.result.employee'].sudo().unlink()
            query = "delete from cv_mapping_result_employee"
            self.env.cr.execute(query)
            # print('duplicate=================',duplicate,self.tagged_employee_ids.mapped('report_id.emp_id.id'))
            tagged_data = list(set(duplicate) - set(self.tagged_employee_ids.mapped('report_id.emp_id.id')))
            if self.tagged_employee_ids:
                # print('tagged_data=================',tagged_data)
                pass
            for emp_id in tagged_data:
                # print("-----------employee id-------------",emp_id)
                final_emp = self.env['hr.employee.mis.report'].search([('emp_id','=', emp_id)]) 
                for values in final_emp:
                    # print('values==============',values)

                    x = self.env['cv.mapping.result.employee'].sudo().create({
                        'employee_id': self.id,
                        'mis_id' : values.id,
                        'employee_code': values.emp_code,
                        'employee_name': values.name,
                        'employee_branch': values.job_branch_id,
                        'employee_dept': values.department_id,
                        'employee_div': values.division,
                        'employee_sec': values.section,
                        'employee_prac': values.practise,
                        'employee_desig': values.job_id,
                        'employee_exp': values.total_experience_in_year,
                        'employee_qual': values.edu_qualification,
                        'employee_cert': values.certification,
                    })

    @api.multi
    def action_apply(self):
        qualification = ','.join(self.qualification_details.mapped('name')) 
        professional = ','.join(self.professional_qualification.mapped('name'))    
        manager = self.env.ref("kw_generate_cv.generate_cv_manager_group").users
        mail_to = ','.join(manager.mapped('employee_ids.work_email'))
        mail_cc = self.account_holder.work_email
        mail_template = self.env.ref('kw_generate_cv.cv_mapping_apply_mail_template')
        mail_template.with_context(mail_to=mail_to,mail_cc=mail_cc,object=self,qualification=qualification,professional=professional).send_mail(
            self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        self.write({'state': 'applied'}) 
        c = self.env['cv_mapping_log'].sudo().create({
                    'state': self.state,
                    'date': date.today(),
                    'action_taken_by': self.env.user.employee_ids.id,
                })
        

    @api.multi
    def action_tag(self):
        # if self.no_of_resources == len(self.tagged_employee_ids):
        form_view_id = self.env.ref("kw_generate_cv.cv_tag_remarks_wizard_form_view").id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tag Remark Wizard',
            'res_model': 'cv_mapping_tag_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'new',
        }
        #     qualification = ','.join(self.qualification_details.mapped('name')) 
        #     professional = ','.join(self.professional_qualification.mapped('name'))    
        #     tag_emp = self.tagged_employee_ids.mapped('report_id.name')  
        #     designation = self.job_id.name  
        #     email_to = self.requested_by.work_email
        #     email_cc = self.account_holder.work_email
        #     template_id = self.env.ref('kw_generate_cv.cv_mapping_tag_mail_template')
        #     template_id.with_context(email_to=email_to,email_cc=email_cc,qualification=qualification,professional=professional,tag_emp=tag_emp,no_of_resources=self.no_of_resources,designation=designation,min_exp_year=self.min_exp_year).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        #     self.write({'state': 'tagged','res_tagged':1})
        # else:
        #     raise ValidationError("You have to tag the exact required number of resources to send this request to be  approved.")
    
    
    @api.multi
    def action_approve(self):
        form_view_id = self.env.ref("kw_generate_cv.cv_approve_remarks_wizard_form_view").id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Approve Remark Wizard',
            'res_model': 'cv_mapping_approve_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'new',
        }
            # qualification = ','.join(self.qualification_details.mapped('name')) 
            # professional = ','.join(self.professional_qualification.mapped('name'))    
            # tag_emp = self.tagged_employee_ids.mapped('report_id.name')  
            # designation = self.job_id.name  
            # manager = self.env.ref("kw_generate_cv.generate_cv_manager_group").users
            # email_to = ','.join(manager.mapped('employee_ids.work_email'))
            # email_cc = self.account_holder.work_email
            # template_id = self.env.ref('kw_generate_cv.cv_mapping_approve_mail_template')
            # template_id.with_context(email_to=email_to,email_cc=email_cc,qualification=qualification,professional=professional,tag_emp=tag_emp,no_of_resources=self.no_of_resources,designation=designation,min_exp_year=self.min_exp_year).send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
            # self.write({'state': 'approve'})

    @api.multi
    def action_reject(self):
        form_view_id = self.env.ref("kw_generate_cv.cv_reject_remarks_wizard_form_view").id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reject Remark Wizard',
            'res_model': 'cv_mapping_reject_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'new',
        }
        
        # qualification = ','.join(self.qualification_details.mapped('name')) 
        # professional = ','.join(self.professional_qualification.mapped('name')) 
        # tag_emp = self.tagged_employee_ids.mapped('report_id.name')  
        # designation = self.job_id.name   
        # manager = self.env.ref("kw_generate_cv.generate_cv_manager_group").users
        # mail_to = ','.join(manager.mapped('employee_ids.work_email'))
        # mail_cc = self.account_holder.work_email
        # mail_template = self.env.ref('kw_generate_cv.cv_mapping_reject_mail_template')
        # mail_template.with_context(object=self,mail_to=mail_to,mail_cc=mail_cc,qualification=qualification,professional=professional,tag_emp=tag_emp,no_of_resources=self.no_of_resources,designation=designation,min_exp_year=self.min_exp_year).send_mail(
        #     self.id, notif_layout="kwantify_theme.csm_mail_notification_light")
        # self.write({'state': 'reject'})
            

    

    @api.multi
    def action_cancel(self):
        form_view_id = self.env.ref("kw_generate_cv.cv_cancel_remarks_wizard_form_view").id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cancel Remark Wizard',
            'res_model': 'cv_mapping_cancel_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'target': 'new',
        }
        # qualification = ','.join(self.qualification_details.mapped('name')) 
        # professional = ','.join(self.professional_qualification.mapped('name'))
        # tag_emp = self.tagged_employee_ids.mapped('report_id.name') 
        # designation = self.job_id.name       
        # email_to = self.requested_by.work_email
        # email_cc = self.account_holder.work_email
        # template_id = self.env.ref('kw_generate_cv.cv_mapping_cancel_mail_template')
        # template_id.with_context(email_to=email_to,email_cc=email_cc,object=self,qualification=qualification,professional=professional,tag_emp=tag_emp,no_of_resources=self.no_of_resources,designation=designation,min_exp_year=self.min_exp_year).send_mail(self.id,
        #                                                                                  notif_layout="kwantify_theme.csm_mail_notification_light")
        # self.write({'state': 'cancel'})  



    def compute_req_approved(self):
        for request in self:
            if request.state in ('approve'):
                request.res_tagged = True
            else:
                request.res_tagged = False   


    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('self.hr.cv.mapping') or '/'
        vals['sequence'] = seq
        return super(HrEmployeeCvMapping, self).create(vals)
            

class HrCvMappingResultEmployee(models.Model):
    _name = 'cv.mapping.result.employee'
    _description = 'HR CV Mapping Result Employees'

    employee_id = fields.Many2one('hr.cv.mapping', 'Employee Name')
    mis_id = fields.Many2one('hr.employee.mis.report', string='Employee')
    employee_code = fields.Char(string="Employee Code", related='mis_id.emp_code')
    employee_name = fields.Char(string="Name", related='mis_id.emp_code')
    employee_branch = fields.Many2one(string="Work Location", related='mis_id.job_branch_id')
    employee_dept = fields.Many2one(string="Department", related='mis_id.department_id')
    employee_div = fields.Many2one(string="Division", related='mis_id.division')
    employee_sec = fields.Many2one(string="Section", related='mis_id.section')
    employee_prac = fields.Many2one(string="Practise", related='mis_id.practise')
    employee_desig = fields.Many2one(string="Designation", related='mis_id.job_id')
    employee_exp = fields.Integer(string="Total Experience in Year", related='mis_id.total_experience_in_year')
    employee_qual = fields.Char(string="Education Qualification", related='mis_id.edu_qualification')
    employee_cert = fields.Char(string="Certification", related='mis_id.certification')


    def tag_emp(self):
        for record in self:
            if len(record.employee_id.tagged_employee_ids.ids) == record.employee_id.no_of_resources:
                raise ValidationError("You have already tagged the required number of resources.")
            else:    
                record.employee_id.tagged_employee_ids = [[0,0,{
                                'report_id': record.mis_id,
                                'emp_code': record.employee_code,
                }]]
                query=f'delete from cv_mapping_result_employee where id = {record.id}'
                self.env.cr.execute(query)

           
class HrEmployeeCvMappingTagging(models.Model):
    _name = 'hr.cv.mapping.tagging'
    _description = 'HR CV Mapping Tagging'

    tagged_by = fields.Many2one('hr.employee', string="Tagged By")



class CvUserTagWizard(models.TransientModel):
    _name = "cv_mapping_tag_wizard"
    _description = "CV User Tag Remark"

    remark = fields.Text('Remark',track_visibility='onchange')
    reg_id = fields.Many2one('hr.cv.mapping')


    @api.multi
    def action_done(self):
        a = self.env['hr.cv.mapping'].browse(self.env.context.get('active_id'))
        for rec in a:
            if rec.no_of_resources == len(rec.tagged_employee_ids):
                qualification = ','.join(rec.qualification_details.mapped('name')) 
                professional = ','.join(rec.professional_qualification.mapped('name'))    
                tag_emp = rec.tagged_employee_ids.mapped('report_id.name')  
                designation = rec.job_id.name  
                email_to = rec.requested_by.work_email
                email_cc = rec.account_holder.work_email
                template_id = rec.env.ref('kw_generate_cv.cv_mapping_tag_mail_template')
                template_id.with_context(email_to=email_to,email_cc=email_cc,qualification=qualification,professional=professional,tag_emp=tag_emp,no_of_resources=rec.no_of_resources,designation=designation,min_exp_year=rec.min_exp_year).send_mail(rec.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                rec.write({'state': 'tagged','res_tagged':1})
                self.env['cv_mapping_log'].sudo().create({
                    'remark': self.remark,
                    'state': rec.state,
                    'date': date.today(),
                    'action_taken_by': rec.env.user.employee_ids.id,
                })
            else:
                raise ValidationError("You have to tag the exact required number of resources to tag done the request.")    

class CvUserApproveWizard(models.TransientModel):
    _name = "cv_mapping_approve_wizard"
    _description = "CV User Approve Wizard"

    remark = fields.Text('Remark',track_visibility='onchange')
    reg_id = fields.Many2one('hr.cv.mapping')


    @api.multi
    def action_approve_remark(self):

        a = self.env['hr.cv.mapping'].browse(self.env.context.get('active_id'))
        for rec in a:
            qualification = ','.join(rec.qualification_details.mapped('name')) 
            professional = ','.join(rec.professional_qualification.mapped('name'))    
            tag_emp = rec.tagged_employee_ids.mapped('report_id.name')  
            designation = rec.job_id.name  
            manager = rec.env.ref("kw_generate_cv.generate_cv_manager_group").users
            email_to = ','.join(manager.mapped('employee_ids.work_email'))
            email_cc = rec.account_holder.work_email
            template_id = rec.env.ref('kw_generate_cv.cv_mapping_approve_mail_template')
            template_id.with_context(email_to=email_to,email_cc=email_cc,qualification=qualification,professional=professional,tag_emp=tag_emp,no_of_resources=rec.no_of_resources,designation=designation,min_exp_year=rec.min_exp_year).send_mail(rec.id,notif_layout="kwantify_theme.csm_mail_notification_light")
            rec.write({'state': 'approve'})
            self.env['cv_mapping_log'].sudo().create({
                    'remark': self.remark,
                    'state': rec.state,
                    'date': date.today(),
                    'action_taken_by': rec.env.user.employee_ids.id,
                })
class CvRejectWizard(models.TransientModel):
    _name = "cv_mapping_reject_wizard"
    _description = "CV User Reject Wizard"

    remark = fields.Text('Remark',track_visibility='onchange')
    reg_id = fields.Many2one('hr.cv.mapping')


    @api.multi
    def action_reject_remark(self):
        a = self.env['hr.cv.mapping'].browse(self.env.context.get('active_id'))
        for rec in a:
            qualification = ','.join(rec.qualification_details.mapped('name')) 
            professional = ','.join(rec.professional_qualification.mapped('name')) 
            tag_emp = rec.tagged_employee_ids.mapped('report_id.name')  
            designation = rec.job_id.name   
            manager = rec.env.ref("kw_generate_cv.generate_cv_manager_group").users
            mail_to = ','.join(manager.mapped('employee_ids.work_email'))
            mail_cc = rec.account_holder.work_email
            mail_template = rec.env.ref('kw_generate_cv.cv_mapping_reject_mail_template')
            mail_template.with_context(object=rec,mail_to=mail_to,mail_cc=mail_cc,qualification=qualification,professional=professional,tag_emp=tag_emp,no_of_resources=rec.no_of_resources,designation=designation,min_exp_year=rec.min_exp_year).send_mail(
            rec.id, notif_layout="kwantify_theme.csm_mail_notification_light")
            rec.write({'state': 'reject'})
            self.env['cv_mapping_log'].sudo().create({
                    'remark': self.remark,
                    'state': rec.state,
                    'date': date.today(),
                    'action_taken_by': rec.env.user.employee_ids.id,
                })
    

class CvCancelWizard(models.TransientModel):
    _name = "cv_mapping_cancel_wizard"
    _description = "CV User Cancel Wizard"

    remark = fields.Text('Remark',track_visibility='onchange')
    reg_id = fields.Many2one('hr.cv.mapping')
    
    @api.multi
    def action_cancel_remark(self):
        a = self.env['hr.cv.mapping'].browse(self.env.context.get('active_id'))
        for rec in a:
            qualification = ','.join(rec.qualification_details.mapped('name')) 
            professional = ','.join(rec.professional_qualification.mapped('name'))
            tag_emp = rec.tagged_employee_ids.mapped('report_id.name') 
            designation = rec.job_id.name       
            email_to = rec.requested_by.work_email
            email_cc = rec.account_holder.work_email
            template_id = rec.env.ref('kw_generate_cv.cv_mapping_cancel_mail_template')
            template_id.with_context(email_to=email_to,email_cc=email_cc,object=rec,qualification=qualification,professional=professional,tag_emp=tag_emp,no_of_resources=rec.no_of_resources,designation=designation,min_exp_year=rec.min_exp_year).send_mail(rec.id,
                                                                                            notif_layout="kwantify_theme.csm_mail_notification_light")
            rec.write({'state': 'cancel'})  
            self.env['cv_mapping_log'].sudo().create({
                    'remark': self.remark,
                    'state': rec.state,
                    'date': date.today(),
                    'action_taken_by': rec.env.user.employee_ids.id,
                })

        

