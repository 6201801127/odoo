import datetime
from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date , datetime



class KwIssueRepairDamageWiz(models.TransientModel):
    _name = 'kw_issue_repair_damage_wiz'
    _description = "Issue Repair Damage Wizard"

    stock_id = fields.Many2one('stock.quant', string="stock_id")
    remark = fields.Text(string='Remark')
    type = fields.Selection([
        ('issue', 'Issue'),
        ('repair', 'Repair'),
        ('damage', 'Damage'),
    ], string='Type',track_visibility='onchange',default='issue')
    # gatepass_type = fields.Selection([
    #     ('returnable', 'Returnable'),
    #     ('nonreturnable', 'Non-Returnable'),
    # ], string='Gatepass Type',track_visibility='onchange')
    requirement_type = fields.Selection([
        ('treasury', 'Treasury'),
        ('project', 'Project'),
    ], string='Requirement Type',default='treasury',track_visibility='onchange')
    department_id = fields.Many2one('hr.department',string='Department')
    # repair_damage = fields.Selection([
    #     ('repair', 'Repair'),
    #     ('damage', 'Damage'),
    # ], string='Repair/Damage',track_visibility='onchange')
    employee_id = fields.Many2one('hr.employee', string="Issued To")
    # repair_date = fields.Date('Repair Date')
    # repair_remark = fields.Text('Repair Remark')
    project_code = fields.Char(string='Project Code')
    
    @api.onchange('department_id')
    def onchange_department_id(self):
        if self.department_id:
            dept_emp = self.env['hr.employee'].search([('department_id','=',self.department_id.id)]).ids or []
            return {'domain': {'employee_id': [('id', 'in', dept_emp)]}}
    
    @api.multi
    def submit_type_action(self):
        if self.type in ['repair','damage']:
            self.stock_id.write({
               'remark':self.remark,
               'project_code':self.project_code,
            })
            
            if self.type == 'repair':
                self.env['kw_product_repair_log'].sudo().create({
                   'products':self.stock_id.product_id.id ,
                   'repair_id': self.stock_id.id,
                   'repaired_on': False,
                   'send_to_repair':date.today(),
                   'action_by':self.env.user.employee_ids.name,
                })
                self.update_asset_logs()
        else:
            self.stock_id.write({
                'department_id':self.department_id.id,
                'employee_id':self.employee_id.id if self.employee_id else False,
               'remark':self.remark,
               'requirement_type':self.requirement_type,
               'project_code':self.project_code,
               'status':'Issued',
               'is_issued':True,
               'is_asset':True,
            })
            self.env['kw_product_assign_release_log'].create({
                "assigned_on":self.write_date,
                "products": self.stock_id.product_id.id,
                "quantity": self.stock_id.quantity,
                "assigned_to": self.employee_id.id,
                "materil_id":self.stock_id.id ,
                "action_by": self.env.user.employee_ids.name,
                "status": 'Issued',
            })
            
          
            template_id = self.env.ref('kw_inventory.stock_quant_direct_asign_email_template')
            # print("self.===============",self.employee_id.work_email)
            template_id.with_context(to_mail=self.employee_id.work_email,user_name=self.employee_id.name,department= self.department_id.name,emp_code=self.employee_id.emp_code,sequence=self.stock_id.product_id.name,product_code=self.stock_id.product_id.default_code).send_mail(self.stock_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
            self.env.user.notify_success(message='Product Assigned successfully.')
        action_id = self.env.ref('kw_inventory.action_window_store_issue').id
        return {
                    'type': 'ir.actions.act_url',
                    'tag': 'reload',
                    'url': f'/web#action={action_id}&model=stock.quant&view_type=list',
                    'target': 'self',
                }
    @api.multi
    def submit_return(self):
        self.stock_id.write({
               'remark':self.remark,
               'project_code':'',
               'requirement_type':False,
            })
        self.env['kw_product_repair_log'].sudo().create({
                   'products':self.stock_id.product_id.id ,
                   'repair_id': self.stock_id.id,
                   'repaired_on': date.today(),
                   'send_to_repair':False,
                   'action_by':self.env.user.employee_ids.name,
                })
        self.update_asset_log()
        action_id = self.env.ref('kw_inventory.action_stock_quant_sent_to_repair').id
        return {
                    'type': 'ir.actions.act_url',
                    'tag': 'reload',
                    'url': f'/web#action={action_id}&model=stock.quant&view_type=list',
                    'target': 'self',
                }
    def update_asset_logs(self):
        asset_data = self.env['account.asset.asset'].sudo().search([('stock_quant_id','=',self.stock_id.id)])
        if asset_data:
            asset_data.repair_history_ids = [(0,0,{
                   'products':self.stock_id.product_id.id ,
                   'repair_id': self.stock_id.id,
                   'repaired_on':False,
                   'send_to_repair':date.today(),
                   'action_by':self.env.user.employee_ids.name,
                })]
    def update_asset_log(self):
        asset_data = self.env['account.asset.asset'].sudo().search([('stock_quant_id','=',self.stock_id.id)])
        if asset_data:
            asset_data.repair_history_ids = [(0,0,{
                   'products':self.stock_id.product_id.id ,
                   'repair_id': self.stock_id.id,
                   'repaired_on': date.today(),
                   'send_to_repair':False,
                   'action_by':self.env.user.employee_ids.name,
                })]
                    
        
class KwProductRepairLog(models.Model):
    _name = "kw_product_repair_log"
    _description = "Product Assign Release Log"
    
    products = fields.Many2one('product.product',string="Products/Items")
    repair_id = fields.Many2one('stock.quant',string='Repair Id')
    repaired_on = fields.Date(string='Repaired On',default=date.today())
    send_to_repair = fields.Date(string='Send to repair on',default=date.today())
    action_by = fields.Char(string='Action Taken By')
    asset_id = fields.Many2one('account.asset.asset')
    
    
    