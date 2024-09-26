from odoo import fields, models, api, tools


class EOSEmployementCorrectionReport(models.Model):
    _name = 'employement_correction_report'
    _description = 'Employement Correction Report'
    _auto = False

    employee_id =fields.Many2one('hr.employee', string='Department')
    department_id = fields.Many2one('hr.department', string='Department')
    designation_id = fields.Many2one('hr.job', string="Designation")
    last_working_day= fields.Date(string='Last Working Day')
    reason = fields.Char("Reason")

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f""" CREATE or REPLACE VIEW %s AS (
        select 
            row_number() over() AS id,
            e.id AS employee_id,
            e.department_id as department_id,
            e.job_id as designation_id,
            e.resignation_reason as reason,
            e.last_working_day as last_working_day             
        from
            hr_employee e where e.active = False and e.resignation_reason is null and last_working_day is null
        
 )""" % (self._table))
        
    @api.multi   
    def employment_corr_btn(self):
        view_id = self.env.ref('kw_eos.employee_close_form_views').id
        return {
            'name': 'Employement Correction',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'close_employment_wizard',
            'view_id': view_id,
            'target': 'new',
            'context': {'default_employee_id':self.employee_id.id, 'create': False, 'delete': False},
            'flags':{'mode':'edit'},
        }


        
        
