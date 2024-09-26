from odoo import models, fields, api
from datetime import date, datetime, time

class ProjectRiskLog(models.Model):
    _name = 'project_risk_log'
    _rec_name = 'risk_name'

    project_id = fields.Many2one("project.project","Project",required=True,ondelete="cascade")
    risk_date = fields.Date("Risk Date",required=True)
    risk_name = fields.Char("Risk Name",required=True)
    risk_category = fields.Many2one('project_risk_category',string="Select Category",required=True)
    risk_description = fields.Text("Risk Description",required=True)
    risk_impact = fields.Text("Risk Impact",required=True)
    probability = fields.Selection([
        (1, f"1 (Unlikely/improbable (0%-25%))"),
        (2, f"2 (Somewhat likely (26%-50%))"),
        (3, f"3 (Likely (51%-75%))"),
        (4, f"4 (Highly likely/probable (76%-100%))"),
        ],string="Select Probability",required=True)
    impact = fields.Selection([
        (1, "1 (Minimal/minor: No impact on business vision but may increase project costs and timescales)"),
        (2, "2 (Moderate: May delay achievement of the vision or reduce project benefits)"),
        (3, "3 (Severe: Threatens the achievement of business vision or severely reduces project benefits)"),
        (4, "4 (Critical: Threatens the viability of the business or represents failure of the project)"),
        ],string="Select Impact",required=True)
    detectibility = fields.Selection([
        (1, "1 (Determined well in advance of occurrence or trigger event)"),
        (2, "2 (Immediately prior to trigger event; can be   mitigated prior to trigger if monitored)"),
        (3, "3 (Realized upon trigger event)"),
        (4, "4 (Determined after impact has been realized)"),
        ],string="Select Detectability",required=True)
    migration_plan = fields.Text("Mitigation Plan",required=True)
    migration_plan_due_date = fields.Date("Mitigation Plan Due Date",required=True)
    contingency_plan = fields.Text("Contingency Plan",required=True)
    contingency_plan_due_date = fields.Date("Contingency Plan Due Date",required=True)
    ontingency_plan_when = fields.Char("Contingency Plan When")
    responsible_person = fields.Many2one('hr.employee',"Responsible Person")
    
    


class ProjectIssueLog(models.Model):
    _name = 'project_issue_log'
    _rec_name = 'project_id'

    project_id = fields.Many2one("project.project","Project",required=True,ondelete="cascade")
    issue_type = fields.Selection([
        ('new', 'New'),
        ('existin', 'Existing'),
        ],default='new',string="Issue Type",required=True)
    risk_name = fields.Many2one('project_risk_log',"Risk Name",domain="[('project_id','=',project_id)]")
    issue_date = fields.Date("Issue Date",required=True)
    reported_by = fields.Many2one('hr.employee',string="Reported By",required=True)
    issue_description = fields.Text("Issue Description",required=True)
    project_impact = fields.Text("Project Impact",required=True)
    action_plan = fields.Text("Action Plan",required=True)
    responsible_person = fields.Many2one('hr.employee',"Responsible Person",required=True)
    escalate_to = fields.Many2one('hr.employee',"Escalate To",required=True)
    plan_closer_date = fields.Date("Plan Closer Date",required=True)
    
    
   
class ProjectDependencyLog(models.Model):
    _name = 'project_dependency_log'
    _rec_name = 'project_id'

    project_id = fields.Many2one("project.project","Project",required=True,ondelete="cascade")
    raise_date = fields.Date("Date Raised",required=True)
    dependency_description = fields.Text("Dependency Description",required=True)
    dependency_type = fields.Selection([
        ('internal', 'Internal'),
        ('external', 'External'),
        ],string="Dependency Type")
    deliverables = fields.Text("Deliverables")
    delivery_date = fields.Date("Delivery Date")
    critical = fields.Selection([
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
        ],string="Critical Type")
    stake_holder_name = fields.Char("Stake Holder Name")
    
    
    
