from datetime import datetime,date
from odoo.tools.misc import format_date
from odoo import models, fields, api, tools, _

class CompetencyReport(models.Model):
    _name           = "competency_report"
    _description    = "Competency Report"
    _auto           = False

    emp_id = fields.Many2one('hr.employee',string="Employee")
    emp_name = fields.Char(string="Employee Name")
    kw_ids = fields.Integer(string="Kw ID")
    finalcompetancy = fields.Text(string="Final Competancy")
    behavior_indicator = fields.Char(string="Behavior Indicator")
    competency = fields.Text(string="Competancy")


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s as (
            
        with c as
        (
            select kw_ids,emp_id,Q.Page_id, quizz_mark,sum(value_number) as value_number , count(*) as total
            from hr_appraisal  A 
            join survey_user_input_line L on L.user_input_id=a.lm_input_id
            join survey_question Q on q.id=L.question_id
            group by emp_id, Q.Page_id, quizz_mark,kw_ids

        ), d  AS
        (
            select emp_id, kw_ids,Page_id,sum(value_number) as value_number, max(total) as maxTotal
            from c
            group by emp_id, Page_id, kw_ids
        ), e as 
        (
            select d.emp_id,d.kw_ids, d.Page_id, max(quizz_mark) as quizz_mark,sum(d.value_number) as value_number
            from d
            join c on d.emp_id=c.emp_id and  d.Page_id=c.Page_id and d.maxTotal=c.Total and c.kw_ids = d.kw_ids
            group by d.emp_id, d.Page_id  ,d.kw_ids      
        ), f as 
        (
            select emp_id,kw_ids,quizz_mark, count(*) as total,sum(value_number) as value_number
            from e
            group by emp_id, quizz_mark,kw_ids
        ), g as
        (
            select emp_id,kw_ids, max(total) as maxTotal,sum(value_number) as value_number
            from f
            group by emp_id,kw_ids
        ), h as 
        (
            select g.emp_id, max(f.quizz_mark) as quizz_mark,g.kw_ids,sum(g.value_number) as value_number
            from g 
            join f on g.emp_id=f.emp_id and g.maxtotal=f.total and g.kw_ids = f.kw_ids
            group by g.emp_id, g.kw_ids
        )
        select row_number() over(ORDER BY em.id) as id,em.id as emp_id, em.name as emp_name, h.kw_ids,h.value_number as user_score,e.value_number as lm_score
        , case h.quizz_mark when 1 then 'Ignorant'  when 2 then 'Learner' when 3 then 'Pracitioner' when 4 then 'Expert' when 5 then 'Role Model' else 'NA' end as FinalCompetancy
        , P.title As "behavior_indicator"
        , case e.quizz_mark when 1 then 'Ignorant'  when 2 then 'Learner' when 3 then 'Pracitioner' when 4 then 'Expert' when 5 then 'Role Model' else CAST (e.value_number AS varchar) end as competency
        from h
		
        join e on e.emp_id=h.emp_id and e.kw_ids = h.kw_ids
        join hr_employee em on em.id=h.emp_id
        join survey_page p on p.id=e.Page_id
        order by h.emp_id,h.kw_ids, e.Page_id  
        )""" % (self._table))

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        # print("no_filter",args)
        query = "select row_number() over(order by id desc) as slno, id from kw_appraisal"
        self._cr.execute(query)
        ids = self._cr.dictfetchall()
        appraisal_id = 0

        if self._context.get('financial_year_check') or self._context.get('filter_current_period'):

            if len(ids) > 0:
                appraisal_id = int(ids[0]['id']) if 'id' in ids[0] else 0

            # print(appraisal_id)
            args += [('kw_ids','=',appraisal_id)]
            # print(args)

        return super(CompetencyReport, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):

        query = "select row_number() over(order by id desc) as slno, id from kw_appraisal"
        self._cr.execute(query)
        ids = self._cr.dictfetchall()
        appraisal_id = 0

        if self._context.get('financial_year_check') or self._context.get('filter_current_period'):

            if len(ids) > 0:
                appraisal_id = int(ids[0]['id']) if 'id' in ids[0] else 0
                # print("read_group",self.appr_id.kw_ids)
            domain += [('kw_ids','=',appraisal_id)]
        
        return super(CompetencyReport, self).read_group(domain, fields, groupby, offset=offset, limit=limit,orderby=orderby, lazy=lazy)
    