from odoo import models, fields, api
import requests, json
import datetime
from datetime import date



class TourProjectBudget(models.Model):
    _name = "kw_tour_project_budget"
    _description = "Tour Project Budget"
    _order = "budget_amount desc"
    _rec_name = "budget_head_id"

    # def get_fiscal_year(self):
    #     current_fiscal = self.env['account.fiscalyear'].search(
    #         [('date_start', '<=', datetime.datetime.today().date()),
    #             ('date_stop', '>=', datetime.datetime.today().date())])
    #     return current_fiscal


    budget_head_id = fields.Many2one('kw_tour_budget_head', 'Budget Head')
    # fiscal_year = fields.Many2one('account.fiscalyear', string="Financial Year")
    project_id = fields.Many2one('crm.lead', 'Project')
    project_name = fields.Char(related='project_id.name',string= 'Project Name')
    project_code = fields.Char(related='project_id.code', string= 'Project Code')
    actual_project_id = fields.Many2one('project.project', 'Actual Project', compute='_compute_project_project',
                                        store=True)
    budget_amount = fields.Float('Budget Amount')
    remaining_amount = fields.Float(compute='_compute_remaining_amount', string='Remaining Amount')
    spent_amount = fields.Float(compute='_compute_remaining_amount', string='Spent Amount + Blocked Amount')
    budget_perc = fields.Float('Budget Used (%)', compute='_compute_get_budget_perc')
    threshold_limit = fields.Float('Threshold Limit (%)', default=80)
    tour_ids = fields.One2many('kw_tour', 'project_budget_id', string='Tours')
    settlement_ids = fields.One2many('kw_tour_settlement', 'project_budget_id', string='Settlements')

    def _CreateUpdateProjectBudget(self):
        budget_head_obj = self.env['kw_tour_budget_head']
        crm_lead_obj = self.env['crm.lead']
        project_project_obj = self.env['project.project']
        project_url = self.env.ref('kw_tour.kw_tour_project_budget_url_system_parameter').sudo().value
        header = {'Content-type': 'application/json', 'Accept': 'text/plain', }
        data = json.dumps({})
        resp_result = requests.post(project_url, headers=header, data=data)
        resp = json.loads(resp_result.text)
        if resp['retBudgetDa']:
            filtered_budget_id = [i['Budget_Head_ID'] for n, i in enumerate(resp['retBudgetDa']) if
                                  i['Budget_Head_ID'] not in resp['retBudgetDa'][n + 1:]]
            for record in list(set(filtered_budget_id)):
                budget_head = budget_head_obj.sudo().search([('kw_id', '=', record)], limit=1)
                filtered_budget_data = [d for d in resp['retBudgetDa'] if d['Budget_Head_ID'] == str(budget_head.kw_id)]
                for rec in filtered_budget_data:
                    lead = crm_lead_obj.sudo().search([('kw_workorder_id', '=', rec['ModuleID'])], limit=1)
                    if lead:
                        project_budget = self.sudo().search([('budget_head_id', '=', budget_head.id),
                                                             ('project_id', '=', lead.id)])
                        actual_project_id = project_project_obj.sudo().search([('crm_id', '=', lead.id),
                                                                               ('active', '=', True)], limit=1)
                        if project_budget:
                            project_budget.sudo().update({
                                'budget_amount': rec['Total_BudgetAmt'],
                                'actual_project_id': actual_project_id.id if actual_project_id else False
                            })
                        if not project_budget:
                            self.sudo().create({
                                'budget_head_id': budget_head.id,
                                'project_id': lead.id,
                                'budget_amount': rec['Total_BudgetAmt'],
                                'actual_project_id': actual_project_id.id if actual_project_id else False
                            })

        # tour_project_budget = self.env['kw_tour_project_budget'].sudo()
        # budget_config = self.env['tour_budget_account_config'].sudo().search([('budget_type', '=', 'project_budget')],
        #                                                                      limit=1)
        # project_account_codes = budget_config.account_code_ids.ids
        # project_budget_line_data = self.env['kw_sbu_project_budget_line'].sudo().search(
        #     [('account_code_id', 'in', project_account_codes), ('state', '=', 'validate')])
        # data_dict = {}
        # for rec in project_budget_line_data:
        #     if rec.id not in data_dict:
        #         data_dict[rec.id] = {
        #             'budget_head':None,
        #             'budget_amount': 0,
        #             'fiscal_year_id': None,
        #             'project_id':None,
        #         }
        #     if rec.id in data_dict and data_dict[rec.id]['budget_head'] == rec.account_code_id.account_sub_head_id.id \
        #         and data_dict[rec.id]['fiscal_year_id'] == rec.sbu_project_budget_id.fiscal_year_id.id \
        #             and data_dict[rec.id]['project_id'] == rec.project_id.crm_lead_id.id:
        #         data_dict[rec.id]['budget_amount'] +=  rec.total_amount
        #     else:
        #         data_dict[rec.id]['budget_head'] = rec.account_code_id.account_sub_head_id.id
        #         data_dict[rec.id]['fiscal_year_id'] = rec.sbu_project_budget_id.fiscal_year_id.id
        #         data_dict[rec.id]['project_id'] = rec.project_id.crm_lead_id.id
        #         data_dict[rec.id]['budget_amount'] = rec.total_amount
        #
        # for data in data_dict:
        #     head_id = self.env['kw_tour_budget_head'].sudo().search([('account_sub_head_id', '=', data_dict[data]['budget_head'])], limit=1).id
        #     project_budget = tour_project_budget.search([('budget_head_id', '=', head_id),
        #                                                  ('fiscal_year', '=', data_dict[data]['fiscal_year_id']),
        #                                                  ('project_id', '=', data_dict[data]['project_id'])])
        #     if project_budget:
        #         project_budget.sudo().update({
        #             'budget_amount': data_dict[data]['budget_amount'],
        #         })
        #     else:
        #         self.sudo().create({
        #             'budget_head_id': head_id,
        #             'project_id': data_dict[data]['project_id'] ,
        #             'budget_amount': data_dict[data]['budget_amount'],
        #             'fiscal_year':data_dict[data]['fiscal_year_id'],
        #         })
        #


    @api.depends('project_id')
    def _compute_project_project(self):
        project_obj = self.env['project.project']
        for record in self:
            record.actual_project_id = False
            project = project_obj.sudo().search([('crm_id', '=', record.project_id.id), ('active', '=', True)], limit=1)
            if project:
                record.actual_project_id = project.id

    @api.multi
    @api.depends('tour_ids', 'tour_ids.total_budget_expense', 'settlement_ids', 'settlement_ids.total_budget_expense')
    def _compute_remaining_amount(self):
        for record in self:
            total_tour_amount = sum(record.tour_ids.sudo().filtered(
                lambda r: r.cancellation_status is False and r.settlement_applied is False).mapped(
                'total_budget_expense'))
            total_settlement_amount = sum(record.settlement_ids.sudo().search(
                [('budget_head_id', '=', record.budget_head_id.id),
                 ('project_id', '=', record.project_id.id), ('state', 'not in', ['Draft','Rejected'])]).mapped(
                'total_budget_expense'))
            record.remaining_amount = record.budget_amount - total_settlement_amount - total_tour_amount
            record.spent_amount = total_settlement_amount + total_tour_amount

    @api.multi
    def _compute_get_budget_perc(self):
        for record in self:
            record.budget_perc = 0
            if record.budget_amount > 0:
                record.budget_perc = (record.budget_amount - record.remaining_amount)/record.budget_amount * 100

    @api.model
    def remind_pm_budget_limit(self):
        project_budget = self.sudo().search([]).filtered(lambda r: r.budget_perc >= r.threshold_limit)
        project_pm = project_budget.filtered(lambda r: r.actual_project_id and r.actual_project_id.emp_id).mapped(
            'actual_project_id.emp_id')
        template = self.env.ref('kw_tour.kw_tour_project_budget_limit_email_template')
        for pm in project_pm:
            budget_record = project_budget.filtered(lambda r: r.actual_project_id.emp_id == pm)
            template.with_context(email_to=pm.work_email, name=pm.name, budget_record=budget_record).send_mail(
                budget_record[-1].id, notif_layout="kwantify_theme.csm_mail_notification_light")

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None, is_integrated=False):
        if self.env.user.has_group('kw_tour.group_kw_tour_travel_desk') \
                or self.env.user.has_group('kw_tour.group_kw_tour_finance') \
                or self.env.user.has_group('kw_tour.group_kw_tour_admin'):
            args += []
        else:
            args += [('actual_project_id.emp_id.user_id', '=', self.env.user.id)]
        return super(TourProjectBudget, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                      access_rights_uid=access_rights_uid)

    @api.multi
    def action_view_details(self):
        tree_view_id = self.env.ref('kw_tour.view_kw_tour_budget_report_view_tree').id
        if not self.project_id:
            raise UserError("No project is associated with this record.")
        domain = [('project_id', '=', self.project_id.id)]
        return {
                'name': 'Tour Project Budget Report',
                'type': 'ir.actions.act_window',
                'res_model': 'kw_tour_budget_report',
                'view_mode': 'tree',
                'view_id': tree_view_id,
                'target': 'current', 
                'domain': domain,
            }