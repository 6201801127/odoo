from odoo import models, fields, api,tools

class ServerAdminProjects(models.Model):
    _name = 'server_admin_projects'
    _description = 'Working in Total Number of Projects'
    _auto = False

    uploaded_by = fields.Many2one('hr.employee', string='Employee')
    project_count = fields.Char(string='Number of Projects')
    project_id = fields.Text(string='Project')
    # service_count = fields.Integer(string='SR Count')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)        
        query = """
           CREATE OR REPLACE VIEW %s AS (
                WITH a AS (
                SELECT ROW_NUMBER() OVER () AS id, COUNT(project_id) AS project_count FROM kw_project_environment_management WHERE active = True), 
            b AS (SELECT per.hr_employee_id AS employee,STRING_AGG(DISTINCT project_project.name, ',') AS projects
                FROM kw_project_environment_management cmr JOIN hr_employee_kw_project_environment_management_rel per ON 
                per.kw_project_environment_management_id = cmr.id JOIN project_project ON cmr.project_id = project_project.id 
            WHERE cmr.active = True GROUP BY per.hr_employee_id)
            SELECT row_number() OVER () as id,per.hr_employee_id AS uploaded_by,b.projects AS project_id,
                '(' || a.project_count || ':' || ARRAY_LENGTH(STRING_TO_ARRAY(b.projects, ','), 1) || ')' AS project_count
            FROM hr_employee_kw_project_environment_management_rel per JOIN b ON per.hr_employee_id = b.employee
            CROSS JOIN a GROUP BY per.hr_employee_id, a.project_count,b.projects,a.id)
        """ % (self._table,)
        
        self.env.cr.execute(query)


class WorkingProjectsbyadmin(models.Model):
    _name = 'working_projects_details_by_server_admin'
    _description = 'Working Number of Projects By Server Admin'
    _auto = False

    uploaded_by = fields.Many2one('hr.employee', string='Server Admin')
    project_code = fields.Char(string='Project Code')
    project_name = fields.Char(string='Project Name')
    cr_count = fields.Integer(string='CR Count')
    service_count = fields.Integer(string='SR Count')
   
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)        
        query = """
            CREATE OR REPLACE VIEW %s AS (	
                        SELECT 
                            km.uploaded_by AS id,
                            km.uploaded_by AS uploaded_by,
                            COUNT(CASE WHEN km.cr_type = 'CR' THEN km.id END) AS cr_count,
                            COUNT(CASE WHEN km.cr_type = 'Service' THEN km.id END) AS service_count,
                            STRING_AGG(DISTINCT proj.name, ',') AS project_name,
                            STRING_AGG(DISTINCT km.project_code, ',') AS project_code
                        FROM 
                            cr_management_report km
                        JOIN 
                            project_project proj ON km.project_id = proj.id
                        WHERE 
                            km.uploaded_by IS NOT NULL 
                            AND state = 'Uploaded'
                        GROUP BY 
                            km.uploaded_by)
        """ % (self._table,)
        
        self.env.cr.execute(query)



   
