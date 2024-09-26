from odoo import models, fields, api, _,tools
from datetime import date
import requests, json
from odoo.exceptions import ValidationError


class GetKwProjectBudget(models.TransientModel):
    _name = "get_project_budget_data"
    _description = "Get Project Budget Data From V5 "

    page_no = fields.Integer(string='Range From', required=True)
    length_of_page = fields.Integer(string='Range To', required=True)

    def create_project_budget_details(self):
        if self.page_no and self.length_of_page > 0:
            project_budget_api_url = self.env.ref('kw_budget.kw_project_budget_details').sudo().value
            header = {'Content-type': 'application/json', 'Accept': 'text/plain', }
            params_data_dict = {
                "pageno": self.page_no,
                "pagesize": self.length_of_page,
            }
            data = json.dumps(params_data_dict)
            resp_result = requests.post(project_budget_api_url, headers=header, data=data)
            resp = json.loads(resp_result.text)
            if resp:
                try:
                    query = ''
                    for project_budget_data in resp:
                        kw_wo_id = int(project_budget_data['kw_wo_id'])
                        kw_proj_id = int(project_budget_data['kw_proj_id']) if project_budget_data['kw_proj_id'] else None
                        kw_sbu_id = int(project_budget_data['int_sbu_id']) if project_budget_data['int_sbu_id'] else None
                        crm_lead = self.env['crm.lead'].sudo().search([('kw_workorder_id','=',kw_wo_id),('active','=',True)])
                        project_id = self.env['project.project'].sudo().search([('kw_id','=',kw_proj_id),('kw_id','>',0),'|', ('active', '=', True), ('active', '=', False)],limit=1)
                        sbu_data = self.env['kw_sbu_master'].sudo().search([('kw_id','=',kw_sbu_id),('kw_id','>',0),('active','=',True)],limit=1)
                        project_budget_table = self.env['kw_project_budget_master_data'].sudo().search([('kw_wo_id','=',kw_wo_id)])
                        if project_budget_table: ### Update the existing project budget
                            project_budget_table.order_value = project_budget_data['dec_wo_amt']
                            project_budget_table.crm_lead_id = crm_lead.id
                            project_budget_table.project_id = project_id.id
                            project_budget_table.project_name = project_budget_data['vch_proj_name']
                            project_budget_table.wo_name = project_budget_data['vch_wo_name']
                            project_budget_table.wo_code = project_budget_data['vch_wo_code']
                            project_budget_table.sbu_id = sbu_data.id
                            for line in project_budget_data['BudgetDetails']:
                                group_type = self.env['kw.group.type'].sudo().search([('name','=',line['vch_GrpType'])],limit=1)
                                group_head = self.env['account.account.type'].sudo().search([('name','=',line['vch_GrpHead'])],limit=1)
                                group_name = self.env['account.group.name'].sudo().search([('name','=',line['vch_GrpName'])],limit=1)
                                account_head = self.env['account.head'].sudo().search([('name','=',line['vch_Acc_Head'])],limit=1)
                                account_sub_head = self.env['account.sub.head'].sudo().search([('name','=',line['vch_Acc_Sub_Head'])],limit=1)

                                check_budget_line = self.env['kw_project_budget_line_items'].search([('project_crm_id','=',project_budget_table.id),('account_sub_head_id','=',account_sub_head.id)],limit=1)
                                if check_budget_line: ### update project budget line ids
                                    query += f"update kw_project_budget_line_items set budget_amount = coalesce({line['dec_budg_amt']},0.0) where id = {check_budget_line.id};"
                                else: ### create project budget line ids
                                    if group_type  and group_head and group_name and account_head and account_sub_head:
                                        query += f"insert into kw_project_budget_line_items(kw_line_id,user_type_id,group_head_id,group_name,account_head_id,account_sub_head_id,project_crm_id,budget_amount) \
                                        values ({line['kw_Acc_subhdID']}, {group_type.id},{group_head.id},{group_name.id},{account_head.id},{account_sub_head.id},{project_budget_table.id},{line['dec_budg_amt']});"
                        else: ### Create the project budget
                            project_budget_id = self.env['kw_project_budget_master_data'].sudo().create({'kw_wo_id':kw_wo_id,'sbu_id':sbu_data.id,'crm_lead_id':crm_lead.id,'project_id':project_id.id,'project_name':project_budget_data['vch_proj_name'] ,'wo_name':project_budget_data['vch_wo_name'],'wo_code':project_budget_data['vch_wo_code'],'order_value': project_budget_data['dec_wo_amt']})
                            if project_budget_id:
                                for line in project_budget_data['BudgetDetails']:  ###Create New Budget Line Items
                                    group_type = self.env['kw.group.type'].sudo().search([('name','=',line['vch_GrpType'])],limit=1)
                                    group_head = self.env['account.account.type'].sudo().search([('name','=',line['vch_GrpHead'])],limit=1)
                                    group_name = self.env['account.group.name'].sudo().search([('name','=',line['vch_GrpName'])],limit=1)
                                    account_head = self.env['account.head'].sudo().search([('name','=',line['vch_Acc_Head'])],limit=1)
                                    account_sub_head = self.env['account.sub.head'].sudo().search([('name','=',line['vch_Acc_Sub_Head'])],limit=1)
                                    if group_type  and group_head and group_name and account_head and account_sub_head:
                                        query += f"insert into kw_project_budget_line_items(kw_line_id,user_type_id,group_head_id,group_name,account_head_id,account_sub_head_id,project_crm_id,budget_amount) \
                                        values ({line['kw_Acc_subhdID']},{group_type.id},{group_head.id},{group_name.id},{account_head.id},{account_sub_head.id},{project_budget_id.id},{line['dec_budg_amt']});"

                    if len(query) >0:
                        self._cr.execute(query)


                    return {
                        'status': 200,
                        'error': 0,
                    }
                except Exception as e:
                    self.env['kw_kwantify_integration_log'].sudo().create({
                        'name': 'Project Budget Data Sync',
                        'error_log': e,
                        'response_result': resp,
                        'request_params': project_budget_api_url,
                    })
                    return {'error': str(e), 'status': 500,'Reference ID': project_budget_data['kw_wo_id']}
        else:
            raise ValidationError("Page Number and Page Length Should Greater Then 0.")




