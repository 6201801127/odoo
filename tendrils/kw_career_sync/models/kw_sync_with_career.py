# -*- coding: utf-8 -*-
from odoo import models, fields, api


class KwCareerSync(models.Model):
    _name = "kw_sync_with_career"
    _description = "Sync Master and Job With Career Site"

    name = fields.Char("Name")

    def sync_master(self):
        rec = self.env['kw_hr_job_positions']
        rec.sync_job_master()

    def sync_job(self):
        rec = self.env['kw_hr_job_positions']
        rec.sync_job_lists()

    def sync_log(self):
        res = self.env['ir.actions.act_window'].for_xml_id(
            'kw_career_sync', 'kw_recruitment_career_sync_act_window')
        return res

    def sync_walkin(self):
        rec = self.env['hr.applicant']
        rec.sync_career_applicant()

    def sync_campus(self):
        rec = self.env['hr.applicant']
        rec.sync_campus_applicant()
