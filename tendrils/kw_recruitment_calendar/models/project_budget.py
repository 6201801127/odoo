from odoo import api, fields, models, _
from odoo import tools
import datetime
from datetime import date, timedelta
from odoo.exceptions import UserError, ValidationError
from datetime import date, timedelta
import calendar


class RecruitmentProjectBudgetLines(models.Model):
    _name = 'kw_recruitment_project_budget_lines'
    _description = "Recruitment Project Budget Lines"
    _rec_name = "code"

    @api.model
    def _get_year_list(self):
        years = 40
        return [(str(i), i) for i in range(years + 1)]

    name = fields.Char('Name')
    parent_ref_id = fields.Many2one('kw_recruitment_positions', string="Ref#")
    fiscalyr = fields.Many2one('account.fiscalyear', string="FY")
    employee_id = fields.Many2one('hr.employee', string="Employee", )
    dept_id = fields.Many2one('hr.department', string='Department', domain=[('dept_type.code', '=', 'department')])
    division = fields.Many2one('hr.department', string="Division", domain=[('dept_type.code', '=', 'division')])
    section = fields.Many2one('hr.department', string="Practice", domain=[('dept_type.code', '=', 'section')])
    practise = fields.Many2one('hr.department', string="Section", domain=[('dept_type.code', '=', 'practice')])
    designation = fields.Many2one('hr.job', string="Designation", required="1")
    project = fields.Many2one('crm.lead', string='Project')
    type_of_project = fields.Selection(string='Type Of Project',
                                       selection=[('work', 'Work Order'), ('opportunity', 'Opportunity')],
                                       default='work')
    resource_type = fields.Selection(string='Resource Type', track_visibility='onchange',
                                     selection=[('fresher', 'Fresher'), ('lateral', 'Lateral')], default='fresher')
    stage_id = fields.Many2one('hr.recruitment.stage', string="Stage")
    technology = fields.Many2one('kw_skill_master', string="Technology")
    branch_id = fields.Many2one('kw_res_branch', string='Branch')
    jan_budget = fields.Char('Jan')
    feb_budget = fields.Char('Feb')
    mar_budget = fields.Char('Mar')
    apr_budget = fields.Char('Apr')
    may_budget = fields.Char('May')
    jun_budget = fields.Char('Jun')
    jul_budget = fields.Char('Jul')
    aug_budget = fields.Char('Aug')
    sep_budget = fields.Char('Sep')
    octo_budget = fields.Char('Oct')
    nov_budget = fields.Char('Nov')
    dec_budget = fields.Char('Dec')
    planned_month = fields.Char('Month')
    status = fields.Selection([('draft', 'Draft'), ('sent', 'Sent'), ('approved', 'Approved'), ('grant', 'Grant')],
                              string="Status", default='draft', readonly=True)
    total_budget = fields.Integer('Total Budget', compute='_compute_total_budget', store=True)
    resource = fields.Integer()
    qualification_ids = fields.Many2many("kw_qualification_master", string="Qualification")
    exp_year = fields.Selection(string='Exp (Years)', selection='_get_year_list', default="0", required="1")
    resource_joined = fields.Many2one('hr.employee', 'Resource Joined')
    resource_tobe_joined = fields.Many2one('hr.applicant', 'Resource To Be Joined',
                                           domain=[('stage_id.code', '=', 'OA')])
    total_incurred = fields.Char('Total [Incurred]')
    total_remaining = fields.Integer('Total [Remaining]', compute='_compute_total_budget', store=True)
    hiring_status = fields.Selection(string='Hiring Status',
                                     selection=[('joined', 'Joined'), ('hold', 'Hold'), ('to_be_hired', 'To be hired'),
                                                ('offered', 'Offered'), ('joined_left', 'Joined & Left')])
    code = fields.Char(string="Reference No.", default="New", readonly="1")

    @api.model
    def create(self, values):
        code = self.env['ir.sequence'].next_by_code('self.pb_seq') or 'New'
        new_code = 'PB/' + code
        values['code'] = new_code
        result = super(RecruitmentProjectBudgetLines, self).create(values)
        self.env.user.notify_success("Records created successfully.")
        return result

    @api.onchange('resource_tobe_joined')
    def _onchange_resource_tobe_joined(self):

        monthly_ctc_amt = 0
        joining_date = self.resource_tobe_joined.joining_date
        if self.resource_tobe_joined and not self.resource_joined:
            if self.resource_tobe_joined.offer_id and self.resource_tobe_joined.offer_id.offer_type:
                monthly_ctc_amt = self.resource_tobe_joined.offer_id.average_1_month
        if self.resource_joined and self.resource_tobe_joined:
            raise ValidationError("Can't change the values.")

        self.get_monthly_ctc_data(monthly_ctc_amt, joining_date)

    @api.onchange('resource_joined')
    def _onchange_resource_joined(self):

        monthly_ctc_amt = 0
        joining_date = self.resource_joined.date_of_joining
        if self.resource_joined and self.resource_tobe_joined:
            monthly_ctc_amt = self.resource_joined.current_ctc
        self.get_monthly_ctc_data(monthly_ctc_amt, joining_date)

    @api.multi
    def get_monthly_ctc_data(self, monthly_ctc_amt, joining_date):
        monthly_ctc = {'4': monthly_ctc_amt,
                       '5': monthly_ctc_amt,
                       '6': monthly_ctc_amt,
                       '7': monthly_ctc_amt,
                       '8': monthly_ctc_amt,
                       '9': monthly_ctc_amt,
                       '10': monthly_ctc_amt,
                       '11': monthly_ctc_amt,
                       '12': monthly_ctc_amt,
                       '1': monthly_ctc_amt,
                       '2': monthly_ctc_amt,
                       '3': monthly_ctc_amt,
                       }
        if self.resource_tobe_joined and joining_date:
            acceptance_month = joining_date.month  # Offer Acceptance Month
            acceptance_day = joining_date.day  # Offer Acceptance day
            month_days = calendar.monthrange(joining_date.year, joining_date.month)[1]  # total month days
            incurred = 0
            if str(acceptance_month) in monthly_ctc:
                count = 0
                for rec in list(monthly_ctc)[list(monthly_ctc).index(str(acceptance_month)):]:
                    if count == 0:
                        incurred = round((month_days - acceptance_day) * (int(monthly_ctc.get(f'{rec}')) / month_days))
                        self.total_incurred = incurred
                        self.total_remaining = int(self.total_budget) - int(self.total_incurred)
                        count += 1
                    else:
                        incurred += int(monthly_ctc.get(f'{rec}'))
                        self.total_incurred = incurred
                        self.total_remaining = int(self.total_budget) - int(self.total_incurred)

    @api.onchange('apr_budget')
    def _onchange_apr_budget(self):
        for rec in self:
            if rec.apr_budget:
                rec.mar_budget = rec.feb_budget = rec.jan_budget = rec.dec_budget = rec.nov_budget = rec.octo_budget = rec.sep_budget = rec.aug_budget = rec.jul_budget = rec.jun_budget = rec.may_budget = rec.apr_budget

    @api.onchange('may_budget')
    def _onchange_may_budget(self):
        for rec in self:
            if rec.may_budget:
                rec.mar_budget = rec.feb_budget = rec.jan_budget = rec.dec_budget = rec.nov_budget = rec.octo_budget = rec.sep_budget = rec.aug_budget = rec.jul_budget = rec.jun_budget = rec.may_budget

    @api.onchange('jun_budget')
    def _onchange_jun_budget(self):
        for rec in self:
            if rec.jun_budget:
                rec.mar_budget = rec.feb_budget = rec.jan_budget = rec.dec_budget = rec.nov_budget = rec.octo_budget = rec.sep_budget = rec.aug_budget = rec.jul_budget = rec.jun_budget

    @api.onchange('jul_budget')
    def _onchange_jul_budget(self):
        for rec in self:
            if rec.jul_budget:
                rec.mar_budget = rec.feb_budget = rec.jan_budget = rec.dec_budget = rec.nov_budget = rec.octo_budget = rec.sep_budget = rec.aug_budget = rec.jul_budget

    @api.onchange('aug_budget')
    def _onchange_aug_budget(self):
        for rec in self:
            if rec.aug_budget:
                rec.mar_budget = rec.feb_budget = rec.jan_budget = rec.dec_budget = rec.nov_budget = rec.octo_budget = rec.sep_budget = rec.aug_budget

    @api.onchange('sep_budget')
    def _onchange_sep_budget(self):
        for rec in self:
            if rec.sep_budget:
                rec.mar_budget = rec.feb_budget = rec.jan_budget = rec.dec_budget = rec.nov_budget = rec.octo_budget = rec.sep_budget

    @api.onchange('octo_budget')
    def _onchange_octo_budget(self):
        for rec in self:
            if rec.octo_budget:
                rec.mar_budget = rec.feb_budget = rec.jan_budget = rec.dec_budget = rec.nov_budget = rec.octo_budget

    @api.onchange('nov_budget')
    def _onchange_nov_budget(self):
        for rec in self:
            if rec.nov_budget:
                rec.mar_budget = rec.feb_budget = rec.jan_budget = rec.dec_budget = rec.nov_budget

    @api.onchange('dec_budget')
    def _onchange_dec_budget(self):
        for rec in self:
            if rec.dec_budget:
                rec.mar_budget = rec.feb_budget = rec.jan_budget = rec.dec_budget

    @api.onchange('jan_budget')
    def _onchange_jan_budget(self):
        for rec in self:
            if rec.jan_budget:
                rec.mar_budget = rec.feb_budget = rec.jan_budget

    @api.onchange('feb_budget')
    def _onchange_feb_budget(self):
        for rec in self:
            if rec.feb_budget:
                rec.mar_budget = rec.feb_budget

    @api.depends('jan_budget', 'feb_budget', 'mar_budget', 'apr_budget', 'may_budget', 'jun_budget', 'jul_budget',
                 'aug_budget', 'sep_budget', 'octo_budget', 'nov_budget', 'dec_budget')
    def _compute_total_budget(self):
        for rec in self:
            total_budget = 0
            if rec.jan_budget:
                total_budget += int(rec.jan_budget)
            if rec.feb_budget:
                total_budget += int(rec.feb_budget)
            if rec.mar_budget:
                total_budget += int(rec.mar_budget)
            if rec.apr_budget:
                total_budget += int(rec.apr_budget)
            if rec.may_budget:
                total_budget += int(rec.may_budget)
            if rec.jun_budget:
                total_budget += int(rec.jun_budget)
            if rec.jul_budget:
                total_budget += int(rec.jul_budget)
            if rec.aug_budget:
                total_budget += int(rec.aug_budget)
            if rec.sep_budget:
                total_budget += int(rec.sep_budget)
            if rec.octo_budget:
                total_budget += int(rec.octo_budget)
            if rec.nov_budget:
                total_budget += int(rec.nov_budget)
            if rec.dec_budget:
                total_budget += int(rec.dec_budget)
            rec.total_budget = int(total_budget)
