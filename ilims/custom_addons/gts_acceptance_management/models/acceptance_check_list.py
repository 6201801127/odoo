# Copyright 2010 NaN Projectes de Programari Lliure, S.L.
# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2014 Oihane Crucelaegui - AvanzOSC
# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models
from odoo.exceptions import ValidationError


class AcceptanceCheckList(models.Model):
    _name = "acceptance.checklist"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Acceptance Check List"

    def object_selection_values(self):
        return set()

    # @api.onchange("type")
    # def onchange_type(self):
    #     if self.type == "generic":
    #         self.object_id = False

    active = fields.Boolean("Active", default=True, tracking=True)
    name = fields.Char(string="Criteria", required=True, translate=True, tracking=True)
    check_list_lines = fields.One2many(
        comodel_name="acceptance.checklist.question",
        inverse_name="check_list",
        string="Acceptances",
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
        tracking=True,
        default="generic",
    )
    category = fields.Many2one(comodel_name="acceptance.checklist.category", string="Category", tracking=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        tracking=True,
        default=lambda self: self.env.company,
    )

    # @api.constrains('check_list_lines', 'check_list_lines.boolean_field')
    # def _check_if_zero(self):
    #     if any(lines.type == 'qualitative' and lines.check_weightage is True for lines in self.check_list_lines):
    #         raise ValidationError(_('Weightage cannot be Zero!'))


class AcceptanceCheckListQuestion(models.Model):
    _name = "acceptance.checklist.question"
    _description = "Acceptance Check List question"
    _order = "sequence, id"

    # @api.constrains("ql_values")
    # def _check_valid_answers(self):
    #     for tc in self:
    #         if (
    #             tc.type == "qualitative"
    #             and tc.ql_values
    #             and not tc.ql_values.filtered("ok")
    #         ):
    #             raise exceptions.ValidationError(
    #                 _(
    #                     "Question '%s' is not valid: "
    #                     "you have to mark at least one value as OK."
    #                 )
    #                 % tc.name_get()[0][1]
    #             )
    #
    # @api.constrains("min_value", "max_value")
    # def _check_valid_range(self):
    #     for tc in self:
    #         if tc.type == "quantitative" and tc.min_value > tc.max_value:
    #             raise exceptions.ValidationError(
    #                 _(
    #                     "Question '%s' is not valid: "
    #                     "minimum value can't be higher than maximum value."
    #                 )
    #                 % tc.name_get()[0][1]
    #             )

    sequence = fields.Integer(string="Sequence", default="10")
    check_list = fields.Many2one(comodel_name="acceptance.checklist", string="Check List")
    name = fields.Char(string="Criteria Line", required=True, translate=True)
    type = fields.Selection(
        [("qualitative", "Qualitative"), ("quantitative", "Quantitative")],
        string="Type",
    )
    ql_values = fields.One2many(
        comodel_name="acceptance.checklist.que.value",
        inverse_name="check_list_line",
        string="Qualitative values",
        copy=True,
    )
    notes = fields.Text(string="Notes")
    min_value = fields.Float(string="Min", digits="Acceptance")
    max_value = fields.Float(string="Max", digits="Acceptance")
    uom_id = fields.Many2one(comodel_name="uom.uom", string="UOM")
    check_weightage = fields.Boolean('check weightage', compute='_compute_weightage')

    @api.depends('ql_values', 'ql_values.ok', 'ql_values.weightage')
    def _compute_weightage(self):
        for record in self:
            record.check_weightage = False
            if record.type == 'qualitative':
                if any(lines.ok is True and lines.weightage == 0 for lines in record.ql_values):
                    record.check_weightage = True


class AcceptanceCheckListQuestionValue(models.Model):
    _name = "acceptance.checklist.que.value"
    _description = "Possible values for qualitative acceptance."

    check_list_line = fields.Many2one(comodel_name="acceptance.checklist.question", string="Check List question")
    name = fields.Char(string="Name", translate=True)
    ok = fields.Boolean(string="Correct answer?", help="When this field is marked, the answer is considered correct.")
    weightage = fields.Integer('Weightage')

    # @api.onchange('ok')
    # def _onchange_ok(self):
    #     if self.ok is False:
    #         self.weightage = 0
