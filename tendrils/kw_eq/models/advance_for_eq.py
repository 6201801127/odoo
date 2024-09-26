from odoo import models, fields,api
from odoo.exceptions import ValidationError
from datetime import date



class AdvanceForApprovedEq(models.Model):
    _name = 'kw_advance_for_eq'
    _description = 'EQ Advance'
    _rec_name = 'eq_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    def get_eq(self):
        emp_ids = self.env.user.employee_ids.ids
        data = self.env['kw_eq_estimation'].sudo().search([('state','=','grant')])
        opp_list =[]
        for rec in data:
            if any(emp_id in [rec.kw_oppertuinity_id.pm_id.id] for emp_id in emp_ids):
                opp_list.append(rec.id)
        return [('id','in',opp_list)]
    

    eq_id =fields.Many2one('kw_eq_estimation',string='Opportunity Name',domain=get_eq)
    applied_by = fields.Many2one('hr.employee',string='PM Name',default=lambda self: self.env.user.employee_ids.id)
    advance_amount = fields.Float("Advance Amount",track_visibility='onchange')
    description = fields.Text("Description",track_visibility='onchange')
    contract_close_date=fields.Date("Expected Closing Date",track_visibility='onchange')
    opp_date=fields.Date("Renewal Date",track_visibility='onchange')
    status = fields.Selection(string="Status", selection=[('Draft', 'Draft'), ('Applied', 'Applied'), ('Approved', 'Approved'), ('Granted', 'Granted'), ('Allocated', 'Allocated'), ('Rejected', 'Rejected')],default='Draft',track_visibility='onchange')
    action_to_be_taken_by = fields.Many2one('hr.employee',track_visibility='onchange')
    action_to_be_taken_by_name=fields.Char('Pending At',track_visibility='onchange')
    is_account = fields.Boolean()
    is_ceo = fields.Boolean()
    advance_log_id = fields.One2many('kw_advance_eq_log','eq_log_id')
    account_sub_head_id = fields.Many2one('kw_eq_acc_head_sub_head','Account SubHead',domain=[('effective_date','<=',date.today()),('code','not in',('ADC','AWMS','AWMA','CS','CI','CSM'))])
    purchase_cost = fields.Float('Approved EQ Amount',track_visibility='onchange')
    workorder_id = fields.Many2one('crm.lead',string='Workorder Name',domain=[('type','=','opportunity'),('stage_id.code','=','workorder')])
    employee_role = fields.Char(string='Role',track_visibility='onchange')
    advance_month_ids = fields.Many2many('kw_advance_eq_month',string="Month",track_visibility='onchange')
    no_of_resource = fields.Integer(string="No of Resource",track_visibility='onchange')

    @api.onchange('account_sub_head_id')
    def _onchange_account_sub_head_id(self):
        if self.account_sub_head_id:
            for rec in self.eq_id.estimate_ids:
                if rec.account_subhead_id.id == self.account_sub_head_id.account_subhead_id.id:
                    self.purchase_cost = rec.purchase_cost
                
    @api.constrains('advance_amount')
    def date_constrains(self):
            if self.purchase_cost < self.advance_amount:
                raise ValidationError("Advance amount can not be greater than approved component amount.")    

    @api.model
    def create(self, vals):
        crm_data=self.env['crm.lead'].sudo().name_get()
        if crm_data:
            first_lead_id = crm_data[0][0]
            vals['eq_id'] = first_lead_id
        user_employee_ids = self.env.user.employee_ids.ids
        opportunities = self.env['kw_eq_estimation'].sudo().search([('state','=','grant')])
        pm_ids = opportunities.mapped('kw_oppertuinity_id.pm_id.id')

        if not any(emp_id in pm_ids for emp_id in user_employee_ids):
            raise ValidationError("You are not authorized to apply for an advance for EQ.")

        return super(AdvanceForApprovedEq, self).create(vals)

    @api.multi
    def apply_advance_for_eq(self):
        view_id = self.env.ref('kw_eq.kw_advance_eq_apply_wiz_form').id
        return {
            'name': 'Apply Remark',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_advance_eq_wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'target': 'new',
            'view_id': view_id,
            'context':{'eq_apply':True,'default_advance_eq_id':self.id}

        }
        

    @api.multi
    def approve_advance_for_eq(self):
        view_id = self.env.ref('kw_eq.kw_advance_eq_apply_wiz_form').id
        return {
            'name': 'Approve Remark',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_advance_eq_wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'target': 'new',
            'view_id': view_id,
            'context':{'eq_approve':True,'default_advance_eq_id':self.id}

        }


    @api.multi
    def grant_advance_for_eq(self):
        view_id = self.env.ref('kw_eq.kw_advance_eq_apply_wiz_form').id
        return {
            'name': 'Grant Remark',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_advance_eq_wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'target': 'new',
            'view_id': view_id,
            'context':{'eq_grant':True,'default_advance_eq_id':self.id}

        }
        

    @api.multi
    def reject_advance_for_eq(self):
        view_id = self.env.ref('kw_eq.kw_advance_eq_apply_wiz_form').id
        return {
            'name': 'Reject Remark',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_advance_eq_wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'target': 'new',
            'view_id': view_id,
            'context':{'default_advance_eq_id':self.id,'eq_reject':True}

        }
       

    @api.multi
    def disburse_advance_for_eq(self):
        view_id = self.env.ref('kw_eq.kw_advance_eq_apply_wiz_form').id
        return {
            'name': 'Allocate Remark',
            'type': 'ir.actions.act_window',
            'res_model': 'kw_advance_eq_wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'target': 'new',
            'view_id': view_id,
            'context':{'eq_allocate':True,'default_advance_eq_id':self.id}

        }
        
    @api.multi
    def view_eq_details(self):
        view_id_form = self.env.ref('kw_eq.kw_eq_estimation_view_form').id
        return {
            'name':"Estimation Details",
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.eq_id.id,
            'res_model': 'kw_eq_estimation',
            'views': [(view_id_form, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'self',
            'domain':[('state','=','grant')],
            'context':{'edit':False,'create':False,'delete':False,'duplicate':False}   
            }
    
    @api.multi
    def render_advance_eq_pending_actions(self):
        tree_view_id = self.env.ref('kw_eq.kw_advance_for_eq_take_action_tree').id
        form_view_id = self.env.ref('kw_eq.kw_advance_for_eq_take_action_form').id
        if self.env.user.has_group('kw_eq.group_eq_finance'):

            action = {
                    'type': 'ir.actions.act_window',
                    'name' : 'Take Actions',
                    'views': [(tree_view_id, 'tree'),(form_view_id,'form')],
                    'view_mode': 'tree,form,search',
                    'res_model': 'kw_advance_for_eq',
                    'domain':[('status','in',['Granted'])],
                    'context':{'advance_eq':True}}
        else:
            
            action = {
                    'type': 'ir.actions.act_window',
                    'name' : 'Pending Action',
                    'views': [(tree_view_id, 'tree'),(form_view_id,'form')],
                    'view_mode': 'tree,form',
                    'res_model': 'kw_advance_for_eq',
                    'domain':[('action_to_be_taken_by.user_id','=',self.env.user.id)],
                    }
        return action
    
    @api.multi
    def render_advance_eq_report_actions(self):
        tree_view_id = self.env.ref('kw_eq.kw_advance_for_eq_report_tree').id
        if self.env.user.has_group('kw_eq.group_eq_manager') or self.env.user.has_group('kw_eq.group_eq_finance') or self.env.user.has_group('kw_eq.group_eq_report_manager'):
            action = {
                    'type': 'ir.actions.act_window',
                    'name' : 'Report',
                    'views': [(tree_view_id, 'tree')],
                    'view_mode': 'tree,search',
                    'res_model': 'kw_advance_for_eq',
                    'domain':[],
                    }
        else:
            action = {
                    'type': 'ir.actions.act_window',
                    'name' : 'Report',
                    'views': [(tree_view_id, 'tree')],
                    'view_mode': 'tree',
                    'res_model': 'kw_advance_for_eq',
                    'domain':[('create_uid','=',self.env.user.id)],
                    }
        return action
    
            
class AdvanceForApprovedEqWizard(models.TransientModel):
    _name = 'kw_advance_eq_wizard'
    _description = 'EQ Advance'

    advance_eq_id = fields.Many2one('kw_advance_for_eq')
    remark = fields.Text("Remark")

    @api.multi
    def action_submit_reject_remark(self):
        action_id = self.env.ref('kw_eq.kw_advance_for_eq_action').id

        self.advance_eq_id.write({'status':'Rejected',
                    'action_to_be_taken_by': False,
                    'action_to_be_taken_by_name':'---',})
        
        self.advance_eq_id.advance_log_id.create({
                'action_taken_by':self.env.user.employee_ids.name,
                'log_status':'Rejected',
                'eq_log_id':self.advance_eq_id.id,
                'action_taken_on':date.today(),
                'action_remark':self.remark,

                 })
        
        template_id = self.env.ref('kw_eq.advance_eq_template')
        template_id.with_context(email_from=self.env.user.employee_ids.work_email,
                                 action_by=self.env.user.employee_ids.name,
                                 status=self.advance_eq_id.status,
                                 eq=self.advance_eq_id.eq_id.kw_oppertuinity_id.name,
                                 name=self.advance_eq_id.applied_by.name,
                                 mail_to=self.advance_eq_id.applied_by.work_email,).send_mail(self.advance_eq_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        return {
                    'type': 'ir.actions.act_url',
                    'tag': 'reload',
                    'url': f'/web#action={action_id}&model=kw_advance_for_eq&view_type=list',
                    'target': 'self',
                }
    
    @api.multi
    def action_submit_apply_remark(self):
        self.advance_eq_id.write({
            'status': 'Applied',
            'action_to_be_taken_by': self.advance_eq_id.applied_by.sbu_master_id.representative_id.id,
            'action_to_be_taken_by_name': self.advance_eq_id.applied_by.sbu_master_id.representative_id.name,
            'employee_role':'Pending at SBU Representative',
            })
        
        self.advance_eq_id.advance_log_id.create({
            'action_taken_by':self.env.user.employee_ids.name,
            'log_status':'Applied',
            'eq_log_id':self.advance_eq_id.id,
            'action_taken_on':date.today(),
            'action_remark':self.remark,
                })
        template_id = self.env.ref('kw_eq.advance_eq_template')
        template_id.with_context(name=self.advance_eq_id.applied_by.sbu_master_id.representative_id.name,
                                 mail_to=self.advance_eq_id.applied_by.sbu_master_id.representative_id.work_email,
                                 action_by=self.env.user.employee_ids.name,
                                 status=self.advance_eq_id.status,
                                 email_from=self.env.user.employee_ids.work_email,
                                 eq=self.advance_eq_id.eq_id.kw_oppertuinity_id.name,).send_mail(self.advance_eq_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        action_id = self.env.ref('kw_eq.kw_advance_for_eq_action').id
        return {
                'type': 'ir.actions.act_url',
                'tag': 'reload',
                'url': f'/web#action={action_id}&model=kw_advance_for_eq&view_type=list',
                'target': 'self',
            }
    
    @api.multi
    def action_submit_approve_remark(self):
        ceo_data = int(self.env['ir.config_parameter'].sudo().get_param('ceo'))
        employee_data =self.env['hr.employee'].sudo().search([('id','=',ceo_data)])
        action_id = self.env.ref('kw_eq.kw_advance_for_eq_action').id
        self.advance_eq_id.write({
            'status': 'Approved',
            'action_to_be_taken_by': employee_data.id,
            'action_to_be_taken_by_name': employee_data.name,
            'employee_role':'Pending at CEO',
            })
        self.advance_eq_id.advance_log_id.create({
            'action_taken_by':self.env.user.employee_ids.name,
            'log_status':'Approved',
            'eq_log_id':self.advance_eq_id.id,
            'action_taken_on':date.today(),
            'action_remark':self.remark,

                })
        template_id = self.env.ref('kw_eq.advance_eq_template')
        template_id.with_context(name=employee_data.name,mail_to=employee_data.work_email,
                                 action_by=self.env.user.employee_ids.name,
                                 status=self.advance_eq_id.status,
                                 email_from=self.env.user.employee_ids.work_email,
                                 eq=self.advance_eq_id.eq_id.kw_oppertuinity_id.name,).send_mail(self.advance_eq_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        return {
                'type': 'ir.actions.act_url',
                'tag': 'reload',
                'url': f'/web#action={action_id}&model=kw_advance_for_eq&view_type=list',
                'target': 'self',
            }
    
    @api.multi
    def action_submit_grant_remark(self):
        emp_data = self.env['res.users'].sudo().search([])
        accounts = emp_data.filtered(lambda user: user.has_group('kw_eq.group_eq_finance') == True)
        action_id = self.env.ref('kw_eq.kw_advance_for_eq_action').id
    
        self.advance_eq_id.write({
            'status': 'Granted',
            'action_to_be_taken_by': False,
            'action_to_be_taken_by_name': ','.join(accounts.mapped('name')) if accounts else '',
            'employee_role':'Pending at Finance',
            })
        
        self.advance_eq_id.advance_log_id.create({
            'action_taken_by':self.env.user.employee_ids.name,
            'log_status':'Granted',
            'eq_log_id':self.advance_eq_id.id,
            'action_taken_on':date.today(),
            'action_remark':self.remark,

                })
        
        template_id = self.env.ref('kw_eq.advance_eq_template')
        template_id.with_context(action_by=self.env.user.employee_ids.name,
                                 status=self.advance_eq_id.status,
                                 email_from=self.env.user.employee_ids.work_email,
                                 eq=self.advance_eq_id.eq_id.kw_oppertuinity_id.name,
                                 name='Concerns',mail_to=','.join(accounts.mapped('email')) if accounts else '').send_mail(self.advance_eq_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        return {
                'type': 'ir.actions.act_url',
                'tag': 'reload',
                'url': f'/web#action={action_id}&model=kw_advance_for_eq&view_type=list',
                'target': 'self',
            }
    @api.multi
    def action_submit_allocate_remark(self):
        action_id = self.env.ref('kw_eq.kw_advance_for_eq_action').id

        self.advance_eq_id.write({
            'status':'Allocated',
            'action_to_be_taken_by': False,
            'action_to_be_taken_by_name':'---' , 
            'employee_role':'---', 
        })

        self.advance_eq_id.advance_log_id.create({
            'action_taken_by':self.env.user.employee_ids.name,
            'log_status':'Allocated',
            'eq_log_id':self.advance_eq_id.id,
            'action_taken_on':date.today(),
            'action_remark':self.remark,

                })
        
        template_id = self.env.ref('kw_eq.advance_eq_template')
        template_id.with_context(action_by=self.env.user.employee_ids.name,
                                 email_from=self.env.user.employee_ids.work_email,
                                 eq=self.advance_eq_id.eq_id.kw_oppertuinity_id.name,
                                 status=self.advance_eq_id.status,name=self.advance_eq_id.applied_by.name,mail_to=self.advance_eq_id.applied_by.work_email).send_mail(self.advance_eq_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        return {
                'type': 'ir.actions.act_url',
                'tag': 'reload',
                'url': f'/web#action={action_id}&model=kw_advance_for_eq&view_type=list',
                'target': 'self',
            }



class AdvanceForApprovedEqLog(models.Model):
    _name = 'kw_advance_eq_log'
    _description = 'EQ Advance Log'

    eq_log_id = fields.Many2one('kw_advance_for_eq')
    action_taken_by =fields.Char(string='Action Taken By')
    log_status = fields.Char('Status')
    action_taken_on = fields.Date("Action Taken On")    
    action_remark= fields.Text("Remark")   


class AdvancemonthTable(models.Model):
    _name = 'kw_advance_eq_month'
    _description = 'EQ Advance month'

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")

