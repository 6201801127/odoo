from odoo import models, fields, api

class TrainingResultNotification(models.TransientModel):
    _name        = 'kw_training_result_notify_session'
    _description = "Wizard: send result notification mail to participants"

    def _default_active_id(self):
        return self.env['kw_training_assessment'].browse(self._context.get('active_id'))


    assessment_id       = fields.Many2one('kw_training_assessment', string="Assessment", default=_default_active_id)
    employee_ids        = fields.Many2many("hr.employee",string="CC:")

    @api.multi
    def send_result_mail(self):
        training        = self.assessment_id.training_id
        plan            = training.plan_ids.filtered(lambda r:r.state == 'approved')
        participants    = plan and plan.participant_ids or self.env['hr.employee']
        
        participant_emails  = ','.join(participants.mapped('work_email'))
        cc_emails           =  ','.join(self.employee_ids.mapped('work_email'))
        data                = []

        if self.assessment_id.assessment_type == 'offline':
            max_mark                = self.assessment_id.score_id and max(self.assessment_id.mapped('score_id.score_detail_ids.score')) or 0
            max_mark_participants   = ','.join(self.assessment_id and self.assessment_id.score_id.score_detail_ids.filtered(lambda r:r.score == max_mark).mapped('participant_id.name') or [''])
            
            participants_scored         = self.assessment_id.score_id.score_detail_ids.filtered(lambda r:r.participant_id in participants)
            participants_not_scored     = participants - participants_scored.mapped('participant_id')
            
            for record in self.assessment_id.score_id.score_detail_ids.sorted(lambda r:r.score,reverse=True).sorted(lambda r:r.attendance):
                data.append({
                    'name':record.participant_id.name,
                    'score':record.attendance == "attended" and f"{record.score} ({record.percentage}%)" or 'Did not appear',
                })
                
            for record in participants_not_scored:
                data.append({
                    'name':record.name,
                    'score':'Did not appear',
                })
            full_mark = self.assessment_id.marks
            

        else:
            online_answers          = self.env['kw_skill_answer_master'].search([('set_config_id','=',self.assessment_id.assessment_id.id)])
            max_mark                =  max(online_answers.mapped('total_mark_obtained')) or 0
            full_mark               = online_answers and online_answers[0].total_mark or 0
            max_mark_participants   = ','.join(online_answers and online_answers.filtered(lambda r:r.total_mark_obtained == max_mark).mapped('emp_rel.name') or [''])
            
            participants_scored     = online_answers.filtered(lambda r:r.emp_rel in participants)
            participants_not_scored = participants - participants_scored.mapped('emp_rel')
            
            for record in participants_scored.sorted(lambda r:r.total_mark_obtained,reverse=True):
                data.append({
                    'name':record.emp_rel.name,
                    'score':f"{record.total_mark_obtained} ({record.strip_percentage})",
                })

            for record in participants_not_scored:
                data.append({
                    'name':record.name,
                    'score':'Did not appear',
                })
            


        template = self.env.ref('kw_training.training_assessment_marks_mail')
        template.with_context(participants=participant_emails,cc_emails=cc_emails,data=data,max_mark=max_mark,max_mark_participants=max_mark_participants,full_mark=full_mark).send_mail(self.assessment_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        self.env.user.notify_success("Assessment Result mail sent successfully.")

        return True