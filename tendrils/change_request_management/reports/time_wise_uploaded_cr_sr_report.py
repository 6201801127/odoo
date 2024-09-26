from odoo import models, fields, api, tools

class TimeRangeWiseCrSrReport(models.Model):
    """
    This class represents Project Wise cr sr report in Odoo.
    """
    _name = 'time_range_wise_cr_sr_report'
    _description = 'Time Range Wise CR SR Report'
    _auto = False


    project_id = fields.Many2one('project.project', string='Project Name')
    morning_cr_count =fields.Integer(string='Monrning CR Count')
    afternoon_cr_count =fields.Integer(string='Afternoon CR Count')
    evening_cr_count =fields.Integer(string='Evening CR Count')
    night_cr_count =fields.Integer(string='NIght CR Count')
    morning_sr_count =fields.Integer(string='Morning SR Count')
    afternoon_sr_count =fields.Integer(string='Afternoon SR Count')
    evening_sr_count =fields.Integer(string='Evening SR Count')                 
    night_sr_count =fields.Integer(string='Night SR Count')


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
               SELECT   
                    ROW_NUMBER() OVER () AS id,
                    kcm.project_id AS project_id,
                    COUNT(CASE WHEN kcm.cr_type = 'CR' AND EXTRACT(HOUR FROM kcm.cr_uploaded_on AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata') BETWEEN 5 AND 11 THEN 1 ELSE NULL END) AS morning_cr_count,
                    COUNT(CASE WHEN kcm.cr_type = 'CR' AND EXTRACT(HOUR FROM kcm.cr_uploaded_on AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata') BETWEEN 12 AND 16 THEN 1 ELSE NULL END) AS afternoon_cr_count,
                    COUNT(CASE WHEN kcm.cr_type = 'CR' AND EXTRACT(HOUR FROM kcm.cr_uploaded_on AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata') BETWEEN 17 AND 20 THEN 1 ELSE NULL END) AS evening_cr_count,
                    COUNT(CASE WHEN kcm.cr_type = 'CR' AND (EXTRACT(HOUR FROM kcm.cr_uploaded_on AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata') >= 21 OR EXTRACT(HOUR FROM kcm.cr_uploaded_on AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata') <= 4) THEN 1 ELSE NULL END) AS night_cr_count,
                    COUNT(CASE WHEN kcm.cr_type = 'Service' AND EXTRACT(HOUR FROM kcm.cr_uploaded_on AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata') BETWEEN 5 AND 11 THEN 1 ELSE NULL END) AS morning_sr_count,
                    COUNT(CASE WHEN kcm.cr_type = 'Service' AND EXTRACT(HOUR FROM kcm.cr_uploaded_on AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata') BETWEEN 12 AND 16 THEN 1 ELSE NULL END) AS afternoon_sr_count,
                    COUNT(CASE WHEN kcm.cr_type = 'Service' AND EXTRACT(HOUR FROM kcm.cr_uploaded_on AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata') BETWEEN 17 AND 20 THEN 1 ELSE NULL END) AS evening_sr_count,
                    COUNT(CASE WHEN kcm.cr_type = 'Service' AND (EXTRACT(HOUR FROM kcm.cr_uploaded_on AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata') >= 21 OR EXTRACT(HOUR FROM kcm.cr_uploaded_on AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata') <= 4) THEN 1 ELSE NULL END) AS night_sr_count
                FROM
                    kw_cr_management AS kcm
                WHERE
                    kcm.stage = 'Uploaded'
                GROUP BY
                    kcm.project_id
          )"""
        self.env.cr.execute(query)
