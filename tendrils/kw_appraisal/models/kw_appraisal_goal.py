from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime,date

class kw_appraisal_goal(models.Model):
    _name = 'kw_appraisal_goal'
    _description = 'Goal & Milestone'
    _rec_name = 'employee_id'
    _order = 'id desc'

    appraisal_period = fields.Many2one('kw_assessment_period_master', string='Appraisal Period')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    emp_deg = fields.Many2one('hr.job','Designation', related='employee_id.job_id')
    emp_dept = fields.Many2one('hr.department','Department', related='employee_id.department_id')
    name = fields.Char('Goal', required=True)
    milestone_id = fields.One2many('kw_appraisal_milestone', 'goal_id')
    lm_score = fields.Char(string='LM Score')
    lm_remarks = fields.Char(string='LM Remarks')
    ulm_remarks = fields.Char(string='ULM Remarks')
    state = fields.Selection(string='Goal Status',selection=[('sent','Sent For Approval'),('rejected','Rejected'),('approved','Approved')])
    updated_milstones = fields.One2many('kw_appraisal_updated_milestone','goal_id',string='Updated Milestones')
    updated_goal = fields.Char('Updated Goal')
    button_hide = fields.Boolean(compute='_get_last_year')
    updated_on = fields.Date(string='Updated On')
    updated_list_hide = fields.Boolean(compute='_get_updated_list_hide')
    training = fields.Char(string='Training Remarks')
    remark = fields.Text(string='Remark')
    log_ids = fields.One2many('goal_action_log','goal_id',string='Log')
    goal_btn = fields.Boolean(compute='_get_goal_btn_hide')

    @api.multi
    def _get_goal_btn_hide(self):
        period_records = self.env['kw_assessment_period_master'].search([])
        period_id = max([periods.id for periods in period_records])
        appraisal_record = self.env['hr.appraisal'].search([('appraisal_year_rel','=',period_id)])
        for record in self:
            result = appraisal_record.filtered(lambda res:res.emp_id.id == record.employee_id.id and res.state.sequence != 6)
            if result:
                record.goal_btn = True
            else:
                record.goal_btn = False

    @api.multi
    def _get_last_year(self):
        for record in self:
            period_records = self.env['kw_assessment_period_master'].search([])
            period_id = max([periods.id for periods in period_records])
            if period_id != record.appraisal_period.id:
                record.button_hide = True
            else:
                record.button_hide = False
    
    @api.multi
    def _get_updated_list_hide(self):
        for record in self:
            record.updated_list_hide = True if not record.updated_milstones else False

    @api.model
    def save_datas(self, args):
        values = []
        try:
            kra_data = self.env['kw_appraisal_kra'].search(['&', ('appraisal_period', '=', int(args.get('appraisal_year'))),
                                                            ('employee_id', '=', int(args.get('employee_name')))], limit=1)
            hr_app_data = self.env['hr.appraisal'].search(
                ['&', ('appraisal_year_rel', '=', int(args.get('appraisal_year'))),
                ('emp_id', '=', int(args.get('employee_name')))], limit=1)
            user_input = self.env['survey.user_input'].sudo().search(['&', ('appraisal_id', '=', hr_app_data.id), ('token', '=', args.get('token'))], limit=1)
            if user_input.state != 'done':
                if args.get('actual'):
                    actual_data = float(args.get('actual'))
                else:
                    actual_data = 0
                if kra_data:
                    kra_data.write(
                        {'appraisal_period': int(args.get('appraisal_year')), 'employee_id': int(args.get('employee_name')),
                        'actual_score': actual_data, 'achievement': args.get('achievement')})
                    hr_app_data.write({'kra_score': actual_data})
                else:
                    self.env['kw_appraisal_kra'].create(
                        {'appraisal_period': int(args.get('appraisal_year')), 'employee_id': int(args.get('employee_name')),
                        'actual_score': actual_data, 'achievement': args.get('achievement')})
                    hr_app_data.write({'kra_score': actual_data})

                prev_year = args.get('someObj', False)
                if prev_year and len(prev_year) > 0 or not prev_year and len(prev_year) == 0:
                    prev_reord = self.env['kw_appraisal_goal'].sudo().search(['&',
                                                                            ('appraisal_period', '=',
                                                                            int(args.get('appraisal_year')) - 1),
                                                                            ('employee_id', '=',
                                                                            int(args.get('employee_name')))],
                                                                            limit=1)
                    if prev_reord:
                        for data in prev_reord.milestone_id:
                            if str(data.id) in prev_year:
                                data.write({'status': True})
                            else:
                                data.write({'status': False})

                survey_id = args.get('survey')
                token = args.get('token')
                if args.get('draft'):
                    user_input.sudo().write({'last_displayed_page_id': 0})
                    values = [hr_app_data.state.name, survey_id, token, args.get('self_employee_id')]
                else:
                    user_input.sudo().write({'last_displayed_page_id': 0})
                    values = [survey_id, token, args.get('self_employee_id')]
                record = self.env['kw_appraisal_goal'].sudo().search(
                    ['&', ('appraisal_period', '=', int(args.get('appraisal_year'))),
                    ('employee_id', '=', int(args.get('employee_name')))])
                if len(record) > 0:
                    mlstn = []
                    if args.get('milestones', False) and len(args.get('milestones')) > 0:
                        recv_milestone = args.get('milestones')
                        recv_milestone_dates = args.get('milestone_dates')
                        record.milestone_id = False

                        for x,y in zip(recv_milestone,recv_milestone_dates):
                            mlstn.append([0, 0, {'name': x,'milestone_date': y}])
                            
                    elif not args.get('milestones', False):
                        for milestones in record.milestone_id:
                            mlstn.append([2, milestones.id, False])
                    record.write({'appraisal_period': int(args.get('appraisal_year')),
                                'employee_id': int(args.get('employee_name')),
                                'name': args.get('goal_name'), 'milestone_id': mlstn, 'lm_remarks': args.get('lm_remark'),
                                'ulm_remarks': args.get('ulm_remark'), 'lm_score': args.get('lm_score'),'training':args.get('training')})
                else:
                    vals = []
                    if args.get('milestones') and args.get('milestone_dates'):
                        for name,date in zip(args.get('milestones'),args.get('milestone_dates')):
                            vals.append([0, 0, {'name': name,'milestone_date':date}])
                    new_record = self.env['kw_appraisal_goal'].sudo().create(
                        {'appraisal_period': int(args.get('appraisal_year')), 'employee_id': int(args.get('employee_name')),
                        'name': args.get('goal_name'),
                        'milestone_id': vals, 'lm_remarks': args.get('lm_remark'), 'ulm_remarks': args.get('ulm_remark'),
                        'lm_score': args.get('lm_score'),'training':args.get('training')
                        })
        except Exception as e:
            # print("Error in Goal milestone during save data : ",e)
            pass
        return values

    @api.multi
    def write(self,vals):
        updated_milestone_model = self.env['kw_appraisal_updated_milestone']
        milestone_model = self.env['kw_appraisal_milestone']
        list1 = []
        list2 = []
        created_records = []
        list1 = self.milestone_id.ids
        update_goal = ''

        if 'name' in vals:
            update_goal = self.name
        else:
            pass

        updated_record = super(kw_appraisal_goal,self).write(vals)

        if self.employee_id.user_id.id == self._uid and ('milestone_id' in vals or 'name' in vals):

            if 'milestone_id' in vals:
                list2 = self.milestone_id.ids

                for records in list2:
                    if records not in list1: # get created items
                        created_records.append(records)

                for created_record in created_records:
                    searched_record2 = milestone_model.browse(created_record)
                    updated_milestone_model.create({
                        'goal_id':self.id,
                        'milestone_id':searched_record2.id,
                        'milestone_name':searched_record2.name,
                        'milestone_status':searched_record2.status,
                        'milestone_remark':searched_record2.remark,
                        'milestone_date':searched_record2.milestone_date,
                        'status':'1',
                    })

            if 'name' in vals:
                self.update({
                    'updated_goal':update_goal
                })

            self.write({
                'updated_on':date.today(),
            })

            if self.state != 'sent' and created_records:

                self.write({
                    'state':'sent',
                })
                
                try:
                    template = self.env.ref('kw_appraisal.kw_goal_apply_mail_template')
                    if template:
                        template.send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
                except Exception as e:
                    pass
                self.env.user.notify_success("Sent for approval successfully.")
            else:
                self.env.user.notify_success("Progress updated successfully.")

        return updated_record
    
    @api.multi
    def update_goal(self):
        self.ensure_one()
        form_res = self.env['ir.model.data'].get_object_reference('kw_appraisal', 'kw_appraisal_set_goal_form')
        form_id = form_res and form_res[1] or False
        return {
            'name': 'Set and Update Goal',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'res_model': 'kw_appraisal_goal',
            'res_id':self.id,
            'views': [(form_id, 'form')],
            'target':'current',
            'flags':{'mode':'edit',}
            }
    
    def action_approve(self):

        form_res = self.env['ir.model.data'].get_object_reference('kw_appraisal', 'kw_appraisal_goal_milestone_approve_form')
        form_id = form_res and form_res[1] or False

        actions = {
            'name': 'Remark',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'res_model': 'kw_appraisal_goal',
            'res_id':self.id,
            'views': [(form_id, 'form')],
            'target':'new'
            }

        return actions
    
    def action_reject(self):

        form_res = self.env['ir.model.data'].get_object_reference('kw_appraisal', 'kw_appraisal_goal_milestone_reject_form')
        form_id = form_res and form_res[1] or False

        actions = {
            'name': 'Remark',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'res_model': 'kw_appraisal_goal',
            'res_id':self.id,
            'views': [(form_id, 'form')],
            'target':'new'
            }

        return actions
    
    @api.multi
    def take_action_goal(self):
        self.ensure_one()
        form_res = self.env['ir.model.data'].get_object_reference('kw_appraisal', 'kw_appraisal_set_goal_take_action_form')
        form_id = form_res and form_res[1] or False
        return {
            'name': 'Take Action',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'res_model': 'kw_appraisal_goal',
            'res_id':self.id,
            'views': [(form_id, 'form')],
            'target':'current'
            }

    @api.multi    
    def approve_goal(self):
        self.ensure_one()
        if self.state == 'sent' and self._uid == self.employee_id.parent_id.user_id.id:
            self.write({
                'state':'approved',
                'updated_goal':False,
            })
            self.milestone_id.write({'state':'approved'})
            milestone_values = ','.join(str(milestones.milestone_name) for milestones in self.updated_milstones)
            self.env['goal_action_log'].create({
                'goal_id':self.id,
                'who':self.env.user.employee_ids.id,
                'when':date.today(),
                'what':'Approved.',
                'remark':self.remark if self.remark else False,
                'milestone': milestone_values,
            })
            self.remark = False
            self.updated_milstones.unlink()
            try:
                template = self.env.ref('kw_appraisal.kw_goal_take_action_mail_template')
                if template:
                    template.send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
            except Exception as e:
                pass
            self.env.user.notify_info("Approved successfuly.")
        else:
            raise ValidationError("You are not allowed to take action.")

    @api.multi
    def reject_goal(self):
        self.ensure_one()
        if self.state == 'sent' and self._uid == self.employee_id.parent_id.user_id.id:
            created_records = self.updated_milstones.filtered(lambda res: res.status == '1')
            for created_record in created_records:
                self.milestone_id.filtered(lambda res: res.id == created_record.milestone_id).write({'state':'rejected','active':False})
                
            deleted_records = self.updated_milstones.filtered(lambda res: res.status == '2')
            for deleted_record in deleted_records:
                self.env['kw_appraisal_milestone'].sudo().create({
                'name':deleted_record.milestone_name,
                'goal_id':deleted_record.goal_id.id,
                'status':deleted_record.milestone_status,
                'remark':deleted_record.milestone_remark,
            })
            updated_records = self.updated_milstones.filtered(lambda res: res.status == '3')
            for updated_record in updated_records:
                update_record = self.env['kw_appraisal_milestone'].sudo().browse(updated_record.milestone_id)
                update_record.write({
                    'name':updated_record.milestone_name,
                    'goal_id':updated_record.goal_id.id,
                    'status':updated_record.milestone_status,
                    'remark':updated_record.milestone_remark,
                })

            self.write({
                'state':'rejected',
                'name':self.updated_goal if self.updated_goal else self.name,
                'updated_goal': False,
            })
            milestone_values = ','.join(str(milestones.milestone_name) for milestones in self.updated_milstones)

            self.env['goal_action_log'].create({
                'goal_id':self.id,
                'who':self.env.user.employee_ids.id,
                'when':date.today(),
                'what':'Rejected.',
                'remark':self.remark if self.remark else False,
                'milestone': milestone_values,
            })
            self.remark = False
            self.updated_milstones.unlink()
            try:
                template = self.env.ref('kw_appraisal.kw_goal_take_action_mail_template')
                if template:
                    template.send_mail(self.id,notif_layout="kwantify_theme.csm_mail_notification_light")
            except Exception as e:
                pass
            self.env.user.notify_info("Rejected successfully.")
        else:
            raise ValidationError("You are not allowed to take action.")