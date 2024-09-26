from odoo import models, fields, api
# from datetime import date, datetime
from odoo.exceptions import ValidationError

class ResourceBudget(models.Model):
    _name = 'kw_resource_budget'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Resource Budget Allocation"
    _rec_name = 'work_order_id'

    fiscal_year = fields.Many2one("account.fiscalyear", string="Fiscal Year",domain="[('id', 'in', available_fiscal_year_ids)]")
    work_order_id = fields.Many2one('fy_wise_budget_plan', string="WorkOrder",track_visibility='onchange')
    wo_code = fields.Char(string="Work Order Code",track_visibility='onchange')
    account_line_ids = fields.One2many('kw_account_code_line', 'resource_budget_id',track_visibility='onchange')
    project_name = fields.Char("Project",related="work_order_id.fy_work_order_id.project_name")
    sbu_id = fields.Many2one('kw_sbu_master',"SBU",related='work_order_id.fy_work_order_id.sbu_id')
    client_name = fields.Char(string="Client")
    order_name = fields.Char(string="Order Name")
    order_value = fields.Float(string="Order Value")
    order_date = fields.Date(string="Order Date")
    account_holder_id = fields.Many2one('hr.employee',string="Account holder name")
    presale_member_id = fields.Many2one('hr.employee',related="work_order_id.fy_work_order_id.crm_lead_id.presales_id", string="Presale Member")
    delivery_manager_id = fields.Many2one('hr.employee', string="Delivery Manager")
    project_manager_id = fields.Many2one('hr.employee', related="work_order_id.fy_work_order_id.crm_lead_id.pm_id", string="Project Manager")
    available_fiscal_year_ids = fields.Many2many('account.fiscalyear', compute='_compute_available_fiscal_years',store=False)

    @api.onchange('fiscal_year','work_order_id')
    def _onchange_fiscal_year(self):
        if self.fiscal_year or self.work_order_id:
            self.wo_code = self.work_order_id.fy_work_order_id.wo_code
            self.client_name = self.work_order_id.fy_work_order_id.crm_lead_id.client_name
            self.order_name = self.work_order_id.fy_work_order_id.wo_name
            self.order_value = self.work_order_id.fy_work_order_id.order_value
            self.order_date = self.work_order_id.fy_work_order_id.crm_lead_id.date_open.date()
            self.account_line_ids = [(5, 0, 0)]
            budget_allocate_lines = self.env['fy_wise_budget_allocate_line'].search([
                ('fy_budget_allocation_id', '=', self.work_order_id.id),
                ('fiscal_year', '=', self.fiscal_year.id)
            ])
            new_lines = []
            for line in budget_allocate_lines:
                new_line = {
                    'account_code_id': line.account_head_id.id,
                    'group_head_id': line.group_head_id.id,
                    'group_name_id': line.group_name_id.id,
                    'account_head_id': line.account_head_id.id,
                    'account_sub_head_id': line.account_sub_head_id.id,
                    'budget': line.budget_to_be_planned
                    # 'fy_wise_budget_allocate_line_id': line.id
                }
                new_lines.append((0, 0, new_line))
            self.account_line_ids = new_lines


    @api.onchange('work_order_id')
    def _onchange_work_order_id(self):
        self.fiscal_year = False 
        self._compute_available_fiscal_years()

    @api.depends('work_order_id')
    def _compute_available_fiscal_years(self):
        for record in self:
            if record.work_order_id:
                budget_allocate_lines = self.env['fy_wise_budget_allocate_line'].search([
                    ('fy_budget_allocation_id', '=', record.work_order_id.id)
                ])
                fiscal_year_ids = budget_allocate_lines.mapped('fiscal_year.id')
                record.available_fiscal_year_ids = fiscal_year_ids
            else:
                record.available_fiscal_year_ids = []      


    def update_account_details(self):
        for record in self:
            if not record.work_order_id:
                continue
            updated = False
            existing_lines = {line.account_code_id.id: line for line in record.account_line_ids}
            for fy_allocate_line in record.work_order_id.fy_account_line_ids:
                for budget_code_line in fy_allocate_line.fy_budget_id:
                    account_code_id = budget_code_line.account_code_id.id
                    if account_code_id in existing_lines:
                        kw_line = existing_lines[account_code_id]
                        if kw_line.budget != budget_code_line.budget or kw_line.total_balance != budget_code_line.available_budget:
                            changes = {}
                            if kw_line.budget != budget_code_line.budget:
                                changes['budget'] = budget_code_line.budget
                            if kw_line.total_balance != budget_code_line.available_budget:
                                changes['total_balance'] = budget_code_line.available_budget
                            kw_line.write(changes)
                            updated = True

                    else:
                        pass

            if updated:
                record.message_post(body="Budget and total balance have been updated.")
            else:
                pass


