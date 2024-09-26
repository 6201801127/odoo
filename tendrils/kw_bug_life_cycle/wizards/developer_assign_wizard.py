from datetime import timedelta,datetime
# import datetime


from odoo import fields, models,api
from odoo.exceptions import ValidationError
from odoo.http import request


class DeveloperAssignWizards(models.TransientModel):
    _name = 'kw_developer_assign_wizards'
    _description = 'Kwantify Developer Assign Wizards'

    def get_dev_id(self):
        record = self.env.context.get('current_record')
        
        data = self.env['kw_raise_defect'].sudo().search([('id', '=', record)],limit=1)
        emp_list = []
        if data.project_id:
            for recc in data.bug_con_id.user_ids:
                if recc.user_type in ['Developer', 'Module Lead']:
                    emp_list.append(recc.employee_id.id)
            current_user_employee_id = self.env.user.employee_ids.id
            emp_list = [emp_id for emp_id in emp_list if emp_id != current_user_employee_id]
            emp_li = [('id', 'in', emp_list)]
            return emp_li

    developer_id = fields.Many2one('hr.employee', string="Assigned To", domain=get_dev_id, track_visibility='always', required=True)
    defect_id = fields.Many2one('kw_raise_defect',default=lambda self: self._context.get('current_record'))
    assign_remarks = fields.Text(string="Remarks")

    def btn_assign(self):
        for rec in self:
            rec.defect_id.pending_at = False
            if rec.developer_id:
                dev_list = []
                ml_list = []
                data = self.env['kw_bug_life_cycle_conf'].sudo().search([('project_id', '=', self.defect_id.project_id.id)])
                for recc in data.user_ids:
                    if recc.user_type == 'Developer':
                        dev_list.append(recc.employee_id.id)
                    if recc.user_type == 'Module Lead':
                        ml_list.append(recc.employee_id.id)
                if rec.developer_id.id in dev_list:
                    self.defect_id.assigned_by = self.env.user.employee_ids.id
                    self.defect_id.developer_assign_boolean = True
                    self.defect_id.pending_at = [(4, rec.developer_id.id, False)]
                    self.defect_id.module_lead_boolean = False
                    self.defect_id.developer_id = rec.developer_id.id
                    self.defect_id.assign_bug_date = datetime.now()
                    user_designation = self.env['kw_bug_life_cycle_conf_user_field'].sudo().search([('employee_id', '=', self.env.user.employee_ids.id), ('cycle_bug_conf_id.project_id', '=', self.defect_id.project_id.id)])
                    self.defect_id.write({'action_log_table_ids':[[0, 0, {'state':'Assigned',
                                                                          'designation':user_designation.user_type,
                                                                          'remark':self.assign_remarks,
                                                                          'action_taken_by': self.env.user.employee_ids.name,
                                                                          }]]})

                elif rec.developer_id.id in ml_list:
                    self.defect_id.pending_at = [(4, rec.developer_id.id, False)]
                    self.defect_id.forward_to = rec.developer_id.id
                    self.defect_id.assigned_by = self.env.user.employee_ids.id
                    self.defect_id.developer_assign_boolean = False
                    self.defect_id.test_lead_boolean = False
                    self.defect_id.module_lead_boolean = True
                    self.defect_id.developer_id = rec.developer_id.id
                    user_designation = self.env['kw_bug_life_cycle_conf_user_field'].sudo().search(
                        [('employee_id', '=', self.env.user.employee_ids.id),
                         ('cycle_bug_conf_id.project_id', '=', self.defect_id.project_id.id)])
                    self.defect_id.write({'action_log_table_ids': [[0, 0, {'state': self.defect_id.state,
                                                                           'action_taken_by': self.env.user.employee_ids.name,
                                                                           'designation': user_designation.user_type,
                                                                           'remark':'Forwarded to Module Lead',
                                                                           }]]})
                else:
                    pass
    def ml_assign_developer(self):
        if self.env.context.get('hide_assign') == True:
            bug_data = self.env['kw_raise_defect'].browse(self._context.get('current_record', []))
            project_ids = bug_data.mapped('project_id.id')
            if len(set(project_ids)) == 1:
                for bug in bug_data:
                    bug.pending_at = False
                    if self.developer_id:
                        dev_list = []
                        ml_list = []
                        data = self.env['kw_bug_life_cycle_conf'].sudo().search([('project_id', '=', bug.project_id.id)])
                        for recc in data.user_ids:
                            if recc.user_type == 'Developer':
                                dev_list.append(recc.employee_id.id)
                            if recc.user_type == 'Module Lead':
                                ml_list.append(recc.employee_id.id)
                        if self.env.user.employee_ids.id in ml_list:
                            if self.developer_id.id in dev_list:
                                bug.assigned_by = self.env.user.employee_ids.id
                                bug.developer_assign_boolean = True
                                bug.pending_at = [(4, self.developer_id.id, False)]
                                bug.module_lead_boolean = False
                                bug.developer_id = self.developer_id.id
                                bug.assign_bug_date = datetime.now()
                                user_designation = self.env['kw_bug_life_cycle_conf_user_field'].sudo().search([('employee_id', '=', self.env.user.employee_ids.id), ('cycle_bug_conf_id.project_id', '=', bug.project_id.id)])
                                bug.write({'action_log_table_ids':[[0, 0, {'state':'Assigned',
                                                                                    'designation':user_designation.user_type,
                                                                                    'remark':self.assign_remarks,
                                                                                    'action_taken_by': self.env.user.employee_ids.name,
                                                                                    }]]})
                            elif self.developer_id.id in ml_list:
                                bug.pending_at = [(4, self.developer_id.id, False)]
                                bug.forward_to = self.developer_id.id
                                bug.assigned_by = self.env.user.employee_ids.id
                                bug.developer_assign_boolean = False
                                bug.test_lead_boolean = False
                                bug.module_lead_boolean = True
                                bug.developer_id = self.developer_id.id
                                user_designation = self.env['kw_bug_life_cycle_conf_user_field'].sudo().search(
                                    [('employee_id', '=', self.env.user.employee_ids.id),
                                    ('cycle_bug_conf_id.project_id', '=', bug.project_id.id)])
                                bug.write({'action_log_table_ids': [[0, 0, {'state': bug.state,
                                                                                    'action_taken_by': self.env.user.employee_ids.name,
                                                                                    'designation': user_designation.user_type,
                                                                                    'remark':'Forwarded to Module Lead',
                                                                                    }]]})
                            else:
                                pass
                        else:
                            raise ValidationError("You have no access to take any actions.")
            else:
                raise ValidationError("Selected records must belong to the same project.")
        else:
            raise ValidationError("You can Assign  multiple  in Take Action menu..")


