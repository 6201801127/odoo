# -*- coding: utf-8 -*-

from odoo import models, fields, api

from odoo.exceptions import ValidationError

class kw_in_memory_data(models.Model):

    _name           = 'kw_in_memory_data'
    _description    = 'Facereader In Memory Data'  
    _rec_name       = 'image_name'


    
    employee_id     = fields.Many2one(
        string='Employee Id',
        comodel_name='hr.employee',
        ondelete='restrict',
    )
    
    face_model_image_ids = fields.One2many(
        string='Face Model Images',
        comodel_name='kw_face_training_data',
        inverse_name='employee_id',
    )

    # face_model_image_ids = fields.Many2many(
    #     string='Face Model Images',
    #     comodel_name='kw_face_training_data',
    #     relation='kw_face_reader_employee_training_rel',
    #     column1='eid',
    #     column2='tid',
    # )
       
    face_model_image_count = fields.Integer(
        string='Model Image Count',compute='_compute_face_model_image_count', default=0
    )
    

    face_matched_log_ids = fields.One2many(
        string='Face Model Matched Logs',
        comodel_name='kw_face_matched_log',
        inverse_name='employee_id',
    )

    # face_matched_log_ids = fields.Many2many(
    #     string='Face Model Matched Logs',
    #     comodel_name='kw_face_matched_log',
    #     relation='kw_face_reader_employee_matched_log_rel',
    #     column1='eid',
    #     column2='mid',
    # )

    
    latest_employee_matched_time = fields.Datetime(
        string='Latest Matched',
        compute='_compute_employee_latest_matched_time',
        store = True
    )
    


    @api.depends('face_model_image_ids')
    def _compute_face_model_image_count(self):
        for rec in self:
            rec.face_model_image_count = len(rec.face_model_image_ids)

    @api.depends('face_matched_log_ids')
    def _compute_employee_latest_matched_time(self):
        for rec in self:
            if rec.face_matched_log_ids:
                rec.latest_employee_matched_time = max(match_rec.match_date_time  for match_rec in rec.face_matched_log_ids)

                #print(rec.latest_employee_matched_time)
                

    
    @api.multi
    def unlink(self):
        """
            Delete all record(s) from recordset
            return True on success, False otherwise
    
            @return: True on success, False otherwise
    
            #TODO: process before delete resource
        """
        raise ValidationError('Deleting records from here will delete the Employee Records. To delete the training record edit each employee record and remove them.')

        #result = super(kw_hr_employee, self).unlink()
    
        # return result
    