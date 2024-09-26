import requests, json
from datetime import datetime,date #,timedelta,
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api


class kw_activity_master(models.Model):
    _inherit = "project.task"
    _description = 'Activity Master'

    prject_category_id = fields.Many2one('kw_project_category_master', string='Category Name')
    project_id = fields.Many2one('project.project', string="Project")
    mapped_to = fields.Many2many('hr.department', string="Department")
    assigned_employee_id = fields.Many2one('hr.employee',string="Task Assigned To",track_visibility='always')
    planning_start_date = fields.Date(string='Planning Start Date',track_visibility='always')
    planning_end_date = fields.Date(string='Planning End Date',track_visibility='always')
    activity_planning_start_date = fields.Date(related="parent_id.planning_start_date",string='Planning Start Date')
    activity_planning_end_date = fields.Date(related="parent_id.planning_end_date",string='Planning End Date')
    activity_module = fields.Many2one(related="parent_id.module_id",string='Module Name')
    tl_employee_id = fields.Many2one('hr.employee', string="Team Leader")
    planning_hour = fields.Float(string="Planning Hour",track_visibility='always')
    activity_planned_hours = fields.Float(related="parent_id.planning_hour",string="Planned Hours")
    activity_remaining_hours = fields.Float(compute='compute_activity_remaining_hours',string="Remaining Hours")
    employee_task_dept = fields.Many2one(related="assigned_employee_id.department_id",string="Department")
    employee_task_designation = fields.Many2one(related="assigned_employee_id.job_id",string="Designation")
    kw_id = fields.Integer(string="KW ID")
    task_status = fields.Char("Activity Status",track_visibility='always',default="Not Started", copy=False)
    project_active_memb = fields.Many2many('hr.employee',compute='_compute_project_active_memb', string='Active Members')

    @api.onchange('project_id')
    def _compute_project_active_memb(self):
        self.project_active_memb = False
        activity_list = []
        active_member_rec = self.env['kw_project_resource_tagging'].sudo().search([('active','=',True),('project_id','=',self.project_id.id)])
        # print('active record>>>>>.',active_member_rec)
        if active_member_rec:
            for rec in active_member_rec:
                activity_list.append(rec.id)
            self.project_active_memb = [(6,0,active_member_rec.mapped('emp_id').ids)]




    
    # @api.depends('effective_hours', 'subtask_effective_hours', 'planned_hours', 'planning_hour')
    # def _compute_remaining_hours(self):
    #     for task in self:
    #         task.remaining_hours = task.planning_hour - task.effective_hours - task.subtask_effective_hours
    
    @api.depends('parent_id')
    def compute_activity_remaining_hours(self):
        for task in self:
            if task.parent_id:
                task_query = f'select remaining_hours from project_task where id = {task.parent_id.id}'
                self.env.cr.execute(task_query)
                remaining_hours = self.env.cr.dictfetchall()
                # print('asiba ama bhai========',remaining_hours)
                var = remaining_hours[0]['remaining_hours']
                task.activity_remaining_hours = var


    @api.depends('timesheet_ids.unit_amount', 'timesheet_ids.active')
    def _compute_effective_hours(self):
        for task in self:
            task.effective_hours = round(sum(task.timesheet_ids.filtered(lambda r: r.active is True).mapped('unit_amount')), 2)

    @api.onchange('prject_category_id')
    def onchange_prj_category_id(self):
        self.project_id = False
        project_list = []
        project_rec = self.env['project.project'].sudo().search(['&',('prject_category_id.mapped_to','=','Project'),'|',('emp_id.user_id','=',self.env.user.id),('resource_id.emp_id.user_id','=',self.env.user.id)])
        if project_rec:
            for rec in project_rec:
                project_list.append(rec.id)
            
            return {'domain': {'project_id': [('id', 'in', project_list)]}}

    
    @api.onchange('project_id')
    def onchange_project_id(self):
        self.parent_id = False
        self.tl_employee_id = False
        self.assigned_employee_id = False
        activity_list = []
        actvity_rec = self.env['project.task'].sudo().search([('project_id', '=', self.project_id.id)])
        active_member_rec = self.env['kw_project_resource_tagging'].sudo().search([('active','=',True),('project_id','=',self.project_id.id)])
        if actvity_rec:
            for rec in actvity_rec:
                activity_list.append(rec.id)
            # print('activity lis>>>>>>>>',activity_list)
            
        return {'domain': {'task_id': [('id', 'in', activity_list)],'assigned_employee_id': [('id','in',active_member_rec.mapped('emp_id').ids)]}}

    # get active projects kw_id in "(34,45)" format used in .net APIs'
    def get_active_project_kw_ids(self):
        active_projects = self.env['project.project'].sudo().search([('kw_id','!=',False),('kw_id','>',0)],order="kw_id desc")
        active_project_kw_ids = "()"
        
        if active_projects:
            active_project_kw_ids = f"({','.join(active_projects.mapped(lambda r:str(r.kw_id)))})"
            
        return active_project_kw_ids

    @api.constrains('activity_planned_hours', 'activity_remaining_hours', 'planned_hours')
    def validate_planning_hour_restriction_check(self):
        for rec in self:
            if rec.parent_id and rec.planned_hours:
                if rec.planned_hours > rec.activity_remaining_hours:
                    raise ValidationError("Task hour should not be more than activity remaining hours.")
    @api.multi
    def action_reopen_task(self):
        if self.task_status == 'Completed':
            self.write({'task_status':'In Progress'})
        if self.task_status == False:
            self.write({'task_status':'In Progress'})
            self.env.user.notify_success("Task Re-Open Successfully.")
       
    @api.multi
    def action_sub_task_details(self):
        form_view_id = self.env.ref('kw_timesheets.kw_sub_task_master_form').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view_id,
            'res_id': self.ids[0],
            'target': 'self',
            'context'   : {'create':False,'edit':False,'delete':False,'duplicate':False,'show_employee':False}
        }

    @api.model
    def syncProjectModules(self):
        url = self.env['ir.config_parameter'].sudo().get_param('kw_proj.project_web_service_url', False)
        header = {'Content-type': 'application/json'}
        # project_kw_ids = self.env.ref('kw_timesheets.kw_project_module_activity_sync_ids_system_parameter').sudo().value
        project_kw_ids = self.get_active_project_kw_ids()
        multi_project_id_json_data = {"ProjectID_multiple":project_kw_ids}
        
        data = json.dumps(multi_project_id_json_data)
        module_url = url + '/GetProjectWise_ModulesDetails'
        
        sync_log = self.env['kw_kwantify_integration_log'].sudo().create({
                                        'name': 'Sync Project Modules From V5',
                                        'request_params':f"URL : {module_url}\n data: {data}"
                                        })
        response_result = ""
        error_log = ""
        new_record_log = ""
        update_record_log = ""
        
        module_list = []
        try:
            api_response = requests.post(module_url, data=data, headers=header)
            response_result = api_response.text
            module_list = json.loads(response_result)

        except Exception as e:
            error_log += f"Error : ({e})"

        project_obj = self.env['project.project'].sudo()
        module_obj = self.env['kw_project.module'].sudo()
        
        for data_dict in module_list:
            project_rec = project_obj.search(
                    [('kw_id', '=', int(data_dict['projectID'])), '|', ('active', '=', True), ('active', '=', False)])
            if project_rec:
                module_dict = {
                    'kw_id':int(data_dict['ModuleID']),
                    'name':data_dict['Modulename'],
                    'project_id':project_rec.id,
                    'last_sync_date':date.today()
                }
                module_rec = module_obj.search([
                    ('kw_id', '=', int(data_dict['ModuleID']))
                    ])
                if module_rec:
                    module_rec.write(module_dict)
                    update_record_log += f"Updated Module : {data_dict}\n"
                else:
                    module_obj.create(module_dict)
                    new_record_log += f"Created Module : {data_dict}"
                       
        sync_log.write({"response_result":response_result,
                        "error_log":error_log,
                        "new_record_log":new_record_log,
                        "update_record_log":update_record_log,
                        })

    @api.model
    def syncProjectResources(self):
        # print("Resource Tagging")
        url = self.env['ir.config_parameter'].sudo().get_param('kw_proj.project_web_service_url', False)
        header = {'Content-type': 'application/json'}
        # project_kw_ids = self.env.ref('kw_timesheets.kw_project_module_activity_sync_ids_system_parameter').sudo().value
        project_kw_ids = self.get_active_project_kw_ids()
        multi_project_id_json_data = {"ProjectID_multiple":project_kw_ids}
        
        data = json.dumps(multi_project_id_json_data)
        resource_tag_url = url + '/MultipleProject_Resource_Details'
        
        sync_log = self.env['kw_kwantify_integration_log'].sudo().create({
                                        'name': 'Sync Project Resources From V5',
                                        'request_params':f"URL : {resource_tag_url}\n data: {data}"
                                        })
        response_result = ""
        error_log = ""
        new_record_log = ""
        update_record_log = ""
        
        resource_tag_list = []
        
        try:
            api_response = requests.post(resource_tag_url, data=data, headers=header)
            response_result = api_response.text
            resource_tag_list = json.loads(api_response.text)
        except Exception as e:
            error_log += f"Error  : ({e})"
            
        project_obj = self.env['project.project'].sudo()
        resource_obj = self.env['kw_project_resource_tagging'].sudo()
        
        resource_tag_list.sort(key=lambda dict_obj : dict_obj['TagStatus'])
        
        for data_dict in resource_tag_list:
            project_rec = project_obj.search(
                        [('kw_id', '=', int(data_dict['ProjectTD'])), '|', ('active', '=', True), ('active', '=', False)])
            
            employee_rec = self.env['hr.employee'].sudo().search(
                        [('kw_id', '=', int(data_dict['UserID'])),'|', ('active', '=', True), ('active', '=', False)], limit=1)
            
            if project_rec and employee_rec:
                resource_tag_dict = {
                            'designation': data_dict['Designation'],
                            'project_id': project_rec.id,
                            'emp_id': employee_rec.id,
                            'active': True if data_dict['TagStatus'] == 1 else False,
                            'start_date' : (datetime.strptime(data_dict['DTM_INVOLVED_FROM'],'%m/%d/%Y %I:%M:%S %p').strftime("%d-%b-%Y")) if data_dict['DTM_INVOLVED_FROM'] else None,
                            'end_date' : (datetime.strptime(data_dict['DTM_INVOLVED_TO'],'%m/%d/%Y %I:%M:%S %p').strftime("%d-%b-%Y")) if data_dict['DTM_INVOLVED_TO'] else None,
                            # 'released_date' : (datetime.strptime(data_dict['DTM_RELEASED_ON'],'%m/%d/%Y %I:%M:%S %p').strftime("%d-%b-%Y")) if data_dict['DTM_RELEASED_ON'] else None,
                        }
                tag_rec = resource_obj.search([
                            ('project_id', '=', project_rec.id),
                            ('emp_id', '=', employee_rec.id), '|', ('active', '=', True), ('active', '=', False)], limit=1)
                
                if tag_rec:
                    if tag_rec.active == False and resource_tag_dict['active'] == False:
                        pass
                    else:
                        tag_rec.write(resource_tag_dict) 
                        update_record_log += f"Updated Resource to Project : {data_dict}"
                    
                else:
                    resource_obj.create(resource_tag_dict)
                    new_record_log += f"Added Resource to Project : {data_dict}"
                       
        sync_log.write({"response_result":response_result,
                        "error_log":error_log,
                        "new_record_log":new_record_log,
                        "update_record_log":update_record_log,
                        })
            
    @api.multi
    def syncProjectActivityMaster(self):
        try:
            params = self.env['ir.config_parameter'].sudo()
            url = params.get_param('kw_proj.project_web_service_url', False)
            # day_diff = int(params.get_param('kw_proj.project_service_diff_days', 1))
            # 
            # resource_json_data = {
            #     "FromDate": (datetime.now() - relativedelta(days=+day_diff)).strftime('%Y-%m-%d'),
            #     "ToDate": datetime.now().strftime('%Y-%m-%d'),
            # }
            # project_kw_ids = self.env.ref('kw_timesheets.kw_project_module_activity_sync_ids_system_parameter').sudo().value
            project_kw_ids = self.get_active_project_kw_ids()
            multi_project_id_json_data = {"ProjectID_multiple": project_kw_ids}
            # # PROJECT Task Method Call and update record data
            project_activity_result = self._ProjectTaskActivity(url, multi_project_id_json_data)
            self._CreateUpdateProjectActivityTaggingData(project_activity_result)
        
            # # RESOURCE TAGGING Method Call and update record data
            # resource_activity_result = self._ResourseProjectActivityTagging(url, multi_project_id_json_data)
            # self._CreateUpdateResourceTaggingData(resource_activity_result)
        except Exception as e:
            # print("Error occurs in main cron method : ", e)
            pass
       
    # # Resource Tagging URL Call and update record Starts :-----
    def _ResourseProjectActivityTagging(self, resource_url, json_data):
        header = {'Content-type': 'application/json', }
        data = json.dumps(json_data)
        # if resource_url:
        #     resource_url = resource_url + '/Project_Resource_Details'
        # else:
        #     resource_url = "https://kwportalservice.csmpl.com/OdooSynSVC.svc/Project_Resource_Details"
        if resource_url:
            resource_url = resource_url + '/MultipleProject_Resource_Details'
        else:
            resource_url = "https://kwportalservice.csmpl.com/OdooSynSVC.svc/MultipleProject_Resource_Details"

        request_params_resource = " Service Url : " + resource_url + " " + str(data)
        try:
            response_result = requests.post(resource_url, data=data, headers=header)
            resource_response = json.loads(response_result.text)
            return {'status': 200, 'response_result': resource_response, 'request_params': request_params_resource}
        except Exception as e:
            return {'status': 500, 'response_result': [], 'error_log': str(e), 'request_params': request_params_resource}
           
    def _CreateUpdateResourceTaggingData(self, result):
        # print("Resource Tagging")
        project_project = self.env['project.project'].sudo()
        resource_tagging = self.env['kw_project_resource_tagging'].sudo()
        record_log = result['error_log'] if 'error_log' in result else ''
        update_record_log = ''
        new_record_log = ''
        try:
            if result['status'] == 200 and result['response_result']:
                resource_responce = result['response_result']
                for resource_data in resource_responce:
                    # print(type(resource_data['TagStatus']))
                    user_data = self.env['hr.employee'].search(
                        [('kw_id', '=', int(resource_data['UserID'])), '|', ('active', '=', True), ('active', '=', False)], limit=1)
                    project_data = project_project.search(
                        [('kw_id', '=', int(resource_data['ProjectTD'])), '|', ('active', '=', True), ('active', '=', False)])

                    if user_data and project_data:
                        tagging_record = resource_tagging.search([
                            ('project_id', '=', project_data.id),
                            ('emp_id', '=', user_data.id), '|', ('active', '=', True), ('active', '=', False)], limit=1)

                        vals = {
                            'designation': resource_data['Designation'] if 'Designation' in resource_data else False,
                            'project_id': project_data.id,
                            'emp_id': user_data.id,
                            'active': True if resource_data['TagStatus'] == 1 else False
                        }

                        if not tagging_record:
                            resource_created = resource_tagging.create(vals)
                            # print("Created")
                            new_record_log += ' ### Start_rec ### ' + str(resource_created.id) + ' ###' + str(vals) + ' ### End_rec ### \n'
                        else:
                            tagging_record.write(vals)
                            # print("Updated")
                            update_record_log += ' ### Start_rec ### ' + str(tagging_record.id) + ' ###' + str(vals) + ' ### End_rec ### \n'

        except Exception as e:
            # print('Error occurs in Project : ', e)
            pass
        finally:
            synch_log = self.env['kw_kwantify_integration_log'].sudo()
            synch_log.create({'name': 'Project Resource Tagging Activity log',
                              'new_record_log': new_record_log,
                              'update_record_log': update_record_log,
                              'error_log': record_log,
                              'request_params': result['request_params'],
                              'response_result': result['response_result']})
            # synch_log.search([('create_date', '<=', (datetime.now() - relativedelta(weeks=+2)).strftime('%Y-%m-%d'))]).unlink()
            self.env.user.notify_success(message='Project Resource tagging Data sync successfully!')

    @api.onchange('parent_id')
    def get_team_leader_department_onchange(self):
        self.mapped_to = False
        self.tl_employee_id = False

        self.tl_employee_id = self.parent_id.tl_employee_id.id

        deptObjs = self.env['hr.department'].sudo().search([('code', 'in', ['BSS', 'Quality Control'])])

        self.mapped_to =  [(6, 0, deptObjs.ids)] if not self.parent_id and not self.parent_id.mapped_to else self.parent_id.mapped_to

    def _ProjectTaskActivity(self, url, json_data):
        header = {'Content-type': 'application/json'}
        data = json.dumps(json_data)
        # print(data)
        if url:
            url = url + '/employee_Phase_Activity'
        else:
            url = "https://kwportalservice.csmpl.com/OdooSynSVC.svc/employee_Phase_Activity"
        # try:
        request_params_opp = " Service Url : " + url + " " + str(data)
        response_result = requests.post(url, data=data, headers=header)
        data = json.loads(response_result.text)
        return {'status': 200, 'response_result': data, 'request_params': request_params_opp}
        # except Exception as e:
        #     return {'status': 500, 'response_result': [], 'error_log': str(e), 'request_params': request_params_opp}

    def _CreateUpdateProjectActivityTaggingData(self, result):
        # print("Activity")
        projectObj = self.env['project.project'].sudo()
        projectCategObj = self.env['kw_project_category_master'].sudo()
        task_model = self.env['project.task'].sudo()

        deptObjs = self.env['hr.department'].sudo().search([('code', 'in', ['BSS', 'Quality Control'])])
        category_id = projectCategObj.search([('name', '=', 'Project Work')])
        new_record_log = ''
        update_record_log = ''
        error_log = result['error_log'] if 'error_log' in result else ''
        try:
            if result['status'] == 200 and result['response_result']:
                result_set = result['response_result']
                # print(result_set, '---------------------->')
                for rec in result_set:
                    # print(rec, '-------------------->>')
                    vals = {
                        'prject_category_id': category_id.id if category_id else False,
                        'name': rec.get('ActivityName', False),
                        'planning_hour': rec.get('Int_PNL_Hour', False),
                        'planned_hours': rec.get('Int_PNL_Hour', False),
                        'task_status': 'In Progress' if rec.get('ActivityStatus', 0) == 1 else 'Completed'
                        # 'active': True if rec.get('ActivityStatus', 0) == 1 else False,
                    }
                    # print(vals,'-------------------->>')
                    if 'DT_PNL_START_DATE' in rec and rec['DT_PNL_START_DATE']:
                        vals['planning_start_date'] = datetime.strptime(rec['DT_PNL_START_DATE'], '%m/%d/%Y %H:%M:%S %p').strftime("%m/%d/%Y")
                        vals['planning_end_date'] = datetime.strptime(rec['DT_PNL_COMPL_DATE'], '%m/%d/%Y %H:%M:%S %p').strftime("%m/%d/%Y")

                    projectTaskObj = task_model.search([('kw_id', '=', rec.get('ActivityID'))])
                    project_id = projectObj.search([('kw_id', '=', rec.get('ProjectTD')), '|', ('active', '=', True), ('active', '=', False)])
                    if project_id:
                        vals.update({'project_id': project_id.id, 'mapped_to': [(6, 0, deptObjs.ids)]})
                        
                    if "ModuleID" in rec and rec["ModuleID"] and rec["ModuleID"] > 0:
                        module = self.env['kw_project.module'].search([('kw_id', '=', rec['ModuleID'])])
                        vals.update({'module_id': module.id})

                    if rec.get('Int_Leader_EmpID', 0):
                        # print(rec.get('Int_Leader_EmpID', 0))
                        empobj = self.env['hr.employee'].sudo().search([('kw_id', '=', rec.get('Int_Leader_EmpID',0))])
                        # print('empobj',empobj)
                        if empobj:
                            vals.update(({'tl_employee_id': empobj.id}))
                            if 'mapped_to' in vals:
                                vals['mapped_to'][0][2].extend(empobj.department_id.ids)# = empobj.department_id.ids + vals['mapped_to'][0][2]
                    
                    if not projectTaskObj:
                        vals.update({'kw_id': rec.get('ActivityID')})
                        projectTaskObj = task_model.create(vals)
                        new_record_log += ' ### Start_rec ### ' + str(projectTaskObj.id) + ' ###' + str(vals) + ' ### End_rec ### \n'
                    else:
                        projectTaskObj.write(vals)
                        update_record_log += ' ### Start_rec ### ' + str(projectTaskObj.ids) + ' ###' + str(vals) + ' ### End_rec ### \n'



        except Exception as e:
            # print('Error occurs in project task : ', e)
            pass
            
        finally:
            synch_log = self.env['kw_kwantify_integration_log'].sudo()
            synch_log.create({'name': 'Project Activity Sync',
                              'new_record_log': new_record_log,
                              'update_record_log': update_record_log,
                              'error_log': error_log,
                              'request_params': result['request_params'],
                              'response_result': result['response_result']})

            # synch_log.search([('create_date', '<=', (datetime.now() - relativedelta(weeks=+2)).strftime('%Y-%m-%d'))]).unlink()
            # self.env.user.notify_success(message='Project Activity Data sync successfully!')