class AccountCodeLine(models.Model):
    _name = 'kw_account_code_line'
    _description = "Budget Set Account Wise "

    account_code_id = fields.Many2one('account.account', string="Account Code")
    group_head_id = fields.Many2one('account.account.type',  string="Group Head")
    group_name_id = fields.Many2one('account.group.name', string="Group Name")
    account_head_id = fields.Many2one('account.head', string="Account Head")
    account_sub_head_id = fields.Many2one("account.sub.head", string="Account Sub Head")
    budget = fields.Float('Budget')
    resource_budget_id = fields.Many2one('kw_resource_budget', string="Work Order")
    resource_add_ids = fields.One2many('kw_resource_add', 'account_code_id')
    total_spent = fields.Float(string="Total Spent")
    total_balance = fields.Float(string="Balance",compute="get_total_budget_balance")
    out_source = fields.Float('Out-Source(I)')
    order_date = fields.Date(string="Order Date",compute="_compute_order_date")
    acc_fiscal_year = fields.Many2one('account.fiscalyear', string="Fiscal Year", compute="_compute_fiscal_year", store=True)
    ctc_perc_data = fields.Char(string="CTC Per", compute="get_ctc_percent", store=False)
    total_ctc_data = fields.Char(string="CTC Per", compute="get_ctc_total", store=False)

    @api.depends('resource_add_ids.tag_resource_id')
    def get_ctc_total(self):
        for record in self:
            contract = self.env['hr.contract'].sudo().search([('employee_id', 'in', record.resource_add_ids.mapped('tag_resource_id').ids), ('state', '=', 'open')])
            self.total_ctc_data = sum(ctc.wage for ctc in contract) + self.out_source

            # self.total_ctc_data = sum(emp.current_ctc for emp in record.resource_add_ids.mapped('tag_resource_id')) + self.out_source


    @api.depends('resource_add_ids.tag_resource_id', 'total_balance')
    def get_ctc_percent(self):
        for record in self:
            # total_ctc = sum(emp.current_ctc for emp in record.resource_add_ids.mapped('tag_resource_id'))
            contract = self.env['hr.contract'].sudo().search(
                [('employee_id', 'in', record.resource_add_ids.mapped('tag_resource_id').ids), ('state', '=', 'open')])
            total_ctc_data = sum(ctc.wage for ctc in contract)
            if record.total_balance > 0:
                record.ctc_perc_data = f"{total_ctc_data / record.total_balance * 100:.2f}%"
            else:
                record.ctc_perc_data = "0.00%"

    @api.depends('resource_budget_id.fiscal_year')
    def _compute_fiscal_year(self):
        for record in self:
            record.acc_fiscal_year = record.resource_budget_id.fiscal_year if record.resource_budget_id else False

    @api.depends('resource_budget_id.order_date')
    def _compute_order_date(self):
        for record in self:
            record.order_date = record.resource_budget_id.order_date


    @api.multi
    def add_details_func(self):
        self.ensure_one()
        form_view_id = self.env.ref('kw_budget.view_details_kw_resource_budget_form').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Account Line Details',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': form_view_id,
            'res_model': 'kw_account_code_line',
            'res_id': self.id,
            'target': 'new',
            'flags': {'mode': 'edit'}
        }


    @api.depends('budget','total_spent')
    def get_total_budget_balance(self):
        for total_amount in self:
            total_amount.total_balance = (total_amount.budget - total_amount.total_spent)


