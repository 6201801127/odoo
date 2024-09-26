from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


class ResourceUpdaterecord(models.TransientModel):
    _name = 'resource_qty_update_wiz'
    _description = "Resource Quantity Update Wiz"

    resource_map_id = fields.Many2one('kw_resource_mapping_report', string='Employee Role')
    resource_no = fields.Integer(string='No of resource required')
    opportunity_id = fields.Many2one('crm.lead',string='Opportunity Name')
    resource_available = fields.Integer(string='No of resource available')
    resource_required = fields.Integer(string='No of resources Requirement')
    # engagement_start_date = fields.Date(sting = "Engagemenet Start Date")
    # engagement_end_date = fields.Date(sting = "Engagemenet End Date")
    no_of_resource_required = fields.Integer(string='No Of Resource Required')
    remark = fields.Text(string='Remark')


    @api.multi
    def btn_resource_qty_update(self):
        for record in self:
            if record.resource_map_id:
                record.resource_map_id.write({
                    'resource_available': record.resource_available,
                    'resource_required':record.resource_required,
                    # 'engagement_start_date': record.engagement_start_date,
                    # 'engagement_end_date': record.engagement_end_date,
                    'no_of_resource_required': record.no_of_resource_required,
                    # 'remark':record.remark
                })


            
    @api.constrains('no_of_resource_required','resource_available')
    def check_resource_available(self):
        if self.no_of_resource_required<self.resource_available:
            raise ValidationError("Resource Availble should be equal to or less than Resources Required.")
        # if self.engagement_end_date < self.engagement_start_date:
        #     raise ValidationError("Engagement End Date should be greater than Engagement Start Date.")