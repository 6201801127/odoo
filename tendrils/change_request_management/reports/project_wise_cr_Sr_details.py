from odoo import models, fields, api, tools

class ProjectWiseCrSreport(models.Model):
    """
    This class represents Project Wise cr sr report in Odoo.
    """
    _name = 'project_wise_cr_sr_report'
    _description = 'Project Wise CR SR Report'
    _auto = False


    project_id = fields.Many2one('project.project', string='Project Name')
    project_code = fields.Char(related='project_id.code',string="Project Code")
    # cr_type = fields.Char(string='Type')
    cr_count =fields.Integer(string='Total CR')
    sr_count =fields.Integer(string='Total SR')


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
               SELECT   ROW_NUMBER() OVER () AS id,
                    kcm.project_id AS project_id,
                    --kcm.cr_type AS cr_type,
                    COUNT(CASE WHEN kcm.cr_type = 'CR' THEN 1 ELSE NULL END) AS cr_count,
                    COUNT(CASE WHEN kcm.cr_type = 'Service' THEN 1 ELSE NULL END) AS sr_count
                FROM
                    kw_cr_management AS kcm
                WHERE
                    kcm.stage = 'Uploaded'
                GROUP BY
                    kcm.project_id
                    --kcm.cr_type
                ORDER BY cr_count DESC ,sr_count DESC LIMIT 15

          )"""
        self.env.cr.execute(query)
