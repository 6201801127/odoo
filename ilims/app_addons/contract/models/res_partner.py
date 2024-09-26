# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ast import literal_eval

from odoo import fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_contract_count = fields.Integer(
        string="Sale Contracts",
        compute="_compute_contract_count",
        tracking=True,
    )
    purchase_contract_count = fields.Integer(
        string="Purchase Contracts",
        compute="_compute_contract_count",
        tracking=True,
    )
    contract_ids = fields.One2many(
        comodel_name="contract.contract",
        inverse_name="partner_id",
        string="Contracts",
        tracking=True,
    )

    def _get_partner_contract_domain(self):
        self.ensure_one()
        return [("partner_id", "child_of", self.ids)]

    def _compute_contract_count(self):
        contract_model = self.env["contract.contract"]
        for partner in self:
            fetch_data = contract_model.read_group(
                partner._get_partner_contract_domain(),
                ["partner_id", "contract_type"],
                ["partner_id", "contract_type"],
                lazy=False,
            )
            result = [
                [data["partner_id"][0], data["contract_type"], data["__count"]]
                for data in fetch_data
            ]
            partner_child_ids = partner.child_ids.ids + partner.ids
            partner.sale_contract_count = sum(
                [r[2] for r in result if r[0] in partner_child_ids and r[1] == "sale"]
            )
            partner.purchase_contract_count = sum(
                [
                    r[2]
                    for r in result
                    if r[0] in partner_child_ids and r[1] == "purchase"
                ]
            )

    def act_show_contract(self):
        """This opens contract view
        @return: the contract view
        """
        self.ensure_one()
        contract_type = self._context.get("contract_type")

        res = self._get_act_window_contract_xml(contract_type)
        action_context = {k: v for k, v in self.env.context.items() if k != "group_by"}
        action_context["default_partner_id"] = self.id
        action_context["default_pricelist_id"] = self.property_product_pricelist.id
        res["context"] = action_context
        res["domain"] = (
            literal_eval(res["domain"]) + self._get_partner_contract_domain()
        )
        return res

    def _get_act_window_contract_xml(self, contract_type):
        if contract_type == "purchase":
            return self.env["ir.actions.act_window"]._for_xml_id(
                "contract.action_supplier_contract"
            )
        else:
            return self.env["ir.actions.act_window"]._for_xml_id(
                "contract.action_customer_contract"
            )

    def open_contracts(self):
        xml_id = 'contract.view_partner_contract_tree'
        tree_view_id = self.env.ref(xml_id).id
        xml_id = 'contract.view_partner_contract_form'
        form_view_id = self.env.ref(xml_id).id
        return {
            'name': _('Contract'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'res_model': 'partner.contract',
            'domain': [('partner_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_partner_id': self.id}
        }

    def _get_contract_count(self):
        contract_obj = self.env['partner.contract']
        for record in self:
            record.contract_count = contract_obj.search_count([('partner_id', '=', record.id)])

    contract_count = fields.Integer(compute='_get_contract_count')
