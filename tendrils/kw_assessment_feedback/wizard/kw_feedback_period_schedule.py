from odoo import api, models,fields
from odoo.exceptions import UserError,ValidationError
from odoo import exceptions,_

class kw_feedback_schedule(models.TransientModel):
    _name       ='kw_feedback_schedule'
    _description= 'Publish Feedback wizard'

    def _get_default_feedback(self):
        datas   = self.env['kw_feedback_assessment_period'].browse(self.env.context.get('active_ids'))
        return datas

    period_ids = fields.Many2many('kw_feedback_assessment_period',readonly=1, default=_get_default_feedback)

    @api.multi
    def schedule_feedback(self):
        final_config = self.env['kw_feedback_final_config']
        feedback_details = self.env['kw_feedback_details']

        for records in self.period_ids:
            if records.state == '1':
                if not records.assessors or not records.assessees:
                    ## If no assessor or no assessee in the list then validation error before generate feedbacks.
                    raise ValidationError("Assessor or Assessee list should not be blank.")
                else:
                    duplicate_rec = feedback_details.search([('period_id', '=', records.id)])
                    if duplicate_rec:
                        assessor = duplicate_rec.filtered(lambda record: record.assessor_id.ids not in records.assessors.ids or record.assessee_id.id not in records.assessees.ids)
                        if assessor:
                            assessor.unlink()

                for assessee in records.assessees:
                    details_vals = {}
                    existing_record = feedback_details.search(
                        [('assessor_id', 'in', records.assessors.ids), ('assessee_id', '=', assessee.id),
                         ('period_id', '=', records.id)])

                    ## if feedback not started then update survey_id else don't
                    if existing_record:

                        if existing_record.feedback_status in ['0','1']:
                            existing_record.update({
                                'survey_id': records.survey_id.id
                                })
                        else:
                            pass

                        ## If exisiting record then update the dates and tag id
                        existing_record.write({
                            'assessment_tagging_id':records.map_resource_id.assessment_tagging_id.id if records.map_resource_id else records.prob_assessment_tag_id.id,
                            'assessment_from_date': records.from_date if records.from_date else False, 
                            'assessment_to_date': records.to_date if records.to_date else False,
                            'assessment_date':records.assessment_date if records.assessment_date else False,
                        })
                    else:
                        details_vals = {
                            'assessor_id': [(6, 0, records.assessors.ids)],
                            'assessee_id': assessee.id,
                            'assessment_tagging_id':records.map_resource_id.assessment_tagging_id.id if records.map_resource_id else records.prob_assessment_tag_id.id,
                            'survey_id': records.survey_id.id,
                            'assessment_from_date': records.from_date if records.from_date else False,
                            'assessment_to_date': records.to_date if records.to_date else False,
                            'assessment_date': records.assessment_date if records.assessment_date else False,
                            'meeting_id': records.meeting_id.id if records.meeting_id else False,
                            'period_id': records.id,
                        }
                       
                        details_created_record = feedback_details.create(details_vals)
                        
                        if details_created_record.assessment_tagging_id.assessment_type == 'probationary':
                            try:
                                template = self.env.ref('kw_assessment_feedback.kw_schedule_probationary_feedback_email_template')
                                if template:
                                    template.send_mail(details_created_record.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                            except Exception as e:
                                pass
                    
                for new_records in records.feedback_id:
                    if new_records.feedback_status in ['0', '1', '2']:
                        duplicate_rec = final_config.search([('feedback_details_id', '=', new_records.id)])
                        if duplicate_rec:
                            assessor_rec = duplicate_rec.filtered(lambda record: record.assessor_id.id not in new_records.assessor_id.ids or record.assessee_id.id != new_records.assessee_id.id)
                            
                            if assessor_rec:
                                assessor_rec.unlink()

                        for assessor in new_records.assessor_id:
                            vals = {}
                            existing_records = final_config.search(
                                [('assessor_id', '=', assessor.id), ('assessee_id', '=', new_records.assessee_id.id),
                                 ('feedback_details_id', '=', new_records.id)])

                            ## if feedback not started then update survey_id else don't
                            if existing_records:
                                for existing_record in existing_records:
                                    if existing_record.feedback_status == '1':
                                        existing_record.update({
                                            'survey_id': new_records.survey_id.id
                                        })
                                    else:
                                        pass

                                    ## If exisiting record then update the dates and tag id
                                    existing_record.write({
                                        'assessment_from_date': new_records.assessment_from_date if new_records.assessment_from_date else False, 
                                        'assessment_to_date': new_records.assessment_to_date if new_records.assessment_to_date else False,
                                        'assessment_date':new_records.assessment_date if new_records.assessment_date else False,
                                    })
                            else:
                                vals = {
                                    'assessor_id': assessor.id,
                                    'assessee_id': new_records.assessee_id.id,
                                    'survey_id': new_records.survey_id.id,
                                    'assessment_from_date': new_records.assessment_from_date if new_records.assessment_from_date else False,
                                    'assessment_to_date': new_records.assessment_to_date if new_records.assessment_to_date else False,
                                    'assessment_date': new_records.assessment_date if new_records.assessment_date else False,
                                    'feedback_details_id': new_records.id
                                }
                                created_record = final_config.create(vals)

                                if created_record.feedback_details_id.assessment_tagging_id.assessment_type == 'periodic':
                                    try:
                                        template = self.env.ref('kw_assessment_feedback.kw_schedule_periodic_feedback_email_template')
                                        if template:
                                            template.send_mail(created_record.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                                    except Exception as e:
                                        pass

                        new_records.write({
                            'feedback_status': '1'
                        })
                records.write({
                    'state': '2'
                })

        self.env.user.notify_success("Assessment scheduled successfully.")
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
