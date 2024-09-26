from odoo import models, fields, api,tools
from odoo.exceptions import ValidationError


class KwEnvironmentSequence(models.Model):
    
    _name = 'kw_cr_environment_sequence'
    _description = "CR Management Environment Report"
    _order = "id desc"
    _auto = False
    
    
    project_id = fields.Many2one('project.project', string='Project')
    prod_env_count = fields.Integer(string="Production(CR)")
    dev_env_count = fields.Integer(string="Development(CR)")
    test_env_count = fields.Integer(string="Testing(CR)")
    stag_env_count = fields.Integer(string="Staging(CR)")
    audit_env_count = fields.Integer(string="Audit(CR)")
    demo_env_count = fields.Integer(string="Demo(CR)")
    preprod_env_count = fields.Integer(string="Pre-production(CR)")
    prototype_env_count = fields.Integer(string="Prototype(CR)")
    
    sr_prod_env_count = fields.Integer(string="Production(Service)")
    sr_dev_env_count = fields.Integer(string="Development(Service)")
    sr_test_env_count = fields.Integer(string="Testing(Service)")
    sr_stag_env_count = fields.Integer(string="Staging(Service)")
    sr_audit_env_count = fields.Integer(string="Audit(Service)")
    sr_demo_env_count = fields.Integer(string="Demo(Service)")
    sr_preprod_env_count = fields.Integer(string="Pre-production(Service)")
    sr_prototype_env_count = fields.Integer(string="Prototype(Service)")
    total_count = fields.Integer(string="Total(CR)")
    sr_total_count = fields.Integer(string="Total(Service)")
    
    
    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
            SELECT
                ROW_NUMBER() OVER () AS id,
                cr.project_id AS project_id,
                MAX(CASE WHEN em.code = 'PRO' THEN cr.cr_sequence END) AS prod_env_count,
                MAX(CASE WHEN em.code = 'STG' THEN cr.cr_sequence END) AS stag_env_count,
                MAX(CASE WHEN em.code = 'TST' THEN cr.cr_sequence END) AS test_env_count,
                MAX(CASE WHEN em.code = 'DEV' THEN cr.cr_sequence END) AS dev_env_count,
                MAX(CASE WHEN em.code = 'AUD' THEN cr.cr_sequence END) AS audit_env_count,
                MAX(CASE WHEN em.code = 'DEM' THEN cr.cr_sequence END) AS demo_env_count,
                MAX(CASE WHEN em.code = 'PP' THEN cr.cr_sequence END) AS preprod_env_count,
                MAX(CASE WHEN em.code = 'PROT' THEN cr.cr_sequence END) AS prototype_env_count,
                
                MAX(CASE WHEN em.code = 'PRO' THEN cr.service_sequence END) AS sr_prod_env_count,
                MAX(CASE WHEN em.code = 'STG' THEN cr.service_sequence END) AS sr_stag_env_count,
                MAX(CASE WHEN em.code = 'TST' THEN cr.service_sequence END) AS sr_test_env_count,
                MAX(CASE WHEN em.code = 'DEV' THEN cr.service_sequence END) AS sr_dev_env_count,
                MAX(CASE WHEN em.code = 'AUD' THEN cr.service_sequence END) AS sr_audit_env_count,
                MAX(CASE WHEN em.code = 'DEM' THEN cr.service_sequence END) AS sr_demo_env_count,
                MAX(CASE WHEN em.code = 'PP' THEN cr.service_sequence END) AS sr_preprod_env_count,
                MAX(CASE WHEN em.code = 'PROT' THEN cr.service_sequence END) AS sr_prototype_env_count,
                
                COALESCE(MAX(CASE WHEN em.code = 'PRO' THEN cr.cr_sequence END), 0) +
                COALESCE(MAX(CASE WHEN em.code = 'STG' THEN cr.cr_sequence END), 0) +
                COALESCE(MAX(CASE WHEN em.code = 'TST' THEN cr.cr_sequence END), 0) +
                COALESCE(MAX(CASE WHEN em.code = 'DEV' THEN cr.cr_sequence END), 0) +
                COALESCE(MAX(CASE WHEN em.code = 'AUD' THEN cr.cr_sequence END), 0) +
                COALESCE(MAX(CASE WHEN em.code = 'DEM' THEN cr.cr_sequence END), 0) +
                COALESCE(MAX(CASE WHEN em.code = 'PP' THEN cr.cr_sequence END), 0) +
                COALESCE(MAX(CASE WHEN em.code = 'PROT' THEN cr.cr_sequence END), 0) AS total_count,
                
                COALESCE(MAX(CASE WHEN em.code = 'PRO' THEN cr.service_sequence END), 0) +
                COALESCE(MAX(CASE WHEN em.code = 'STG' THEN cr.service_sequence END), 0) +
                COALESCE(MAX(CASE WHEN em.code = 'TST' THEN cr.service_sequence END), 0) +
                COALESCE(MAX(CASE WHEN em.code = 'DEV' THEN cr.service_sequence END), 0) +
                COALESCE(MAX(CASE WHEN em.code = 'AUD' THEN cr.service_sequence END), 0) +
                COALESCE(MAX(CASE WHEN em.code = 'DEM' THEN cr.service_sequence END), 0) +
                COALESCE(MAX(CASE WHEN em.code = 'PP' THEN cr.service_sequence END), 0) +
                COALESCE(MAX(CASE WHEN em.code = 'PROT' THEN cr.service_sequence END), 0) AS sr_total_count
            FROM kw_environment_sequence cr
            JOIN kw_environment_master em ON cr.environment_id = em.id
            GROUP BY cr.project_id)"""
        self.env.cr.execute(query)