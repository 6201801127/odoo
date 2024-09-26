from odoo import models, fields, api
from odoo import tools
from datetime import date, datetime


class YearOnYearResourceReport(models.Model):
    _name = "mis_report_employees_joined_and_resigned"
    _description = "mis report employees joined and resigned"
    _rec_name = 'year'
    _auto = False
    _order = "year asc"

    year = fields.Integer(string="Year")
    month = fields.Char(string="Month")

    fte_opening = fields.Integer(string="Existing FTE")
    fte_totalonboard = fields.Integer(string="Joined FTE")
    fte_totaloffboard = fields.Integer(string="Left FTE")
    fte_closing = fields.Integer(string="Total FTE")

    ret_opening = fields.Integer(string="Existing RET")
    ret_totalonboard = fields.Integer(string="Joined RET")
    ret_totaloffboard = fields.Integer(string="Left RET")
    ret_closing = fields.Integer(string="Total RET")

    ce_opening = fields.Integer(string="Existing Contractual")
    ce_totalonboard = fields.Integer(string="Joined Contractual")
    ce_totaloffboard = fields.Integer(string="Left Contractual")
    ce_closing = fields.Integer(string="Total Contractual")

    grand_total = fields.Integer(string="Grand Total", help="Total of 'Total RET'+'Total FTE'+'Total Contractual'")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f""" CREATE or REPLACE VIEW {self._table} as (
        with RECURSIVE a as 
        (
            SELECT employement_type , 
            date_part('Year', last_working_day) AS Year, TO_CHAR(last_working_day, 'Month') AS Month, 
            count(last_working_day) AS TotalOffboard
            FROM hr_employee WHERE employement_type != 5
            group by employement_type, date_part('Year', last_working_day), TO_CHAR(last_working_day, 'Month') 
        ), 
        b AS 
        (
            SELECT employement_type, 
            date_part('Year', date_of_joining) AS Year, TO_CHAR(date_of_joining, 'Month') AS Month , 
            count(date_of_joining) AS TotalOnboard 
            FROM hr_employee where employement_type != 5
            group by employement_type , date_part('Year', date_of_joining) , TO_CHAR(date_of_joining, 'Month')
        ), 
        c AS 
        (
            SELECT coalesce(a.employement_type, b.employement_type) AS employement_type, coalesce(a.year,b.Year) AS Year, 
            coalesce(a.Month,b.Month) AS Month
            , TO_DATE(concat(coalesce(a.year,b.Year), coalesce(a.Month,b.Month),'01') , 'yyyyMonth DD') AS Date
            , coalesce(TotalOnboard, 0) AS TotalOnboard, coalesce(TotalOffboard, 0) AS TotalOffboard
            FROM a 
            full outer join b on a.Year=b.Year and a.Month=b.Month and a.employement_type=b.employement_type
        ), 
        curr  AS 
        (
            SELECT ROW_NUMBER() over (partition by employement_type  order by date) AS rid, 
             employement_type, Year, Month, Date, 0 as Opening, TotalOnboard, TotalOffboard
            FROM c
        ), 
        e AS
        (
                SELECT employement_type, Year, Month, Date, Opening,  TotalOnboard, TotalOffboard,
                cast(Opening+TotalOnboard-TotalOffboard AS int) AS Closing, rid
                FROM curr
                where rid=1
            union all
                SELECT curr.employement_type, curr.Year, curr.Month, curr.date, 
                curr.opening + prev.closing, curr.TotalOnboard, curr.TotalOffboard, 
                cast(curr.opening + prev.closing + curr.TotalOnboard - curr.TotalOffboard AS int) AS closingbal, 
                curr.rid
                FROM curr 
                inner join e prev on curr.rid = prev.rid + 1 and curr.employement_type=prev.employement_type
        )
        SELECT row_number() over() as id, Year, TRIM(Month) as Month
        , SUM(CASE WHEN employement_type=1 THEN opening ELSE 0 END) AS fte_opening
        , SUM(CASE WHEN employement_type=1 THEN TotalOnboard ELSE 0 END) AS fte_totalonboard 
        , SUM(CASE WHEN employement_type=1 THEN TotalOffboard ELSE 0 END) AS fte_totaloffboard
        , SUM(CASE WHEN employement_type=1 THEN Closing ELSE 0 END) AS fte_closing 
        , SUM(CASE WHEN employement_type IN (2,3) THEN opening ELSE 0 END) AS ret_opening
        , SUM(CASE WHEN employement_type IN (2,3) THEN TotalOnboard ELSE 0 END) AS ret_totalonboard 
        , SUM(CASE WHEN employement_type IN (2,3) THEN TotalOffboard ELSE 0 END) AS ret_totaloffboard
        , SUM(CASE WHEN employement_type IN (2,3) THEN Closing ELSE 0 END) AS ret_closing 
        , SUM(CASE WHEN employement_type=6 THEN opening ELSE 0 END) AS ce_opening
        , SUM(CASE WHEN employement_type=6 THEN TotalOnboard ELSE 0 END) AS ce_totalonboard 
        , SUM(CASE WHEN employement_type=6 THEN TotalOffboard ELSE 0 END) AS ce_totaloffboard
        , SUM(CASE WHEN employement_type=6 THEN Closing ELSE 0 END) AS ce_closing 
        , SUM(Closing) AS grand_total
        FROM e
        group by Year, Month, Date
        ORDER BY Date
        )"""
        # print("tracker quey",query)
        self.env.cr.execute(query)
        
        
        
        
        
class kw_MIS_employee_report(models.TransientModel):
    _name = "kw_mis_employee_reports_wizard"
    _description = "wizard year"

        # def get_years():
        #     year_list = []
        #     # start_year = (date.today().year - (date.today().year - 2000))
        #     for i in range((date.today().year), 1997, -1):
        #         year_list.append((i, str(i)))
        #     return year_list
    def get_fiscal_year(self):
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        return current_fiscal
        
    fiscalyr = fields.Many2one('account.fiscalyear', string="Finacial Year", default=get_fiscal_year)

    def get_year_to_year_employee_report(self):
        # select_year = self.env['mis_report_employees_joined_and_resigned'].search([])
        # if select_year:
        #     select_year.check_year = self.year
        # else:
        #     self.env['mis_report_employees_joined_and_resigned'].create({'year': self.check_year.id})

        tree_view_id = self.env.ref('kw_employee_info_system.kw_MIS_report_list_tree').id
        # check_year_name = self.year
        search_domain = ['|','&',('year','=',self.fiscalyr.date_start.year),('month','in',['April','May','June','July','August','September','October','November','December']),
                        '&',('year', '=', self.fiscalyr.date_stop.year),('month','in',['January','February','March'])]
        
    
        action = {
            'name': f'Year on Year Resources ({self.fiscalyr.name})',
            'type': 'ir.actions.act_window',
            'res_model': 'mis_report_employees_joined_and_resigned',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(tree_view_id, 'tree')],
            'target': 'main',
            'domain': search_domain,
            'view_id': tree_view_id
        }
        return action





