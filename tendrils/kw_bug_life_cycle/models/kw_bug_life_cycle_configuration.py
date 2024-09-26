from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.exceptions import ValidationError
from odoo import api, models, exceptions


class KwBugLifeCycleConf(models.Model):
    _name = 'kw_bug_life_cycle_conf'
    _description = 'kw_bug_life_cycle_conf'
    _rec_name='project_id'

    project_id = fields.Many2one('project.project', string="Project Name", required=True)
    sla_escalation = fields.Integer('SLA Escalation(In Hours):')
    user_ids = fields.One2many('kw_bug_life_cycle_conf_user_field', 'cycle_bug_conf_id')

    onnew_defect_count = fields.Integer(string="Number of New State Bug ", compute='_compute_new_bug_count')
    onprogressive_defect_count = fields.Integer(string="Number of Progressive State Bug ", compute='_compute_progressive_bug_count')
    onhold_defect_count = fields.Integer(string="Number of Hold State Bug ", compute='_compute_hold_bug_count')
    ondone_defect_count = fields.Integer(string="Number of Done State Bug ", compute='_compute_done_bug_count')
    onrejected_defect_count = fields.Integer(string="Number of Rejected State Bug ", compute='_compute_rejected_bug_count')
    onclosed_defect_count = fields.Integer(string="Number of Closed State Bug ", compute='_compute_closed_bug_count')
    ontotal_defect_count = fields.Integer(string="Number of total Bug ", compute='_compute_total_bug_count')
    onalive_defect_count = fields.Integer(string="Number of alive Bug ", compute='_compute_alive_bug_count')
    ondev_perc_data_count  = fields.Float(string="Pending % @ Dev", compute="_compute_pending_dev_count")
    ontest_perc_data_count  = fields.Float(string="Pending % @ Test", compute="_compute_pending_test_count")

    fixed_and_closed_count = fields.Integer(string="Fixed And Closed", compute="_compute_fixed_and_closed_count")
    rejected_and_closed_count = fields.Integer(string="Rejected And Closed", compute="_compute_fixed_and_closed_count")
    on_draft_defect_count = fields.Integer(string="Draft", compute="_compute_draft_bug_count")

    bug_data_ids =fields.One2many('kw_raise_defect', 'bug_con_id')
    dev_test_ratio = fields.Char(string = 'Developement : Testing',compute='_compute_dev_test_ratio')
    bug_days = fields.Char(string="Days",compute='_compute_bug_days_ratio')

    # @api.model
    # def create(self, vals):
    #     ref_id = self.env.ref('kw_bug_life_cycle.group_Test_lead_bug_life_cycle').id
    #     data = self.env['res.groups'].sudo().search([('id', '=', ref_id)])
    #     record = super(KwBugLifeCycleConf, self).create(vals)
    #     data.users = False
    #     for rec in self.env['kw_bug_life_cycle_conf_user_field'].sudo().search([]):
    #         if rec.user_type == 'Test Lead':
    #             data.users = [(4, rec.employee_id.user_id.id)]
    #     return record
    
    @api.depends()
    def _compute_bug_days_ratio(self):
       for rec in self:
            if rec.project_id:
                bug_data = self.env["kw_raise_defect"].sudo().search([
                    ('project_id', '=', rec.project_id.id)],order="id asc")
                bug_close_data = self.env["kw_raise_defect"].sudo().search([
                    ('state','=','Closed'),('project_id', '=', rec.project_id.id)])
                if bug_data and bug_close_data :
                    date_of_create = [bug.create_date for bug in bug_data]
                    date_of_closed = [bug.closed_bug_date for bug in bug_close_data]
                    days_diff = (date_of_closed[-1] - date_of_create[0]).days
                    rec.bug_days = f"{days_diff} Days"
                else:
                    rec.bug_days = "0 Days"
    @api.depends('bug_data_ids', 'bug_data_ids.state')
    def _compute_draft_bug_count(self):
        for record in self:
            bug_on_draft = self.env["kw_raise_defect"].search_count(
                [('state', '=', 'Draft'), ('project_id', '=', record.project_id.id)])
            if bug_on_draft:
                record.on_draft_defect_count = bug_on_draft
    @api.depends('bug_data_ids', 'bug_data_ids.state')
    def _compute_new_bug_count(self):
        for record in self:
            bug_onnew = self.env["kw_raise_defect"].search_count([('state','=','New') ,('project_id','=',record.project_id.id)])
            if bug_onnew:
                record.onnew_defect_count = bug_onnew

    @api.depends()
    def _compute_progressive_bug_count(self):
        for record in self:
            bug_progressive = self.env["kw_raise_defect"].sudo().search_count([('state','=','Progressive'),('project_id','=',record.project_id.id)])
            if bug_progressive:
                record.onprogressive_defect_count = bug_progressive
    @api.depends()
    def _compute_hold_bug_count(self):
        for record in self:
            bug_onhold = self.env["kw_raise_defect"].sudo().search_count([('state','=','Hold'),('project_id','=',record.project_id.id)])
            if bug_onhold:
                record.onhold_defect_count = bug_onhold
    @api.depends()
    def _compute_done_bug_count(self):
        for record in self:
            bug_ondone= self.env["kw_raise_defect"].sudo().search_count([('state','=','Done'),('project_id','=',record.project_id.id)])
            if bug_ondone:
                record.ondone_defect_count = bug_ondone
    @api.depends()
    def _compute_rejected_bug_count(self):
        for record in self:
            bug_onrejected= self.env["kw_raise_defect"].sudo().search_count([('state','=','Rejected'),('project_id','=',record.project_id.id)])
            if bug_onrejected:
                record.onrejected_defect_count = bug_onrejected
    @api.depends()
    def _compute_closed_bug_count(self):
        for record in self:
            bug_onclosed= self.env["kw_raise_defect"].sudo().search_count([('state','=','Closed'),('project_id','=',record.project_id.id)])
            if bug_onclosed:
                record.onclosed_defect_count = bug_onclosed
    @api.depends()
    def _compute_total_bug_count(self):
        for record in self:
            bug_ontotal= self.env["kw_raise_defect"].sudo().search_count([('project_id','=',record.project_id.id)])
            if bug_ontotal:
                record.ontotal_defect_count = bug_ontotal
    @api.depends()
    def _compute_alive_bug_count(self):
        for record in self:
            bug_ontotal= self.env["kw_raise_defect"].sudo().search_count([('project_id','=',record.project_id.id),('state','!=','Draft')])
            bug_onclosed= self.env["kw_raise_defect"].sudo().search_count([('state','=','Closed'),('project_id','=',record.project_id.id)])
            if bug_ontotal:
                alive_data = bug_ontotal - bug_onclosed
                record.onalive_defect_count = alive_data

    @api.depends()
    def _compute_pending_dev_count(self):
        for record in self:
            bug_dev_data = self.env["kw_raise_defect"].search_count([('state','in',['New', 'Progressive','Hold']),('project_id','=',record.project_id.id)])
            if bug_dev_data:
                dev_data = ((bug_dev_data)/ record.onalive_defect_count) * 100
                record.ondev_perc_data_count = dev_data

    @api.depends()
    def _compute_pending_test_count(self):
        for record in self:
            bug_test_data = self.env["kw_raise_defect"].search_count([('state','in',['Rejected','Done']),('project_id','=',record.project_id.id)])
            if bug_test_data:
                test_data = ((bug_test_data)/ record.onalive_defect_count) * 100
                record.ontest_perc_data_count = test_data

    @api.depends()
    def _compute_fixed_and_closed_count(self):
        for record in self:
            fix_and_close = 0
            reject_and_close = 0
            closed_bug_data = self.env["kw_raise_defect"].search(
                [('state', 'in', ['Closed']), ('project_id', '=', record.project_id.id)])
            for rec in closed_bug_data:
                action_logs = rec.action_log_table_ids
                last_two_records = action_logs[-2:] if len(action_logs) >= 2 else action_logs[:]
                if last_two_records:
                    second_last_record_data = last_two_records[-2]
                    last_record_data = last_two_records[-1]
                    if second_last_record_data.state == 'Fixed & Deployed In Test Server' and last_record_data.state == 'Closed':
                        fix_and_close += 1
                    elif second_last_record_data.state == 'Rejected' and last_record_data.state == 'Closed':
                        reject_and_close += 1
                    else:
                        fix_and_close += 0
                        reject_and_close += 0
            record.fixed_and_closed_count = fix_and_close
            record.rejected_and_closed_count = reject_and_close


    @api.depends('user_ids.user_type')
    def _compute_dev_test_ratio(self):
        for record in self:
            developer_count = 0
            tester_count = 0
            total = 0
            for rec in record.user_ids:
                if rec.user_type in ['Developer','Module Lead']:
                    developer_count += 1
                    total += 1
                elif rec.user_type in ['Tester','Test Lead']:
                    tester_count += 1
                    total += 1
            dev_percentage = (developer_count / total) * 100 if total != 0 else 0
            test_percentage = 100 - dev_percentage
            formatted_ratio = f"Development:Testing :: {int(developer_count)}:{int(tester_count)}"
            record.dev_test_ratio = formatted_ratio


    @api.onchange('project_id')
    def get_user_ids(self):
        if self.project_id:
            data = self.env['project.project'].sudo().search([('id', '=', self.project_id.id)])
            emp_id = []
            for rec in data:
                for record in rec.resource_id:
                    emp_id.append(record.emp_id.id)
            return {'domain':{'user_ids':[('employee_id', 'in', emp_id)]}}

    @api.constrains('project_id')
    def validate_weekdays(self):
        template_rec = self.env['kw_bug_life_cycle_conf'].search([]) - self
        filtered_rec = template_rec.filtered(lambda x: x.project_id.id == self.project_id.id)
        if len(filtered_rec) > 0:
            raise ValidationError("The Project \"" + self.project_id.name + "\" already exists.")


    def new_bug_btn(self):
        pass
        # action = {
        #     'name': ('Dashboard'),
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'tree',
        #     'view_type': 'form',
        #     'res_model': 'kw_raise_defect',
        #     'domain':[('project_id', '=', self.project_id.id ), ('state', '=', 'New')] ,
        #     'target': 'self',
        #     'context': {'search_default_this_month_raise_defect':1}
        # }
        # return action

    def progressive_bug_btn(self):
        pass
        # action = {
        #     'name': ('Dashboard'),
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'tree',
        #     'view_type': 'form',
        #     'res_model': 'kw_raise_defect',
        #     'domain': [('project_id', '=', self.project_id.id), ('state', '=', 'Progressive')],
        #     'target': 'self',
        #     'context': {'search_default_this_month_raise_defect':1}
        # }
        # return action

    def hold_bug_btn(self):
        pass
        # action = {
        #     'name': ('Dashboard'),
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'tree',
        #     'view_type': 'form',
        #     'res_model': 'kw_raise_defect',
        #     'domain': [('project_id', '=', self.project_id.id), ('state', '=', 'Hold')],
        #     'target': 'self',
        #     'context': {'search_default_this_month_raise_defect':1}
        # }
        # return action

    def done_bug_btn(self):
        pass
        # action = {
        #     'name': ('Dashboard'),
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'tree',
        #     'view_type': 'form',
        #     'res_model': 'kw_raise_defect',
        #     'domain': [('project_id', '=', self.project_id.id), ('state', '=', 'Done')],
        #     'target': 'self',
        #     'context': {'search_default_this_month_raise_defect':1}
        # }
        # return action

    def reject_bug_btn(self):
        pass
        # action = {
        #     'name': ('Dashboard'),
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'tree',
        #     'view_type': 'form',
        #     'res_model': 'kw_raise_defect',
        #     'domain': [('project_id', '=', self.project_id.id), ('state', '=', 'Rejected')],
        #     'target': 'self',
        #     'context': {'search_default_this_month_raise_defect': 1}
        # }
        # return action

    def close_bug_btn(self):
        pass
        # action = {
        #     'name': ('Dashboard'),
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'tree',
        #     'view_type': 'form',
        #     'res_model': 'kw_raise_defect',
        #     'domain': [('project_id', '=', self.project_id.id), ('state', '=', 'Closed')],
        #     'target': 'self',
        #     'context': {'search_default_this_month_raise_defect': 1}
        # }
        # return action


