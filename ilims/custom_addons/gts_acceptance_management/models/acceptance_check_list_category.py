# Copyright 2010 NaN Projectes de Programari Lliure, S.L.
# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2014 Oihane Crucelaegui - AvanzOSC
# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class AcceptanceCheckListTemplateCategory(models.Model):
    _name = "acceptance.checklist.category"
    _description = "Check List Category"

    @api.depends("name", "parent_id")
    def _compute_get_complete_name(self):
        for record in self:
            names = [record.name or ""]
            parent = record.parent_id
            while parent:
                names.append(parent.name)
                parent = parent.parent_id
            record.complete_name = " / ".join(reversed(names))

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if not self._check_recursion():
            raise exceptions.UserError(
                _("Error! You can not create recursive categories.")
            )

    name = fields.Char("Name", required=True, translate=True, track_visibility='always')
    parent_id = fields.Many2one(
        comodel_name="acceptance.checklist.category", string="Parent Category", track_visibility='always'
    )
    complete_name = fields.Char(
        compute="_compute_get_complete_name", string="Full name", track_visibility='always'
    )
    child_ids = fields.One2many(
        comodel_name="acceptance.checklist.category",
        inverse_name="parent_id",
        track_visibility='always',
        string="Child categories",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        track_visibility='always',
        help="This field allows you to hide the category without removing it.",
    )
