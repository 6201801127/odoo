from odoo import models, fields, api
from datetime import date, datetime, time

class KWProjectEnvInfo(models.Model):
    _name = 'kw_project_env_info'
    _rec_name = 'project_id'
    
    
    project_id = fields.Many2one('project.project',"Project",required=True)
    project_name = fields.Char("Project Name",related='project_id.name',readonly=True)
    project_code = fields.Char("Project ID/Ref. Code",related='project_id.code',readonly=True)
    short_code = fields.Char("Short Code",related='project_id.code',readonly=True)
    # project_type = fields.Many2one('kw_project_type_master', "Project Type",readonly=True)
    project_manager_id = fields.Many2one('hr.employee',"Project Manager",related='project_id.emp_id',readonly=True)
    account_holder = fields.Many2one('hr.employee',"Account Holder",related='project_id.reviewer_id',readonly=True)
    check_project_details = fields.Boolean(string="View Project Information",default=False)
    
    env_detail_ids = fields.One2many(
        string='Enviornment Infos',
        comodel_name='kw_project_env_info_relation',
        inverse_name='project_id',
    )
    
    
class KWProjectEnvInfo(models.Model):
    _name = 'kw_project_env_info_relation'
    
    
    project_id = fields.Many2one('kw_project_env_info')
    env_type = fields.Selection([
        ('audit', 'Audit'),
        ('development', 'Development'),
        ('production', 'Production'),
        ('staging', 'Staging'),
        ('testing', 'Testing'),
        ],string="Enviornment Type",required=True)
    application_server = fields.Char("Application Server")
    database_server = fields.Char("Database Server")
    database_user = fields.Char("Database Use")
    ftp_user = fields.Char("FTP User")
    technology_id = fields.Many2one('kw_skill_master',"Technology",required=True)
    technology_version = fields.Char("Version",required=True)
    architecture_id = fields.Many2one('project_architecture_type_master',"Architecture",required=True)
    ui_id = fields.Many2one('kw_skill_master',"UI",required=True)
    ui_version = fields.Char("Version",required=True)
    database_id = fields.Many2one('kw_skill_master',"Database",required=True)
    database_version = fields.Char("Version",required=True)
    
    
    