class KwBugLifeCycleConfUserField(models.Model):
    _name = 'kw_bug_life_cycle_conf_user_field'
    _description = 'kw_bug_life_cycle_conf_user_field'

    employee_id = fields.Many2one('hr.employee', string="User Name")
    user_type = fields.Selection([('Tester', 'Tester'), ('Developer', 'Developer'), ('Test Lead', 'Test Lead'),
                                  ('Module Lead', 'Module Lead'), ('Manager', 'Manager'),('BA', 'BA'),('Reviewer/VP','Reviewer/VP')], string="User Type",
                                 required=True)
    cycle_bug_conf_id = fields.Many2one('kw_bug_life_cycle_conf')

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.user_type = False
        selected_employees = self.cycle_bug_conf_id.user_ids.mapped('employee_id')
        return {
            'domain': {
                'employee_id': [('id', 'not in', selected_employees.ids)]
            }
        }

    @api.model
    def _update_groups(self, user_type):
        data = self.env['kw_bug_life_cycle_conf_user_field'].search([])
        if user_type in ['Tester']:
            tester = data.filtered(lambda x: x.user_type == 'Tester').mapped('employee_id.user_id').ids
            self.env.ref('kw_bug_life_cycle.group_tester_bug_life_cycle').sudo().write({
                'users': [(6, 0, tester)]
            })
        elif user_type in ['BA']:
            ba = data.filtered(lambda x: x.user_type == 'BA').mapped('employee_id.user_id').ids
            self.env.ref('kw_bug_life_cycle.group_ba_bug_life_cycle').sudo().write({
                'users': [(6, 0, ba)]
            })
        elif user_type in ['Manager']:
            manager = data.filtered(lambda x: x.user_type == 'Manager').mapped('employee_id.user_id').ids
            self.env.ref('kw_bug_life_cycle.group_pm_bug_life_cycle').sudo().write({
                'users': [(6, 0, manager)]
            })
        elif user_type in ['Test Lead']:
            test_lead = data.filtered(lambda x: x.user_type == 'Test Lead').mapped('employee_id.user_id').ids
            self.env.ref('kw_bug_life_cycle.group_Test_lead_bug_life_cycle').sudo().write({
                'users': [(6, 0, test_lead)]
            })
        elif user_type in ['Reviewer/VP']:
            reviewer_user = data.filtered(lambda x: x.user_type == 'Reviewer/VP').mapped('employee_id.user_id').ids
            self.env.ref('kw_bug_life_cycle.group_reviewer_bug_life_cycle').sudo().write({
                'users': [(6, 0, reviewer_user)]
            })
        elif user_type in ['Module Lead']:
            module_lead_user = data.filtered(lambda x: x.user_type == 'Module Lead').mapped('employee_id.user_id').ids
            self.env.ref('kw_bug_life_cycle.group_module_lead_bug_life_cycle').sudo().write({
                'users': [(6, 0, module_lead_user)]
            })    
        else:
            tester = data.filtered(lambda x: x.user_type == 'Tester').mapped('employee_id.user_id').ids
            ba = data.filtered(lambda x: x.user_type == 'BA').mapped('employee_id.user_id').ids
            manager = data.filtered(lambda x: x.user_type == 'Manager').mapped('employee_id.user_id').ids
            test_lead = data.filtered(lambda x: x.user_type == 'Test Lead').mapped('employee_id.user_id').ids
            reviewer = data.filtered(lambda x: x.user_type == 'Reviewer/VP').mapped('employee_id.user_id').ids
            module_lead = data.filtered(lambda x: x.user_type == 'Module Lead').mapped('employee_id.user_id').ids
            self.env.ref('kw_bug_life_cycle.group_tester_bug_life_cycle').sudo().write({
                'users': [(6, 0, tester)]
            })
            self.env.ref('kw_bug_life_cycle.group_ba_bug_life_cycle').sudo().write({
                'users': [(6, 0, ba)]
            })
            self.env.ref('kw_bug_life_cycle.group_pm_bug_life_cycle').sudo().write({
                'users': [(6, 0, manager)]
            })
            self.env.ref('kw_bug_life_cycle.group_Test_lead_bug_life_cycle').sudo().write({
                'users': [(6, 0, test_lead)]
            })
            self.env.ref('kw_bug_life_cycle.group_reviewer_bug_life_cycle').sudo().write({
                'users': [(6, 0, reviewer)]
            })
            self.env.ref('kw_bug_life_cycle.group_module_lead_bug_life_cycle').sudo().write({
                'users': [(6, 0, module_lead)]
            })

    @api.model
    def create(self, vals):
        res =  super(KwBugLifeCycleConfUserField, self).create(vals)
        if 'user_type' in vals and vals.get('user_type') not in ['Developer']:
            self._update_groups(vals.get('user_type'))
        return res

    @api.multi
    def write(self, vals):
        if 'employee_id' or 'user_type' in vals:
            data = self.env['kw_raise_defect'].search([('pending_at', 'in', [self.employee_id.id]),
                                                    ('project_id', '=', self.cycle_bug_conf_id.project_id.id)])
            if data:
                raise ValidationError('User Can\'t be modify as ticket(s) is/are pending. ')
            
        res = super(KwBugLifeCycleConfUserField, self).write(vals)
        self._update_groups('all')
        return res
        
    @api.multi
    def unlink(self):
        data = self.env['kw_raise_defect'].search([('pending_at', 'in', [self.employee_id.id]), ('project_id', '=', self.cycle_bug_conf_id.project_id.id)])
        if data:
            raise ValidationError('User Can\'t be deleted as ticket(s) is/are pending. ')
        res = super(KwBugLifeCycleConfUserField, self).unlink()
        self._update_groups('all')
        return res

