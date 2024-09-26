from datetime import date, datetime
from odoo import models,fields,api
# from odoo.addons.kw_hr_leaves.models import hr_leave

# start_date, end_date = hr_leave.lv_get_current_financial_dates()

class KwComputeCFEncashmentPeriod(models.Model):

    _name           = 'kw_compute_cf_encashment'
    _description    = "Compute Carry Forward and Encashment"
    _rec_name       = "employee_id"
    _order          = 'date_of_joining asc'


    employee_id     = fields.Many2one('hr.employee',string='Employee')
    emp_name        = fields.Char(related="employee_id.name",string="Name")
    emp_code        = fields.Char(related="employee_id.emp_code",string="Emp. Code")
    emp_designation = fields.Many2one(related="employee_id.job_id",string="Designation")
    leave_type_id   = fields.Many2one('hr.leave.type',string='Leave Type')
   
    fisc_year       = fields.Integer(string="Year")
    fisc_year_id    = fields.Many2one('account.fiscalyear', 'Fiscal Year')
    entitled        = fields.Float(string='Entitled')
    leave_taken     = fields.Float(string='Leave Taken')
    lapse_days      = fields.Float(string="Lapse Days")
    leave_balance   = fields.Float(string='Leave Balance')
    carry_forward   = fields.Float(string='Carry Forward')
    encashment      = fields.Float(string="Encashment")    
    
   
    cf_status       = fields.Selection(string="Carry Forward Status" ,selection=[('0', 'Draft'),('1', 'Allocation Created'),('2', 'Allocation Updated'),('5', 'Error Occured')],default='0')
    encash_status   = fields.Selection(string="Encashment Status" ,selection=[('0', 'Draft'),('1', 'Inserted'),('2', 'Updated'),('5', 'Error Occured')],default='0')
    
    pending_leave_request = fields.Boolean(string='Pending Leave Request',)
    
    branch          = fields.Char(string="Location",related="employee_id.job_branch_id.name")
    department      = fields.Char(string="Department",related="employee_id.department_id.name")
    division        = fields.Char(string="Division",related="employee_id.division.name")
    #section         = fields.Char(string="Section",related="employee_id.section.name")
    #designation     = fields.Char(string="Designation",related="employee_id.job_id.name")
    date_of_joining = fields.Date(string="Date of Joining",related="employee_id.date_of_joining",store=True)

    grade           = fields.Char(string="Grade",related="employee_id.grade.name")
    band            = fields.Char(string="Band",related="employee_id.emp_band.name")


    basic           = fields.Float(string='Basic')
    basic_encash    = fields.Float(string='Leave Encashment On Basic')
    gross           = fields.Float(string='Gross')
    gross_encash    = fields.Float(string='Leave Encashment On Gross')
    final_gross     = fields.Float(string="Final Gross")
    final_gross_encash     = fields.Float(string="Leave Encashment On Final Gross")
    ctc             = fields.Float(string='CTC')
    ctc_encash      = fields.Float(string='Leave Encashment On CTC')
    total_working_days = fields.Float(string="Total Working Days")
    current_financial_year = fields.Boolean("Current Financial Year",compute='_compute_current_financial_year',search="_lv_search_current_financial_year")
    previous_financial_year = fields.Boolean("Previous Financial Year",compute='_compute_previous_financial_year',search="_lv_search_previous_financial_year")
    encashment_eligible = fields.Boolean(string="Leave Encashment Eligible")
    applied_eos = fields.Selection([('Yes','Yes'),('No','No')],string="Resignated")
    
    @api.multi
    def _compute_current_financial_year(self):
        for record in self:
            pass 
    
    @api.multi
    def _lv_search_current_financial_year(self, operator, value):
        start_date , end_date = self.env['hr.leave'].lv_get_current_financial_dates()
        return [('fisc_year', '=', start_date.year)]

    @api.multi
    def _lv_search_previous_financial_year(self,operator,value):
        start_date , end_date = self.env['hr.leave'].lv_get_current_financial_dates()
        return [('fisc_year', '=', start_date.year - 1)]
    
    _sql_constraints = [
        ('employee_cf_cycle_uniq', 'unique(employee_id,leave_type_id,fisc_year)',
        "Employee carry forward and encashment details for the selected year already exists."),
    ]