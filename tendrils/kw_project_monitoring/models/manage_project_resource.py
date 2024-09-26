from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date, datetime, time


class ManageProjectResources(models.Model):
    _name = "manage_project_resources"
    _description = "Manage Tendrils Project Resources"
    _rec_name = "project_id"
    
    
    def get_serial_no(self):
        count=1
        for record in self:
            record.sl_no = count + 1
            count = count + 1
            
    sl_no = fields.Integer("SL#", compute="get_serial_no")
    project_id = fields.Many2one('project.project',string='Project',)
    account_holder_id = fields.Many2one('hr.employee',string='Account Holder',readonly=True)
    delivery_person_id = fields.Many2one('hr.employee',string='Delivery Person',readonly=True)
    project_reviewer_id = fields.Many2one('hr.employee',string='Project Reviewer',readonly=True)
    sbu_id = fields.Many2one('kw_sbu_master',string='SBU',readonly=True)
    project_role = fields.Many2one('kwmaster_category_name',string='Project Role',)
    project_user_ids = fields.Many2many('hr.employee', string="Project Members")
    project_resource_type = fields.Selection([('active', 'Active'), ('all', 'All'), ('release', 'Release')],default='active')
    plan_start_date = fields.Date("Plan Start Date")
    plan_end_date =  fields.Date("Exp. Comp. Date")
    action_type = fields.Selection([('resource_allocation', 'Resource Allocation'), ('resource_release', 'Resource Release')],default='resource_allocation')
    all_date_from = fields.Date("Involvement Period From")
    all_date_to = fields.Date("Involvement Period To")
    allocate_days = fields.Integer("Involvement Period Days")
    
    @api.onchange('project_id')
    def get_project_details(self):
        self.account_holder_id = False
        self.delivery_person_id = False
        self.project_reviewer_id = False
        self.sbu_id = False
        if self.project_id:
            self.account_holder_id = self.project_id.crm_id.sales_person_id.id
            self.delivery_person_id = self.project_id.crm_id.sales_person_id.id
            self.project_reviewer_id = self.project_id.reviewer_id.id
            self.sbu_id = self.project_id.sbu_id.id
            
    def edit_button(self):
        pass
    
    def allocate_resource(self):
        pass
    
    def release_resource(self):
        pass