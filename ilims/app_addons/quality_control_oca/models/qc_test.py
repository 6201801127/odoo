# Copyright 2010 NaN Projectes de Programari Lliure, S.L.
# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2014 Oihane Crucelaegui - AvanzOSC
# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models
from odoo.exceptions import ValidationError


class QcTest(models.Model):
    """
    A test is a group of questions along with the values that make them valid.
    """

    _name = "qc.test"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Quality control test"

    def object_selection_values(self):
        return set()

    @api.onchange("type")
    def onchange_type(self):
        if self.type == "generic":
            self.object_id = False

    active = fields.Boolean("Active", default=True, tracking=True)
    name = fields.Char(string="Name", required=True, translate=True, tracking=True)
    test_lines = fields.One2many(
        comodel_name="qc.test.question",
        inverse_name="test",
        string="Questions",
        tracking=True,
        copy=True,
    )
    object_id = fields.Reference(
        string="Reference object", selection="object_selection_values", tracking=True,
    )
    fill_correct_values = fields.Boolean(string="Pre-fill with correct values", tracking=True)
    type = fields.Selection(
        [("generic", "Generic"), ("related", "Related")],
        string="Type",
        required=True,
        tracking=True,
        default="generic",
    )
    category = fields.Many2one(comodel_name="qc.test.category", string="Category", tracking=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        tracking=True,
        default=lambda self: self.env.company,
    )

    @api.constrains('test_lines', 'test_lines.boolean_field')
    def _check_if_zero(self):
        if any(lines.type == 'qualitative' and lines.check_weightage is True for lines in self.test_lines):
            raise ValidationError(_('Weightage cannot be Zero!'))


class QcTestQuestion(models.Model):
    """Each test line is a question with its valid value(s)."""

    _name = "qc.test.question"
    _description = "Quality control question"
    _order = "sequence, id"

    @api.constrains("ql_values")
    def _check_valid_answers(self):
        for tc in self:
            if (
                tc.type == "qualitative"
                and tc.ql_values
                and not tc.ql_values.filtered("ok")
            ):
                raise exceptions.ValidationError(
                    _(
                        "Question '%s' is not valid: "
                        "you have to mark at least one value as OK."
                    )
                    % tc.name_get()[0][1]
                )

    @api.constrains("min_value", "max_value")
    def _check_valid_range(self):
        for tc in self:
            if tc.type == "quantitative" and tc.min_value > tc.max_value:
                raise exceptions.ValidationError(
                    _(
                        "Question '%s' is not valid: "
                        "minimum value can't be higher than maximum value."
                    )
                    % tc.name_get()[0][1]
                )

    sequence = fields.Integer(string="Sequence", required=True, default="10", tracking=True)
    test = fields.Many2one(comodel_name="qc.test", string="Test", tracking=True)
    name = fields.Char(string="Name", required=True, translate=True, tracking=True)
    type = fields.Selection(
        [("qualitative", "Qualitative"), ("quantitative", "Quantitative")],
        string="Type",
        required=True,
        tracking=True,
    )
    ql_values = fields.One2many(
        comodel_name="qc.test.question.value",
        inverse_name="test_line",
        string="Qualitative values",
        copy=True,
        tracking=True,
    )
    notes = fields.Text(string="Notes", tracking=True)
    min_value = fields.Float(string="Min", digits="Quality Control", tracking=True)
    max_value = fields.Float(string="Max", digits="Quality Control", tracking=True)
    uom_id = fields.Many2one(comodel_name="uom.uom", string="UOM", tracking=True)
    check_weightage = fields.Boolean('check_weightage', compute='_compute_weightage')

    @api.depends('ql_values', 'ql_values.ok', 'ql_values.weightage')
    def _compute_weightage(self):
        for record in self:
            record.check_weightage = False
            if record.type == 'qualitative':
                if any(lines.ok is True and lines.weightage == 0 for lines in record.ql_values):
                    record.check_weightage = True


class QcTestQuestionValue(models.Model):
    _name = "qc.test.question.value"
    _description = "Possible values for qualitative questions."

    test_line = fields.Many2one(comodel_name="qc.test.question", string="Test question", tracking=True)
    name = fields.Char(string="Name", required=True, translate=True, tracking=True)
    ok = fields.Boolean(
        string="Correct answer?",
        help="When this field is marked, the answer is considered correct.",
        tracking=True,
    )
    weightage = fields.Integer('Weightage', tracking=True)

    @api.onchange('ok')
    def _onchange_ok(self):
        if self.ok is False:
            self.weightage = 0
