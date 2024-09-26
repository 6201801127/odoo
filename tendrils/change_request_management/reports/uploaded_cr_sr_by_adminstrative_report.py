from odoo import models, fields, tools
from odoo.exceptions import AccessError, ValidationError


class UploadedReport(models.Model):
    _name = 'uploaded_by_administrators_report'
    _description = 'Uploaded Report By Adminstrators'
    _auto = False

    uploaded_by = fields.Many2one('hr.employee', string='Uploaded By')
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
                COUNT(CASE WHEN km.cr_type = 'Service' THEN km.id END) AS service_count
            FROM 
                kw_cr_management km
            WHERE 
                km.uploaded_by IS NOT NULL 
                and stage = 'Uploaded'
            GROUP BY 
                km.uploaded_by
            )
        """ % (self._table,)
        
        self.env.cr.execute(query)

class DaywiseReport(models.Model):
    _name = 'day_wise_cr_sr_report'
    _description = 'Day Wise CR SR Report'
    _auto = False
    _order = "uploaded_date asc"

    uploaded_date = fields.Date(string='Uploaded Date')
    cr_count = fields.Integer(string='CR Count')
    sr_count = fields.Integer(string='SR Count')


    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)        
        query = """
            CREATE OR REPLACE VIEW %s AS (
                            WITH all_dates AS (
                                SELECT 
                                    generate_series(
                                        (SELECT DATE_TRUNC('day', MIN(cr_uploaded_on)) FROM kw_cr_management WHERE stage = 'Uploaded'),
                                        (SELECT DATE_TRUNC('day', MAX(cr_uploaded_on)) FROM kw_cr_management WHERE stage = 'Uploaded'),
                                        INTERVAL '1 day'
                                    ) AS uploaded_date
                            )
                            SELECT  
                                row_number() over () as id,
                                COUNT(kcm.cr_type = 'CR' OR NULL) AS cr_count,
                                COUNT(kcm.cr_type = 'Service' OR NULL) AS sr_count,
                                DATE(ad.uploaded_date) AS uploaded_date
                            FROM
                                all_dates ad
                            LEFT JOIN
                                kw_cr_management AS kcm ON DATE_TRUNC('day', kcm.cr_uploaded_on) = DATE_TRUNC('day', ad.uploaded_date) AND kcm.stage = 'Uploaded'
                            GROUP BY
                                DATE(ad.uploaded_date)
                            ORDER BY
                                DATE(ad.uploaded_date) ASC


                )
        """ % (self._table,)
        
        self.env.cr.execute(query)
