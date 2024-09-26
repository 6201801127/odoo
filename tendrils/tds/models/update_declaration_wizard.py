from odoo import models, fields, api, _
from datetime import datetime, date, timedelta


class DeclarationUpdateWizard(models.TransientModel):
    _name = 'update_declaration_wizard'
    _description = 'Wizard For IT Declaration'

    def _default_financial_yr(self):
        current_fiscal = self.env['account.fiscalyear'].search(
            [('date_start', '<=', datetime.today().date()), ('date_stop', '>=', datetime.today().date())])
        return current_fiscal
    
    @api.onchange('date_range')
    def calculate_no_of_tds(self):
        if self.date_range:
            self.total_records = len(self.env['hr.declaration'].sudo().search([('date_range','=',self.date_range.id)]))
            self.total__log_records = len(self.env['declaration_stored_data'].sudo().search([('date_range','=',self.date_range.id)]))



    date_range = fields.Many2one('account.fiscalyear', 'Financial Year', track_visibility='always',
                                 default=_default_financial_yr)
    
    total_records = fields.Integer(readonly=True,string='Total Records In Declaration')
    total__log_records = fields.Integer(readonly=True,string='Total Records In Log')



    def update_declarations(self):
        tds_rec = self.env['hr.declaration'].sudo().search([('date_range','=',self.date_range.id)])
        selected_data = self.env['declaration_stored_data'].sudo().search([])
        log_data = selected_data.filtered(lambda x:x.tds_id.id in tds_rec.ids and x.date_range.id == self.date_range.id).ids[:100]
        if len(log_data) > 0:
            for record in log_data:
                tds_rec.filtered(lambda x:x.id == selected_data.browse(record).tds_id.id).button_compute_tax()
                self.env.cr.execute(f"delete from declaration_stored_data where id = {record}")
        else:
            query = ''
            for rec in tds_rec:
                if rec.employee_id.enable_payroll == 'yes':
                    query += f"insert into declaration_stored_data (tds_id,date_range) values({rec.id},{rec.date_range.id});"
            self.env.cr.execute(query)

    def delete_declarations_btn(self):
        query = f"delete from declaration_stored_data;"
        self.env.cr.execute(query)


class DeclaratioStoreWizard(models.Model):
    _name = 'declaration_stored_data'
    _description = 'Wizard For IT Declaration Storage'

    tds_id = fields.Many2one('hr.declaration')
    date_range = fields.Many2one('account.fiscalyear', 'Financial Year', track_visibility='always',)
                                 