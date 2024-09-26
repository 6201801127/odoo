from odoo import models, fields

class DailyActivityReport(models.Model):
    _name = 'daily_activity_report'
    _description = 'Daily Activity Report'
    _rec_name = 'project_id'

    logged_in_employee = fields.Many2one('res.users', string="Logged-In Employee", default=lambda self: self.env.user, readonly=True)
    project_id = fields.Many2one('project.project', string="Project", required=True)
    activity_type = fields.Selection([
        ('manual', 'Manual'),
        ('automation', 'Automation'),
        ('database', 'Database'),
        ('performance', 'Performance'),
        ('mobile', 'Mobile'),
        ('api', 'API')
    ], string="Activity Type", required=True)
    module = fields.Char(string="Module")
    sub_module = fields.Char(string="Sub Module(s)")
    date = fields.Date(string="Date", required=True)
    requirement_count = fields.Integer(string="Requirement Count", default=0)
    scenario_count = fields.Integer(string="Scenario Count", default=0)
    tcw_tcrw_count = fields.Integer(string="TCW/TCRW Count", default=0)
    tcw_tcrw_effort = fields.Float(string="TCW/TCRW Effort (In Hours)", default=0)
    tce_tcre_count = fields.Integer(string="TCE/TCRE Count", default=0)
    tce_tcre_effort = fields.Float(string="TCE/TCRE/TDP Effort (In Hours)", default=0)
    defect_found = fields.Integer(string="Defect Found", default=0)
    activity_details = fields.Text(string="Activity Details")
    
    
    # TC Creation fields (Boolean Checkboxes)
    performance_test_script_preparation = fields.Boolean(string="Performance Test Script Preparation")
    created_test_cases = fields.Boolean(string="Created Test Cases")
    reviewed_test_cases = fields.Boolean(string="Reviewed of Test Cases")
    updated_test_cases = fields.Boolean(string="Updated of Test Cases")
    test_data_preparation = fields.Boolean(string="Test Data Preparation")
    automation_script_preparation = fields.Boolean(string="Automation Script Preparation")
    automation_script_maintenance = fields.Boolean(string="Automation Script Maintenance")
    reviewed_automation_script = fields.Boolean(string="Reviewed Automation Script")
    database_query_writing = fields.Boolean(string="Database Query Writing")
    database_query_reviewed = fields.Boolean(string="Database Query Reviewed")

    # TC Execution fields (Boolean Checkboxes)
    performance_test_script_execution = fields.Boolean(string="Performance Test Script Execution")
    executed_test_cases = fields.Boolean(string="Executed Test Cases")
    logged_defects_manual = fields.Boolean(string="Logged Defects (Manual)")
    logged_defects_automation = fields.Boolean(string="Logged Defects (Automation)")
    reviewed_defects = fields.Boolean(string="Reviewed Defects")
    retested_defects = fields.Boolean(string="Retested Defects")
    sanity_smoke_testing = fields.Boolean(string="Sanity / Smoke / Adhoc Testing")
    regression_testing_manual = fields.Boolean(string="Regression Testing (Manual)")
    regression_testing_automation = fields.Boolean(string="Automation Script Batch Run")
    database_query_execution = fields.Boolean(string="Database Query Execution")

    # Miscellaneous fields (Boolean Checkboxes)
    task_planning_assignment = fields.Boolean(string="Task Planning & Assignment")
    test_report_preparation = fields.Boolean(string="Test Report Preparation")
    given_training = fields.Boolean(string="Given Training")
    attended_training = fields.Boolean(string="Attended Training")
    documentation = fields.Boolean(string="Documentation")
    requirement_understanding = fields.Boolean(string="Requirement Understanding")
    knowledge_transfer_sharing = fields.Boolean(string="Knowledge Transfer / Sharing")
    question_preparation = fields.Boolean(string="Question Preparation")
    scrum_sprint_meeting = fields.Boolean(string="Scrum / Sprint / Daily Standup Meeting")
    email_communication = fields.Boolean(string="Email Communication")
    general_meeting = fields.Boolean(string="General Meeting")