class ResourceAddBudgetWise(models.Model):
    _name = 'kw_resource_add'
    _description = "Resource Set Account Wise "

    account_code_id = fields.Many2one('kw_account_code_line')
    role_id = fields.Many2one('kwmaster_role_name',string="Role", required=True)
    category_id =fields.Many2one('kwmaster_category_name',string="Category", required=True)
    tag_resource_id = fields.Many2one('hr.employee',string="Tag Resource", required=True)
    resource_ids = fields.Many2many('hr.employee',string="Tag Resource",)
    availability_type = fields.Selection([('1','One Third'), ('2','50:50'), ('3','Fixed to One'), ('4','Two Third')],string="Availability",required=True)
    involvement_period_from = fields.Date(string="Involvement Period From", required=True)
    involvement_period_to = fields.Date(string="Involvement Period To", required=True)
    engaged_data = fields.Char(string="Engaged",store=False,compute="get_calculate_engaged_percent")
    role_ids = fields.Many2many('kwmaster_role_name', 'kw_resource_add_kwmaster_role_name_rel',)
    category_ids = fields.Many2many('kwmaster_category_name', 'kw_resource_add_kwmaster_category_name_rel',)


    def get_calculate_engaged_percent(self):
        for rec in self:
            if rec.availability_type == '1':
                rec.engaged_data = '33.33%'
            elif rec.availability_type == '2':
                rec.engaged_data = '50%'
            elif rec.availability_type == '3':
                rec.engaged_data = '100%'
            elif rec.availability_type == '4':
                rec.engaged_data = '66.66%'

    @api.constrains('involvement_period_from', 'involvement_period_to')
    def _check_involvement_period(self):
        for record in self:
            if record.account_code_id and record.account_code_id.acc_fiscal_year:
                fiscal_year = record.account_code_id.acc_fiscal_year
                if (record.involvement_period_from < fiscal_year.date_start or
                        record.involvement_period_from > fiscal_year.date_stop or
                        record.involvement_period_to < fiscal_year.date_start or
                        record.involvement_period_to > fiscal_year.date_stop):
                    raise ValidationError(
                        "Involvement periods must fall within the fiscal year."
                    )

    @api.onchange('role_id')
    def get_role(self):
        self.category_id = False
        self.tag_resource_id = False
        context = dict(self._context)
        resource_id = self.env['kw_account_code_line']
        data = resource_id.browse(context.get("active_id")).account_sub_head_id.id
        role = self.env['sub_head_wise_role_tagging'].sudo().search([('account_sub_head_id', '=', data)])
        role_list = [rec.role_id.id for rec in role]
        self.role_ids = False
        self.role_ids = [(4, rec) for rec in role_list]

    @api.onchange('role_id', 'category_id')
    def get_category(self):
        self.category_ids = False
        self.tag_resource_id = False
        if self.role_id:
            category = self.env['sub_head_wise_role_tagging'].sudo().search([('role_id', '=', self.role_id.id)])
            category_list = [rec.category_ids.ids for rec in category]
            flat_category_list = [item for sublist in category_list for item in sublist]
            self.category_ids = [(4, rec_id) for rec_id in flat_category_list]

    @api.onchange('role_id','category_id')
    def _get_onchange_role(self):
        self.resource_ids = False
        context = dict(self._context)
        resource_id = self.env['kw_account_code_line']
        tag_resource = resource_id.browse(context.get("active_id"))
        domain = self.env['hr.employee'].sudo().search([('emp_category', '=', self.category_id.id), ('sbu_master_id','=',tag_resource.resource_budget_id.sbu_id.id),('sbu_type','=','sbu')]).mapped('id')
        if self.role_id or self.category_id:
            self.resource_ids =[(4, rec) for rec in domain]
   