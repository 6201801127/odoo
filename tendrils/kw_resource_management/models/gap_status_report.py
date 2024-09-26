from odoo import models, fields, api
from odoo import tools


class SbuReportGapStatus(models.Model):
    _name = "sbu_report_gap_status"
    _description = "SBU report Gap Status"
    _auto = False

    location_id = fields.Many2one('kw_res_branch', string="Location")
    skill_id = fields.Many2one('kw_skill_master',string = "Skill")

    existing_manger = fields.Integer('Existing Manager')
    existing_tl_pl = fields.Integer('Existing TL/PL')
    existing_sr_dev = fields.Integer('Existing Sr.Dev')
    existing_dev = fields.Integer('Existing Dev')
    existing_intern = fields.Integer('Existing Intern')
    existing_ba = fields.Integer('Existing BA')

    required_manger = fields.Integer('Required Manager')
    required_tl_pl = fields.Integer('Required TL/PL')
    required_sr_dev = fields.Integer('Required Sr.Dev')
    required_dev = fields.Integer('Required Dev')
    required_intern = fields.Integer('Required Intern')
    required_ba = fields.Integer('Required BA')

    offered_manger = fields.Integer('Offered Manager')
    offered_tl_pl = fields.Integer('Offered TL/PL')
    offered_sr_dev = fields.Integer('Offered Sr.Dev')
    offered_dev = fields.Integer('Offered Dev')
    offered_intern = fields.Integer('Offered Intern')
    offered_ba = fields.Integer('Offered BA')


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        
        query = f""" CREATE or REPLACE VIEW {self._table} as (
          
            SELECT row_number() over() AS id, 
            a.location as location_id,
            a.skill  as skill_id,
            a.existing_manger,
            a.existing_tl_pl,
            a.existing_sr_dev,
            a.existing_dev,
            a.existing_intern,
            a.existing_ba,
            b.required_manger,
            b.required_tl_pl,
            b.required_sr_dev,
            b.required_dev,
            b.required_intern,
            b.required_ba,
            0 as offered_manger,
            0 as offered_tl_pl,
            0  as offered_sr_dev,
            0 as offered_dev,
            0 as offered_intern,
            0 as offered_ba
            from (select
            hr.job_branch_id as location,
            hr.primary_skill_id as skill,
            count(sdm.name) FILTER (WHERE sdm.name = 'Manager') AS "existing_manger",
            count(sdm.name) FILTER (WHERE sdm.name = 'TL/PL') AS "existing_tl_pl",
            count(sdm.name) FILTER (WHERE sdm.name = 'Sr.Dev') AS "existing_sr_dev",
            count(sdm.name) FILTER (WHERE sdm.name = 'Dev') AS "existing_dev",
            count(sdm.name) FILTER (WHERE sdm.name = 'Intern') AS "existing_intern",
            count(sdm.name) FILTER (WHERE sdm.name = 'BA') AS "existing_ba"
            from hr_employee as hr
            left join hr_job_sbu_designation_master_rel as jd on jd.hr_job_id = hr.job_id
            left join sbu_designation_master as sdm on sdm.id = jd.sbu_designation_master_id
            where hr.emp_project_id is not null and hr.sbu_type = 'sbu'
            group by hr.job_branch_id,hr.primary_skill_id) as a
            left join 
            (select
            hr.job_branch_id as location,
            hr.primary_skill_id as skill,
            count(sdm.name) FILTER (WHERE sdm.name = 'Manager') AS "required_manger",
            count(sdm.name) FILTER (WHERE sdm.name = 'TL/PL') AS "required_tl_pl",
            count(sdm.name) FILTER (WHERE sdm.name = 'Sr.Dev') AS "required_sr_dev",
            count(sdm.name) FILTER (WHERE sdm.name = 'Dev') AS "required_dev",
            count(sdm.name) FILTER (WHERE sdm.name = 'Intern') AS "required_intern",
            count(sdm.name) FILTER (WHERE sdm.name = 'BA') AS "required_ba"
            from hr_employee as hr
            left join hr_job_sbu_designation_master_rel as jd on jd.hr_job_id = hr.job_id
            left join sbu_designation_master as sdm on sdm.id = jd.sbu_designation_master_id
            where hr.emp_project_id is null and hr.sbu_type = 'sbu'
            group by hr.job_branch_id,hr.primary_skill_id) as b on a.location = b.location
            
        )"""
        self.env.cr.execute(query)
   