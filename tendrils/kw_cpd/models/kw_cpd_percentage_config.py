from odoo import models, api, fields
from odoo.exceptions import UserError



class kw_cpd_percentage_config(models.Model):
    _name = 'kw_cpd_percentage_config'


    percentage = fields.Integer(string='CPD Disbursement Percentage')
    existing_percentage = fields.Integer(default=lambda self: self._default_existing_percentage(),string='CPD Disbursement Percentage',required = True)


    @api.model
    def create(self, vals):
        existing_record = self.search([], limit=1)
        record = super(kw_cpd_percentage_config, self).create(vals)
        if existing_record:
            existing_record.percentage = record.existing_percentage
            existing_record.existing_percentage = record.existing_percentage
            self.env.user.notify_success(f"CPD Disbursement Percentage updated to {record.existing_percentage}%.")
            record.unlink()
            return existing_record
        else:
            record.percentage = record.existing_percentage
            self.env.user.notify_success(f"CPD Disbursement Percentage set to {record.percentage}%.")
            return record
        

    
    @api.model
    def _default_existing_percentage(self):
        existing_record = self.search([], limit=1)
        return existing_record.percentage if existing_record else 0