class BugType(models.Model):
    _name = 'bug_type_master'
    _description = 'bug_type_master'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string="Code", required=True)


class ModuleMaster(models.Model):
    _name = 'bug_module_master'
    _description = 'bug_global_link_master'
    _rec_name = 'module_name'

    def get_project_id(self):
        logged_in_employee_id = self.env.user.employee_ids.id
        project_id = []
        data = self.env['kw_bug_life_cycle_conf_user_field'].sudo().search([('employee_id', '=', logged_in_employee_id), ('user_type', '=', 'Test Lead')])
        for rec in data:
            project_id.append(rec.cycle_bug_conf_id.id)
        return [('id', 'in', project_id)]


    module_name = fields.Char(string='Global Link', required=True)
    project_id = fields.Many2one('kw_bug_life_cycle_conf',string="Project", required=True, domain=get_project_id)
    active = fields.Boolean(string='Active', default=True)
    new_module_name = fields.Char(string="Module")

    @api.constrains('module_name')
    def _check_duplicate(self):
        if self.module_name:
            duplicate_data = self.env['bug_module_master'].sudo().search([('module_name','=',self.module_name), ('project_id', '=', self.project_id.id)]) - self
            if duplicate_data:
                raise ValidationError("Global Link Name already exist.")

class SubModuleMaster(models.Model):
    _name = 'bug_sub_module_master'
    _description = 'bug_sub_module_master'
    _rec_name='sub_module_name'

    def get_project_id(self):
        logged_in_employee_id = self.env.user.employee_ids.id
        project_id = []
        data = self.env['kw_bug_life_cycle_conf_user_field'].sudo().search([('employee_id', '=', logged_in_employee_id), ('user_type', '=', 'Test Lead')])
        for rec in data:
            project_id.append(rec.cycle_bug_conf_id.id)
        return [('id', 'in', project_id)]

    sub_module_name = fields.Char(string='Sub Module', required=True)
    module_id = fields.Many2one("bug_module_master", string='Module', required=True)
    project_id = fields.Many2one('kw_bug_life_cycle_conf', string="Project", required=True, domain=get_project_id)
    active = fields.Boolean(string='Active', default=True)
    screen_ids = fields.One2many('screen_master', 'reg_sub_module_id', string='Screen')

    @api.onchange('project_id')
    def get_change_sub_module(self):
        if self.project_id:
            self.module_id = False

    @api.constrains('sub_module_name')
    def _check_duplicate(self):
        if self.sub_module_name:
            duplicate_data = self.env['bug_sub_module_master'].sudo().search([('sub_module_name', '=', self.sub_module_name), ('module_id', '=', self.module_id.id), ('project_id', '=', self.project_id.id)]) - self
            if duplicate_data:
                raise ValidationError("SubModule Name already exist.")

    @api.onchange('project_id')
    def get_module_id_data(self):
        if self.project_id:
            data = self.env['kw_bug_life_cycle_conf'].sudo().search([('id', '=', self.project_id.id)]).id
            dataa = self.env['bug_module_master'].sudo().search([('project_id', '=', data)]).mapped('id')
            return {'domain': {'module_id': [('id', 'in', dataa)]}}


class ScreenMaster(models.Model):
    _name = 'screen_master'
    _description = 'screen_master'
    _rec_name = 'screen'

    screen = fields.Char(string='Screen', required=True)
    active = fields.Boolean(string='Active', default=True)
    reg_sub_module_id = fields.Many2one('bug_sub_module_master')