class DelegateWizards(models.TransientModel):
    _name = 'kw_delegate_wizards'
    _description = 'Kwantify Tester delegate Wizards'

    def get_tester_id(self):
        record = self.env.context.get('current_record')

        data = self.env['kw_raise_defect'].sudo().search([('id', '=', record)], limit=1)
        emp_list = []
        if data.project_id:
            for recc in data.bug_con_id.user_ids:
                if recc.user_type in ['Tester']:
                    emp_list.append(recc.employee_id.id)
            emp_li = [('id', 'in', emp_list)]
            return emp_li

    tester_id = fields.Many2one('hr.employee', string="Delegate To", domain=get_tester_id, track_visibility='always',
                                   required=True)
    defect_id = fields.Many2one('kw_raise_defect', default=lambda self: self._context.get('current_record'))
    assign_remarks = fields.Text(string="Remarks")

    def btn_delegate(self):
        if self.env.context.get('my_project') == True:
            bug_data = self.env['kw_raise_defect'].browse(self._context.get('current_record', []))
            project_ids = bug_data.mapped('project_id.id')
            if len(set(project_ids)) == 1:
                for bug in bug_data:
                    if bug.employee_id.id  in bug.pending_at.ids:
                        bug.pending_at = False
                        bug.pending_at = [(4, self.tester_id.id)]
                        bug.developer_id = self.tester_id.id
                    bug.employee_id = self.tester_id.id
                    bug.create_uid = self.tester_id.user_id.id
            else:
                raise ValidationError("Selected records must belong to the same project.")
        else:
            raise ValidationError("You can delegate it in My Project menu..")



        
