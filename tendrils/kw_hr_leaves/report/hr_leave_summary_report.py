from datetime import datetime,date
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import format_date
from odoo import models, fields, api, tools, _

# from odoo.addons.kw_hr_leaves.models import hr_leave

# start_date, end_date = hr_leave.lv_get_current_financial_dates()

class HrLeaveSummaryReport(models.Model):
    _name           = "all_hr_leave_summary_report"
    _description    = "All Leave Summary Report"
    _auto           = False

    leave_id        = fields.Many2one('hr.leave',string='Leave')
    holiday_type_id = fields.Many2one('hr.leave.type',string="Leave Id",related="leave_id.holiday_status_id")
    leave_code      = fields.Char('Leave Code',related="holiday_type_id.leave_code")
    medical_doc     = fields.Binary(string='Document',related='leave_id.medical_doc',attachment=True)
    ref_name        = fields.Char(string='File Name',related='leave_id.ref_name')
    leave_address1  = fields.Text(string="Leave Address(1)",related='leave_id.leave_address1')
    leave_address2  = fields.Text(string="Leave Address(2)",related='leave_id.leave_address2')
    phone_no        = fields.Char(string="Mobile No",related='leave_id.phone_no')
    employee_id     = fields.Many2one('hr.employee',string="Employee Name")
    pending_at      = fields.Many2one('hr.employee',string="Pending With/ Approved By",compute='_compute_pending_taken')
    applied_by      = fields.Selection(selection=[('1','Employee'),('2','RA'),('3','HR Manager')],related='leave_id.applied_by',string='Applied By')
    department      = fields.Char(string="Department")
    division        = fields.Char(string="Division")
    section         = fields.Char(string="Section")
    practice        = fields.Char(string='Practice',related='employee_id.practise.name')
    designation     = fields.Char(string="Designation")
    applied_date    = fields.Date(string="Applied On")
    approved_date   = fields.Date(string='Approved On')
    date_from       = fields.Char(string="Date From",compute='_compute_from_to')
    date_to         = fields.Char(string="Date To",compute='_compute_from_to')
    leave_date      = fields.Date(string='Leave Date',compute='_compute_current_financial_year',search="_search_leave_date")
    req_date_from   = fields.Date(string="Date From")
    req_date_to     = fields.Date(string="Date To")
    leave_type      = fields.Char(string="Leave Type")
    no_of_days      = fields.Float(string="No. of days")
    status          = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Rejected'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved'),
        ('hold', 'On Hold'),
        ('forward', 'Forwarded'),
        ], string='Status')

    reason              = fields.Text(string="Reason",related='leave_id.name')
    leave_status_reason = fields.Text(string="Reason",related='leave_id.name')
    authority_remark    = fields.Text(string="Remark",related='leave_id.authority_remark')
    current_financial_year = fields.Boolean("Current Financial Year",compute='_compute_current_financial_year',search="_lv_search_current_financial_year") 
    previous_financial_year = fields.Boolean("Previous Financial Year",compute='_compute_current_financial_year',search="_lv_search_previous_financial_year") 
    company_id = fields.Many2one('res.company',string="Company")
    
    @api.multi
    def _compute_pending_taken(self):
        for leave in self:
            if leave.leave_id:
                if leave.status and leave.status in ['confirm','validate1','hold','forward','refuse']:
                    leave.pending_at = leave.leave_id.second_approver_id.id if leave.leave_id.second_approver_id else False
                else:
                    leave.pending_at = leave.leave_id.first_approver_id.id if leave.leave_id.first_approver_id else False

    @api.multi
    def _compute_from_to(self):
        for leave in self:
            if leave.leave_id:
                
                """From Day Half"""
                if leave.leave_id.request_unit_half :
                    if leave.leave_id.request_date_from_period == 'am':
                        leave.date_from = str(format_date(self.env , leave.leave_id.request_date_from) if leave.leave_id.request_date_from else '')+ " First Half"
                    if leave.leave_id.request_date_from_period == 'pm':
                        leave.date_from = str(format_date(self.env , leave.leave_id.request_date_from) if leave.leave_id.request_date_from else '')+ " Second Half"
                else:
                    leave.date_from = str(format_date(self.env , leave.leave_id.request_date_from) if leave.leave_id.request_date_from else '')

                """To Day Half"""
                if leave.leave_id.request_unit_half_to_period :
                    if leave.leave_id.request_date_to_period == 'am':
                        leave.date_to = str(format_date(self.env , leave.leave_id.request_date_to) if leave.leave_id.request_date_to else '')+ " First Half"
                    if leave.leave_id.request_date_to_period == 'pm':
                        leave.date_to = str(format_date(self.env , leave.leave_id.request_date_to) if leave.leave_id.request_date_to else '')+ " Second Half"
                else:
                    leave.date_to = str(format_date(self.env , leave.leave_id.request_date_to) if leave.leave_id.request_date_to else '')

    @api.multi
    def view_leave_details(self):
        self.ensure_one()
        actions = {
            'name': 'Leave Details',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'context': {'create': False,'edit': False,'delete': False,"toolbar":False}
            }
        
        if self._context and 'status_report' in self._context and self._context.get('status_report',False):
            form_res = self.env['ir.model.data'].get_object_reference('kw_hr_leaves', 'view_all_hr_leave_summary_report_form')
            actions.update({'res_model': 'all_hr_leave_summary_report','res_id':self.id,'target':'new'})
        else:
            form_res = self.env['ir.model.data'].get_object_reference('kw_hr_leaves', 'kw_apply_leave_primary_form_view')
            actions.update({'res_model': 'hr.leave','res_id':self.id,'target':'current'})
        
        form_id = form_res and form_res[1] or False
        actions['views'] = [(form_id, 'form')]    
        return actions

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""CREATE or REPLACE VIEW %s as (
            select hl.id as id,
                hl.id as leave_id,
                he.id as employee_id,
                he.company_id as company_id,
                dept.name as department,
                (select name from hr_department where id = he.division ) as division,
                (select name from hr_department where id = he.section ) as section,
                job.name as designation,
                date(hl.create_date) as applied_date,
                date(hl.action_taken_on) as approved_date,
                hlt.name AS leave_type,
                hl.number_of_days as no_of_days,
                hl.request_date_from as req_date_from,
                hl.request_date_to as req_date_to,
                hl.state as status
                from hr_leave hl
                join hr_leave_type hlt on hlt.id = hl.holiday_status_id
                left join hr_employee he on he.id = hl.employee_id
                LEFT OUTER JOIN hr_department dept on dept.id = he.department_id
                LEFT OUTER JOIN hr_job job on job.id = he.job_id
            ORDER BY id DESC
        )""" % (self._table))   

    @api.multi
    def _lv_search_current_financial_year(self, operator, value):
        start_date , end_date = self.env['hr.leave'].lv_get_current_financial_dates()
        return ['&', ('applied_date', '>=', start_date), ('applied_date', '<=', end_date)]
    
    @api.multi
    def _lv_search_previous_financial_year(self,operator, value):
        start_date , end_date = self.env['hr.leave'].lv_get_current_financial_dates()
        start = start_date - relativedelta(years=1)
        end = end_date - relativedelta(years=1)
        return ['&', ('applied_date', '>=', start), ('applied_date', '<=', end)]

    @api.multi
    def _search_leave_date(self, operator, value):
        leave_records = self.env['hr.leave'].sudo().search([
            ('date_from', '<=', value), ('date_to', '>=', value),
            ])
        return [('leave_id', 'in', leave_records.ids)]