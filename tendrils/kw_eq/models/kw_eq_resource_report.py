# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date

class ResourceReport(models.Model):
    _name = 'kw_resource_mapping_report'
    _description = 'Resource Report'

    eq_id = fields.Many2one('kw_eq_software_development_config', string='EQ ID')
    csg = fields.Many2one('hr.employee', string='CSG')
    account_holder = fields.Many2one('hr.employee', string='Acc Holder')
    opp_code = fields.Char(string='OPP Code')
    client_name = fields.Char(string='Client')
    oppertuinity_id = fields.Many2one('crm.lead', string='Opportunity')
    oppertuinity_name = fields.Char(related='oppertuinity_id.name', string='Opportunity')
    reviewer_id = fields.Many2one('hr.employee', string='Reviewer')
    technology_id = fields.Many2one('kw_skill_master', string='Technology')
    job_id = fields.Many2one('hr.job', string='Position')
    pm_id = fields.Many2one('hr.employee', string='Project Manager')
    sbu_id = fields.Many2one('hr.employee', string='SBU')
    implementation_man_month = fields.Integer(string='Implementation Man Month')
    no_of_resource_required = fields.Integer(string='No Of Resource Required')
    resource_available = fields.Integer(string='No Resource Available')
    resource_required = fields.Integer(string='No Of Resources Requirement', compute="get_resources_from_rcm")
    check_representative = fields.Boolean(string='Representative', compute='_representative_check')
    # engagement_start_date = fields.Date(string='Engagement Start Date')
    # engagement_end_date = fields.Date(string='Engagement End Date')
    remark = fields.Text(string='Remark')
    eq_data_id = fields.Many2one('kw_eq_estimation', string='EQ Data Id')
    revised_id = fields.Many2one('kw_eq_revision')
    active = fields.Boolean()

    @api.depends('no_of_resource_required', 'resource_available')
    def get_resources_from_rcm(self):
        for rec in self:
            if rec.no_of_resource_required and rec.resource_available:
                rec.resource_required = rec.no_of_resource_required - rec.resource_available
            else:
               rec.resource_required = rec.no_of_resource_required - rec.resource_available

    def update_resource_quantity(self):
        form_view_id = self.env.ref('kw_eq.resource_qty_update_wiz_form_view').id
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Update Resource available Quantity',
            'views': [(form_view_id, 'form')],
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'resource_qty_update_wiz',
            'target': 'new',
            'context': {
                'default_resource_map_id': self.id,
                'default_resource_no': self.implementation_man_month,
                'default_opportunity_id': self.oppertuinity_id.id,
                'default_no_of_resource_required':self.no_of_resource_required,
                'default_resource_available':self.resource_available,
                'default_resource_required':self.resource_required,
                # 'default_engagement_start_date':self.engagement_start_date,
                # 'default_engagement_end_date':self.engagement_end_date,
                'default_remark':self.remark
            }
        }
        return action

    def _representative_check(self):
        for rec in self:
            if self.env.user.has_group('kw_resource_management.group_sbu_representative'):
                login_user_id = self.env.user.employee_ids.id
                rec.check_representative = login_user_id == rec.sbu_id.id
            else:
                rec.check_representative = False


    @api.model
    def eq_resource_mapping(self):
        tree_view_id = self.env.ref('kw_eq.view_kw_resource_mapping_report_tree').id

        query = """
        SELECT
            eqsd.id AS eq_id,
            eq.id as eq_data_id,
            eqsd.implementation_man_month,
            crm.csg_head_id AS csg,
            crm.sales_person_id AS account_holder,
            crm.code AS opp_code,
            crm.client_name,
            eq.kw_oppertuinity_id AS oppertuinity_id,
            crm.reviewer_id AS reviewer_id,
            crm.pm_id AS pm_id,
            eqsd.skill_id AS technology_id,
            eqsd.designation_id AS job_id,
            (SELECT representative_id FROM kw_sbu_master WHERE id = pm.sbu_master_id) AS sbu_id,
            eqsd.remark as remark
        FROM
            kw_eq_estimation AS eq
            RIGHT JOIN crm_lead AS crm ON crm.id = eq.kw_oppertuinity_id
            RIGHT JOIN kw_eq_software_development_config AS eqsd ON (
                eq.id = eqsd.core_estimate_id OR
                eq.id = eqsd.java_estimate_id OR
                eq.id = eqsd.php_estimate_id OR
                eq.id = eqsd.odoo_estimate_id OR
                eq.id = eqsd.mobile_estimate_id OR
                eq.id = eqsd.sas_estimate_id OR
                eq.id = eqsd.etl_estimate_id OR
                eq.id = eqsd.tableu_estimate_id OR
                eq.id = eqsd.estimation_id
            )
            LEFT JOIN hr_employee AS pm ON crm.pm_id = pm.id
        WHERE
            eq.state = 'grant'
            AND eqsd.implementation_man_month > 0
            AND eq.id NOT IN (
                SELECT estimation_id
                FROM kw_eq_revision
                WHERE state = 'grant'
            )
        UNION
        SELECT
            eqsd.id AS eq_id,
            ker.estimation_id as revised_id,
            eqsd.implementation_man_month,
            crm.csg_head_id AS csg,
            crm.sales_person_id AS account_holder,
            crm.code AS opp_code,
            crm.client_name,
            ker.kw_oppertuinity_id AS oppertuinity_id,
            crm.reviewer_id AS reviewer_id,
            crm.pm_id AS pm_id,
            eqsd.skill_id AS technology_id,
            eqsd.designation_id AS job_id,
            (SELECT representative_id FROM kw_sbu_master WHERE id = pm.sbu_master_id) AS sbu_id,
            eqsd.remark as remark
        FROM
            kw_eq_revision AS ker
            RIGHT JOIN crm_lead AS crm ON crm.id = ker.kw_oppertuinity_id
            RIGHT JOIN kw_eq_software_development_config AS eqsd ON (
                ker.id = eqsd.revision_id OR
                ker.id = eqsd.java_estimate_revision_id OR
                ker.id = eqsd.php_estimate_revision_id OR
                ker.id = eqsd.core_estimate_revision_id OR
                ker.id = eqsd.mobile_estimate_revision_id OR
                ker.id = eqsd.odoo_estimate_revision_id OR
                ker.id = eqsd.tableu_estimate_revision_id OR
                ker.id = eqsd.sas_estimate_revision_id OR
                ker.id = eqsd.etl_estimate_revision_id
            )
            LEFT JOIN hr_employee AS pm ON crm.pm_id = pm.id
        WHERE
            ker.state = 'grant'
            AND eqsd.implementation_man_month > 0
            AND ker.id IN (
                SELECT sub.id
                FROM (
                    SELECT id, kw_oppertuinity_id, revision_status,
                        ROW_NUMBER() OVER (PARTITION BY kw_oppertuinity_id,(select a.approval_type from kw_eq_estimation as a where a.id =kw_eq_revision.estimation_id) ORDER BY revision_status DESC) as rn
                    FROM kw_eq_revision
                    WHERE state = 'grant'
                ) sub
                WHERE sub.rn = 1
            )
        ORDER BY oppertuinity_id
        """

        self._cr.execute(query)
        results = self._cr.dictfetchall()

        records_to_create = []
        eq_ids_to_keep_active = set()

        for result in results:
            eq_id = result['eq_id']
            revised_id = result.get('revised_id')
            implementation_man_month = result['implementation_man_month']
            csg = result['csg']
            account_holder = result['account_holder']
            opp_code = result['opp_code']
            client_name = result['client_name']
            oppertuinity_id = result['oppertuinity_id']
            reviewer_id = result['reviewer_id']
            pm_id = result['pm_id']
            technology_id = result['technology_id']
            job_id = result['job_id']
            sbu_id = result['sbu_id']
            remark = result['remark']
            

            # Check if a record with the same eq_id already exists
            existing_record = self.env['kw_resource_mapping_report'].sudo().search([('eq_id', '=', eq_id)])
            
            if not existing_record:
                records_to_create.append({
                    'eq_id': eq_id,
                    'revised_id': revised_id,
                    'implementation_man_month': implementation_man_month,
                    'csg': csg,
                    'account_holder': account_holder,
                    'opp_code': opp_code,
                    'client_name': client_name,
                    'oppertuinity_id': oppertuinity_id,
                    'reviewer_id': reviewer_id,
                    'pm_id': pm_id,
                    'technology_id': technology_id,
                    'job_id': job_id,
                    'sbu_id': sbu_id,
                    'remark':remark,
                    'active': True
                })
            else:
                # If record exists, ensure it's active and add eq_id to the set of ids to keep active
                existing_record.write({'active': True,'remark':remark})
                eq_ids_to_keep_active.add(eq_id)

        # Deactivate records that are not in the fetched results
        records_to_deactivate = self.env['kw_resource_mapping_report'].sudo().search([
            ('eq_id', 'not in', list(eq_ids_to_keep_active))
        ])
        records_to_deactivate.write({'active': False})

        # Create new records
        if records_to_create:
            self.env['kw_resource_mapping_report'].sudo().create(records_to_create)

        all_rec = self.env['kw_resource_mapping_report'].sudo().search([])
        reviewer = all_rec.filtered(lambda x: x.reviewer_id.id == self.env.user.employee_ids.id)
        sbu = all_rec.filtered(lambda x: x.sbu_id.id == self.env.user.employee_ids.id)
        domain = [('id', '=', False)]
        if self.env.user.employee_ids in reviewer.mapped('reviewer_id'):
            domain = [('id', 'in', reviewer.ids)]
        if self.env.user.employee_ids in sbu.mapped('sbu_id'):
            domain = [('id', 'in', sbu.ids)]
        if self.env.user.has_group("kw_resource_management.group_budget_manager"):
            domain = [('id', 'in', all_rec.ids)]
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Resource Mapping Report',
            'views': [(tree_view_id, 'tree')],
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'kw_resource_mapping_report',
            'target': 'main',
            'domain': domain,
        }

        return action

    