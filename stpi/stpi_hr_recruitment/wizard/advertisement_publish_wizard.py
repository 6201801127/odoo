from odoo import fields,models,api

class AdvertisementPublish(models.TransientModel):
    _name = 'advertisement.publish'
    _description = 'Advertisement Publish Wizard'

    advertisement_id = fields.Many2one("hr.requisition.application","Advertisement",required=True)
    job_ids = fields.Many2many("hr.job",string="Job Positions")
    
    @api.multi
    def action_confirm_publish_advertisement(self):
        query = f'select job_id,branch_id,directorate_id,count(job_id) as no_of_post from advertisement_line where allowed_category_id = {self.advertisement_id.id} group by job_id,branch_id,directorate_id'

        self._cr.execute(query)
        result = self._cr.dictfetchall()
        # self.published_advertisements = False
        if self.advertisement_id.published_advertisements:
            self.advertisement_id.published_advertisements.unlink()

        self.advertisement_id.published_advertisements = [[0,0,data] for data in result]

        self.advertisement_id.write({'state':'published'})