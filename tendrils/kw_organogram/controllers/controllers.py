# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.exceptions import UserError, ValidationError


class HrDepartmentHierarchy(http.Controller):
    @http.route('/get_dept_data', type='json', auth="user", website=True)
    def get_department_data(self, **args):
        """
        RET: S & C
        FTE: P
        Outsourced: O
        Contractual: CE
        """
        t_head = ""
        d_head = ""
        t_body = ""
        d_body = ""
        check_ret_update = False
        check_ret = False
        employee_count = 0
        dpt_count = 0
        th_class = "py-0 px-1 m-0"
        search_emp = request.env['hr.employee']
        search_dept = request.env['hr.department']
        total_count = search_emp.search_count([('employement_type.code', '!=', 'O')])
        employment_types = request.env['kwemp_employment_type'].search([('code', '!=', 'O')])
        department_types_ids = request.env['kw_hr_department_type'].search([])
        for types in department_types_ids:
            if types.code == 'department':
                dpt_count = search_dept.search_count([('dept_type.code', '=', types.code)])
            if types.code == 'division':
                dpt_count = search_dept.search_count([('dept_type.code', '=', types.code)])
            if types.code == 'section':
                dpt_count = search_dept.search_count([('dept_type.code', '=', types.code)])
            if types.code == 'practice':
                dpt_count = search_dept.search_count([('dept_type.code', '=', types.code)])
            d_head += f"<th class='{th_class}'>{types.name}</th>"
            d_body += f"<td>{dpt_count}</td>"
        if total_count:
            d_head += f"<th class='{th_class}'>Employee</th>"
            d_body += f"<td>{total_count}</td>"
        for types in employment_types:
            if types.code in ['S', 'C'] and not check_ret:  # RET
                employee_count = search_emp.search_count([('employement_type.code', 'in', ['S', 'C'])])
                check_ret = True
            elif types.code == 'P':  # FTE
                employee_count = search_emp.search_count([('employement_type.code', '=', 'P')])
            elif types.code == 'O':  # Outsourced
                employee_count = search_emp.search_count([('employement_type.code', '=', 'O')])
            else:
                employee_count = search_emp.search_count([('employement_type.code', '=', 'CE')])
            if types.code not in ['S', 'C']:
                t_head += f"<th class='{th_class}'>{types.name}</th>"
                t_body += f"<td>{employee_count}</td>"
            else:
                if not check_ret_update:
                    t_head += f"<th class='{th_class}'>RET</th>"
                    check_ret_update = True
                    t_body += f"<td>{employee_count}</td>"
        title = f'<br/><table class="table table-bordered mb-1 info_nodes"><thead>{d_head}</thead><tbody><tr>{d_body}</tr></tbody></table>' \
                f'<table class="table table-bordered"><thead>{t_head}</thead><tbody><tr>{t_body}</tr></tbody></table>'
        data = {
            'name': request.env.user.company_id.name,
            'title': title,
            'children': [],
        }
        departments = request.env['hr.department'].sudo().search([('parent_id', '=', False)])
        # employment_types = request.env['kwemp_employment_type'].search([])
        # department_types_ids = request.env['kw_hr_department_type'].search([])
        # print('department_types_ids.mapped("name") >>> ', department_types_ids.mapped("name"))
        for department in departments:
            data['children'].append(self.get_children(department, 'middle-level', employment_types, department_types_ids))

        return {'values': data}

    def get_employee_count(self, dep, types):
        employee_count = 0
        search_emp = request.env['hr.employee']
        if dep.dept_type.code == 'department':
            employee_count = search_emp.search_count([('department_id', '=', dep.id), ('employement_type', '=', types.id)])
        elif dep.dept_type.code == 'division':
            employee_count = search_emp.search_count([('division', '=', dep.id), ('employement_type', '=', types.id)])
        elif dep.dept_type.code == 'section':
            employee_count = search_emp.search_count([('section', '=', dep.id), ('employement_type', '=', types.id)])
        elif dep.dept_type.code == 'practice':
            employee_count = search_emp.search_count([('practise', '=', dep.id), ('employement_type', '=', types.id)])
        return employee_count

    def get_ret_employee_count(self, dep, types):
        employee_count = 0
        search_emp = request.env['hr.employee']
        if dep.dept_type.code == 'department':
            employee_count = search_emp.search_count([('department_id', '=', dep.id), ('employement_type.code', 'in', ['S', 'C'])])
        elif dep.dept_type.code == 'division':
            employee_count = search_emp.search_count([('division', '=', dep.id), ('employement_type.code', 'in', ['S', 'C'])])
        elif dep.dept_type.code == 'section':
            employee_count = search_emp.search_count([('section', '=', dep.id), ('employement_type.code', 'in', ['S', 'C'])])
        elif dep.dept_type.code == 'practice':
            employee_count = search_emp.search_count([('practise', '=', dep.id), ('employement_type.code', 'in', ['S', 'C'])])
        return employee_count
        # return {'department_count': department_count, 'department_name': department_name}

    def get_children(self, dep, style=False, employment_types=False, department_types_ids=False):
        emp_count = 0
        data = []

        search_dept = request.env['hr.department']
        search_emp = request.env['hr.employee']
        t_head = ""
        d_head = ""
        t_body = ""
        d_body = ""
        chech_ret_update = False
        chech_ret = False
        th_class = "py-0 px-1 m-0"
        for types in employment_types:
            if types.code in ['S', 'C'] and not chech_ret:
                employee_count = self.get_ret_employee_count(dep, types)
                chech_ret = True
            else:
                employee_count = self.get_employee_count(dep, types)
            if types.code not in ['S', 'C']:
                t_head += f"<th class='{th_class}'>{types.name}</th>"
                t_body += f"<td>{employee_count}</td>"
            else:
                if not chech_ret_update:
                    t_head += f"<th class='{th_class}'>RET</th>"
                    t_body += f"<td>{employee_count}</td>"
                    chech_ret_update = True
        department_count = 0
        department_name = ""
        section_dict = {}
        practise_dict = {}
        section_list = []
        practice_list = []
        if dep.dept_type.name == 'Department':
            division_count = search_dept.search([('parent_id', '=', dep.id)])
            if division_count:
                division_name = set(division_count.mapped("dept_type.name"))
                d_head += f"<th class='{th_class}'>{str(division_name)[2:-2]}</th>"
                d_body += f"<td>{len(division_count)}</td>"
                for division in division_count:
                    section_ids = search_dept.search([('parent_id', '=', division.id)])
                    section_name = set(section_ids.mapped("dept_type.name"))
                    section_count = len(section_ids)
                    if section_count and section_name:
                        section_dict['section_name'] = str(section_name)[2:-2]
                        if section_dict.get("section_count") is not None:
                            section_dict.update({'section_count': int(section_dict.get("section_count")) + section_count})
                        else:
                            section_dict['section_count'] = section_count
                        for section_id in section_ids:
                            practise_ids = search_dept.search([('parent_id', '=', section_id.id)])
                            practice_name = set(practise_ids.mapped("dept_type.name"))
                            practice_count = len(practise_ids)
                            if practice_name and practice_count:
                                section_dict['practice_name'] = str(practice_name)[2:-2]
                                if section_dict.get("practice_count") is not None:
                                    section_dict.update({'practice_count': int(section_dict.get("practice_count")) + practice_count})
                                else:
                                    section_dict['practice_count'] = practice_count
                            else:
                                if "Practice" not in section_dict.values():
                                    section_dict['practice_name'] = "Practice"
                                    section_dict['practice_count'] = 0
                    else:
                        for section in department_types_ids.mapped("name")[2:]:
                            if section not in section_dict.values() and section == 'Section':
                                section_dict['section_name'] = section
                                section_dict['section_count'] = 0
                            if section not in section_dict.values() and section == 'Practice':
                                section_dict['practice_name'] = section
                                section_dict['practice_count'] = 0
                if section_dict:
                    if section_dict.get("section_name"):
                        d_head += f"<th class='py-1 px-1 m-1'>{section_dict.get('section_name')}</th>"
                        d_body += f"<td>{section_dict.get('section_count')}</td>"
                    if section_dict.get("practice_name"):
                        d_head += f"<th class='{th_class}'>{section_dict.get('practice_name')}</th>"
                        d_body += f"<td>{section_dict.get('practice_count')}</td>"
            else:
                for division in department_types_ids.mapped("name")[1:]:
                    d_head += f"<th class='py-1 px-1 m-1'>{division}</th>"
                    d_body += f"<td>0</td>"
            emp_count = search_emp.search_count([('department_id', '=', dep.id), ('employement_type.code', '!=', 'O')])
            d_head += f"<th class='py-1 px-1 m-1'>Employee</th>"
            d_body += f"<td>{emp_count}</td>"

        if dep.dept_type.name == 'Division':
            section_count = search_dept.search([('parent_id', '=', dep.id)])
            if section_count:
                section_name = set(section_count.mapped("dept_type.name"))
                d_head += f"<th class='{th_class}'>{str(section_name)[2:-2]}</th>"
                d_body += f"<td>{len(section_count)}</td>"
                for section in section_count:
                    practise_ids = search_dept.search([('parent_id', '=', section.id)])
                    practice_name = set(practise_ids.mapped("dept_type.name"))
                    practice_count = len(practise_ids)
                    if practice_count and practice_name:
                        practise_dict['practice_name'] = str(practice_name)[2:-2]
                        if practise_dict.get("practice_count") is not None:
                            practise_dict.update({'practice_count': int(practise_dict.get("practice_count")) + practice_count})
                    else:
                        if "Practice" not in practise_dict.values():
                            practise_dict['practice_name'] = "Practice"
                            practise_dict['practice_count'] = 0
                if practise_dict:
                    if practise_dict.get("section_name"):
                        d_head += f"<th class='{th_class}'>{practise_dict.get('section_name')}</th>"
                        d_body += f"<td>{practise_dict.get('section_count')}</td>"
                    if practise_dict.get("practice_name"):
                        d_head += f"<th class='{th_class}'>{practise_dict.get('practice_name')}</th>"
                        d_body += f"<td>{practise_dict.get('practice_count')}</td>"
            else:
                for section in department_types_ids.mapped("name")[2:]:
                    d_head += f"<th class='{th_class}'>{section}</th>"
                    d_body += f"<td>0</td>"
            emp_count = search_emp.search_count([('division', '=', dep.id), ('employement_type.code', '!=', 'O')])
            d_head += f"<th class='{th_class}'>Employee</th>"
            d_body += f"<td>{emp_count}</td>"

        if dep.dept_type.name == 'Section':
            practice_count = search_dept.search([('parent_id', '=', dep.id)])
            if practice_count:
                practice_name = set(practice_count.mapped("dept_type.name"))
                d_head += f"<th class='{th_class}'>{str(practice_name)[2:-2]}</th>"
                d_body += f"<td>{len(practice_count)}</td>"
            else:
                for practice in department_types_ids.mapped("name")[3:]:
                    d_head += f"<th class='{th_class}'>{practice}</th>"
                    d_body += f"<td>0</td>"
            emp_count = search_emp.search_count([('section', '=', dep.id), ('employement_type.code', '!=', 'O')])
            d_head += f"<th class='{th_class}'>Employee</th>"
            d_body += f"<td>{emp_count}</td>"

        if dep.dept_type.name == 'Practice':
            emp_count = search_emp.search_count([('practise', '=', dep.id), ('employement_type.code', '!=', 'O')])
            d_head += f"<th class='{th_class}'>Employee</th>"
            d_body += f"<td>{emp_count}</td>"

        dep_manager_name = dep.manager_id.name if dep.manager_id.name else ''
        dep_manager_name += f'({dep.manager_id.emp_code})' if dep.manager_id.emp_code else ''
        title = f'{dep_manager_name}<br/>' \
                f'<table class="table table-bordered mb-1"><thead>{d_head}</thead><tbody><tr>{d_body}</tr></tbody></table>' \
                f'<table class="table table-bordered"><thead>{t_head}</thead><tbody><tr>{t_body}</tr></tbody></table>'
        dep_data = {'name': dep.name,
                    'title': title,
                    'collapsed': True}
        childrens = request.env['hr.department'].sudo().search([('parent_id', '=', dep.id)])
        for child in childrens:
            sub_child = request.env['hr.department'].sudo().search([('parent_id', '=', child.id)])
            child_dep_manager_name = child.manager_id.name if child.manager_id.name else ''
            child_dep_manager_name += f'({child.manager_id.emp_code})' if child.manager_id.emp_code else ''
            next_style = self._get_style(style)
            d_head = ""
            d_body = ""
            if not sub_child:
                if child.dept_type.name == 'Division':
                    emp_count = search_emp.search_count([('division', '=', child.id), ('employement_type.code', '!=', 'O')])
                    for dpt in department_types_ids.mapped("name")[2:]:
                        d_head += f"<th class='{th_class}'>{dpt}</th>"
                        d_body += f"<td>0</td>"
                if child.dept_type.name == 'Section':
                    emp_count = search_emp.search_count([('section', '=', child.id), ('employement_type.code', '!=', 'O')])
                    for dpt in department_types_ids.mapped("name")[3:]:
                        d_head += f"<th class='{th_class}'>{dpt}</th>"
                        d_body += f"<td>0</td>"
                if child.dept_type.name == 'Practice':
                    emp_count = search_emp.search_count([('practise', '=', child.id), ('employement_type.code', '!=', 'O')])
                d_head += f"<th class='{th_class}'>Employee</th>"
                d_body += f"<td>{emp_count}</td>"
                title = f'{child_dep_manager_name}<br/>' \
                        f'<table class="table table-bordered mb-1"><thead>{d_head}</thead><tbody><tr>{d_body}</tr></tbody></table>' \
                        f'<table class="table table-bordered"><thead>{t_head}</thead><tbody><tr>{t_body}</tr></tbody></table>'
                data.append({'name': child.name,
                             'title': title,
                             'className': next_style})
            else:
                data.append(self.get_children(child, next_style, employment_types, department_types_ids))

        if childrens:
            dep_data['children'] = data
        if style:
            dep_data['className'] = style

        return dep_data

    def _get_style(self, last_style):
        if last_style == 'middle-level':
            return 'product-dept'
        elif last_style == 'product-dept':
            return 'rd-dept'
        elif last_style == 'rd-dept':
            return 'pipeline1'
        elif last_style == 'pipeline1':
            return 'frontend1'

        return 'middle-level'

    @http.route('/get_employee_data', type='json', auth="user", website=True)
    def get_employee_data(self):
        Model = request.env['hr.employee'].sudo()
        emp_list = Model.search([('employement_type.code', '!=', 'O')])
        parent_emp = Model.search([('parent_id', '=', False), ('employement_type.code', '!=', 'O')]) - Model.search([('user_id.login', '=', 'admin'), ('employement_type.code', '!=', 'O')])
        # temp_lis = [emp.name for emp in parent_emp]
        # if len(temp_lis) > 1:
        # 	raise UserError(f'More than one employee have no Administrative authority {temp_lis}')
        data = {}
        count = 0
        for emp in parent_emp:
            data_dict = {
                'id': emp.id,
                'name': emp.name,
                'title': f'{self._get_position(emp)}<br/>{emp.emp_code if emp.emp_code else ""}',
                'children': [],
                'office': self._get_image(emp),
                'direct_sub': len(emp_list.filtered(lambda r: r.parent_id.id == emp.id)),
                # 'indirect_sub': self._get_indirect_sub(emp)
            }
            employees = emp_list.filtered(lambda r: r.parent_id.id == emp.id)
            count += 1
            for employee in employees:
                data_dict['children'].append(self.get_emp_children(employee, 'middle-level'))
            data[count] = data_dict
        return {'values': data}

    @http.route('/get_project_data', type='json', auth="user", website=True)
    def get_project_data(self):
        projects = request.env['project.project'].sudo().search([], order="emp_id asc,name asc")
        # data_dict = {}
        data_dict = []
        count = 0
        for project in projects:
            data = {
                'id': project.id,
                'name': project.name,
                'manager': project.emp_id.display_name,
            }
            count += 1
            data_dict.append(data)
        # print("data==",data_dict)
        return data_dict

    @http.route('/get_hierarchy_data', type='json', auth="user", website=True)
    def get_hierarchy_data(self, **kwargs):
        # print("controller called-----------------------------",kwargs.get('pid'))
        pid = int(kwargs.get('pid', 0))
        Model = request.env['kw_project_resource_tagging'].sudo()
        project_team = Model.search([('project_id', '=', pid)])
        # print("project_emp$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$44-",project_team)
        data = {}
        count = 0
        # parent reporting
        team_data = project_team.filtered(lambda r: r.reporting_id.id != False)
        manager_data = project_team.filtered(lambda r: r.reporting_id.id == False)

        # print(("reporting_data----", reporting_data))
        # # print(("set reporting_data----",set(reporting_data.mapped('reporting_id'))))
        # print("reporting_data.mapped('reporting_id').ids===========", reporting_data.mapped('reporting_id').ids)
        # emp_data = project_team.filtered(lambda r: r.emp_id.id in reporting_data.mapped('reporting_id').ids)
        # print("emp_data========", emp_data)
        for team in manager_data:
            direct_sub = len(team_data.filtered(lambda r: team.emp_id.id == r.reporting_id.id))
            data_dict = {
                'id': team.emp_id.id,
                'name': team.emp_id.display_name,
                'title': f'{team.designation if team.designation else ""} <br/><table class="table table-bordered m-0 p-0 info_nodes"><tbody><tr><td>Reporting</td><td>{direct_sub}</td></tr></tbody></table>',
                'children': [],
                'office': self._get_image(team.emp_id)
            }
            
            # 'direct_sub': len(project_emp.filtered(lambda r: r.id == reporting_id.id)),
            child_data = team_data.filtered(lambda r: team.emp_id.id == r.reporting_id.id)
            # print(("child_data===#######################", child_data))
            count += 1
            for child in child_data:
                data_dict['children'].append(self.get_child_data(child, 'middle-level', team_data))
            
            data[count] = data_dict
        # print("data==",data)
        return {'values': data}

    def get_child_data(self, team, style='root-node', team_data=None):
        data = []
        total_sub = 0
        emp_job_position = f'{team.designation if team.designation else ""}'
        # emp_job_position += emp.emp_code if emp.emp_code else ''
        # Model = request.env['kw_project_resource_tagging'].sudo().search([("reporting_id", "=", "")])
        # Model = team_data
        # print("Model team_data >>> ",team, " >>> ", team_data)
        direct_sub = len(team_data.filtered(lambda r: team.emp_id.id == r.reporting_id.id))
        # print("direct_sub >>>> ", direct_sub)
        # indirect_sub = sum(len(child.child_ids) for child in emp.child_ids)
        # total_sub = direct_sub + indirect_sub
        emp_data = {'id': team.emp_id.id, 
                    'name': team.emp_id.display_name,
                    'className': 'root-node',
                    'title': f'{emp_job_position}<br/><table class="table table-bordered info_nodes"><tbody><tr><td>Reporting</td><td>{direct_sub}</td></tr></tbody></table>',
                    'office': self._get_image(team.emp_id),
                    'collapsed': False,
                    }
        
        children = team_data.filtered(lambda r: team.emp_id.id == r.reporting_id.id)
        # print("children ????????????????????? ", children)
        for child in children:
            sub_child = team_data.filtered(lambda r: child.emp_id.id == r.reporting_id.id)
            # print("sub_child >>>>>> ", sub_child)
            next_style = self._get_style(style)
            if not sub_child:
                data.append({'id': child.id,
                             'name': child.emp_id.display_name,
                             'title': f'{child.designation if child.designation else ""}',
                             'className': next_style,
                             'office': self._get_image(child.emp_id),
                             'direct_sub': len(team_data.filtered(lambda r: child.reporting_id.id == r.emp_id.id))
                             })
                
            else:
                # print(("if sub child-------------------------------------------"))
                data.append(self.get_child_data(child, next_style, team_data))

        if children:
            emp_data['children'] = data
        if style:
            emp_data['className'] = style
        # print("emp_data===",emp_data)
        return emp_data

    def get_emp_children(self, emp, style=False):
        data = []
        total_sub = 0
        emp_job_position = f'{self._get_position(emp)}<br/>{emp.emp_code if emp.emp_code else ""}'
        # emp_job_position += emp.emp_code if emp.emp_code else ''
        Model = request.env['hr.employee'].sudo().search([('employement_type.code', '!=', 'O')])
        direct_sub = len(Model.filtered(lambda r: r.parent_id.id == emp.id))
        indirect_sub = sum(len(child.child_ids) for child in emp.child_ids)
        total_sub = direct_sub + indirect_sub
        emp_data = {'id': emp.id, 'name': emp.name,
                    'title': f'{emp_job_position}<br/><table class="table table-bordered info_nodes"><tbody><tr><td>Direct Sub-ordinates</td><td>{direct_sub}</td></tr><tr><td>Indirect Sub-ordinates</td><td>{indirect_sub}</td></tr><tr><td>Total</td><td>{total_sub}</td></tr></tbody></table>',
                    'office': self._get_image(emp),
                    'collapsed': True,
                    }
        childrens = Model.filtered(lambda r: r.parent_id.id == emp.id)
        for child in childrens:
            sub_child = Model.filtered(lambda r: r.parent_id.id == child.id)
            next_style = self._get_style(style)
            if not sub_child:
                data.append({'id': child.id, 'name': child.name,
                             'title': f'{self._get_position(child)}<br/>{child.emp_code if child.emp_code else ""}',
                             'className': next_style,
                             'office': self._get_image(child),
                             'direct_sub': len(Model.filtered(lambda r: r.parent_id.id == child.id))})
            else:
                data.append(self.get_emp_children(child, next_style))

        if childrens:
            emp_data['children'] = data
        if style:
            emp_data['className'] = style

        return emp_data

    def _get_image(self, emp):
        image_path = "<img src='/web/image?model=hr.employee&id=" + str(emp.id) + "&field=image_medium'/>"
        return image_path

    def _get_position(self, emp):
        if emp.sudo().job_id:
            return emp.sudo().job_id.name
        return ""

    # def _get_indirect_sub(self, emp):
    # 	import pdb;pdb.set_trace();
    # 	print(f"emp ==>{emp} child_ids ==> {emp.mapped('child_ids')}")
    # 	sub_child_count = 0
    # 	Model = request.env['hr.employee'].sudo()
    # 	for child in emp.child_ids:
    # 		sub_children = Model.search([('parent_id','=',child.id)])
    # 		sub_child_count = Model.search_count([('parent_id','=',child.id)])
    # 		if sub_child_count != 0:
    # 			self.demo_method(sub_child_count)
    # 			for sub_child in sub_children:
    # 				self._get_indirect_sub(sub_child)
    # 		else:
    # 			tot_count = self.demo_method(0)
    # 			return tot_count

    # def demo_method(self, sub_child_count):
    # 	if sub_child_count != 0:
    # 		global total_count
    # 		total_count+=sub_child_count
    # 	else:
    # 		return total_count

    @http.route('/get_grade_level_data', type='json', auth="user", website=True)
    def get_grade_level_data(self, **args):
        data = {
            'name': request.env.user.company_id.name,
            'title': '',
            'children': []
        }
        levels = request.env['kw_grade_level'].sudo().search([])
        for level in levels:
            data['children'].append({'name': level.name})

        return {'values': data}

# def get_grade_level_children(self, level, style=False):
# 	data = []
# 	level_data = {'name': level.name, 'title': '', 'collapsed': True}
# 	childrens = request.env['kw_grade_level'].sudo().search([('parent_id','=',level.id)])
# 	for child in childrens:
# 		sub_child = request.env['kw_grade_level'].sudo().search([('parent_id','=',child.id)])
# 		next_style= self._get_style(style)
# 		if not sub_child:
# 			data.append({'name': child.name, 'title': '', 'className': next_style})
# 		else:
# 			data.append(self.get_grade_level_children(child, next_style))

# 	if childrens:
# 		level_data['children'] = data
# 	if style:
# 		level_data['className'] = style

# 	return level_data
