from odoo import models, fields, tools

class EnvironmentCRServiceCount(models.Model):
    """
        This class reprsents the server instance report in change request mangement.
    """
    _name = 'environment_cr_service_count'
    _description = 'Environment CR and Service Count'
    _auto = False  # This tells Odoo not to create an actual table for this model

    environment_id = fields.Many2one('kw_environment_master', string='Environment')
    cr_count = fields.Integer(string='CR Count')
    service_count = fields.Integer(string='Service Count')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)        
        query = """
            CREATE OR REPLACE VIEW environment_cr_service_count AS (
                SELECT
                    c.environment_id as id,
                    c.environment_id AS environment_id,
                    COUNT(CASE WHEN c.cr_type = 'CR' THEN 1 END) AS cr_count,
                    COUNT(CASE WHEN c.cr_type = 'Service' THEN 1 END) AS service_count
                FROM
                    kw_cr_management c
                WHERE
                    c.stage = 'Uploaded'
                GROUP BY
                    c.environment_id
            ) """
        self.env.cr.execute(query)
