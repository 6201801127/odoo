# -*- coding: utf-8 -*-

import re
import datetime
from datetime import datetime
from collections import Counter
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kw_workstation_master(models.Model):
    _name = 'kw_workstation_master'
    _description = "A master model to create the Work Station"

    name = fields.Char(string="Name", required=True, size=100)
    workstation_type = fields.Many2one('kw_workstation_type', string="Workstation Type", required=True)
    infrastructure = fields.Many2one('kw_workstation_infrastructure', string="Infrastructure", required=True,
                                     domain="[('branch_unit_id','=', branch_unit_id)]")
    # employee_id = fields.Many2one('hr.employee', string="Employee")
    # employee_id = fields.Many2many('hr.employee', 'kw_workstation_hr_employee_rel', string="Employee")
    employee_id = fields.Many2many(comodel_name='hr.employee',
                                   relation='kw_workstation_hr_employee_rel',
                                   column1='wid',
                                   column2='eid',
                                   string='Employee')
    layout_id = fields.Char('Layout ID', )
    is_wfh = fields.Boolean('WFH ?', track_visibility='onchange')
    branch_id = fields.Many2one('kw_res_branch', string="Branch/SBU",)
    branch_unit_id = fields.Many2one('kw_res_branch_unit', string='Unit', domain="[('branch_id', '=', branch_id)]")
    is_blocked = fields.Boolean(default=False, string='Reserved')
    # is_reserved = fields.Boolean(default=False, string='Reserved')
    is_contractual = fields.Boolean(default=False, string='Contractual')
    is_hybrid = fields.Boolean(default=False, string='Hybrid')
    note = fields.Char(string="Note")
    # employement_type = fields.Many2one('kwemp_employment_type')

    @api.onchange('is_contractual')
    def onchange_is_contractual(self):
        for rec in self:
            if rec.is_contractual is True:
                rec.is_blocked = True

    @api.onchange('is_blocked')
    def onchange_is_blocked(self):
        for rec in self:
            if rec.is_blocked is False:
                rec.is_contractual = False

    @api.constrains('name')
    def check_constraints(self):
        for rec in self:
            if self.env['kw_workstation_master'].sudo().search([('name', '=', rec.name)]) - self:
                raise ValidationError(f"The Workstation {rec.name} already exists.")

    # @api.constrains('name')
    # def validate_workstation_name(self):
    #     if re.match("^[a-zA-Z0-9 ,./()_+-]+$", self.name) == None:
    #         raise ValidationError("Invalid Workstation Name! Please provide a valid Work Station Name.")
    #     record = self.env['kw_workstation_master'].search([]) - self
    #     for info in record:
    #         if info.name.lower() == self.name.lower():
    #             raise ValidationError(f"The Workstation {self.name} already exists.")

    @api.constrains('employee_id')
    def _check_employee_id(self):
        all_data = self.env['kw_workstation_master'].search([])
        for record in self:
            if len(record.employee_id) > 2:
                raise ValidationError("Maximum two employees allowed to tag for a workstation.")
            if record.employee_id:
                all_rec = all_data - record
                for employees in record.employee_id:
                    existing_employee = all_rec.filtered(lambda rec: employees.id in rec.employee_id.ids)
                    # print(existing_employee,existing_employee.name)
                    if existing_employee:
                        raise ValidationError(f"{employees.name} has already assigned to {existing_employee[0].name}")

    # @api.constrains('layout_id')
    # def _check_layout_id(self):
    #     for record in self:
    #         if record.layout_id:
    #             layout_data = self.env['kw_workstation_master'].search([('layout_id', '=', record.layout_id)])
    #             print('layout_data : ', layout_data)
    #             if layout_data:
    #                 print('layout_data : ', record.name, ' : ', record.layout_id, ' : ', record.id)
    #                 raise ValidationError(f"{record.name} has already assigned.")

    @api.model
    def create(self, vals):
        new_record = super(kw_workstation_master, self).create(vals)
        self.env.user.notify_success(message='Workstation created successfully.')
        return new_record

    @api.multi
    def unlink(self):
        result = super(kw_workstation_master, self).unlink()
        self.env.user.notify_success(message='Workstation deleted successfully.')
        return result

    @api.multi
    def write(self, vals):
        res = super(kw_workstation_master, self).write(vals)
        self.env.user.notify_success(message='Workstation updated successfully.')
        return res

    # @api.model
    # def get_project_data_workstation(self, args):
    #     infra = args.get('infra', False)
    #     project = args.get('project', False)

    #     project_rec = self.env['project.project'].sudo().search(
    #         [('resource_id.emp_id','in',project_data),('emp_id','!=',False)])
    #     # project_data= self.env['kw_project_resource_tagging'].search([('active','=', True),('project_id','=',int(project))]).mapped('emp_id.id')
    #     # print('project_data>>>>>>>>>>>>>>>>>>.',project_data)
    #     # print(infra,project)
    #     if infra == 'all':
    #         workstation = self.env['kw_workstation_master'].search([('employee_id','in',project_data)])
    #         print('workstation all>>>>>>>>>>>>>>>',workstation)
    #     else:
    #         workstation = self.env['kw_workstation_master'].search([('infrastructure.code', '=', infra),('employee_id','in',project_data)])
    #         print('else workstation>>>>>>>>>>>>>>>>>>',workstation)
    #     return {"workstation": list(map(str, workstation.ids))}

    @api.model
    def get_seat_map(self, args):
        # print(args)
        branch_id = args.get('branch_id', False)
        unit_id = args.get('unit_id', False)
        infra_id = args.get('infra_id', False)
        project_id = args.get('project', False)
        prt_model = self.env['kw_project_resource_tagging']
        project_data = []
        if project_id is not False or project_id != '':
            project_data = prt_model.search([('active', '=', True), ('project_id', '=', int(project_id))]).mapped('emp_id.id')

        ws_infra_list = self.env['kw_workstation_infrastructure'].search([])
        infra_ids = ws_infra_list.ids
        branch_ids = ws_infra_list.mapped('address_id.id')
        branch_unit_ids = ws_infra_list.mapped('branch_unit_id.id')

        domain = [('branch_id', 'in', branch_ids), ('branch_unit_id', 'in', branch_unit_ids), ('infrastructure', 'in', infra_ids)]

        if branch_id != 'all':
            domain += [('branch_id.code', '=', branch_id)]
        if unit_id != 'all':
            domain += [('branch_unit_id.code', '=', unit_id)]
        if infra_id != 'all':
            domain += [('infrastructure.code', '=', infra_id)]
        # print("domain >>> ", domain)
        workstation = self.env['kw_workstation_master'].search(domain)
        # print(workstation)

        """ total ws counts Counter({'runningws': 101, 'midws': 35, 'srws': 8, 'chamber': 2, 'reception': 1, 'ceochamber': 1})"""
        total_ws_data = Counter([item.workstation_type.code for sublist in workstation for item in sublist])

        """ assigned ws count """
        assigned_ws_data = Counter([item.workstation_type.code for sublist in workstation for item in sublist if item.employee_id])

        """ hybrid ws count """
        hybrid_ws_data = Counter(['hybrid' for sublist in workstation for item in sublist if item.is_hybrid])

        """ occupied ws count """
        occupied_ws_data = Counter([item.workstation_type.code for sublist in workstation for item in sublist if item.employee_id for emp in item.employee_id])

        """ total WFH and WFO ws count """
        wfh_ws_data = Counter(['wfh' if emp.is_wfh else 'wfo' for sublist in workstation for item in sublist if item.employee_id for emp in item.employee_id])

        """ total contractual and reserved ws count """
        contract_ws_data = Counter(['contract' if (sublist.is_contractual and sublist.is_blocked) else 'reserved' for sublist in workstation if sublist.is_blocked or (sublist.is_contractual and sublist.is_blocked)])

        """ total emp system type count """
        sys_type_ws_data = Counter([emp.issued_system for sublist in workstation for item in sublist if item.employee_id for emp in item.employee_id])

        """ total emp system location count """
        sys_loc_ws_data = Counter([emp.system_location for sublist in workstation for item in sublist if item.employee_id for emp in item.employee_id if emp.issued_system == 'pc'])

        stat = {
            "total_runningws": total_ws_data.get('runningws', 0),
            "total_midws": total_ws_data.get('midws', 0),
            "total_srws": total_ws_data.get('srws', 0),
            "total_chamber": total_ws_data.get('chamber', 0),
            "total_reception": total_ws_data.get('reception', 0),
            "total_ceochamber": total_ws_data.get('ceochamber', 0),
            "total_interns": total_ws_data.get('interns', 0),

            "asgn_runningws": assigned_ws_data.get('runningws', 0),
            "asgn_midws": assigned_ws_data.get('midws', 0),
            "asgn_srws": assigned_ws_data.get('srws', 0),
            "asgn_chamber": assigned_ws_data.get('chamber', 0),
            "asgn_reception": assigned_ws_data.get('reception', 0),
            "asgn_ceochamber": assigned_ws_data.get('ceochamber', 0),
            "asgn_interns": assigned_ws_data.get('interns', 0),

            "occupied_runningws": occupied_ws_data.get('runningws', 0),
            "occupied_midws": occupied_ws_data.get('midws', 0),
            "occupied_srws": occupied_ws_data.get('srws', 0),
            "occupied_chamber": occupied_ws_data.get('chamber', 0),
            "occupied_reception": occupied_ws_data.get('reception', 0),
            "occupied_ceochamber": occupied_ws_data.get('ceochamber', 0),
            "occupied_interns": occupied_ws_data.get('interns', 0),

            "total_wfo": wfh_ws_data.get('wfo', 0),
            "total_wfh": wfh_ws_data.get('wfh', 0),
            "total_cont": contract_ws_data.get('contract', 0),
            "total_reserved": contract_ws_data.get('reserved', 0),
            "total_hybrid": hybrid_ws_data.get('hybrid', 0),

            "total_laptop": sys_type_ws_data.get('laptop', 0),
            "total_pc": sys_type_ws_data.get('pc', 0),
            "pc_home": sys_loc_ws_data.get('home', 0),
            "pc_office": sys_loc_ws_data.get('office', 0),
        }

        seats = []
        grade_list = []
        designation_list = []
        for record in workstation:
            # is_wfh = False
            # if record.employee_id:
            #     for id_emp in record.employee_id:
            #         if id_emp.is_wfh:
            #             is_wfh = True
            is_wfh = [True for emp in record.employee_id if emp.is_wfh]

            emp_display_name = [[''+emp.emp_display_name+'(WFH)' if emp.is_wfh else ' '+emp.emp_display_name+'(WFO)'] for emp in record.employee_id]
            for emp in record.employee_id:
                grade_list.append({'id': emp.grade.id, 'name': emp.grade.name})
                designation_list.append({'id': emp.job_id.id, 'name': emp.job_id.name})

            emp_rec = record.employee_id
            # [0] if len(record.employee_id) > 1 else record.employee_id
            project_ids = prt_model.search([('active', '=', True), ('emp_id', 'in', emp_rec.ids)])
            # project_ids = prt_model.search([('active', '=', True), ('resource_id', 'in', emp_rec.ids)])
            project_tag = False
            # print("project_data >>>>> ", project_data, project_ids, emp_rec)
            if len(emp_rec) > 1:
                for emp in emp_rec:
                    if emp.id in project_data:
                        project_tag = emp.sbu_master_id.type or 'sbu'
            elif emp_rec.id in project_data:
                project_tag = emp_rec.sbu_master_id.type or 'sbu'
            # print("project_tag >>>>>>>>>>>>>>>> ", project_tag)
            seats.append({'path_id': record.layout_id if record.layout_id else '',
                          'emp_name': emp_display_name,
                          'emp_ids': [emp.id if emp.emp_display_name else '' for emp in record.employee_id],
                          'project_ids': [[project.project_id.id, project.project_id.name] if project else '' for project in project_ids],
                          'is_wfh': is_wfh,
                          'name': record.name,
                          'project': project_tag,
                          'station_id': record.id,
                          'is_blocked': record.is_blocked if record.is_blocked is True and record.is_contractual is False else False,
                          'is_contractual': record.is_contractual if record.is_contractual is True else False,
                          'is_hybrid': record.is_hybrid if record.is_hybrid is True else False,
                          'note': record.note if record.is_blocked is True or record.is_contractual is True else '',
                          'infrastructure': workstation[0].infrastructure.name,
                          })
        # print(" grade_list >>>> ", grade_list)
        # print(" designation_list >>>> ", designation_list)
        return {"seats": seats, "stat": stat}

    @api.model
    def save_seat_map(self, args):
        workstation = self.env['kw_workstation_master'].search([('id', '=', args['ws_id'])])
        workstation['layout_id'] = args['svg_id']
        # print("args >>>>>>>>> ", args)
        if args['emp_ids']:
            employee_ids = [int(i) for i in args['emp_ids']]
            """release previous workstation"""
            if bool(args['override']):
                ws_data = self._get_emp_ws(employee_ids)
                # print("ws_data >>> ", ws_data)
                for ws in ws_data:
                    # print("ws.employee_id.ids >>> ", ws.employee_id.ids, list(set(ws.employee_id.ids) - set(employee_ids)), employee_ids)
                    ws.employee_id = [(6, 0, list(set(ws.employee_id.ids) - set(employee_ids)))]
            """update new workstation"""
            workstation['employee_id'] = [(6, 0, employee_ids)]
            # for emp in args['emp_ids']:
            #     employee = self.env['hr.employee'].search([('id', '=', int(emp))])
            #     if employee:
            #         if args['wfh_status'] == '':
            #             args['wfh_status'] = False
            #         employee.write({'is_wfh':args['wfh_status']})
        else:
            workstation['employee_id'] = [(5, 0, 0)]
        # workstation['is_wfh'] = args['wfh_status']
        res = self.write(workstation)
        return args

    def _get_emp_ws(self, employee_id):
        ws_data = self.env['kw_workstation_master'].search([('employee_id', 'in', employee_id)])
        return ws_data

    @api.model
    def get_workstations(self, args):
        infra = dict()
        infra_id = self.env['kw_workstation_infrastructure'].search([('id', '=', int(args.get('infra_id')))])
        infra['infrastructure'] = self.env['kw_workstation_infrastructure'].search([])
        infra['infra_code'] = infra_id.code
        infra['employees'] = self.env['hr.employee'].search([])
        if infra_id.code and infra_id.code != 'all':
            workstation_data = self.search([('infrastructure.code', '=', infra_id.code)])
        else:
            workstation_data = self.search([])
        infra['workstations'] = [(station.id, station.name) for station in workstation_data]
        # print(infra)
        return infra

    @api.model
    def get_employee_information(self, args):
        emp_id = args.get('emp_id', 0)
        employee_ids = int(emp_id) if ',' not in emp_id else [int(x) for x in emp_id.split(',')]
        # print("args >>>> ", args, emp_id, employee_ids)

        emp_rec = self.env['hr.employee'].browse(employee_ids)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        response = []
        for rec in emp_rec:
            info = {
                "image": f"{base_url}/web/image?model=hr.employee&field=image_medium&id={rec.id}",
                "name": rec.name,
                "code": rec.emp_code,
                "email": rec.work_email,
                "phone": rec.mobile_phone,
                "doj": datetime.strptime(str(rec.date_of_joining), "%Y-%m-%d").strftime("%d-%b-%Y") if rec.date_of_joining else '',
                "job": rec.job_id.name,
                "department": rec.department_id.name or '',
                "division": rec.division.name or '',
                "section": rec.section.name or '',
                "practice": rec.practise.name or '',
                "location": rec.job_branch_id.alias,
                "ra": rec.parent_id.display_name,
            }
            response.append(info)
        return response