class KwProjectBudgetSyncData(models.Model):

    _name = "kw_project_budget_master_data"
    _description = "Kw Project Budget Data Sync"
    _rec_name = 'workorder_name'


    kw_wo_id = fields.Integer("Kw WorkOrder Id")
    crm_lead_id = fields.Many2one('crm.lead',"Work Order")
    project_id = fields.Many2one('project.project',"Project")
    project_name = fields.Char("Kw Project Name")
    # sbu_id = fields.Many2one('kw_sbu_master',"SBU",related='project_id.sbu_id')
    sbu_id = fields.Many2one('kw_sbu_master',"SBU")
    wo_name = fields.Char("WO Name")
    wo_code = fields.Char("WO Code")
    project_budget_ids = fields.One2many('kw_project_budget_line_items','project_crm_id')
    workorder_name = fields.Char(string='Combination', compute='_compute_fields_workorder_name', store=True)
    order_value = fields.Float(string='Order Value')

    @api.depends('wo_name', 'wo_code')
    def _compute_fields_workorder_name(self):
        for rec in self:
            rec.workorder_name = rec.wo_name + ' ' + rec.wo_code

    def name_get(self):
        result = []
        for rec in self:
            name = str(rec.wo_code +' - '+ rec.wo_name )
            result.append((rec.id, name))
        return result



class KwProjectBudgetLineItems(models.Model):

    _name = "kw_project_budget_line_items"
    _description = "Kw Project Budget Master"


    user_type_id = fields.Many2one('kw.group.type')
    group_head_id = fields.Many2one('account.account.type')
    group_name = fields.Many2one('account.group.name')
    account_head_id = fields.Many2one('account.head')
    account_sub_head_id = fields.Many2one('account.sub.head')
    project_crm_id = fields.Many2one('kw_project_budget_master_data',ondelete='cascade',)
    budget_amount = fields.Float("Budget Amount")
    actual_amount = fields.Float("Actual Amount",compute='_get_actual_amount')
    kw_line_id = fields.Integer("Kw Line Id")
    old_fy_balance = fields.Float(string="Old FY Balance")
    balance = fields.Float(string="Balance", compute='_get_balance_amount')

    @api.multi
    def _get_actual_amount(self):
        for rec in self:
            move_line_ids = self.env['account.move.line'].search([('project_wo_id','=',rec.project_crm_id.id),('budget_type','=','project'),('account_id.account_sub_head_id','=',rec.account_sub_head_id.id)])
            rec.actual_amount = sum(move_line_ids.mapped('balance'))

    @api.multi
    def _get_balance_amount(self):
        for rec in self:
            rec.balance = rec.budget_amount - (rec.old_fy_balance + rec.actual_amount)

    @api.multi
    def get_voucher_details(self):
        return {
            'name': 'Preview Vouchers',
            'type': 'ir.actions.client',
            'tag': 'kw_accounting.preview_budget_account_vouchers',
            'target': 'new',
            'context': {'active_id': self.id}
        }