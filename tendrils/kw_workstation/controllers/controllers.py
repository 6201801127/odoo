# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class kw_workstation_seatmap(http.Controller):

    @http.route('/seat-map', auth="public", website=True)
    def workstation_seat_map(self, **args):
        if http.request.session.uid is None:
            return http.request.redirect('/web')
        infra = dict()
        branch_code = (args['branch']) if 'branch' in args.keys() and args['branch'] else ''
        unit_code = (args['unit']) if 'unit' in args.keys() and args['unit'] else 'hq'
        infra_code = (args['code']) if 'code' in args.keys() and args['code'] else 'sixth-c'

        ws_infra_list = http.request.env['kw_workstation_infrastructure'].search([])
        branch_data = ws_infra_list.mapped('address_id.id')
        infra['branches'] = http.request.env['kw_res_branch'].search([('id', 'in', branch_data)])
        # print("branch_data >>>> ", branch_data, infra)

        unit_domain = [('id', 'in', ws_infra_list.mapped('branch_unit_id.id'))]
        infra_domain = ws_domain = []
        if branch_code != '' and branch_code != 'all':
            branch_id = http.request.env['kw_res_branch'].search([('code', '=', branch_code)]).id
            unit_domain += [('branch_id', '=', branch_id)]
            infra_domain = [('address_id', '=', branch_id)]
            ws_domain = [('branch_id', '=', branch_id)]

        if unit_code != '' and unit_code != 'all':
            infra_domain = [('branch_unit_id.code', '=', unit_code)]
            ws_domain = [('branch_unit_id.code', '=', unit_code)]

        # print("unit_domain >>> ", unit_domain, infra_domain)

        infra['branch_unit'] = http.request.env['kw_res_branch_unit'].search(unit_domain)
        infra['infrastructure'] = http.request.env['kw_workstation_infrastructure'].search(infra_domain)
        infra['infra_codes'] = infra['infrastructure'].mapped(lambda x: x.code)

        if branch_code == '':
            branch_code = infra['branches'][0].id

        infra['branch_code'] = branch_code
        infra['unit_code'] = unit_code
        infra['infra_code'] = infra_code

        # infra['project_data'] = request.env["project.project"].sudo().search([('active', '=', True)])
        # infra['employee_data'] = http.request.env['hr.employee'].search([('active', '=', True)])
        infra['employees'] = http.request.env['hr.employee'].search([('active', '=', True), ('employement_type.code', '!=', 'O')])
        if infra_code and infra_code != 'all':
            workstation_data = http.request.env['kw_workstation_master'].search([('infrastructure.code', '=', infra_code)])
        else:
            workstation_data = http.request.env['kw_workstation_master'].search(ws_domain)
        infra['workstations'] = [(station.id, station.name) for station in workstation_data]
        # print("infra  >>>>  ", infra)
        return http.request.render('kw_workstation.kw_workstation_seat_map', infra)

    @http.route('/infrastructurefilter/', type="json", auth='public', website=True)
    def search_country(self, **args):
        if args['branch_id'] != 'all':
            domain = [('branch_unit_id.code', '=', args['branch_id'])]
        else:
            domain = []
        model_data = http.request.env['kw_workstation_infrastructure'].sudo().search(domain)
        if len(model_data) > 0:
            infrastructure = dict()
            for infra in model_data:
                infrastructure[infra.code] = infra.name
            # print(states)
            return infrastructure
        return 'None'
