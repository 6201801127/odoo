# -*- coding: utf-8 -*-
"""
Module: Traineeship Submit Wizard

Summary:
    This module contains the TraineeshipSubmitWizard class, which represents a wizard for submitting traineeship details.

Description:
    The TraineeshipSubmitWizard class defines a transient model used for submitting traineeship details.
    It provides functionalities for guiding users through the process of submitting traineeship-related information.

"""
from datetime import date, datetime
from odoo.exceptions import ValidationError
from odoo import models, fields, api


class TraineeshipSubmitWizard(models.TransientModel):
    """
    Wizard for submitting traineeship details.

    This class represents a transient model used for guiding users through the process of submitting traineeship details.

    Attributes:
        _name (str): The technical name of the model.
    """
    _name = "traineeship_submit_wizard"
    _description = "Traineeship Submit Wizard"

    remark = fields.Text('Remark')
    score_traineeship = fields.Float(string="Score")
    l_k_batch_id = fields.Many2one('lk_batch_details', default=lambda self: self._context.get('current_record'))
    batch_lk_id = fields.Many2one('lk_batch', default=lambda self: self._context.get('current_id'))

    # complete_all_batch_traineeship = fields.Many2one('lk_batch',default=lambda self: self._context.get('current_record'))

    @api.constrains('score_traineeship')
    def _check_score_traineeship(self):
        for rec in self:
            if rec.score_traineeship < 0:
                raise ValidationError(f'Score should not be less than 0 against.')

    @api.multi
    def action_done(self):
        if self.remark and self._context.get('button') == 'approve':
            if self.l_k_batch_id.traineeship_status != 'Applied':
                raise ValidationError("You cannot complete this traineeship program.")
            else:
                # 'id': self.l_k_batch_id.id,
                self.l_k_batch_id.write({
                    'traineeship_comments_approved': self.remark,
                    'traineeship_status': 'Approved',
                    'traineeship_completion_date': date.today(),
                    'traineeship_complete_check': True,
                    #  'internship_id': self.l_k_batch_id.batch_id.id,
                    'lk_payroll': self.l_k_batch_id.batch_id.id})
                # record_emp = self.env['hr.employee'].sudo().search([('id', '=', self.l_k_batch_id.employee_id.id)])
                # if record_emp:
                #     record_emp.write({'training_completion_date': self.l_k_batch_id.traineeship_completion_date})
        if self.remark and self._context.get('button') == 'reject':
            if self.l_k_batch_id.traineeship_status != 'Applied':
                raise ValidationError("You cannot complete this traineeship program.")
            else:
                # 'id': self.l_k_batch_id.id,
                self.l_k_batch_id.write({'hide_button_applied': False,
                                         'traineeship_comments_approved': self.remark,
                                         'traineeship_status': 'Rejected'
                                         })
            # self.l_k_batch_id.internship_id = self.l_k_batch_id.batch_id.id
            # self.l_k_batch_id.lk_payroll = self.l_k_batch_id.batch_id.id

        elif self.remark and self._context.get('button') == 'approve_all':
            self.batch_lk_id.state = 'approve'
            for rec in self.batch_lk_id.training_completion_details_ids:
                if rec.traineeship_status == 'Applied':
                    rec.write({'batch_id': self.batch_lk_id.id,
                               'traineeship_comments_approved': self.remark,
                               'traineeship_status': 'Approved',
                               'traineeship_completion_date': date.today(),
                               'hide_button_applied': True,
                               'traineeship_complete_check': True,
                               'internship_id': self.batch_lk_id.id,
                               'lk_payroll': self.batch_lk_id.id
                               })

        elif self._context.get('button') == 'approve_rh_internship':
            if self.l_k_batch_id.internship_status in ['Approved']:
                raise ValidationError("The Internship has already been approved.")
            else:
                # 'id': self.l_k_batch_id.id,
                self.l_k_batch_id.write({
                    'internship_comments_approved': self.remark if self.remark else '',
                    'internship_status': 'Approved',
                    'internship_completion_date': date.today(),
                    'internship_complete_check': True,
                    'lk_payroll_internship': self.l_k_batch_id.internship_id.id
                })
            # self.l_k_batch_id.lk_payroll_internship = self.l_k_batch_id.internship_id.id
        elif self._context.get('button') == 'reject_rh_internship':
            if self.l_k_batch_id.internship_status in ['Approved']:
                raise ValidationError("The Internship has already been approved.")
            elif self.l_k_batch_id.internship_status == False:
                raise ValidationError("You cannot complete this internship program.")
            else:
                # 'id': self.l_k_batch_id.id,
                self.l_k_batch_id.write({
                    'internship_comments_approved': self.remark if self.remark else '',
                    'internship_status': 'Rejected',
                })
                # 'internship_completion_date': date.today(),
                # 'internship_complete_check': True,
                # 'lk_payroll_internship': self.l_k_batch_id.internship_id.id
        elif self._context.get('button') == 'approve_all_rh_internship':
            self.batch_lk_id.state = 'approve'
            for rec in self.batch_lk_id.internship_completion_details_ids:
                rec.write({
                    'internship_id': self.batch_lk_id.id,
                    'lk_payroll_internship': self.batch_lk_id.id,
                    'internship_comments_approved': self.remark,
                    'internship_status': 'Approved',
                    'internship_completion_date': date.today(),
                    'internship_complete_check': True
                })
        elif self._context.get('button') == 'Complete_all_traineeship_manager':

            self.batch_lk_id.state = 'confirm'
            for rec in self.batch_lk_id.training_completion_details_ids:
                # 'batch_id': self.batch_lk_id.id,
                if rec.traineeship_status == 'In Progress':
                    rec.write({
                        'traineeship_status': 'Applied',
                        'traineeship_score': self.score_traineeship,
                        'traineeship_comments_applied': self.remark
                    })
        elif self._context.get('button') == 'Complete_all_internship':
            self.batch_lk_id = 'confirm'
            for rec in self.batch_lk_id.internship_completion_details_ids:
                # 'batch_id': self.batch_lk_id.id,
                rec.write({
                    'internship_score': self.score_traineeship,
                    'internship_comments_applied': self.remark
                })
        else:
            pass
