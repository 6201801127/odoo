import pytz
import math
from datetime import datetime, date
from werkzeug import urls

from odoo import models, fields, api, SUPERUSER_ID
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import ValidationError


class kw_feedback_details(models.Model):
    _name = 'kw_feedback_config_details'
    _description = 'Counselling feedback'
    
    
    
    deliverable_rec = fields.Text(string="Deliverables")
    excepted_achivement_rec = fields.Text(string="Expected Outcome")
    
    pip_counselling_id = fields.Many2one('kw_pip_counselling_details')
    pip_assessor_counselling_id = fields.Many2one('kw_pip_counselling_details')
    assessor_id = fields.Many2one('hr.employee',string='Assessor',domain="[('id','!=',assessee_id)]")
    assessee_id = fields.Many2one('hr.employee',string='Assessee')
    keep_observation = fields.Selection(string="To Keep under observation", selection=[('Yes', 'Yes'), ('No', 'No')])
    observation_duration = fields.Selection(string="Observation Duration",
                                            selection=[('7', '7 Days'), ('15', '15 Days'), ('30', '30 Days'),
                                                       ('45', '45 Days'), ('60', '60 Days')], )
    improve_remark  = fields.Text(string='Describe The Reason')
    assessor_status = fields.Selection(string="Status",selection=[('1','Counselling Feedback'),('2','Improvement feedback')])
    areas_improvement_data = fields.Text(string="Remark")
    accessor_final_feedback = fields.Selection(string="Feedback",selection=[('Meet Expectations', 'Meet Expectations'), ('Doesn’t meet expectation', 'Doesn’t meet expectation'),('Not Applicable','Not Applicable')])
    
    pip_improve_counselling_id = fields.Many2one('kw_pip_counselling_details')
    deliverables_uplod_doc = fields.Binary(string=u'Upload Document', attachment=True, )
    file_name = fields.Char(string='Document Name')
    upload_doc_user_enable = fields.Boolean(string="Doc upload",default=False,compute="_compute_doc_upload")
    deliver_status_user = fields.Selection(string="Status",selection=[('Not Started', 'Not Started'), ('In Progress', 'In Progress'),('Completed','Completed')])
    pip_final_assessor_feedback_id = fields.Many2one('kw_pip_counselling_details')
    final_assessor_id = fields.Many2one('hr.employee',string="Assessor")
    assessor_final_outcome=fields.Selection(string="Final Outcome",selection=[('Meet Expectations', 'Meet Expectations'), ('Doesn’t meet expectation', 'Doesn’t meet expectation')])
    assessor_final_remark= fields.Text(string="Final remark Assessor")

    # user_hide_doc_upload = fields.Boolean(string="Hide doc upload field",default=False,compute="_compute_doc_upload")

    def _compute_doc_upload(self):
        for rec in self:
            record_counselling = self.env['kw_pip_counselling_details'].sudo().search(
                [('id', '=', rec.pip_counselling_id.id)])
            if record_counselling and record_counselling.feedback_status in ['3','4']:
                rec.upload_doc_user_enable = True
            # if record_counselling and record_counselling.pip_ref_id.raised_by.id != record_counselling.assessee_id.id:
            #     print(record_counselling,"=========record_counselling===========",self.env.user.employee_ids.id,rec.assessee_id.id)
            #     rec.user_hide_doc_upload = True
