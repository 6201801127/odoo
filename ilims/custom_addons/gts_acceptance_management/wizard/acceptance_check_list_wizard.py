# Copyright 2010 NaN Projectes de Programari Lliure, S.L.
# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2014 Oihane Crucelaegui - AvanzOSC
# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AcceptanceInspectionSetCheckList(models.TransientModel):
    _name = "acceptance.inspection.set.checklist"
    _description = "Set check list for inspection"

    check_list = fields.Many2one(comodel_name="acceptance.checklist", string="Acceptance Criteria")

    def action_create_check_list(self):
        inspection = self.env["acceptance.inspection"].browse(self.env.context["active_id"])
        inspection.check_list = self.check_list
        inspection.inspection_lines.unlink()
        inspection.inspection_lines = inspection._prepare_inspection_lines(self.check_list)
        return True
