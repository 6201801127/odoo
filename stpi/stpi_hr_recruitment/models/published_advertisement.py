from odoo import models, fields

class PublishedAdvertisement(models.Model):
    _name ='published.advertisement'
    _description ='Stores information of published advertisements in website'
    _rec_name = 'advertisement_id'

    advertisement_id = fields.Many2one("hr.requisition.application","Advertisement",required=True,ondelete="cascade")
    job_id = fields.Many2one("hr.job","Job Position")
    directorate_id = fields.Many2one('res.branch','Directorate',domain="['|',('parent_branch_id.code','=','HQ'),('code','=','HQ')]")
    branch_id = fields.Many2one("res.branch","Center")
    no_of_post = fields.Integer("No. of Post")