class ProjectOpportunityLog(models.Model):
    _name = 'project_opportunity_log'
    _rec_name = 'project_id'

    project_id = fields.Many2one("project.project","Project",required=True,ondelete="cascade")
    enterd_date = fields.Date("Date Entered",required=True)
    opportunity_name = fields.Char("Opportunity Name",required=True)
    catagory = fields.Selection([
        ('enhancement', 'Enhancement'),
        ('growth', 'Growth'),
        ('standalone', 'Standalone'),
        ('strategic', 'Strategic'),
        ],string="Select Category",required=True)
    opportunity_description = fields.Text("Opportunity Description",required=True)
    impact = fields.Text("Impact",required=True)
    response_trategy = fields.Text("Response Strategy",required=True)
    probability = fields.Selection([
        (1, f"1 (Unlikely/improbable (0%-25%))"),
        (2, f"2 (Somewhat likely (26%-50%))"),
        (3, f"3 (Likely (51%-75%))"),
        (4, f"4 (Highly likely/probable (76%-100%))"),
        ],string="Select Probability",required=True)
    select_impact = fields.Selection([
        (1, "1 (Minimal/minor: No impact on business vision but may increase project costs and timescales)"),
        (2, "2 (Moderate: May delay achievement of the vision or reduce project benefits)"),
        (3, "3 (Severe: Threatens the achievement of business vision or severely reduces project benefits)"),
        (4, "4 (Critical: Threatens the viability of the business or represents failure of the project)"),
        ],string="Select Impact",required=True)
    detectibility = fields.Selection([
        (1, "1 (Determined well in advance of occurrence or trigger event)"),
        (2, "2 (Immediately prior to trigger event; can be   mitigated prior to trigger if monitored)"),
        (3, "3 (Realized upon trigger event)"),
        (4, "4 (Determined after impact has been realized)"),
        ],string="Select Detectability",required=True)
    realization_plan = fields.Text("Realization Plan")
    responsible_person = fields.Many2one('hr.employee',"Responsible Person",required=True)
    actions = fields.Text("Actions")
    contingency_plan = fields.Text("Contingency Plan",required=True)
    contingency_plan_when = fields.Char("Contingency Plan When")
    contingency_responsible_person = fields.Many2one('hr.employee',"Responsible Person")
    
    
# ************************************************************************   
# """ Reports Section # """
# ************************************************************************


class GetFilteredRiskLog(models.TransientModel):
    _name = 'filtered_risk_log_wizard'

    
    risk_category = fields.Many2one('project_risk_category',string="Select Category",required=True)
    project_id = fields.Many2one("project.project","Project",required=True,ondelete="cascade")
    
    
    def get_filtered_risk_log(self):
        if self.risk_category and self.project_id :
            tree_view_id = self.env.ref('kw_project_monitoring.view_project_risk_log_tree').id
            form_view_id = self.env.ref('kw_project_monitoring.view_project_risk_log_form').id
            return {
                'type': 'ir.actions.act_window',
                'name': 'Filtered Project Risk Logs',
                'view_mode': 'tree,form',
                'res_model': 'project_risk_log',
                'views': [(tree_view_id, 'tree'),(form_view_id, 'form')],
                'domain': [('risk_category', '=', self.risk_category.id), ('project_id', '=', self.project_id.id)],
                'target': 'current',
                'context':{'edit':False,'create':False,'import':False,'delete':False,'duplicate':False}
            }

class GetFilteredIssuekLog(models.TransientModel):
    _name = 'filtered_issue_log_wizard'

    
    project_id = fields.Many2one("project.project","Project",required=True,ondelete="cascade")
    issue_type = fields.Selection([
        ('new', 'New'),
        ('existin', 'Existing'),
        ],default='new',string="Issue Type",required=True)
    
    
    def get_filtered_issue_log(self):
        if self.issue_type and self.project_id :
            tree_view_id = self.env.ref('kw_project_monitoring.view_project_issue_log_tree').id
            form_view_id = self.env.ref('kw_project_monitoring.view_project_issue_log_form').id
            return {
                'type': 'ir.actions.act_window',
                'name': 'Filtered Project Issue Logs',
                'view_mode': 'tree,form',
                'res_model': 'project_issue_log',
                'views': [(tree_view_id, 'tree'),(form_view_id, 'form')],
                'domain': [('issue_type', '=', self.issue_type), ('project_id', '=', self.project_id.id)],
                'target': 'current',
                'context':{'edit':False,'create':False,'import':False,'delete':False,'duplicate':False}
            }


