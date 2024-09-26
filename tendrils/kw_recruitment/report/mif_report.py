from odoo import fields, models, _, api
from odoo import tools
from datetime import date, datetime


class ManpowerIndentFormReport(models.Model):
    _name = 'manpower_indent_form_report'
    _description = 'Manpower Indent Form Report'
    _auto = False
    _order = "mif_id DESC"

    mif_id = fields.Integer('MIF ID')
    mif_code = fields.Char('MIF Number')
    mrf_code = fields.Char('MRF Number')

    # dept_id = fields.Char(string="Department")
    fiscal_year = fields.Many2one('account.fiscalyear', string='Fiscal Year')
    dept_id = fields.Many2one('hr.department', string="Department",
                              domain="[('dept_type.code', '=', 'department')]")
    desig_id = fields.Many2one('hr.job', string='Designation')
    resource = fields.Selection(string='New/Replacement',
                                selection=[('new', 'New'), ('replacement', 'Replacement')])
    skill = fields.Char(string="Skill")
    project_type = fields.Selection(string="Project Type",
                                    selection=[('work', 'Work Order'), ('opportunity', 'Opportunity')])
    project = fields.Many2one('crm.lead', string='Project')
    sbu_id = fields.Many2one(comodel_name="kw_sbu_master", string="SBU")
    raised_by_id = fields.Many2one('hr.employee', 'Requester')

    effective_date = fields.Date('Effective Date of deployment')
    branch_id = fields.Char(string="Required Location")
    doj = fields.Char('Date of joining')
    technology = fields.Many2one('kw_skill_master', string="Skill/Technology")
    status = fields.Char(string="Status")
    # onboard_location = fields.Char( string="Onboard Location")
    onboard_location = fields.Many2one('kw_res_branch', 'Onboard Location')
    approval_authority_date = fields.Date(string="Requisition date")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
                SELECT
                row_number() OVER () AS id,fiscal_year, mif_id,
                mrf_code, mif_code, dept_id, desig_id, resource, skill, technology, project_type,
                project, sbu_id, raised_by_id, effective_date, branch_id, status,
                approval_authority_date, STRING_AGG(TO_CHAR(doj, 'YYYY-MM-DD'), ', ') AS doj,
                onboard_location
            FROM
            (
                SELECT
                    mif.id AS mif_id,
                    mif.current_fy AS fiscal_year,
                    mrf.code AS mrf_code,
                    mif.code AS mif_code,
                    mif.dept_name AS dept_id,
                    mif.job_position AS desig_id,
                    mif.resource AS resource,
                    mif.skill_set AS skill,
                    mif.technology AS technology,
                    mif.type_project AS project_type,
                    mif.project AS project,
                    mif.sbu_id AS sbu_id,
                    mif.req_raised_by_id AS raised_by_id,
                    mif.approval_date AS approval_authority_date,
                    mif.effective_date_of_deployment AS effective_date,
                    (
                        SELECT STRING_AGG(name, ', ')
                        FROM kw_recruitment_location
                        WHERE id IN (
                            SELECT kw_recruitment_location_id
                            FROM kw_manpower_indent_form_kw_recruitment_location_rel
                            WHERE kw_manpower_indent_form_id = mif.id
                        )
                    ) AS branch_id,
                    CASE
                        WHEN en.id is not null THEN 'Onboard' 
                        WHEN appli.id is not null THEN 'Offered'
                        ELSE ''
                    END AS status,
                    he.date_of_joining AS doj,
                    he.base_branch_id AS onboard_location
                FROM kw_manpower_indent_form mif
                LEFT JOIN kw_recruitment_requisition mrf ON mrf.mif_rec_id = mif.id
                LEFT JOIN hr_applicant appli ON appli.mrf_id = mrf.id
                LEFT JOIN hr_employee he ON he.mrf_id = mrf.id
                LEFT JOIN kwonboard_enrollment en ON en.id=he.onboarding_id
                GROUP BY en.id, appli.id, mrf.code, mrf.id, mif.code, he.base_branch_id, he.date_of_joining,
                    he.onboarding_id, mif.id
            ) subquery
            GROUP BY mrf_code, fiscal_year, mif_id, mif_code, dept_id, desig_id, resource, skill, technology, project_type, project,
                sbu_id, raised_by_id, effective_date, branch_id, approval_authority_date, status, onboard_location
                )"""
        self.env.cr.execute(query)
