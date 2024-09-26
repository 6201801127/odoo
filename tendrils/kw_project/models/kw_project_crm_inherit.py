# -*- coding: utf-8 -*-
import requests, json
from datetime import datetime,date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class kw_project_crm_inherit(models.Model):
    _inherit = 'crm.lead'

    kw_opportunity_id = fields.Integer('Opportunity Id')
    kw_workorder_id = fields.Integer('Workorder Id')
    code = fields.Char('Code')
    date = fields.Date("Work Order Date")  
    pm_id = fields.Many2one('hr.employee',string="PM")
    # sbu_head_id = fields.Many2one('hr.employee',string="Sbu Head")
    reviewer_id = fields.Many2one('hr.employee',string="Reviewer")
    ceo_id = fields.Many2one('hr.employee',string="CEO")
    # hod_id = fields.Many2one('hr.employee',string="HOD")
    csg_head_id = fields.Many2one('hr.employee',string="CSG Head")
    presales_id = fields.Many2one('hr.employee',string="Presales Head")
    cso_id = fields.Many2one('hr.employee',string="Sales")
    cfo_id = fields.Many2one('hr.employee',string="CFO")            
    client_name = fields.Char(string='Client Name')
    client_short_name = fields.Char(string='Client Short Name')
    csg_name = fields.Char(string='CSG Name')
    sales_person_id = fields.Many2one('hr.employee',string="Account Holder")
    pac_status = fields.Integer('PAC Status')



    

    @api.constrains('kw_opportunity_id')
    def check_kw_opportunity_id(self):
        crm_leads = self.env['crm.lead'].sudo().search(['|',('kw_opportunity_id','!=',0),('kw_opportunity_id','!=',False)])

        for lead in self.filtered(lambda r:r.kw_opportunity_id not in [False,0]):
            duplicate_lead = crm_leads.filtered(lambda r:r.kw_opportunity_id == lead.kw_opportunity_id) - lead
            if duplicate_lead:
                raise ValidationError("This kw_opportunity_id already exists.")
           
    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if self._context.get('advance_eq'):
                record_name = str(record.name) 
                result.append((record.id, record_name))
            
            else:
                if record.code:
                    record_name = str(record.code) + ' | ' + str(record.name)
                else:
                    record_name = str(record.name)
                result.append((record.id, record_name))
        return result

    # # Main method called from CRON Starts: ---
    def syncKwantifyProjectData(self):
        try:
            params = self.env['ir.config_parameter'].sudo()
            url = params.get_param('kw_proj.project_web_service_url', False)
            day_diff = int(params.get_param('kw_proj.project_service_diff_days', 1))

            json_data = {
                "FromDate": (datetime.now() - relativedelta(days=+day_diff)).strftime('%Y-%m-%d'),
                "ToDate": datetime.now().strftime('%Y-%m-%d'),
            }
            # # CRM Method Call and update record data
            # crm_result = self._ResponsefromKwantifyConfigCrm(url, json_data)
            # self._CreateUpdateCRMData(crm_result)
            # # PROJECT Method Call and update record data
            project_result = self._ResponsefromKwantifyConfigProject(url, json_data)
            self._CreateUpdateProjectData(project_result)
            # # RESOURCE TAGGING Method Call and update record data
            # resource_result = self._ResponsefromKwantifyConfigResourceTagging(url, json_data)
            # self._CreateUpdateResourceTaggingData(resource_result)
            # # # MANAGE RESOURCE DATE Method Call and send mail to PM(s)
            # self._ManageResourceDate()
        except Exception as e:
            # print("Error occurs in main cron method : ", e)
            pass

    def sync_v5_opportunies(self):
        # try:
        params = self.env['ir.config_parameter'].sudo()
        url = params.get_param('kw_proj.project_web_service_url', False)
        day_diff = int(params.get_param('kw_proj.project_service_diff_days', 1))
        # print(day_diff,'============================day_diff')

        json_data = {
            "FromDate": (datetime.now() - relativedelta(days=+day_diff)).strftime('%Y-%m-%d'),
            "ToDate": datetime.now().strftime('%Y-%m-%d'),
        }
        # print('=============json_data==============',json_data)
        # CRM Method Call and update record data
        crm_result = self._ResponsefromKwantifyConfigCrm(url, json_data)
        self._CreateUpdateCRMData(crm_result)
        # except Exception as e:
        #     print("Error occurs in main cron method : ", e)
        #     pass
        
    # # Main method called from CRON Ends: ---

    # # Opportunity(CRM) URL call and Update record Starts :------
    def _ResponsefromKwantifyConfigCrm(self, url, json_data):
        header = {'Content-type': 'application/json', }
        data = json.dumps(json_data)
        if url:
            crm_url = url + '/GetOpportunity'

        request_params_opp = " Service Url : " + crm_url + " " + str(data)
        # print("request_params_opp=================================",request_params_opp)
        try:
            response_result = requests.post(crm_url, data=data, headers=header)
            opportunity_resp = json.loads(response_result.text)
            return {'status': 200, 'result': opportunity_resp, 'request_params_opp': request_params_opp}
        except Exception as e:
            return {'status': 500, 'error_log': str(e),'request_params_opp':request_params_opp}
    
    def _CreateUpdateCRMData(self, result):
        # print('===================',result)
        crm_lead = self.env['crm.lead'].sudo()
        crm_stage = self.env['crm.stage'].sudo()
        opp = crm_stage.search([('sequence', '=', 3)])
        wor = crm_stage.search([('sequence', '=', 70)])
        record_log = result['error_log'] if 'error_log' in result else ''
        update_record_log = ''
        new_record_log = ''
        # try:
        opp_data_ceo = int(self.env['ir.config_parameter'].sudo().get_param('ceo'))
        opp_data_cso = int(self.env['ir.config_parameter'].sudo().get_param('cso'))
        opp_data_presales = int(self.env['ir.config_parameter'].sudo().get_param('presales_head'))
        opp_data_cfo = int(self.env['ir.config_parameter'].sudo().get_param('cfo'))
        emp_ceo= self.env['hr.employee'].sudo().search([('id','=',opp_data_ceo)])
        emp_cso= self.env['hr.employee'].sudo().search([('id','=',opp_data_cso)])
        emp_presales= self.env['hr.employee'].sudo().search([('id','=',opp_data_presales)])
        emp_cfo= self.env['hr.employee'].sudo().search([('id','=',opp_data_cfo)])

        # print("======================================",type(opp_data_ceo),opp_data_cso,emp_ceo,emp_cso,emp_presales)

        # print("result status-------------------------------",)
        if result['status'] == 200 and result['result']:
            # print('yes======++++++++++++++++++++++++++++++++==========',result['status'] )
            result_set = result['result']
            for crm_data in result_set:
                user_data4 = self.env['hr.employee'].search([('kw_id','=',int(crm_data['PMId']))],limit=1) if (crm_data['PMId']) else []
                user_data5 = self.env['hr.employee'].search([('kw_id','=',int(crm_data['ReviewerID']))],limit=1) if (crm_data['ReviewerID']) else []
                user_data8 = self.env['hr.employee'].search([('kw_id','=',int(crm_data['CsgHeadID']))],limit=1) if (crm_data['CsgHeadID']) else []
                user_data9 = self.env['hr.employee'].search([('kw_id','=',int(crm_data['SalespersonId']))],limit=1) if (crm_data['SalespersonId']) else []

                Vch_ClientName = crm_data['Vch_ClientName'] if (crm_data['Vch_ClientName']) else []
                Vch_ClientshortName = crm_data['VchClientShortName'] if (crm_data['VchClientShortName']) else []
                csgname = crm_data['Csgname'] if (crm_data['Csgname']) else []
                # print(crm_data['Vch_Pac_Status'],'==============++++++++++++++++++++++++++++++++++++++++++')
                pacstatus = crm_data['Vch_Pac_Status'] if (crm_data['Vch_Pac_Status']) else []



               
                vals = {
                    'name': crm_data['OpportunityName'],
                    # 'date': crm_data['WorkOrderDate'] if crm_data['WorkOrderDate'] else False,
                    'code': crm_data['Code'] if crm_data['Code'] else False,
                    'active': True if crm_data['Status'] == '1' else False,
                    'pm_id':user_data4.id if len(user_data4) else False,
                    'reviewer_id':user_data5.id if len(user_data5) else False,
                    'csg_head_id':user_data8.id if len(user_data8) else False,
                    'cso_id':emp_cso.id if emp_cso else False,
                    'cfo_id':emp_cfo.id if emp_cfo else False,
                    'ceo_id':emp_ceo.id if emp_ceo else False,
                    'presales_id':emp_presales.id if emp_presales else False,
                    'client_name':Vch_ClientName if Vch_ClientName else '',
                    'client_short_name':Vch_ClientshortName if Vch_ClientshortName else '',
                    'csg_name':csgname if csgname else '',
                    'sales_person_id':user_data9.id if len(user_data9) else False,
                    'pac_status':pacstatus if pacstatus else False,


                
                }
                # print(vals,'=================vals')
                if crm_data['WorkOrderDate']:
                    vals.update({'date': crm_data['WorkOrderDate']})
                opportunity_id = int(crm_data['OpportunityId'] if crm_data['OpportunityId'] else '0')
                workorder_id = int(crm_data['WorkorderId'] if crm_data['WorkorderId'] else '0')
                # print("op============",opportunity_id)
                # print("wo================",workorder_id)
                if opportunity_id != 0 and workorder_id == 0:
                    # print('yes1-------')
                    # print('Opp != 0 and work == 0 ',crm_data)
                    opp1_id = crm_lead.search(
                        [('kw_opportunity_id', '=', opportunity_id), '|', ('active', '=', True),
                            ('active', '=', False)],limit=1)
                    # print("Opp data -------------------",opp1_id)
                    if len(opp1_id):
                        # print("Opp exist=============")
                        vals.update({'stage_id': opp.id,
                                     'type': 'opportunity'})
                        opp1_id.write(vals)
                        # print("Write done")
                        update_record_log += ' ### Start_rec ### ' + str(opp1_id.id) + ' ###' + str(vals) + ' ### End_rec ### \n'
                    else:
                        # print("Opp not exist===============")
                        vals.update({'kw_opportunity_id': opportunity_id,
                                        'kw_workorder_id': workorder_id,
                                        'stage_id': opp.id,
                                        'type': 'opportunity'})
                        new_created_record = crm_lead.create(vals)
                        # print("Create Done===============")
                        new_record_log += ' ### Start_rec ### ' + str(new_created_record.id) + ' ###' + str(vals) + ' ### End_rec ### \n'
                elif opportunity_id != 0 and workorder_id != 0:
                    # print('Opp != 0 and work != 0 ',crm_data)
                    opp2_id = crm_lead.search(
                        [('kw_opportunity_id', '=', opportunity_id), '|', ('active', '=', True),
                            ('active', '=', False)],limit=1)
                    # print("Opp data ------------------------------------",opp2_id)
                    if len(opp2_id):
                        # print("Opp exist")
                        vals.update({'kw_workorder_id': workorder_id, 'stage_id': wor.id,'type': 'opportunity'})
                        opp2_id.write(vals)
                        # print("Write done")
                        update_record_log += ' ### Start_rec ### ' + str(opp2_id.id) + ' ###' + str(vals) + ' ### End_rec ### \n'
                    else:
                        # print("Opp not exist")
                        vals.update({'kw_opportunity_id': opportunity_id,
                                        'kw_workorder_id': workorder_id,
                                        'stage_id': wor.id,
                                        'type': 'opportunity'})
                        new_created_record = crm_lead.create(vals)
                        # print("Create Done")
                        new_record_log += ' ### Start_rec ### ' + str(new_created_record.id) + ' ###' + str(vals) + ' ### End_rec ### \n'
                elif opportunity_id == 0 and workorder_id != 0:
                    # print('Opp == 0 and work != 0 ', crm_data)
                    wor_id = crm_lead.search(
                        [('kw_workorder_id', '=', workorder_id), '|', ('active', '=', True),
                            ('active', '=', False)],limit=1)
                    # print("Workorder data ----------------------", wor_id)
                    if len(wor_id):
                        # print("Work exist")
                        vals.update({'kw_opportunity_id': opportunity_id,
                                        'kw_workorder_id': workorder_id,
                                        'stage_id': wor.id,
                                        'type': 'opportunity'})
                        wor_id.write(vals)
                        # print("Write done")
                        update_record_log += ' ### Start_rec ### ' + str(wor_id.id) +' ###' + str(vals) + ' ### End_rec ### \n'
                    else:
                        # print("Work not exist")
                        vals.update({'kw_opportunity_id': opportunity_id,
                                        'kw_workorder_id': workorder_id,
                                        'stage_id': wor.id,
                                        'type': 'opportunity'})
                        new_created_record = crm_lead.create(vals)
                        # print("Create Done")
                        new_record_log += ' ### Start_rec ### ' + str(new_created_record.id) + ' ###' + str(vals) + ' ### End_rec ### \n'
        #     print("Successfully done with Opportunity and WorkOrder : ", len(result_set))
        # except Exception as e:
        #     print('Error occurs in CRM : ', e)
        #     pass
        # finally:
        #     # # Enter data into log model
        #     synch_log = self.env['kw_kwantify_integration_log'].sudo()
        #     synch_log.create({'name': 'Kwantify Opportunity and WorkOrder Data',
        #                       'new_record_log': new_record_log,
        #                       'update_record_log': update_record_log,
        #                       'error_log': record_log,
        #                       'request_params': result['request_params_opp'],
        #                       'response_result': result['result'] if 'result' in result else []})

            # # If any record. delete last 15 days log record
            # synch_log.search([('create_date', '<=', (datetime.now() - relativedelta(weeks=+2)).strftime('%Y-%m-%d'))]).unlink()

    # # Opportunity(CRM) URL call and Update record Ends :------

    # # Project URL call and Update record Starts :------
    def _ResponsefromKwantifyConfigProject(self, url, json_data):
        header = {'Content-type': 'application/json', }
        data = json.dumps(json_data)
        if url:
            # project_url = url + '/GetProject'
            project_url = url + '/GetActiveProject'

        request_params_project = " Service Url : " + project_url + " " + str(data)
        try:
            response_result = requests.post(project_url, data=data, headers=header)
            project_resp = json.loads(response_result.text)
            return {'status': 200, 'project_result': project_resp, 'request_params_project': request_params_project}
        except Exception as e:
            return {'status': 500, 'error_log': str(e), 'request_params_project': request_params_project}

    def _CreateUpdateProjectData(self, result):
        crm_lead = self.env['crm.lead']
        project_project = self.env['project.project']
        projectCategObj = self.env['kw_project_category_master'].sudo().search([('name', '=', 'Project Work')])
        record_log = result['error_log'] if 'error_log' in result else ''
        update_record_log = ''
        new_record_log = ''

        try:
            if result['status'] == 200 and result['project_result']:
                project_responce = result['project_result']
                valid_kw_id_projects = self.env['project.project'].with_context(active_test = False).search([('kw_id','!=',False),('kw_id','>',0)])
                # print("valid_kw_id_projects -->",valid_kw_id_projects)
                updated_kw_ids = []
                for project_data in project_responce:
                    user_data = self.env['hr.employee'].search(
                        [('kw_id', '=', int(project_data['PMId'])), '|', ('active', '=', True), ('active', '=', False)],
                        limit=1)
                    
                    reviewer = False
                    if 'ReviewerID' in project_data and project_data['ReviewerID']:
                        reviewer = self.env['hr.employee'].search(
                            [('kw_id', '=', int(project_data['ReviewerID'])), '|', ('active', '=', True), ('active', '=', False)],
                            limit=1)
                        reviewer = reviewer and reviewer.id or False
                        
                    vals = {
                        'emp_id': user_data.id if user_data else False,
                        'reviewer_id':reviewer,
                        'code': project_data['ProjCode'],
                        'kw_id': int(project_data['ProjId']),
                        'name': project_data['ProjName'],
                        'active': True if project_data['Status'] == '1' else False,
                        # 'prject_category_id':projectCategObj.id if projectCategObj else False,
                        'prject_category_id':[(4,projectCategObj.id)],
                    }
                    
                    if project_data['RefId'] and project_data['RefType'] and project_data['RefType'] == 'W':
                        word_order_id = crm_lead.search(
                            [('kw_workorder_id', '=', int(project_data['RefId'])), '|', ('active', '=', True),
                             ('active', '=', False)], limit=1)
                        if len(word_order_id):
                            # print('W found')
                            vals.update({'crm_id': word_order_id.id})
                    elif project_data['RefId'] and project_data['RefType'] and project_data['RefType'] == 'O':
                        opportunity_id = crm_lead.search(
                            [('kw_opportunity_id', '=', int(project_data['RefId'])), '|', ('active', '=', True),
                             ('active', '=', False)], limit=1)
                        if len(opportunity_id):
                            # print('O found')
                            vals.update({'crm_id': opportunity_id.id})

                    kw_ids = project_project.search(
                        [('kw_id', '=', int(project_data['ProjId'])), '|', ('active', '=', True),
                         ('active', '=', False)])
                    updated_kw_ids.append(int(project_data['ProjId']))
                    if len(kw_ids):
                        kw_ids.write(vals)
                        update_record_log += ' ### Start_rec ### ' + str(kw_ids.id) + ' ###' + str(vals) + ' ### End_rec ### \n'
                    else:
                        new_created_record = project_project.create(vals)
                        new_record_log += ' ### Start_rec ### ' + str(new_created_record.id) + ' ###' + str(vals) + ' ### End_rec ### \n'
                # print("Successfully Done With Project Data : ", len(project_responce))
                # print("updated_kw_ids -->",updated_kw_ids)
                inactive_projects = valid_kw_id_projects.filtered(lambda r:r.kw_id not in updated_kw_ids)
                # print("inactive_projects -->",inactive_projects)
                inactive_projects.write({'active':False})
        except Exception as e:
            # print('Error occurs in Project : ', e)
            pass
        finally:
            # #enter data into log model
            synch_log = self.env['kw_kwantify_integration_log'].sudo()
            synch_log.create({'name': 'Kwantify Project Data',
                              'new_record_log': new_record_log,
                              'update_record_log': update_record_log,
                              'error_log': record_log,
                              'request_params': result['request_params_project'],
                              'response_result': result['project_result'] if 'project_result' in result else []})

            # #if any record.   delete last 15 days log record
            # synch_log.search([('create_date', '<=', (datetime.now() - relativedelta(weeks=+2)).strftime('%Y-%m-%d'))]).unlink()

    # # Project URL call and Update record Ends :-------

    # # Resource Tagging URL Call and update record Starts :-----
    def _ResponsefromKwantifyConfigResourceTagging(self, url, json_data):
        header = {'Content-type': 'application/json', }
        data = json.dumps(json_data)
        if url:
            resource_tagging_url = url + '/GetResourceTagging'

        request_params_resource = " Service Url : " + resource_tagging_url + " " + str(data)
        try:
            response_result = requests.post(resource_tagging_url, data=data, headers=header)
            resource_resp = json.loads(response_result.text)
            return {'status': 200, 'resource_result': resource_resp, 'request_params_resource': request_params_resource}
        except Exception as e:
            return {'status': 500, 'error_log': str(e), 'request_params_resource': request_params_resource}

    def _CreateUpdateResourceTaggingData(self, result):
        project_project = self.env['project.project'].sudo()
        resource_tagging = self.env['kw_project_resource_tagging'].sudo()
        record_log = result['error_log'] if 'error_log' in result else ''
        update_record_log = ''
        new_record_log = ''
        try:
            if result['status'] == 200 and result['resource_result']:
                resource_responce = result['resource_result']
                for resource_data in resource_responce:
                    user_data = self.env['hr.employee'].search(
                        [('kw_id', '=', int(resource_data['ResourceId'])), '|', ('active', '=', True),
                         ('active', '=', False)], limit=1)
                    project_data = project_project.search(
                        [('kw_id', '=', int(resource_data['ProjId'])), '|', ('active', '=', True),
                         ('active', '=', False)])

                    # kw_ids = resource_tagging.search(
                    #     [('kw_id', '=', int(resource_data['RoleId'])), '|', ('active', '=', True),
                    #      ('active', '=', False)], limit=1)
                    
                    if user_data and project_data:
                        vals = {
                            'project_id': project_data.id,
                            'emp_id': user_data.id,
                            'start_date': resource_data['InvolvedFrom'],
                            'end_date': resource_data['InvolvedTo'],
                            'active': True if resource_data['Status'] == '1' else False,
                            'kw_id': int(resource_data['RoleId'])
                        }
                        kw_ids = resource_tagging.search(
                            [('project_id', '=', project_data.id), ('emp_id', '=', user_data.id), '|',
                             ('active', '=', True),
                             ('active', '=', False)], limit=1)

                        if len(kw_ids):
                            # print("exist",resource_data)
                            kw_ids.write(vals)
                            update_record_log += ' ### Start_rec ### ' + str(kw_ids.id) + ' ###' + str(vals) + ' ### End_rec ### \n'
                        else:
                            # print("not exist",resource_data)
                            new_created_record = resource_tagging.create(vals)
                            new_record_log += ' ### Start_rec ### ' + str(new_created_record.id) + ' ###' + str(vals) + ' ### End_rec ### \n'
                # print("Successfully Done With Resource Tagging : ", len(resource_responce))
        except Exception as e:
            # print('Error occurs in Resource Tagging : ', e)
            pass
        finally:
            # #enter data into log model
            synch_log = self.env['kw_kwantify_integration_log'].sudo()
            synch_log.create({'name': 'Kwantify Resource Tagging Data',
                              'new_record_log': new_record_log,
                              'update_record_log': update_record_log,
                              'error_log': record_log,
                              'request_params': result['request_params_resource'],
                              'response_result': result['resource_result'] if 'resource_result' in result else []})

            # #if any record.   delete last 15 days log record
            # synch_log.search([('create_date', '<=', (datetime.now() - relativedelta(weeks=+2)).strftime('%Y-%m-%d'))]).unlink()

    # # Resource Tagging URL Call and update record Ends :-----

    # # Manage Resource Date and send mail Starts :-----
    def _ManageResourceDate(self):
        resource_tagging = self.env['kw_project_resource_tagging']
        try:
            # # Making Resources status 'False' whose end_date already crossed
            resources_datas = resource_tagging.search([('end_date', '<', date.today())])
            for resouce_date in resources_datas:
                resouce_date.write({'active': False})
            # Sending advanced 7,15,30 days reminder mail
            project_datas = self.env['project.project'].search([])
            template = self.env.ref("kw_project.kw_project_reminder_mail_template")
            for projects in project_datas:
                resource_records = projects.resource_id.filtered(
                    lambda rec: rec.end_date and rec.end_date == (date.today() + relativedelta(days=15)) or rec.end_date == (
                            date.today() + relativedelta(days=30)))
                if len(resource_records):
                    # self.env['mail.template'].browse(template.id).send_mail(projects.id)
                    template.send_mail(projects.id, notif_layout="kwantify_theme.csm_mail_notification_light")
                else:
                    pass
            # print("Successfully Done with Mail And Resource Active/Inactive.")
        except Exception as e:
            # print('Error occurs in Manage resource : ', e)
            pass
    # # Manage Resource Date and send mail Ends :-----
