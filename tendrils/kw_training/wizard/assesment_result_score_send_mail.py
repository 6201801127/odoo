from odoo import models, fields, api

class TrainingResultScoreSendMail(models.TransientModel):
    _name        = 'kw_training_result_score_send_mail'
    _description = "Training offline assessment result send mail to participants"

    employee_ids        = fields.Many2many("hr.employee",string="CC:")
    score_id            = fields.Many2one('kw_training_score',
                            default=lambda self:self.env['kw_training_score'].browse(self._context.get('active_id',0))
                            )
    assessment_id       = fields.Many2one(string="Assessment" ,related='score_id.assessment_id')

    @api.multi
    def send_result_mail(self):
        training        = self.score_id.assessment_id.training_id
        # print('training:',training)
        plan            = training.plan_ids.filtered(lambda r:r.state == 'approved')
        # print('plan:',plan)
        participants    = plan and plan.participant_ids or self.env['hr.employee']
        # print('par:',participants)
        
        participant_emails  = ','.join(participants.mapped('work_email'))
        cc_emails           =  ','.join(self.employee_ids.mapped('work_email'))
        data                = []
       
        max_mark                = max(self.score_id.mapped('score_detail_ids.score')) or 0
        # print('maX mark:',max_mark)
        max_mark_participants   = ','.join(self.score_id.score_detail_ids.filtered(lambda r:r.score == max_mark).mapped('participant_id.name') or [''])
        # print(self.score_id.score_id.score_detail_ids)
        # print('max mark participant:',max_mark_participants)

        participants_scored         = self.score_id.score_detail_ids.filtered(lambda r:r.participant_id in participants)
        # print('scored:',participants_scored)

        participants_not_scored     = participants - participants_scored.mapped('participant_id')
        # print('participant scored:',participants_scored)
        # print("participants not scored :",participants_not_scored)
        for record in self.score_id.score_detail_ids.sorted(lambda r:r.score,reverse=True).sorted(lambda r:r.attendance):
            data.append({
                'name': record.participant_id.name,
                'score': record.attendance == "attended" and f"{record.score} ({record.percentage}%)" or 'Did not appear',
            })
            
        for record in participants_not_scored:
            data.append({
                'name': record.name,
                'score': 'Did not appear',
            })
        full_mark = self.score_id.full_marks
        # print('full mark:',full_mark)
        # print('data:',data)    

        template = self.env.ref('kw_training.training_assessment_marks_mail')
        template.with_context(participants=participant_emails,
                            cc_emails=cc_emails,
                            data=data,max_mark=max_mark,
                            max_mark_participants=max_mark_participants,
                            full_mark=full_mark).send_mail(self.assessment_id.id,notif_layout="kwantify_theme.csm_mail_notification_light")
        self.env.user.notify_success("Assessment Result mail sent successfully.")

        return True