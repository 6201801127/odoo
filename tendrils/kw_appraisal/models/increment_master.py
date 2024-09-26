from odoo import models, fields, api, exceptions

class IncrementMaster(models.Model):
    _name = "increment_master"
    _description = "Increment Master"
    _rec_name = 'department'

    period_id = fields.Many2one(comodel_name='kw_assessment_period_master', string="Period")
    department = fields.Many2one('hr.department', string='Department',domain=[('dept_type.code', '=', 'department')])
    division = fields.Many2one('hr.department', string='Division',)
    # level = fields.Many2one('kw_grade_level', string='Level')
    grade_ids = fields.Many2many('kwemp_grade_master', 'kw_appraisal_increment_grade', 'appraisal_grade_id', 'grade_id', string='Grade')
    per_increment = fields.Integer(string='Percentage Increment')
    emp_count = fields.Integer(compute='_get_emp_count')
    process_bol = fields.Boolean(string='Process')
    
    @api.onchange('department')
    def change_div(self):
        if self.department:
            self.division = False
            return {'domain': {'division': [('parent_id', '=', self.department.id)]}}


    @api.depends('period_id', 'department', 'division','grade_ids')
    def _get_emp_count(self):
        for rec in self:
            inc = self.env['shared_increment_promotion'].sudo().search([('period_id','=',rec.period_id.id),('department_id','=',rec.department.id),('grade_id','in',rec.grade_ids.ids)])
            if inc:
                inc_rec = inc.filtered(lambda x:x.division.id == rec.division.id)
                if inc_rec:
                    rec.emp_count = len(inc_rec)
                else:
                    rec.emp_count = len(inc.filtered(lambda x:x.division.id == False))


    @api.constrains('department', 'division', 'grade_ids')
    def check_unique_grades_within_department_division(self):
        for record in self:
            department_id = record.department.id
            division_id = record.division.id
            if not division_id:
                division_id = False
            grades_set = set(record.grade_ids.ids)
            existing_record = self.env['increment_master'].search([
                ('department', '=', department_id),
                ('division', '=', division_id),
                ('id', '!=', record.id),
                ('grade_ids', 'in', list(grades_set))
            ])
            if existing_record:
                raise exceptions.ValidationError('Grades cannot be repeated for same configuration.')

    
    @api.constrains('per_increment')
    def check_per_increment(self):
        for record in self:
            if record.per_increment > 100 or record.per_increment < 0:
                raise exceptions.ValidationError('Percentage Increment must be between 0 and 100.')