class DelegateWizardsDeveloper(models.TransientModel):
    _name = 'kw_delegate_wizards_developer'
    _description = 'Kwantify Tester delegate Wizards'

    def get_developer_id(self):
        record = self.env.context.get('current_record')

        data = self.env['kw_raise_defect'].sudo().search([('id', '=', record)], limit=1)
        emp_list = []
        if data.project_id:
            for recc in data.bug_con_id.user_ids:
                if recc.user_type in ['Developer']:
                    emp_list.append(recc.employee_id.id)
            emp_li = [('id', 'in', emp_list)]
            return emp_li

    developer_id = fields.Many2one('hr.employee', string="Delegate", domain=get_developer_id, track_visibility='always',
                                   required=True)
    defect_id = fields.Many2one('kw_raise_defect', default=lambda self: self._context.get('current_record'))
    assign_remarks = fields.Text(string="Remarks")

    def btn_delegate_developer(self):
        if self.env.context.get('my_project') == True:
            bug_data = self.env['kw_raise_defect'].browse(self._context.get('current_record', []))
            project_ids = bug_data.mapped('project_id.id')
            if len(set(project_ids)) == 1:
                for bug in bug_data:
                    dev_list = []
                    ml_list = []
                    for recc in bug.bug_con_id.user_ids:
                        if recc.user_type in ['Developer']:
                            dev_list.append(recc.employee_id.id)
                        if recc.user_type in ['Module Lead']:
                            ml_list.append(recc.employee_id.id)
                    if self.env.user.employee_ids.id in ml_list:
                        is_all_present = all(item in dev_list for item in bug.pending_at.ids)
                        if is_all_present:
                            bug.pending_at = False
                            bug.dev_filed_boolean = False
                            bug.developer_assign_boolean = True
                            bug.assign_bug_date = datetime.now()
                            bug.pending_at = [(4, self.developer_id.id, False)]
                            bug.developer_id = self.developer_id.id
                            bug.state = 'New'
                            bug.assigned_by = self.env.user.employee_ids.id
                            user_designation = self.env['kw_bug_life_cycle_conf_user_field'].sudo().search([('employee_id', '=', self.env.user.employee_ids.id), ('cycle_bug_conf_id.project_id', '=', self.defect_id.project_id.id)])
                            bug.write({'action_log_table_ids':[[0, 0, {'state':'Submitted',
                                                                    'designation': user_designation.user_type,
                                                                    'remark':'Delegate to developer',
                                                                    'action_taken_by': self.env.user.employee_ids.name,
                                                                    }]]})
                        else:
                            raise ValidationError("The bug cannot be delegated, as it is pending at testing end.")
                    else:
                        raise ValidationError("Only module lead has the access to delegate a developer.")
            else:
                raise ValidationError("Selected records must belong to the same project.")
        else:
            raise ValidationError("You can delegate it in My Project menu..")


