from odoo import models, fields, api


class TechSkillDesConfig(models.Model):
    _name = 'kw_eq_software_master'
    _description = 'Software Configuration for Development and Functional'
    _order = "sort_no asc"
    _rec_name = 'skill_id'



    skill_id = fields.Many2one('kw_skill_master',string="Technology")
    designation_id = fields.Many2one('hr.job',string="Designation")
    experience = fields.Selection(string="Experience",selection=[('1', '<= 2yrs'), ('2', '> 2 to ≤4 Yrs'),('3', '> 4 to ≤6 Yrs'),('4', '> 6 to ≤8 Yrs'),('5', '> 8 to ≤10 Yrs'),('6', '> 10 Yrs')])
    ctc = fields.Float(string="CTC")
    effective_date = fields.Date(string="Effective Date")
    section = fields.Selection(string="Section",selection=[('1','Section 1'),('2', 'Section 2'),('3', 'Section 3'),('4', 'Section 4'),('5', 'Section 5'),('6', 'Section 6'),('7', 'Section 7'),('8', 'Section 8'),('9', 'Section 9')])# section is used to separate all the skill according to different One2many fields
    sort_no = fields.Integer()


    @api.onchange('experience')
    def _get_experience(self):
        if self.experience == '1':
            self.sort_no = 1
        elif self.experience == '2':
            self.sort_no = 2
        elif self.experience == '3':
            self.sort_no = 3
        elif self.experience == '4':
            self.sort_no = 4
        elif self.experience == '5':
            self.sort_no = 5
        elif self.experience == '6':
            self.sort_no = 6

    # @api.depends('write_date')
    # def compute_effective_date(self):
    #     for rec in self:
    #         rec.effective_date = rec.write_date.date()