class GetFilteredDependencyLog(models.TransientModel):
    _name = 'filtered_dependency_log_wizard'

    
    project_id = fields.Many2one("project.project","Project",required=True,ondelete="cascade")
    dependency_type = fields.Selection([
        ('internal', 'Internal'),
        ('external', 'External'),
        ],string="Dependency Type",required=False)
    critical = fields.Selection([
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
        ],string="Critical Type",required=False)
    
    def get_filtered_dependency_log(self):
        tree_view_id = self.env.ref('kw_project_monitoring.view_project_dependency_log_tree').id
        form_view_id = self.env.ref('kw_project_monitoring.view_project_dependency_log_form').id
        domain = []
        if self.project_id:
            domain.append(('project_id', '=', self.project_id.id))
        if self.dependency_type:
            domain.append(('dependency_type', '=', self.dependency_type))
        if self.critical:
            domain.append(('critical', '=', self.critical))
        return {
            'type': 'ir.actions.act_window',
            'name': 'Filtered Project Dependency Logs',
            'view_mode': 'tree,form',
            'res_model': 'project_dependency_log',
            'views': [(tree_view_id, 'tree'),(form_view_id, 'form')],
            'domain': domain,
            'target': 'current',
            'context':{'edit':False,'import':False,'create':False,'delete':False,'duplicate':False}
        }

class GetFilteredOpportunityLog(models.TransientModel):
    _name = 'filtered_opportunity_log_wizard'

    
    project_id = fields.Many2one("project.project","Project",required=True,ondelete="cascade")
    catagory = fields.Selection([
        ('enhancement', 'Enhancement'),
        ('growth', 'Growth'),
        ('standalone', 'Standalone'),
        ('strategic', 'Strategic'),
        ],string="Select Category",required=True)
    probability = fields.Selection([
        (1, f"1 (Unlikely/improbable (0%-25%))"),
        (2, f"2 (Somewhat likely (26%-50%))"),
        (3, f"3 (Likely (51%-75%))"),
        (4, f"4 (Highly likely/probable (76%-100%))"),
        ],string="Select Probability",required=True)
    select_impact = fields.Selection([
        (1, "1 (Minimal/minor: No impact on business vision but may increase project costs and timescales)"),
        (2, "2 (Moderate: May delay achievement of the vision or reduce project benefits)"),
        (3, "3 (Severe: Threatens the achievement of business vision or severely reduces project benefits)"),
        (4, "4 (Critical: Threatens the viability of the business or represents failure of the project)"),
        ],string="Select Impact",required=True)
    
    
    def get_filtered_opportunity_log(self):
        if self.project_id and self.catagory and self.probability and self.select_impact:
            tree_view_id = self.env.ref('kw_project_monitoring.view_project_opportunity_log_tree').id
            form_view_id = self.env.ref('kw_project_monitoring.view_project_opportunity_log_form').id
            return {
                'type': 'ir.actions.act_window',
                'name': 'Filtered Opportunity Risk Logs',
                'view_mode': 'tree,form',
                'res_model': 'project_opportunity_log',
                'views': [(tree_view_id, 'tree'),(form_view_id, 'form')],
                'domain': [('project_id', '=', self.project_id.id),('catagory', '=', self.catagory),('probability', '=', self.probability),('select_impact', '=', self.select_impact),],
                'target': 'current',
                'context':{'edit':False,'create':False,'import':False,'delete':False,'duplicate':False}
            }
