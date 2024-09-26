import io
import base64
import xlsxwriter
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date, datetime, time
from odoo.http import request, content_disposition


class KWNewProjectsOfProjectMonitoring(models.Model):
    _name           = "kw_project_monitoring_new_projects"
    _description  = "New Projects"
    _rec_name='fy_id'
    
    
    def _default_financial_year(self):
            current_fiscal = self.env['account.fiscalyear'].search(
                [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
            return current_fiscal
        
        
    fy_id = fields.Many2one('account.fiscalyear',default=lambda self: self._default_financial_year(),string='Financial Year',required=True)
    order_type=fields.Selection([
        (1, 'Opportunity'),
        (2, 'Project Order'),
        (3, 'Work Order'),
        ], 'Order Type', default=3,required=True)
    project_type_id = fields.Many2one('kw_project_type_master', "Project Type",required=True)
    
    
    project_ids = fields.One2many('pm_tag_projects', 'new_project_id', string="Projects")
    
    @api.onchange('fy_id')
    def _onchange_fy_id(self):
        if self.fy_id:
            self.project_ids = [(5, 0, 0)]  # Clear existing lines
            # Fetch related records from pm_tag_projects based on fy_id
            related_projects = self.env['pm_tag_projects'].search([('fiscal_id','=',self.fy_id.id)])
            project_lines = []
            for project in related_projects:
                project_lines.append((0, 0, {
                    'wo_code': project.wo_code,
                    'wo_name': project.wo_name,
                    'client_name': project.client_name,
                    'project_id': project.project_id,
                    'wo_cost': project.wo_cost,
                    'wo_issue_date': project.wo_issue_date,
                    'account_holder_id': project.account_holder_id,
                    'reviewer_id': project.reviewer_id,
                    'lead_id': project.lead_id,
                    
                }))
            self.project_ids = project_lines
        else:
            self.project_ids = [(5, 0, 0)]
      
class PMtaggingProjectsProject(models.Model):
    _name = "pm_tag_projects"
    _auto = False
    
    def get_serial_no(self):
        count=1
        for record in self:
            record.sl_no = count + 1
            count = count + 1
            
    
    new_project_id = fields.Many2one('kw_project_monitoring_new_projects')
    sl_no = fields.Integer("SL#", compute="get_serial_no")
    wo_code = fields.Char("Work Order Code")
    wo_name = fields.Char("Work Order Name")
    client_name = fields.Char("Client Name")
    project_id = fields.Many2one('project.project', "Project Name")
    # module_id = fields.Many2one('ir.module.module', "Module Name")
    wo_cost = fields.Float("Work Order Cost")
    wo_issue_date = fields.Date("Work Order Issue date")
    account_holder_id = fields.Many2one('hr.employee', "Account Holder")
    reviewer_id = fields.Many2one('hr.employee', "Reviewer")
    pm_id = fields.Many2one('hr.employee', "Project Manager")
    lead_id = fields.Many2one('crm.lead')
    fiscal_id = fields.Many2one('account.fiscalyear', string='Financial Year')
    
    @api.model_cr
    def init(self):
        # Drop the existing table if it exists
        self.env.cr.execute(f"DROP TABLE IF EXISTS {self._table} CASCADE")
        
        # Create the new table
        create_table_query = f"""
            CREATE TABLE {self._table} (
                id serial PRIMARY KEY,
                new_project_id INTEGER,
                lead_id INTEGER,
                sl_no INTEGER,
                wo_name VARCHAR,
                wo_code VARCHAR,
                client_name VARCHAR,
                project_id INTEGER,
                pm_id INTEGER,
                wo_cost FLOAT,
                wo_issue_date DATE,
                account_holder_id INTEGER,
                reviewer_id INTEGER,
                fiscal_id INTEGER
            )
        """
        self.env.cr.execute(create_table_query)

        # Populate the new table with data
        # insert_data_query = f"""
        #     INSERT INTO {self._table} (lead_id,wo_name,wo_code, client_name, project_id, wo_cost, wo_issue_date, account_holder_id, reviewer_id,pm_id,fiscal_id)
        #     SELECT
        #         cl.id AS lead_id,
        #         cl.name AS wo_name,
        #         cl.code AS wo_code,
        #         cl.client_name AS client_name,
        #         cl.project_id AS project_id,
        #         cl.planned_revenue AS wo_cost,
        #         cl.date_open AS wo_issue_date,
        #         cl.sales_person_id AS account_holder_id,
        #         cl.reviewer_id AS reviewer_id,
        #         cl.pm_id AS pm_id,
        #         (select id from account_fiscalyear fy where cl.create_date between fy.date_start and fy.date_stop) AS fiscal_id
        #     FROM crm_lead cl
        #     WHERE cl.pm_id IS NULL AND cl.pac_status IN (2, 3)
        # """
        # self.env.cr.execute(insert_data_query)

    
    def tag_pm_to_project(self):
        view_id = self.env.ref('kw_project_monitoring.pm_tag_wizard_view_form').id
        return {
            'name': 'Assign Project Manager',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'tag_project_manager_wizard',
            'view_id': view_id,
            'context': {'default_lead_id': self.lead_id.id,'default_workorder_name': self.wo_name,'default_workoder_code': self.wo_code,'default_client_name': self.client_name,'default_workorder_date': self.wo_issue_date,'default_account_holder_id': self.account_holder_id.id,'default_reviewer_id': self.reviewer_id.id},
            'target': 'new',
        }

class TagProjectManagerWizard(models.TransientModel):
    _name = 'tag_project_manager_wizard'
    _description = 'Tag Project Manager Wizard'

    def get_serial_no(self):
        count=1
        for record in self:
            record.sl_no = count + 1
            count = count + 1
            
    def _get_project_manager_domain(self):
        project_manager_group = self.env.ref('project.group_project_manager')
        return [('user_id', 'in', project_manager_group.users.ids)]
         
    project_id = fields.Many2one('project.project', "Project Name" ,readonly=True)
    lead_id = fields.Many2one('crm.lead')
    workorder_name = fields.Char("Work Order Name" ,readonly=True)
    account_holder_id = fields.Many2one('hr.employee', "Account Holder Name" ,readonly=True)
    reviewer_id = fields.Many2one('hr.employee', "Reviewer" ,readonly=True)
    workoder_code = fields.Char("Work Order Code" ,readonly=True)
    # client_id = fields.Many2one('hr.employee', "Client Name" ,readonly=True)
    client_name = fields.Char("Client Name",readonly=True)
    workorder_date = fields.Date("Work Order Date" ,readonly=True)
    select_bool = fields.Boolean(default=False) 
    sl_no = fields.Integer(compute="get_serial_no")
    acc_head_id = fields.Many2one('hr.employee', "Head Name" ,readonly=True)
    acc_sub_head_id = fields.Many2one('hr.employee', "Sub-Head Name" ,readonly=True)
    project_type_id = fields.Many2one('kw_project_type_master', "Project Type",readonly=True)

    allocated_budget = fields.Float("Allocated Budget",required=True)
    select_pm = fields.Many2one('hr.employee',"Project Manager",required=True,domain=lambda self: self._get_project_manager_domain())
    
    total_budget = fields.Float("Total Budget", compute="_compute_total_budget")

    @api.depends('select_bool', 'allocated_budget')
    def _compute_total_budget(self):
        total = 0.0
        for record in self:
            if record.select_bool:
                total += record.allocated_budget
        self.total_budget = total
    
    def confirm_project_details(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            pm_project = self.env['pm_tag_projects'].browse(active_id)
            lead = pm_project.lead_id.id
            crm_lead = self.env['crm.lead'].search([('id','=',lead)])
            if crm_lead:
                crm_lead.write({
                    'pm_id': self.select_pm.id,
                })
    
    def reset_project_details(self):
        self.project_type_id = False
        self.allocated_budget = False
        self.select_pm = False
        
        


class ManageOwnProjectByPM(models.Model):
    _name = 'pm_project_management'
    _description = 'Project management By Project Managers'
    _rec_name = 'project_id'

    project_id = fields.Many2one('project.project', "Project Name" ,readonly=True)
    workorder_name = fields.Char("Work Order Name" ,readonly=True)
    workoder_code = fields.Char("Work Order Code" ,readonly=True)
    client_id = fields.Many2one('hr.employee', "Client Name" ,readonly=True)
    account_holder_id = fields.Many2one('hr.employee', "Account Holder Name" ,readonly=True)
    reviewer_id = fields.Many2one('hr.employee', "Reviewer" ,readonly=True)
    workorder_date = fields.Date("Work Order Date" ,readonly=True)
    
    short_code = fields.Char("Project Short Code",required=True)
    life_cycle_id = fields.Many2one('kw_life_cycle_master', "Life Cycle",required=True) 
    ppb_id = fields.Many2one('project.project', "PPB",required=True)
    schedule_start_date = fields.Date("Schedule Start Date	",required=True)
    schedule_end_date = fields.Date("Expected Completion Date	",required=True)
    description = fields.Text("Description",required=True)
    
    def pm_project_take_action(self):
        form_view_id = self.env.ref('kw_project_monitoring.pm_project_management_form').id
        return {
            # 'name': 'Project Details',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(form_view_id, 'form')],
            'res_model': 'pm_project_management',
            'view_id': form_view_id,
            'context': {'default_project_id': self.project_id.id,'default_workorder_name':self.workorder_name,'default_workoder_code':self.workoder_code,'default_client_id':self.client_id.id,'default_account_holder_id':self.account_holder_id.id,'default_reviewer_id':self.reviewer_id.id,'default_workorder_date':self.workorder_date},
            'target': 'current',
        }
     
    @api.onchange('schedule_start_date','schedule_end_date','workorder_date')
    def _onchange_wo_date(self):
        if self.workorder_date and self.schedule_start_date and self.schedule_start_date < self.workorder_date:
            self.schedule_start_date = False
            return {
                'warning': {
                    'title': "Invalid  Date",
                    'message': "Schedule Start Date should be greater than Work Order Date",
                }
            }
        if self.schedule_start_date and self.schedule_end_date and self.schedule_end_date < self.schedule_start_date:
            self.schedule_end_date = False
            return {
                'warning': {
                    'title': "Invalid  Date",
                    'message': "Expected Completion Date  should be greater than Schedule Start Date",
                }
            } 
    

 
class KwProjectActivityMaster(models.Model):
    _name = 'kw_project_activity_master'
    _description = 'Project Activity Master '
    _rec_name = "activity_name"

    project_id = fields.Many2one('project.project', "Project",required=True)
    life_cycle_id = fields.Many2one('kw_life_cycle_master', "Life Cycle Phase",required=True) 
    module_id = fields.Many2one('kw_project_module_master', "Module Name",domain="[('project_id','=',project_id)]") 
    life_cycle_info = fields.Char("Life Cycle Phase Info",readonly=True)  
    activity_name = fields.Char("Activity Name",required=True)
    activity_leader_id = fields.Many2one('hr.employee',"Activity Leader",required=True)
    plan_start_date = fields.Date("Plan Start Date",required=True)
    plan_end_date = fields.Date("Plan Completion Date",required=True)
    effort_hour = fields.Float("Activity Effort (in Hrs)",required=True)
    activity_description = fields.Text("Description",required=True)
            
    

    _sql_constraints = [
        ('name_uniq', 'unique(activity_name)', 'Activity already exist.'),
    ]

   