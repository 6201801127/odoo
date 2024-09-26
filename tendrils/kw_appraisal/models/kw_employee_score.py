from odoo import models, fields, api
from odoo.exceptions import  ValidationError


class kw_employee_score(models.Model):
    _name = 'kw_employee_score'
    _description = 'Employee score'
    _rec_name    = 'year_id'

    year_id = fields.Many2one('kw_archives_year',string='Kw Period ID')
    employee_id = fields.Many2one('hr.employee',string='Employee')
    appraisal_mark = fields.Char(string='Appraisal Score')
    kra = fields.Float(string="KRA Score")
    year = fields.Char(related='year_id.year',string="Year")
    prd_no = fields.Integer(related='year_id.period_no',string="Period No")
    kw_id = fields.Integer(related='employee_id.kw_id',string="Kw Id")
    kw_period = fields.Integer(related='year_id.kw_period_id',string="Tendrils Period No")

    @api.multi
    def previous_appraisal_button(self):
        pid = self.kw_period
        uid = self.kw_id
        url = "https://portal.csmpl.com/Appraisal/FinalApdetails.aspx?Pid=%d&uid=%d"%(pid,uid)
        return{
            'type': 'ir.actions.act_url',
            'name': "previous appraisal",
            'target': 'blank',
            'url': url
        }