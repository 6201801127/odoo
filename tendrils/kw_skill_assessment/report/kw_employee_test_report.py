from odoo import models, fields, api
from odoo import tools

class EmployeeSkillIndexReport(models.Model):
    _name = 'kw_employee_skill_index_report'
    _description = 'Employee Skill Index Report'
    _auto = False
    _rec_name = 'employee_name'

    employee_id = fields.Many2one(string='Employee Id',comodel_name='hr.employee',) 
    designation = fields.Char(string="Designation", related='employee_id.job_id.name')
    department = fields.Char(string="Department", compute="compute_department",)
    skill_category = fields.Char(string='Skill Category')
    skill = fields.Char(string='Skill')
    employee_name = fields.Char(string="Employee")
    question_set = fields.Char(string="Test Name")
    test_date = fields.Date(string="Test Date")
    test_status = fields.Char(string="Test Status")
    skill_score = fields.Char(string="Skill Score Status")
    time_taken = fields.Char(string="Time Taken")
    total_mark = fields.Integer(string="Total Mark")
    total_mark_obtained = fields.Integer(string="Total Mark Obtained")
    percentage_scored = fields.Float(string="Percentage scored")
    test_order = fields.Char(string="Test Order")
    test_reverse_order = fields.Char(string="Test Reverse Order")
    child_ids = fields.One2many('kw_skill_answer_child', 'ans_id', string="Child Ids")

       
    def get_root_departments(self, departments):
        parent_departments = departments.mapped('parent_id')
        root_departments = departments.filtered(lambda r : r.parent_id.id == 0)
        if parent_departments:
            root_departments |= self.get_root_departments(parent_departments)
        return root_departments
    
    def view_answer_master_details(self):
        result_id = self.env['kw_skill_answer_master'].browse(self.id)
        view_id = self.env.ref('kw_skill_assessment.kw_question_user_report_form_view').id
        if len(result_id):
            return {
                    'name':'Employee Test Result',
                    'type': 'ir.actions.act_window',
                    'res_model': 'kw_skill_answer_master',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_id':result_id.id,
                    'view_id': view_id,
                    'target': 'same',
                    'flags': {'mode': 'readonly'},
                    }
        else:
            pass

    @api.multi
    def compute_department(self):
        for rec in self:
            if rec.employee_id.department_id:
                department = self.get_root_departments(rec.employee_id.department_id)
                if department:
                    rec.department = department.name

    @api.model
    def _strip_percentage(self):
        for record in self:
            s = str(format(record.percentage_scored, '.2f'))
            z = s.rstrip('0').rstrip('.') if '.' in s else s
            record.strip_percentage = z + "%"


    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(""" CREATE or REPLACE VIEW %s as (
            select sam.id, sam.emp_rel as employee_id, stm.skill_type as skill_category , sm.name as skill, emp.name as employee_name, 
            qs.name as question_set, sam.created_date as test_date, ssm.name as skill_score, sam.status as test_status,
            coalesce(Cast(TO_CHAR((sam.time_taken || 'second')::interval, 'HH24 : MI : SS') as varchar), '00 : 00 : 00') as time_taken,
            sam.total_mark as total_mark, sam.total_mark_obtained as total_mark_obtained, sam.percentage_scored as percentage_scored,
            row_number() over(partition by sam.emp_rel order by sam.id asc) as test_order,
            row_number() over(partition by sam.emp_rel order by sam.id desc) as test_reverse_order 
            from kw_skill_answer_master sam 
            join kw_skill_type_master stm on stm.id = sam.skill_type_id
            join kw_skill_master sm on sm.id = sam.skill_id
            join hr_employee emp on emp.id = sam.emp_rel 
            join kw_skill_question_set_config qs on qs.id = sam.set_config_id
            left join kw_skill_score_master ssm on ssm.id = sam.score_id
            where qs.assessment_type = 'skill'
        )""" % (self._table))