class FilterWizard(models.TransientModel):
    _name = "filter_bug_raised_wizard"
    _description = "filter_bug_raised_wizard"

    MONTH_LIST = [('1', 'January'), ('2', 'February'),
                  ('3', 'March'), ('4', 'April'),
                  ('5', 'May'), ('6', 'June'),
                  ('7', 'July'), ('8', 'August'),
                  ('9', 'September'), ('10', 'October'),
                  ('11', 'November'), ('12', 'December')
                  ]
    
    
    fiscal_year = fields.Many2one('account.fiscalyear', "Financial Year",)
    filter_data = fields.Selection(string="Filter Data",selection=[(5, 'Yearly'),(1, 'All'),],required=True) #(2, 'Monthly'),(3, 'Quartly'),(4, 'Half Yearly'),
    current_quater = fields.Selection(string="Quarter",selection=[(1, 'First Quarter'),(2, 'Second Quarter'),(3, 'Third Quarter'),(4, 'Fourth Quarter')])
    monthly_data = fields.Selection(MONTH_LIST, string='Month')
    half_yearly = fields.Selection(string="Half yearly",selection=[(1, 'First Half'),(2, 'Second Half')])
    bug_report_id = fields.Many2one('life_cycle_bug_report',default=lambda self: self._context.get('current_record'))
    
    @api.multi
    def bug_report_filter(self):
        self.env["life_cycle_bug_report"].sudo().search([])
        tree_view_id = self.env.ref('kw_bug_life_cycle.Bug_report_view_tree_view').id
        year = self.fiscal_year.date_start.year if self.fiscal_year else False
        domain = []
        name=''
        
        if self.fiscal_year and self.filter_data == 5:
            name = f'Defect Report : Year-{self.fiscal_year.name}'
            domain=[('date', '>=', self.fiscal_year.date_start.strftime('%Y-%m-%d')),
                ('date', '<=', self.fiscal_year.date_stop.strftime('%Y-%m-%d'))]
           
        elif self.fiscal_year and self.filter_data == 2:
            name = f'Defect Report : Year-{self.fiscal_year.name} of {dict(self.MONTH_LIST)[self.monthly_data]}'
            first_day = datetime(year, int(self.monthly_data), 1)
            if self.monthly_data == 12:
                last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                last_day = datetime(year, int(self.monthly_data) + 1, 1) - timedelta(days=1)
            domain=[('date', '>=',first_day.strftime('%Y-%m-%d')),
                ('date', '<=',last_day.strftime('%Y-%m-%d'))]
        elif self.fiscal_year and self.filter_data == 3:
            name = f'Defect Report : Year-{self.fiscal_year.name} of Quartly {self.current_quater.key}'
            quarter = self.current_quater
            if quarter == 1:
                first_day = datetime(year, 1, 1)
                last_day = datetime(year, 3, 31)
            elif quarter == 2:
                first_day = datetime(year, 4, 1)
                last_day = datetime(year, 6, 30)
            elif quarter == 3:
                first_day = datetime(year, 7, 1)
                last_day = datetime(year, 9, 30)
            elif quarter == 4:
                first_day = datetime(year, 10, 1)
                last_day = datetime(year, 12, 31)
                domain = [('date', '>=', first_day.strftime('%Y-%m-%d')),
                          ('date', '<=', last_day.strftime('%Y-%m-%d'))]
            # domain=[('date', '>=',first_day.strftime('%Y-%m-%d')),
            #     ('date', '<=',last_day.strftime('%Y-%m-%d'))]
        elif self.fiscal_year and self.filter_data == 4:
            name = f'Defect Report : Year-{self.fiscal_year.name} of Half Yearly {self.half_yearly.key}'
            half_year = self.half_yearly
            if half_year == 1:
                first_day = datetime(year, 1, 1)
                last_day = datetime(year, 6, 30)
            else:
                first_day = datetime(year, 7, 1)
                last_day = datetime(year, 12, 31)
            domain=[('date', '>=',first_day.strftime('%Y-%m-%d')),
                ('date', '<=',last_day.strftime('%Y-%m-%d'))]
        elif self.filter_data == 1:
            name = f'Bug Report'
            domain = []

        return {
            'type': 'ir.actions.act_window',
            'name': name,
            'views': [(tree_view_id, 'tree')],
            'view_mode': 'tree',
            'view_type': 'form',
            'res_model': 'life_cycle_bug_report',
            'target': 'main',
            'domain' : domain,

        }


class SecretWizard(models.TransientModel):
    _name = "secret_wizard"
    _description = "secret_wizard"

    check_int = fields.Integer(string="Check")


    def secret_btn_assign(self):
        defects_data = self.env['kw_raise_defect'].sudo().search([])
        for data in defects_data:
            if data.defect_create_ids:
                data.write({
                    'bug_type':data.defect_create_ids[0].bug_type.id,
                    'description':data.defect_create_ids[0].description,
                    'snap_shot':data.defect_create_ids[0].snap_shot
                })