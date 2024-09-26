# -*- coding: utf-8 -*-
from datetime import date
from odoo import tools
from odoo import models, fields, api
from odoo.addons.kw_hr_attendance.models.kw_daily_employee_attendance import DAY_STATUS_WORKING, DAY_STATUS_RWORKING
from odoo.modules.module import get_module_resource
import base64
import logging


class HrEmployeeInfo(models.Model):
    _name = "hr_employee_info"
    _description = "Employee Details"
    _auto = False
    _rec_name = 'name'
    _order = 'employees_rank asc,sort_no desc,name asc'

    # @api.model
    # def _default_image(self):
    #     image_path = get_module_resource('hr', 'static/src/img', 'default_image.png')
    #     return tools.image_resize_image_big(base64.b64encode(open(image_path, 'rb').read()))

    name = fields.Char(string=u'Employee')
    employee_id = fields.Many2one('hr.employee', string="Employee")
    # default=_default_image,
    image = fields.Binary("Photo", related='employee_id.image',
                          help="This field holds the image used as photo for the employee, limited to 1024x1024px.")
    image_medium = fields.Binary(
        "Medium-sized photo", attachment=True, related='employee_id.image_medium',
        help="Medium-sized photo of the employee. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved. "
             "Use this field in form views or some kanban views.")
    image_small = fields.Binary(
        "Small-sized photo", attachment=True, related='employee_id.image_small',
        help="Small-sized photo of the employee. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.")

    parent_id = fields.Many2one('hr_employee_info', string="Administrative Authority")
    child_ids = fields.One2many(related='employee_id.child_ids', string='Subordinates')
    coach_id = fields.Many2one('hr_employee_info', string="Functional Authority")
    emp_code = fields.Char(string=u'Employee Code', size=100)
    work_email = fields.Char(string=u'Work Email', size=100)
    work_phone = fields.Char(string=u'Work Phone No', size=18)
    mobile_phone = fields.Char(string=u'Mobile No', size=15)
    whatsapp_no = fields.Char(string=u'WhatsApp No.', size=15)
    epbx_no = fields.Char(string=u'EPBX ', size=100)
    resource_calendar_id = fields.Many2one('resource.calendar', string="Shift")
    date_of_joining = fields.Date(string="Joining Date")
    company_id = fields.Many2one('res.company', string="Company")
    base_branch_id = fields.Many2one('kw_res_branch', 'Base Location')
    base_branch_name = fields.Char(string='Location')
    job_branch_id = fields.Many2one('kw_res_branch', 'Work Location')
    acc_branch_unit_id = fields.Many2one('accounting.branch.unit', string='Branch Unit')
    department_id = fields.Many2one('hr.department', string="Department",
                                    domain="[('dept_type.code', '=', 'department')]")
    division = fields.Many2one('hr.department', string="Division", domain="[('dept_type.code', '=', 'division')]")
    section = fields.Many2one('hr.department', string="Practice", domain="[('dept_type.code', '=', 'section')]")
    practise = fields.Many2one('hr.department', string="Section", domain="[('dept_type.code', '=', 'practice')]")
    job_id = fields.Many2one('hr.job', string="Job Position")
    blood_group = fields.Many2one('kwemp_blood_group_master', string="Blood Group")
    employement_type = fields.Many2one('kwemp_employment_type', ondelete='cascade', string="Type of Employment")
    work_location_id = fields.Many2one('res.partner', string="Work Location ID",
                                       domain="[('parent_id', '=', company_id)]", help="Employee's working location.")

    active = fields.Boolean(string='Active', )

    work_location = fields.Char(string="Work Location", related='work_location_id.city', readonly=True)
    # sbu_type = fields.Selection(string='SBU Type', selection=[('sbu', 'SBU'), ('horizontal', 'Horizontal'), ('others', 'Others')])
    # sbu_master_id = fields.Many2one('kw_sbu_master', string="SBU", help="SBU")
    sort_no = fields.Integer(string="Sort No")
    employees_rank = fields.Integer(string="Employee Rank")

    @api.model_cr
    def init(self):
        # current_date = date.today().strftime('%Y-%m-%d')
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW %s as (
              SELECT emp.id AS id,
            emp.id AS employee_id,
            emp.name AS name,
            emp.active AS active,
            emp.parent_id AS parent_id,
            emp.coach_id AS coach_id,
            emp.emp_code AS emp_code,
            emp.work_email AS work_email,
            emp.work_phone AS work_phone,
            emp.mobile_phone AS mobile_phone,
            emp.whatsapp_no AS whatsapp_no,
            emp.epbx_no AS epbx_no,
            emp.resource_calendar_id AS resource_calendar_id,
            emp.date_of_joining AS date_of_joining,
            emp.company_id AS company_id,
            emp.base_branch_id AS base_branch_id,
            emp.base_branch_name AS base_branch_name,
            emp.job_branch_id AS job_branch_id,
            emp.acc_branch_unit_id AS acc_branch_unit_id,
            emp.department_id AS department_id,
            emp.division AS division,
            emp.section AS section,
            emp.practise AS practise,
            emp.job_id AS job_id,
            
            emp.blood_group AS blood_group,
            emp.employement_type AS employement_type,
            emp.work_location_id AS work_location_id,
        coalesce(case WHEN emp.emp_band > 0 THEN 
            (SELECT sort_no FROM kwemp_grade WHERE grade_id = (SELECT grade FROM hr_employee WHERE id = emp.id) 
            AND band_id = (SELECT emp_band FROM hr_employee WHERE id = emp.id) LIMIT 1)
        ELSE
            (SELECT sort_no FROM kwemp_grade WHERE grade_id = (SELECT grade FROM hr_employee WHERE id = emp.id)  LIMIT 1) 
        END,0) AS sort_no,
	    CASE
	    WHEN emp.id in (SELECT manager_id FROM hr_department WHERE dept_type = (SELECT id FROM kw_hr_department_type WHERE code = 'department')) THEN 1 
	    WHEN emp.id in (SELECT manager_id FROM hr_department WHERE dept_type = (SELECT id FROM kw_hr_department_type WHERE code = 'division')) THEN 2
	    WHEN emp.id in (SELECT manager_id FROM hr_department WHERE dept_type = (SELECT id FROM kw_hr_department_type WHERE code = 'section')) THEN 3
	    WHEN emp.id in (SELECT manager_id FROM hr_department WHERE dept_type = (SELECT id FROM kw_hr_department_type WHERE code = 'practice')) THEN 4
	    ELSE 5
	    END AS employees_rank	
	    FROM hr_employee emp 
	    where emp.active in (True,False)
			

        )""" % (self._table)
        # emp.sbu_master_id AS sbu_master_id,emp.sbu_type AS sbu_type,
        # print(query)
        self.env.cr.execute(query)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        res = super().search_read(self.get_domain(domain), fields, offset, limit, order)
        return res

    def get_domain(self, domain):
        dept_code = False
        cust_domain = domain
        dept_domain, dept_key = False, 0
        for i, j in enumerate(cust_domain):
            if j[0] == 'department_id' and type(j[2]) == int:
                dept_key = i
                dept_domain = j
        if dept_domain and dept_domain[0] == 'department_id' and type(dept_domain[2]) == int:
            dept_code = self.env['hr.department'].sudo().browse(dept_domain[2]).dept_type.code
            if dept_code:
                if dept_code == 'practice':
                    temp_domain = ('practise', '=', dept_domain[2])
                elif dept_code == 'department':
                    temp_domain = ('department_id', '=', dept_domain[2])
                else:
                    temp_domain = (dept_code, '=', dept_domain[2])
                domain[dept_key] = temp_domain

        return domain

    # @api.multi
    # def read(self,fields=None, load='_classic_read'):
    #     if not self.env.user.has_group('hr.group_hr_manager') and not self.env.user.has_group('kw_employee.group_payroll_manager'):
    #         fields = ['name','employee_id','image','image_medium','image_small','parent_id','child_ids','coach_id','emp_code','work_email','work_phone','mobile_phone','whatsapp_no','epbx_no','resource_calendar_id','date_of_joining','company_id','base_branch_id','base_branch_name','job_branch_id','acc_branch_unit_id','department_id','division','section','practise','job_id','sbu_master_id','blood_group','employement_type','work_location_id','active','work_location','sbu_type']
    #     res = super().read(fields,load)
    #     return res
