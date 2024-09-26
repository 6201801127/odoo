from odoo import http
from odoo.http import request


class EqAuditTrailDetails(http.Controller):
    @http.route('/audit_trail_details/<opp_id>', auth='public', website=True)
    def audit_trail_details(self, opp_id, **args):
        try:
            kw_oppertuinity_id = int(opp_id)
            crm = request.env['crm.lead'].sudo().search([('kw_opportunity_id', '=', kw_oppertuinity_id)])
            eq_search = request.env['kw_eq_audit_trail_details'].search([
                ('kw_oppertuinity_id', '=', crm.id)], limit=1)
            if eq_search:
                view_id = http.request.env.ref('kw_eq.kw_eq_relpica_view_form').id
                action_id = http.request.env.ref("kw_eq.kw_eq_audit_trail_details_action").id
                return http.request.redirect(
                    '/web#id=%s&view_type=form&action=%s&model=kw_eq_audit_trail_details&view_id=%s' % (eq_search.id, action_id, view_id)
                )
            else:
                return "No matching record found in EQ Audit Trail Details."
        
        except ValueError:
            return "No matching record found"