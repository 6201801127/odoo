import re
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError, Warning
from datetime import date, datetime, time, timedelta
from dateutil.relativedelta import relativedelta
import datetime, calendar
from ast import literal_eval
from lxml import etree
import json

class RewardAndRecgnition(models.Model):
    _name = "reward_and_recognition"
    _description = "STARLIGHT"
    _rec_name = 'sequence'
    _order = "id desc"

    @api.depends('rnr_division_id')
    @api.multi
    def _compute_rnr_btn_access(self):
        for record in self:
            """ DRAFT STATE """
            if self.env.user.has_group('kw_reward_and_recognition.rnr_sbu') and record.state == 'draft':
                record.show_btn_nominate = True

            """ SBU STATE """
            if record.pending_at.user_id.id == self.env.user.id and record.state == 'nominate':
                record.show_btn_scrutinize = True
            else:
                if self.env.user.has_group('kw_reward_and_recognition.rnr_sbu') and record.state == 'sbu':
                    record.show_btn_scrutinize = True
                elif record.state == 'sbu' and record.pending_at.user_id.id == self.env.user.id:
                    record.show_btn_scrutinize = True
                else:
                    record.show_btn_scrutinize = False
            if record.pending_at.user_id.id != self.env.user.id and record.state == 'nominate':
                record.show_btn_scrutinize = False

            """ Scrutinized STATE """
            if record.state == 'nominate' and self.env.user.has_group('kw_reward_and_recognition.rnr_reviewer'):
                record.show_btn_award = True
                record.show_btn_reject = True

            else:
                if record.pending_at.user_id.id != self.env.user.id:
                    record.show_btn_award = False
                    record.show_btn_reject = False

            if record.pending_at.user_id.id != self.env.user.id and record.state == 'nominate':
                record.show_btn_award = False
                record.show_btn_reject = False

            """ Final Review STATE """
            if record.state == 'award' and self.env.user.has_group('kw_reward_and_recognition.rnr_final_reviewer'):
                record.show_btn_finalise = True
            else:
                if record.pending_at.user_id.id != self.env.user.id:
                    record.show_btn_finalise = False
            if record.pending_at.user_id.id != self.env.user.id and record.state == 'award' and not self.env.user.has_group(
                    'kw_reward_and_recognition.rnr_final_reviewer'):
                record.show_btn_finalise = False
            config_data = self.get_config_data()
            if date.today() < config_data.show_publish_option_date:
                record.show_btn_finalise = False


            if record.state == 'reject':
                record.show_btn_finalise = False
                record.show_btn_award = False
                record.show_btn_reject = False
                record.show_btn_scrutinize = False

    @api.depends('month', 'year')
    @api.multi
    def _compute_year_month(self):
        for record in self:
            if record.year and record.month:
                record.compute_month = default = date.today().strftime("%B")
                record.compute_year = default = date.today().strftime("%Y")

    @api.depends('reason_justification')
    @api.multi
    def _compute_login_restriction(self):
        for record in self:
            if self.env.user.has_group('kw_reward_and_recognition.rnr_sbu') and not self.env.user.has_group('kw_reward_and_recognition.rnr_reviewer') and record.state != 'sbu':
                record.compute_login = True
            else:
                record.compute_login = False
    
    @api.depends('rnr_division_id')
    @api.multi
    def _hide_rnr_div(self):
        for record in self:
            if not self.env.user.has_group('kw_reward_and_recognition.rnr_manager') or not self.env.user.has_group('kw_reward_and_recognition.rnr_final_reviewer') and self.env.user.has_group('kw_reward_and_recognition.rnr_sbu') or self.env.user.has_group('kw_reward_and_recognition.rnr_reviewer'):
                record.hide_rnr_div = True
            else:
                record.hide_rnr_div = False
    
    @api.depends('rnr_division_id')
    @api.multi
    def _compute_offboarding_data(self):
        offboarding = self.env['kw_resignation'].sudo()
        for record in self:
            offboarding_rec = offboarding.search([('applicant_id','=',record.employee_id.id),('state','not in',['cancel','reject'])])
            if offboarding_rec.state == 'apply':
                record.get_offboarding_data = 'RL Applied'
            elif offboarding_rec.state == 'confirm':
                record.get_offboarding_data = 'RL Approved'
            elif offboarding_rec.state == 'forward':
                record.get_offboarding_data = 'RL Forwarded'
            elif offboarding_rec.state == 'grant':
                record.get_offboarding_data = 'RL Granted'
            else:
                record.get_offboarding_data = 'NIL'
    
    @api.depends('rnr_division_id')
    @api.multi
    def _compute_award_details(self):
        for record in self:
            if self.env.user.has_group('kw_reward_and_recognition.rnr_reviewer') and record.state in ['nominate','award','finalise']:
                awarded,total_award = self.call_award_validation(self.rnr_division_id.id)
                award_left = 0
                if total_award:
                    award_left = int(total_award[0][0]) - len(awarded) if int(total_award[0][0]) >= len(awarded) else 0
                record.total_awards = int(total_award[0][0])
                record.awarded = len(awarded)
                record.awards_left = award_left
            else:
                record.total_awards = 0
                record.awarded = 0
                record.awards_left = 0

    def get_employee(self):
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
        return employee

    sequence = fields.Char(string="Service Number", readonly=True, required=True, copy=False, default='New')
    state = fields.Selection([('sbu', 'Draft'), ('nominate', 'Nominated'), ('review', 'Reviewed'), ('award', 'Awarded'),
                              ('finalise', 'Published'), ('reject', 'Rejected')], default='sbu',
                             track_visibility='onchange')
    employee_id = fields.Many2one('hr.employee', string="Nominee", track_visibility='onchange')
    # reason  = fields.Text(string="Reason",track_visibility='onchange')
    # reason_justification = fields.Text(string="Reason & Justification",track_visibility='onchange')
    reason_justification = fields.One2many(comodel_name='starlight_reason_lines', inverse_name='rnr_id',
                                           string="Reason & Justification", track_visibility='onchange')
    employee_image = fields.Binary(string="Nominee Photo", related='employee_id.image_small')
    # compute='_compute_employee_details'
    department_id = fields.Many2one('hr.department', string="Department", compute='_compute_employee_details')
    division = fields.Many2one('hr.department', string="Division", compute='_compute_employee_details')
    section = fields.Many2one('hr.department', string="Practice", compute='_compute_employee_details')
    practise = fields.Many2one('hr.department', string="Section", compute='_compute_employee_details')
    job_id = fields.Many2one('hr.job', string="Designation", compute='_compute_employee_details')
    location = fields.Many2one('kw_res_branch', string="Work Location", compute='_compute_employee_details')
    sbu_feedback = fields.Char(track_visibility='onchange')
    reviewer_feedback = fields.Char(track_visibility='onchange')
    final_reviewer_feedback = fields.Char(track_visibility='onchange')
    action_log_ids = fields.One2many(comodel_name='reward_recognition_action_log', inverse_name='rnr_id',
                                     track_visibility='onchange')
    rnr_division_id = fields.Many2one('kw_division_config', string='Department', track_visibility='onchange')

    """ Action taken by and Action Taken on details """
    action_taken_by = fields.Many2one('hr.employee', string="Action taken by", track_visibility='onchange')
    pending_at = fields.Many2one('hr.employee', string="Pending At", track_visibility='onchange')
    pending_at_status = fields.Char(string="Pending At",compute='_compute_pending_at_status')
    action_taken_on = fields.Date(string='Action Taken On', track_visibility='onchange')
    publish_on = fields.Date(string='Publish On', track_visibility='onchange')

    """ Buttons Hide details """
    show_btn_nominate = fields.Boolean(compute='_compute_rnr_btn_access')
    show_btn_scrutinize = fields.Boolean(compute='_compute_rnr_btn_access')
    show_btn_final_review = fields.Boolean(compute='_compute_rnr_btn_access')
    show_btn_finalise = fields.Boolean(compute='_compute_rnr_btn_access')
    show_btn_award = fields.Boolean(compute='_compute_rnr_btn_access')
    show_btn_reject = fields.Boolean(compute='_compute_rnr_btn_access')
    nominated_by = fields.Many2one('hr.employee', default=get_employee)

    month = fields.Integer(string='Month', default=date.today().month)
    year = fields.Integer(string='Year', default=date.today().year)
    compute_month = fields.Char(string='Month', compute='_compute_year_month', store=True)
    compute_year = fields.Char(string='Year', compute='_compute_year_month', store=True)
    reviewed_by = fields.Many2one('hr.employee', string="Reviewed By")
    compute_login = fields.Boolean(string='Restrict Edit', compute='_compute_login_restriction')
    hide_rnr_div = fields.Boolean(string='Hide RNR Division', compute='_hide_rnr_div')
    get_offboarding_data = fields.Char(string='Offboarding Status', compute='_compute_offboarding_data')
    total_awards = fields.Integer(string='Total Awards :', compute='_compute_award_details')
    awarded = fields.Integer(string='Awarded :', compute='_compute_award_details')
    awards_left = fields.Integer(string='Award Left :', compute='_compute_award_details')
    active = fields.Boolean(string="Active",default=True) 

    @api.multi
    def get_config_data(self):
        general_config_id = self.env['kw_starlight_general_configuration'].sudo().search([],order='id desc',limit=1)
        return general_config_id

    @api.model
    def default_get(self, fields):
        res = super(RewardAndRecgnition, self).default_get(fields)
        general_config_id = self.get_config_data()
        if self._context.get('rnr_action') and general_config_id and general_config_id.nomination_start_date and general_config_id.nomination_end_date:
            if date.today() < general_config_id.nomination_start_date or date.today() > general_config_id.nomination_end_date:
                start_date = general_config_id.nomination_start_date.strftime('%B %d, %Y')
                end_date = general_config_id.nomination_end_date.strftime('%B %d, %Y')
                raise ValidationError(f'Nomination Window is currently closed now.Duration of the nomination window is from {start_date} to {end_date}')
        else:
            raise ValidationError('Nomination Window is currently closed now.')

        
        login_user = self.env.user.employee_ids.id
        division_ids = self.env['kw_division_config'].sudo().search([])
        if login_user:
            for division in division_ids:
                if login_user in division.nominator_ids.ids:
                    res['rnr_division_id'] = division.id

        """ Raise Validation when Maximum nomination reached """
        if 'rnr_division_id' in res:
            nominate_datas,nominate_count_datas = self.call_nomination_validation(int(res['rnr_division_id']))
            if nominate_datas and nominate_count_datas:
                if len(nominate_datas) >= int(nominate_count_datas[0][0]):
                    raise ValidationError(f"Maximum nomination limit ({nominate_count_datas[0][0]}) has reached.You cannot nominate more.")
        return res
    
    @api.multi
    def archive_starlight_record(self):
        self.ensure_one()
        if self.env.user.has_group('kw_reward_and_recognition.rnr_sbu') or self.env.user.has_group('kw_reward_and_recognition.rnr_manager'):
            if self._context.get("archive_record"):
                self.active = False
            if self._context.get("unarchive_record"):
                self.active = True
    
    @api.multi
    def write(self,vals):
        if 'active' in vals:
            if (vals['active'] == False or vals['active'] == True) and self.env.user.has_group('kw_reward_and_recognition.rnr_reviewer'):
                raise ValidationError(f"You cannot Archive/Unarchive Starlight Records.")
        res = super(RewardAndRecgnition, self).write(vals)
        return res
    
    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, 
    #     submenu=False):
    #     res = super(RewardAndRecgnition, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     if view_type == 'tree' and self.user_has_groups('kw_reward_and_recognition.rnr_reviewer'):
    #         doc = etree.XML(res['arch'])
    #         for node in doc.xpath("/header/o_main_content/o_control_panel/o_cp_left/btn-group/o_dropdown/Archive"):
    #             node.set('modifiers', json.dumps({'invisible': 1}))
    #         res['arch'] = etree.tostring(doc, encoding='unicode')
    #     return res

    @api.multi
    def offboarding_rl_status(self):
        
        pass
    @api.multi
    def call_nomination_validation(self,div_id):
        nominate_count_datas = False
        nominate_datas = False
        nominate_query = f"""select a.nomination_count,b.starlight_max_nomination_award_id 
        from starlight_max_nomination_award a 
        join starlight_max_nomination_award_grade_master b on a.id = b.starlight_max_nomination_award_id 
        where b.div_id = {div_id} limit 1"""
        self._cr.execute(nominate_query)
        nominate_count_datas = self._cr.fetchall()
        if nominate_count_datas:
            nominate_count_query = f"""select b.starlight_max_nomination_award_id,b.div_id from starlight_max_nomination_award a 
            join starlight_max_nomination_award_grade_master b on a.id = b.starlight_max_nomination_award_id 
            join reward_and_recognition c on c.rnr_division_id=b.div_id 
            where a.id = {nominate_count_datas[0][1]} and c.month ='{int(date.today().month)}' and c.year ='{int(date.today().year)}' 
            and c.state in {"award","finalise","nominate"}"""
            self._cr.execute(nominate_count_query)
            nominate_datas = self._cr.fetchall()

        return nominate_datas,nominate_count_datas
    
    @api.multi
    def call_award_validation(self,div_id):
        award_count_data = False
        award_datas = False
        award_query = f"""select a.award_count,b.starlight_max_nomination_award_id from starlight_max_nomination_award a join starlight_max_nomination_award_grade_master b on a.id = b.starlight_max_nomination_award_id where b.div_id = {div_id} limit 1"""
        self._cr.execute(award_query)
        award_count_data = self._cr.fetchall()
        if award_count_data:
            award_count_query = f"""select b.starlight_max_nomination_award_id,b.div_id from starlight_max_nomination_award a join starlight_max_nomination_award_grade_master b on a.id = b.starlight_max_nomination_award_id join reward_and_recognition c on c.rnr_division_id=b.div_id where a.id = {award_count_data[0][1]} and c.month ='{int(date.today().month)}' and c.year ='{int(date.today().year)}'  and c.state in {"award","finalise"}"""            
            self._cr.execute(award_count_query)
            award_datas = self._cr.fetchall()

        return award_datas,award_count_data

    @api.onchange('rnr_division_id')
    def onchange_rnr_division_id(self):
        dept = self.rnr_division_id.department_ids
        sbu_type = self.rnr_division_id.type
        sbu_id = self.rnr_division_id.sbu_master_id
        domain = []
        grade_datas = self.env['kw_starlight_grade_configuration'].sudo().search([],order='id desc',limit=1)
        if sbu_type == 'sbu':
            domain = ['|', '&', '&', '&', '&', '&', ('grade', 'in', grade_datas.grade_ids.ids),
                      ('on_probation', '=', False), ('sbu_type', '=', 'sbu'), ('sbu_master_id', '=', sbu_id.id),
                      ('department_id', 'in', dept.ids), ('employement_type.code', '!=', 'O'),
                      '&', '&', '&', ('sbu_type', '=', 'horizontal'), ('grade', 'in', grade_datas.grade_ids.ids),
                      ('on_probation', '=', False), ('employement_type.code', '!=', 'O')]
        else:
            domain = [('grade', 'in', grade_datas.grade_ids.ids), ('on_probation', '=', False),
                      ('department_id', 'in', dept.ids), '|', ('sbu_type', '!=', 'sbu'), ('sbu_type', '=', False),
                      ('employement_type.code', '!=', 'O')]
        emp = self.env['hr.employee'].sudo().search(domain) - self.env.user.employee_ids
        resignation_datas = self.env['kw_resignation'].sudo().search(
            [('applicant_id', 'in', emp.ids), ('state', '=', 'grant')]).mapped('applicant_id')
        filtered_employees = emp - resignation_datas
        if filtered_employees:
            return {'domain': {'employee_id': [('id', 'in', filtered_employees.ids)]}}
        else:
            return {'domain': {'employee_id': [('id', '=', False)]}}

    @api.constrains('rnr_division_id')
    def _check_duplicate(self):
        if self.rnr_division_id:
            if len(self.reason_justification) == 0:
                raise ValidationError('Please Provide Reason And Justification.')

            nominate_datas,nominate_count_datas = self.call_nomination_validation(int(self.rnr_division_id.id))
            
            if nominate_datas and nominate_count_datas and self._context.get('rnr_action') and not self._context.get('award'):
                if len(nominate_datas) >= int(nominate_count_datas[0][0]):
                    raise ValidationError(f"Maximum nomination limit ({nominate_count_datas[0][0]}) has reached.You cannot nominate more.")

    @api.constrains('reason_justification')
    def validate_reason_justification(self):
        curr_reason = self.reason_justification.mapped('reason_type_id')
        all_reason = self.env['starlight_reason_master'].sudo().search([('mendatory','=',True)])
        left_reason_ids = all_reason - curr_reason
        if left_reason_ids:
            raise ValidationError(f"Please add all the reasons ({','.join(left_reason_ids.mapped('name'))})")
        for reason in self.reason_justification:
            if reason.reason_type_id and not reason.reason:
                raise ValidationError(f"Please add Justification against Reason ({reason.reason_type_id.name})")
            if not reason.reason_type_id and reason.reason:
                raise ValidationError(f"Please add Reasons against the justification({reason.reason}) )")
            if not reason.reason_type_id and not reason.reason:
                raise ValidationError(f"Please add Reasons and justification of empty record.")

    
    @api.constrains('employee_id')
    def validate_duplicate_nomination(self):
        if self.employee_id:
            employee_record = self.env['reward_and_recognition'].sudo().search(
                [('employee_id', '=', self.employee_id.id), ('state', 'not in', ['reject']),
                 ('month', '=', date.today().month),('year', '=', date.today().year)])

            if len(employee_record) > 1:
                raise ValidationError('Duplicate Nominations are not allowed for the current month.')

    @api.depends('employee_id')
    def _compute_employee_details(self):
        for rec in self:
            # rec.employee_image = rec.employee_id.image_small
            rec.department_id = rec.employee_id.department_id.id
            rec.division = rec.employee_id.division.id
            rec.section = rec.employee_id.section.id
            rec.practise = rec.employee_id.practise.id
            rec.job_id = rec.employee_id.job_id.id
            rec.location = rec.employee_id.job_branch_id.id
    
    @api.depends('state')
    def _compute_pending_at_status(self):
        for rec in self:
            if rec.pending_at and rec.state != 'award':
                rec.pending_at_status = f"Pending at {rec.pending_at.name}"
            elif rec.state == 'reject':
                rec.pending_at_status = ''
            elif rec.state == 'sbu':
                rec.pending_at_status = ''
            elif rec.state == 'finalise':
                rec.pending_at_status = ''
            else:
                rec.pending_at_status = 'Pending at Publisher'

    def send_to_final_reviewer(self):
        form_view_id = self.env.ref('kw_reward_and_recognition.view_rnr_remark_wizard').id
        users = self.env['res.users'].sudo().search([])
        emp_users = users.filtered(
            lambda user: user.has_group('kw_reward_and_recognition.rnr_final_reviewer') == True).mapped(
            'employee_ids').ids
        return {
            'name': 'Remark',
            'type': 'ir.actions.act_window',
            'res_model': 'rnr_remark_wizard',
            'view_mode': 'form',
            'view_id': form_view_id,
            'context': {'create': False, 'edit': False, 'default_send_to_emps': emp_users},
            'target': 'new',
        }

    def send_to_reviewer(self):
        # if str(date.today().strftime("%B")) != str(self.compute_month):
        #     raise ValidationError(f'You cannot nominate the migrated record in past date.')
        data = self.env['starlight_reason_master'].sudo().search([])
        mapped_data = []
        for record in self.reason_justification:
            mapped_data.append(record.reason_type_id.id)
        if data and self.reason_justification:
            for rec in data:
                count_data = mapped_data.count(rec.id)
                if count_data >= 2:
                    raise ValidationError(f'Duplicate reason {rec.name} is not allowed.')

        form_view_id = self.env.ref('kw_reward_and_recognition.view_rnr_remark_wizard').id

        return {
            'name': 'Remark',
            'type': 'ir.actions.act_window',
            'res_model': 'rnr_remark_wizard',
            'view_mode': 'form',
            'view_id': form_view_id,
            'context': {'create': False, 'edit': False, 'default_send_to_emp': self.rnr_division_id.reviewer_id.id},
            'target': 'new',
        }

 
    def call_rnr_report_action(self):
        form_view_id = self.env.ref('kw_reward_and_recognition.view_rnr_report_wizard').id
        return {
            'name': 'Starlight Report',
            'type': 'ir.actions.act_window',
            'res_model': 'rnr_report_wizard',
            'view_mode': 'form',
            'view_id': form_view_id,
            'target': 'new',
        }

    def button_apply(self):
        form_view_id = self.env.ref('kw_reward_and_recognition.view_rnr_remark_wizard').id
        return {
            'name': 'Remark',
            'type': 'ir.actions.act_window',
            'res_model': 'rnr_remark_wizard',
            'view_mode': 'form',
            'view_id': form_view_id,
            'context': {'create': False, 'edit': False},
            'target': 'new',
        }

    def starlight_takeaction(self):
        general_config_id = self.get_config_data()
        if self._context.get('take_action') and general_config_id and general_config_id.nomination_start_date and general_config_id.nomination_end_date and self.state != 'award':
            if date.today() < general_config_id.review_start_date or date.today() > general_config_id.review_end_Date:
                start_date = general_config_id.review_start_date.strftime('%B %d, %Y')
                end_date = general_config_id.review_end_Date.strftime('%B %d, %Y')
                raise ValidationError(f'Review Window is currently closed now.Duration of the review window is from {start_date} to {end_date}')
        
            award_datas,award_count_data = self.call_award_validation(self.rnr_division_id.id)
            if award_datas and award_count_data:
                if len(award_datas) >= int(award_count_data[0][0]):
                    raise ValidationError(f"Maximum award limit({award_count_data[0][0]}) has reached.You cannot award more.")
        
        form_view_id = self.env.ref('kw_reward_and_recognition.reward_andrecognition_view_form').id
        edit=False
        if self.state == 'award':
            edit=True
        if self.state in ['nominate']:
            edit=False
        for rec in self:
            return {
                'name': 'Take Action',
                'type': 'ir.actions.act_window',
                'res_model': 'reward_and_recognition',
                'view_mode': 'form',
                'view_id': form_view_id,
                'target': 'self',
                'res_id': rec.id,
                'flags': {'create': False, 'edit':edit},
            }
    
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'sbu' and self.env.user.has_group('kw_reward_and_recognition.rnr_sbu') and not self.env.user.has_group('kw_reward_and_recognition.rnr_manager') \
                or self.env.user.has_group('kw_reward_and_recognition.rnr_reviewer') and not self.env.user.has_group('kw_reward_and_recognition.rnr_manager') \
                or self.env.user.has_group('kw_reward_and_recognition.rnr_reviewer') and not self.env.user.has_group('kw_reward_and_recognition.rnr_final_reviewer'):
                raise ValidationError(f'You cannot delete the starlight record in {rec.state.capitalize()} state.You can delete only in Draft state.')
        record = super(RewardAndRecgnition, self).unlink()
        if record:
            self.env.user.notify_success(message='Starlight record deleted successfully.')
        return record

    @api.model
    def _migrate_startlight_to_next_month(self):
        param = self.env['kw_starlight_general_configuration'].sudo().search([],order='id desc',limit=1)
        review_start_date = datetime.datetime.strptime(str(param.review_start_date), "%Y-%m-%d").date()
        review_end_date = datetime.datetime.strptime(str(param.review_end_Date), "%Y-%m-%d").date()
        mail_from = param.congratulation_mail_from
        cc=','.join(param.cc_notify.mapped('work_email'))
        rnr_division = []
        migrated_list = []
        if date.today() >= review_start_date and date.today() <= review_end_date:
            """ First looping Starlight divisions to get max awarded count of each divisions """
            starlight_max_nomination_records = self.env['starlight_max_nomination_award'].sudo().search([])
            starlight_data = self.env['reward_and_recognition'].sudo().search(
                [('state', 'not in', ['reject', 'sbu']), ('month', '=', date.today().month),
                 ('year', '=', date.today().year)])
            for record in starlight_max_nomination_records:
                div_ids = record.mapped('division_ids')
                awarded_nominee_count = starlight_data.filtered(lambda x: x.rnr_division_id.id in div_ids.ids and x.month == date.today().month and x.state in ['award','finalise'])
                if len(awarded_nominee_count) >= int(record.award_count):
                    nominated_nominee_count = starlight_data.filtered(lambda x: x.rnr_division_id.id in div_ids.ids and x.month == date.today().month and x.state == 'nominate')
                    if nominated_nominee_count:
                        for rec in nominated_nominee_count:
                            migrated_list.append(rec)
                            rnr_division.append(rec.rnr_division_id.name)
                            month = int(date.today().month) + 1
                            year = int(date.today().year) if date.today().month != 12 else (int(date.today().year + 1))
                            migrated_to = date.today() + relativedelta(months=1, day=1)
                            create_date = rec.create_date + relativedelta(months=1, day=1)
                            write_date = rec.write_date + relativedelta(months=1, day=1)
                            compute_month = (date.today() + relativedelta(months=1)).strftime("%B")
                            action_taken_by = "Odoo Bot"
                            action_remark = "Automatically Forwarded to Next Month"
                            rec.execute_forward_to_next_month(rec, year, month, migrated_to, write_date, create_date,
                                                              compute_month, action_taken_by, action_remark)

        """ Archive starlight data if RL Applied.  """
        if migrated_list:
            # for migrate in migrated_list:
            rnr_division = ','.join(set(rnr_division))
            template = self.env.ref('kw_reward_and_recognition.kw_starlight_migration_template')
            template.with_context(months=date.today().strftime("%B"),
                                  year=date.today().year,
                                  records=migrated_list,
                                  email_to=cc,
                                  rnr_division=rnr_division,
                                  email_from=mail_from).send_mail(migrated_list[0].action_log_ids[0].id,notif_layout="kwantify_theme.csm_mail_notification_light")
    
    @api.multi
    def execute_forward_to_next_month(self, rec, year, month, migrated_to, write_date, create_date, compute_month,
                                      action_taken_by, action_remark):
        """ Updating Starlight Log Data """
        starlight_log_query = f"""INSERT INTO reward_recognition_action_log (state, action_remark, action_taken_by, action_taken_on, rnr_id) 
        VALUES ('{"sbu"}','{action_remark}','{action_taken_by}','{date.today()}',{rec.id}) ON CONFLICT DO NOTHING;"""
        self._cr.execute(starlight_log_query)

        """ Updating Migrated Starlight Log Data """
        migrated_starlight_log_query = f"""INSERT INTO starlight_migration_log (employee_id,migration_sequence, 
        migrated_rnr_id, migrated_on, migrated_state, migration_remark,migrated_to) VALUES ('{action_taken_by}',
        '{rec.sequence}',{rec.id},'{date.today()}','{"sbu"}','{action_remark}','{migrated_to}') ON CONFLICT DO NOTHING;"""
        self._cr.execute(migrated_starlight_log_query)
        
        """ Migrating Starlight Data """
        migrating_starlight_query = f"""update reward_and_recognition set state = 'sbu' , create_date = '{create_date}', write_date = '{write_date}' ,
        pending_at = null , nominated_by = null , month = {month} , year = {year} , reviewed_by = null , action_taken_by = null,
         action_taken_on = null , compute_month='{compute_month}'
        where id = {rec.id}"""
        self._cr.execute(migrating_starlight_query)

    @api.model
    def _congratulation_reminder(self):
        param = self.env['kw_starlight_general_configuration'].sudo().search([], order='id desc', limit=1)
        nomination_remainder_date = param.congratulation_reminder
        congratulation_mail_from = param.congratulation_mail_from
        congratulation_mail_to = param.congratulation_mail_to
        nomination_date = datetime.datetime.strptime(str(nomination_remainder_date), "%Y-%m-%d")
        if date.today() == nomination_date.date():
            awarded_nominee = self.sudo().search(
                [('state', '=', 'finalise'), ('month', '=', self.month), ('year', '=', self.year)])
            if not awarded_nominee.empty():
                template = self.env.ref('kw_reward_and_recognition.kw_rnr_congratulation_mailer_template')
                log = self.env['nomination_log'].sudo().create({
                    'send_to': congratulation_mail_to,
                    'send_from': 'System User (Odoo Bot)',
                    'status': 'success',
                    'date': date.today()
                })
                template.with_context(months=date.today().strftime("%B"),
                                      records=awarded_nominee,
                                      month_year=datetime.datetime.strptime(str(date.today()), "%Y-%m-%d").strftime("%B %Y"),
                                      congratulation_mail_from=congratulation_mail_from,
                                      congratulation_mail_to=congratulation_mail_to).send_mail(log.id, notif_layout="kwantify_theme.csm_mail_notification_light")

    @api.model
    def _nomination_reminder(self):
        param = self.env['kw_starlight_general_configuration'].sudo().search([],order='id desc',limit=1)
        nomination_start_date = datetime.datetime.strptime(str(param.nomination_start_date), "%Y-%m-%d").date()
        nomination_end_date = datetime.datetime.strptime(str(param.nomination_end_date), "%Y-%m-%d").date()
        review_start_date = datetime.datetime.strptime(str(param.review_start_date), "%Y-%m-%d").date()
        review_end_date = datetime.datetime.strptime(str(param.review_end_Date), "%Y-%m-%d").date()
        publish_start_date = datetime.datetime.strptime(str(param.show_publish_option_date), "%Y-%m-%d").date()
        publish_end_date = datetime.datetime.strptime(str(param.show_publish_option_end_date), "%Y-%m-%d").date()

        rnr_records = self.env['reward_and_recognition']
        cc = ','.join(param.cc_notify.mapped('work_email'))
        """ Nomination remainder """
        if nomination_start_date <= date.today() <= nomination_end_date:
            rnr_data = rnr_records.sudo().search(
                [('state', 'not in', ['sbu']), ('month', '=', date.today().month), ('year', '=', date.today().year)])
            nominated_officers = rnr_data.mapped('nominated_by')
            officer_users = self.env['res.users'].sudo().search([]).filtered(lambda user: user.has_group('kw_reward_and_recognition.rnr_sbu') == True).mapped('employee_ids')
            if officer_users:
                send_users_data = officer_users - nominated_officers
                if send_users_data:
                    template = self.env.ref('kw_reward_and_recognition.kw_rnr_nomination_reminder_email_template')
                    view_id = self.env.ref('kw_reward_and_recognition.reward_and_recognition_action').id
                    for employee in send_users_data:
                        log = self.env['nomination_log'].sudo().create({
                            'send_to': employee.name,
                            'send_from': 'System User (Odoo Bot)',
                            'status': 'success',
                            'date': date.today()
                        })
                        nomination_month = datetime.datetime.now() - relativedelta(months=1)
                        template.with_context(emails=employee.work_email,
                                              month=date.today().strftime("%B"),
                                              name=employee.name,
                                              emp_code=employee.emp_code,
                                              view_id=view_id,
                                              cc=cc,
                                              nomination_month=nomination_month.strftime("%B %Y"),
                                              nomination_date=nomination_end_date.strftime('%B %d, %Y')).send_mail(log.id, notif_layout="kwantify_theme.csm_mail_notification_light")

        """ Review remainder """
        emp_all_data = self.env['hr.employee']
        rnr_datas = rnr_records.sudo().search(
            [('state', 'in', ['nominate', 'award']), ('month', '=', date.today().month), ('year', '=', date.today().year)])
        users = self.env['res.users'].sudo().search([])
        if review_start_date <= date.today() <= review_end_date:
            if rnr_datas:
                reviewers = users.filtered(lambda user: user.has_group('kw_reward_and_recognition.rnr_reviewer') == True).mapped('employee_ids')
                for reviewer in reviewers:
                    review_record_list = []
                    review_record = rnr_datas.filtered(lambda x: x.state in ['nominate'] and x.pending_at.id == reviewer.id)
                    for rec in review_record:
                        award_datas,award_count_data = self.call_award_validation(rec.rnr_division_id.id)
                        if award_datas and award_count_data:
                            if len(award_datas) >= int(award_count_data[0][0]):
                                pass
                            else:
                                review_record_list.append(rec)
                    if review_record_list:
                        send_to = reviewer.name
                        final_emails = reviewer.work_email
                        log = self.create_rnr_log(send_to)
                        template = self.env.ref('kw_reward_and_recognition.kw_rnr_review_reminder_email_template')
                        self.send_rnr_group_review_email(final_emails, review_record_list, review_end_date, log,
                                                         template, cc, send_to)
        
        """ Publish remainder """
        if publish_start_date <= date.today() <= publish_end_date:
            if rnr_datas:
                final_review_reminder = rnr_datas.filtered(lambda x: x.state == 'award')
                if final_review_reminder:
                    send_to = 'Publisher'
                    emp_users = users.filtered(lambda user: user.has_group('kw_reward_and_recognition.rnr_final_reviewer') == True).mapped('employee_ids').ids
                    empls = emp_all_data.search([('id', 'in', emp_users), ('active', '=', True)]).mapped('work_email')
                    final_emails = ','.join(empls)
                    log = self.create_rnr_log(send_to)
                    template = self.env.ref('kw_reward_and_recognition.kw_starlight_publish_reminder_email_template')
                    self.send_rnr_group_review_email(final_emails, final_review_reminder, publish_end_date, log,
                                                     template, cc, send_to)

    @api.multi
    def create_rnr_log(self, send_to):
        log = self.env['nomination_log'].sudo().create({
            'send_to': send_to,
            'send_from': 'System User (Odoo Bot)',
            'status': 'success',
            'date': date.today()
        })
        return log

    @api.multi
    def send_rnr_group_review_email(self, user_email, records, review_end_date, log, template, cc, send_to):
        template.with_context(emails=user_email,
                              month=date.today().strftime("%B"),
                              records=records,
                              cc=cc,
                              send_to=send_to,
                              review_date=review_end_date.strftime('%B %d,%Y')).send_mail(log.id, notif_layout="kwantify_theme.csm_mail_notification_light")

    @api.model
    def create(self, vals):
        vals['sequence'] = self.env['ir.sequence'].next_by_code('starlight') or '/'
        result = super(RewardAndRecgnition, self).create(vals)
        return result
