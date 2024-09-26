from odoo import models, fields, api
from odoo import tools


class SbuReportVertical(models.Model):
    _name = "sbu_report_employees_vertical"
    _description = "SBU report employees Vertical"
    _auto = False

    location_id = fields.Many2one('kw_res_branch', string="Location")
    skill_id = fields.Many2one('kw_skill_master',string = "Skill")

    existing_manger = fields.Integer('Existing Manager')
    existing_tl_pl = fields.Integer('Existing TL/PL')
    existing_sr_dev = fields.Integer('Existing Sr.Dev')
    existing_dev = fields.Integer('Existing Dev')
    existing_intern = fields.Integer('Existing Intern')
    existing_ba = fields.Integer('Existing BA')

    bench_manger = fields.Integer('Bench Manager')
    bench_tl_pl = fields.Integer('Bench TL/PL')
    bench_sr_dev = fields.Integer('Bench Sr.Dev')
    bench_dev = fields.Integer('Bench Dev')
    bench_intern = fields.Integer('Bench Intern')
    bench_ba = fields.Integer('Bench BA')

    forecasted_manger = fields.Integer('Forecasted Released Manager')
    forecasted_tl_pl = fields.Integer('Forecasted Released TL/PL')
    forecasted_sr_dev = fields.Integer('Forecasted Released Sr.Dev')
    forecasted_dev = fields.Integer('Forecasted Released Dev')
    forecasted_intern = fields.Integer('Forecasted Released Intern')
    forecasted_ba = fields.Integer('Forecasted Released BA')


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
            b.bench_manger,
            b.bench_tl_pl,
            b.bench_sr_dev,
            b.bench_dev,
            b.bench_intern,
            b.bench_ba,
            0 as forecasted_manger,
            0 as forecasted_tl_pl,
            0  as forecasted_sr_dev,
            0 as forecasted_dev,
            0 as forecasted_intern,
            0 as forecasted_ba
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
            count(sdm.name) FILTER (WHERE sdm.name = 'Manager') AS "bench_manger",
            count(sdm.name) FILTER (WHERE sdm.name = 'TL/PL') AS "bench_tl_pl",
            count(sdm.name) FILTER (WHERE sdm.name = 'Sr.Dev') AS "bench_sr_dev",
            count(sdm.name) FILTER (WHERE sdm.name = 'Dev') AS "bench_dev",
            count(sdm.name) FILTER (WHERE sdm.name = 'Intern') AS "bench_intern",
            count(sdm.name) FILTER (WHERE sdm.name = 'BA') AS "bench_ba"
            from hr_employee as hr
            left join hr_job_sbu_designation_master_rel as jd on jd.hr_job_id = hr.job_id
            left join sbu_designation_master as sdm on sdm.id = jd.sbu_designation_master_id
            where hr.emp_project_id is null and hr.sbu_type = 'sbu'
            group by hr.job_branch_id,hr.primary_skill_id) as b on a.location = b.location
            
        )"""
        self.env.cr.execute(query)
   