from odoo import models, fields, api
import json, requests
from datetime import datetime,timedelta



class KwPortletSync(models.Model):
    _name = 'kw_sync_portlet_data'
    _description = "Model used for syncing Portlet Debtor And Opportunity data with Kwantify"
    _rec_name = 'model_id'
    _order = 'id desc'

    model_id = fields.Char(string="Model Name")
    rec_id = fields.Integer(string="Record ID")
    json_data = fields.Text('Json Data')
    response = fields.Text('Response')
    status = fields.Integer(string="Status")



    def action_button_sync_record_opp_debt(self,active_record_id):
        current_rec_id = active_record_id if isinstance(active_record_id, int) else active_record_id['id']
        check_sync_data = self.env['kw_sync_portlet_data'].sudo().search([('id', '=',current_rec_id),('status', '=', '0')])
        if check_sync_data:
            header = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            employees = self.env['hr.employee'].sudo().search([])
            check_model_opp = check_sync_data.filtered(lambda x : x.model_id == 'kw_opp_port')
            check_model_debtor = check_sync_data.filtered(lambda x : x.model_id == 'kw_debtor_list_master')
            check_model_billing = check_sync_data.filtered(lambda x : x.model_id == 'kw_billing_dashboard_port')
            url = self.env['ir.config_parameter'].sudo().search([('key','=','URL for Sales Portlet Data Sync')]).value
            if check_model_opp:
                opportunityurl = url+'/UpdateActiveOppExpWo'
                for opp in check_model_opp:
                    opportunity_sync = {}
                    opportunity_data = []
                    opp_data = self.env['kw_opp_port'].search([('id', '=', opp.rec_id)])
                    modified_employee = employees.filtered(lambda emp: emp.user_id.id == opp_data.write_uid.id if opp_data.write_uid.id else None)
                    opportunity_sync['Int_Opp_ID'] = opp_data.opp_id if opp_data.opp_id else 0
                    opportunity_sync['Dtm_Exp_WoDate'] = opp_data.expected_closing_date.strftime('%Y-%m-%d') if opp_data.expected_closing_date else None
                    opportunity_sync['UpDateBy'] = modified_employee.kw_id if modified_employee else 0
                    # opportunity_sync['LastModifiedDateTime'] = opp_data.user_last_modified_date.strftime('%Y-%m-%d %H:%M:%S') if opp_data.user_last_modified_date else None
                    opportunity_data.append(opportunity_sync)
                    resp = requests.post(opportunityurl, headers=header, data=json.dumps(opportunity_data))
                    j_data = json.dumps(resp.json())
                    json_record = json.loads(j_data)

                    result = {'json_data':opportunity_data,'response':resp.text}
                    if json_record['status'] == 1:
                        result.update({'status':1})
                    elif json_record['status'] == 2:
                        result.update({'status':2})
                    elif json_record['status'] == 3:
                        result.update({'status':3})

                    opp.write(result)

            if check_model_debtor:
                debtorurl = url+'/Update_Invoice_Coll_SheduleDtls'
                for debt in check_model_debtor:
                    debtor_sync = {}
                    debtor_data = []
                    debt_data = self.env['kw_debtor_list_master'].search([('id', '=', debt.rec_id)])
                    modified_employee = employees.filtered(lambda emp: emp.user_id.id == debt_data.write_uid.id if debt_data.write_uid.id else None)
                    debtor_sync['Int_Inv_ID'] = debt_data.kw_invoice_id if debt_data.kw_invoice_id else 0
                    debtor_sync['Dtm_Coll_SheduleDate'] = debt_data.expected_date.strftime('%Y-%m-%d') if debt_data.expected_date else None
                    debtor_sync['UpdateBy'] = modified_employee.kw_id if modified_employee else 0
                    debtor_sync['Inv_Type'] = debt_data.invoice_type
                    # debtor_sync['LastModifiedDateTime'] = debt_data.user_last_modified_date.strftime('%Y-%m-%d %H:%M:%S') if debt_data.user_last_modified_date else None
                    debtor_data.append(debtor_sync)
                    resp = requests.post(debtorurl, headers=header, data=json.dumps(debtor_data))
                    j_data = json.dumps(resp.json())
                    json_record = json.loads(j_data)

                    result = {'json_data':debtor_data,'response':resp.text}
                    if json_record['status'] == 1:
                        result.update({'status':1})
                    elif json_record['status'] == 2:
                        result.update({'status':2})
                    elif json_record['status'] == 3:
                        result.update({'status':3})

                    debt.write(result)

            if check_model_billing:
                billingurl = url+'/UpdateBillingTarget'
                for bill in check_model_billing:
                    billing_sync = {}
                    billing_data = []
                    bill_data = self.env['kw_billing_dashboard_port'].search([('id', '=', bill.rec_id)])
                    modified_employee = employees.filtered(lambda emp: emp.user_id.id == bill_data.write_uid.id if bill_data.write_uid.id else None)
                    billing_sync['int_kw_milestoneid'] = bill_data.kw_milestone_id if bill_data.kw_milestone_id else 0
                    billing_sync['BillingTargetDate'] = bill_data.billing_target_date.strftime('%Y-%m-%d') if bill_data.billing_target_date else None
                    billing_sync['UpdateBy'] = modified_employee.kw_id if modified_employee else 0
                    billing_data.append(billing_sync)
                    resp = requests.post(billingurl, headers=header, data=json.dumps(billing_data))
                    j_data = json.dumps(resp.json())
                    json_record = json.loads(j_data)

                    result = {'json_data':billing_data,'response':resp.text}
                    if json_record['status'] == 1:
                        result.update({'status':1})
                    elif json_record['status'] == 2:
                        result.update({'status':2})
                    elif json_record['status'] == 3:
                        result.update({'status':3})

                    bill.write(result)


















    def FetchV5Data(self):
        # DEBTOR DATA SYNC
        last_updated_on = (datetime.now() + timedelta(hours=5, minutes=30)).strftime('%d-%b-%Y %I:%M %p')
        next_execution_time = (self.env['ir.cron'].sudo().search([('cron_name','=','Sales || SEND Tendrils Portlet Data')]).nextcall + timedelta(hours=5, minutes=30)).strftime('%d-%b-%Y %I:%M %p')
        employees = self.env['hr.employee'].sudo().search([])
        projects = self.env['project.project'].sudo().search([])
        debtor_url = self.env['ir.config_parameter'].sudo().search([]).filtered(lambda x: x.key == 'URL for Sales Portlet Data Sync').value + '/GetInvCollSheduleDetails' 
        debt_header = {'Content-type': 'application/json', 'Accept': 'text/plain', }
        debt_request = requests.post(debtor_url, headers=debt_header)
        debtor_data = json.loads(debt_request.text)

        debtor_ids = self.env['kw_debtor_list_master'].search(['|',('active','=',True),('active','=',False)]).mapped('kw_invoice_id')
        debt_create_query = "INSERT INTO kw_debtor_list_master(active,bad_debtor_provision_amt,kw_invoice_id, wo_code, invoice_no, invoice_date, invoice_amt, pending_amt, expected_date, wo_id, acc_manager_id, invoice_type,updated_by ,account_manager_name, csg, client_address, client_name,reviewer_id,teamleader_id,last_updated_on,next_execution_time) VALUES (True,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,  %s,  %s, %s, %s, %s, %s, %s, %s, %s);"
        debt_update_query = """UPDATE kw_debtor_list_master SET active=True,bad_debtor_provision_amt=%s,wo_code = %s,invoice_no = %s,invoice_date = %s,invoice_amt = %s,pending_amt = %s,expected_date = %s,wo_id = %s,acc_manager_id = %s,invoice_type = %s,updated_by = %s,account_manager_name = %s,csg = %s,client_address = %s,client_name = %s,reviewer_id = %s,teamleader_id = %s,last_updated_on = %s,next_execution_time=%s WHERE kw_invoice_id = %s"""

        debt_create_params = []
        debt_update_params = []
        debt_lst = []
        
        if debtor_data:
            for rec in debtor_data:
                dtm_inv_date = datetime.strptime(rec['Dtm_Inv_Date'], '%m/%d/%Y %I:%M:%S %p').strftime('%Y-%m-%d') if rec['Dtm_Inv_Date'] else None
                dtm_coll_sheduleDate = rec['Dtm_Coll_SheduleDate'] if rec['Dtm_Coll_SheduleDate'] else None 
                acc_manager_id = employees.filtered(lambda x: x.kw_id == int(rec['Int_kw_EmpID'])) if (rec['Int_kw_EmpID'] and not (int(rec['Int_kw_EmpID']) is None) and (int(rec['Int_kw_EmpID'])) != 0) else False
                reviewer_id = employees.filtered(lambda x: x.kw_id == int(rec['Int_kw_EmpID_Reviewer'])) if (rec['Int_kw_EmpID_Reviewer'] and not (int(rec['Int_kw_EmpID_Reviewer']) is None) and (int(rec['Int_kw_EmpID_Reviewer'])) != 0) else False
                teamleader_id = employees.filtered(lambda x: x.kw_id == int(rec['Int_kw_EmpID_TeamLeader'])) if (rec['Int_kw_EmpID_TeamLeader'] and not (int(rec['Int_kw_EmpID_TeamLeader']) is None) and (int(rec['Int_kw_EmpID_TeamLeader'])) != 0) else False
                if rec['Int_Inv_ID'] not in debtor_ids:
                    debt_create_params.append((rec['Dec_Bad_DebtorProvision'],rec['Int_Inv_ID'], rec['Vch_Wo_Code'], rec['Vch_Inv_No'], dtm_inv_date, rec['Dec_Inv_Amt'], rec['Dec_Inv_Pending_Amt'], dtm_coll_sheduleDate, rec['Int_Wo_ID'],acc_manager_id.id if acc_manager_id else None, rec['Inv_Type'],rec['UpdateBy'], rec['Vch_Acc_Mngr'], rec['Vch_CSG'], rec['Vch_ClientAddress'], rec['Vch_Client_Name'], reviewer_id.id if reviewer_id else None, teamleader_id.id if teamleader_id else None,last_updated_on ,next_execution_time if next_execution_time else None))
                else:
                    debt_update_params.append((rec['Dec_Bad_DebtorProvision'],rec['Vch_Wo_Code'], rec['Vch_Inv_No'], dtm_inv_date, rec['Dec_Inv_Amt'], rec['Dec_Inv_Pending_Amt'], dtm_coll_sheduleDate, rec['Int_Wo_ID'],acc_manager_id.id if acc_manager_id else None, rec['Inv_Type'],rec['UpdateBy'], rec['Vch_Acc_Mngr'], rec['Vch_CSG'], rec['Vch_ClientAddress'], rec['Vch_Client_Name'],  reviewer_id.id if reviewer_id else None, teamleader_id.id if teamleader_id else None,last_updated_on,next_execution_time if next_execution_time else None, rec['Int_Inv_ID']))

                debt_lst.append(rec['Int_Inv_ID'])
                

        if debt_create_params:
            self.env.cr.executemany(debt_create_query, debt_create_params)
        if debt_update_params:
            self.env.cr.executemany(debt_update_query, debt_update_params)


        debt_tuple = tuple(debt_lst)
        self.env.cr.execute(f"update kw_debtor_list_master set active = False where kw_invoice_id not in {debt_tuple}")


        # OPPORTUNITY DATA SYNC
        opp_url = self.env['ir.config_parameter'].sudo().search([]).filtered(lambda x: x.key == 'URL for Sales Portlet Data Sync').value + '/GetActiveOppDetails'
        opp_header = {'Content-type': 'application/json', 'Accept': 'text/plain', }
        opp_request = requests.post(opp_url, headers=opp_header)
        opp_data = json.loads(opp_request.text)

        opp_ids = self.env['kw_opp_port'].search(['|',('active','=',True),('active','=',False)]).mapped('opp_id')
        opp_create_query = "INSERT INTO kw_opp_port(active,pac_status,opp_id ,opp_code, client_name,client_short_name, opp_name, a_manager, expected_closing_date,opp_val,acc_manager_id,updated_by,csg,client_address,reviewer_id,teamleader_id,last_updated_on,next_execution_time) VALUES (True,%s,%s, %s, %s, %s, %s,%s,%s, %s, %s, %s, %s, %s, %s, %s, %s,%s);"
        opp_update_query = """UPDATE kw_opp_port SET active=True,pac_status = %s,opp_code = %s,client_name = %s,client_short_name = %s,opp_name = %s,a_manager = %s,expected_closing_date = %s,opp_val = %s,acc_manager_id = %s,updated_by = %s,csg = %s,client_address = %s,reviewer_id = %s,teamleader_id = %s,last_updated_on=%s,next_execution_time=%s WHERE opp_id = %s"""
        
        opp_create_params = []
        opp_update_params = []
        opp_lst = []
        
        
        if opp_data:
            for rec in opp_data:
                dtm_exp_wodate = rec['Dtm_Exp_WoDate'] if rec['Dtm_Exp_WoDate'] else None
                acc_manager_id = employees.filtered(lambda x: x.kw_id == int(rec['Int_kw_EmpID'])) if (rec['Int_kw_EmpID'] and not (int(rec['Int_kw_EmpID']) is None) and (int(rec['Int_kw_EmpID'])) != 0) else False
                reviewer_id = employees.filtered(lambda x: x.kw_id == int(rec['Int_kw_EmpID_Reviewer'])) if (rec['Int_kw_EmpID_Reviewer'] and not (int(rec['Int_kw_EmpID_Reviewer']) is None) and (int(rec['Int_kw_EmpID_Reviewer'])) != 0) else False
                teamleader_id = employees.filtered(lambda x: x.kw_id == int(rec['Int_kw_EmpID_TeamLeader'])) if (rec['Int_kw_EmpID_TeamLeader'] and not (int(rec['Int_kw_EmpID_TeamLeader']) is None) and (int(rec['Int_kw_EmpID_TeamLeader'])) != 0) else False
                if rec['Int_Opp_ID'] not in opp_ids:
                    opp_create_params.append((rec['Vch_Pac_Status'],rec['Int_Opp_ID'], rec['Vch_Opp_Code'], rec['Vch_ClientName'], rec['VchClientShortName'],rec['Vch_Opp_Name'], rec['Vch_Acc_Mngr'], dtm_exp_wodate,rec['Dec_Opp_Value'], acc_manager_id.id if acc_manager_id else None,rec['UpDateBy'],rec['Vch_CSG'], rec['Vch_ClientAddress'], reviewer_id.id if reviewer_id else None, teamleader_id.id if teamleader_id else None,last_updated_on,next_execution_time if next_execution_time else None))
                else:
                    opp_update_params.append((rec['Vch_Pac_Status'],rec['Vch_Opp_Code'], rec['Vch_ClientName'],rec['VchClientShortName'], rec['Vch_Opp_Name'], rec['Vch_Acc_Mngr'], dtm_exp_wodate, rec['Dec_Opp_Value'],acc_manager_id.id if acc_manager_id else None, rec['UpDateBy'], rec['Vch_CSG'], rec['Vch_ClientAddress'],reviewer_id.id if reviewer_id else None, teamleader_id.id if teamleader_id else None,last_updated_on,next_execution_time if next_execution_time else None,rec['Int_Opp_ID']))

                opp_lst.append(rec['Int_Opp_ID'])

        if opp_create_params:
            self.env.cr.executemany(opp_create_query, opp_create_params)
        if opp_update_params:
            self.env.cr.executemany(opp_update_query, opp_update_params)
        opp_tuple = tuple(opp_lst)
        self.env.cr.execute(f"update kw_opp_port set active = False where opp_id not in {opp_tuple}")





        # BILLING DATA SYNC
        billing_url = self.env['ir.config_parameter'].sudo().search([]).filtered(lambda x: x.key == 'URL for Sales Portlet Data Sync').value + '/GetActiveMileStoneDetails'
        billing_header = {'Content-type': 'application/json', 'Accept': 'text/plain', }
        billing_request = requests.post(billing_url, headers=billing_header)
        billing_data = json.loads(billing_request.text)

        billing_milestone_ids = self.env['kw_billing_dashboard_port'].search(['|',('active','=',True),('active','=',False)]).mapped('kw_milestone_id')
        billing_create_query = "INSERT INTO kw_billing_dashboard_port(active,sbu_name, wo_code, wo_name, billing_amount, milestone_details, billing_plan_date, collection_plan_date, billing_target_date, kw_milestone_id, project_id, project_manager_id,account_leader_id,account_manager_id,reviewer_id,sbu_head_id,updated_by,last_updated_on,next_execution_time) VALUES (True,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        billing_update_query = """UPDATE kw_billing_dashboard_port SET active=True, sbu_name = %s,wo_code = %s,wo_name = %s,billing_amount = %s,milestone_details = %s,billing_plan_date = %s,collection_plan_date = %s,billing_target_date=%s,project_id = %s,project_manager_id = %s,account_leader_id=%s,account_manager_id=%s,reviewer_id=%s,sbu_head_id=%s,updated_by = %s,last_updated_on= %s, next_execution_time=%s WHERE kw_milestone_id = %s"""

        billing_create_params = []
        billing_update_params = []
        milestone_lst = []

        if billing_data:
            for rec in billing_data:
                billing_plan_date = rec['Dtm_Billing_PnDate'] if rec['Dtm_Billing_PnDate'] else None
                collection_plan_date = rec['Dtm_MileStone_Date'] if rec['Dtm_MileStone_Date'] else None 
                billing_target_date = rec['Dtm_Billing_TargetDate'] if rec['Dtm_Billing_TargetDate'] else None 
                project_manager_id = employees.filtered(lambda x: x.kw_id == int(rec['Int_Pm_kw_ID'])) if (rec['Int_Pm_kw_ID'] and not (int(rec['Int_Pm_kw_ID']) is None) and (int(rec['Int_Pm_kw_ID'])) != 0) else False
                account_leader_id = employees.filtered(lambda x: x.kw_id == int(rec['Int_AccLeader_kw_ID'])) if (rec['Int_AccLeader_kw_ID'] and not (int(rec['Int_AccLeader_kw_ID']) is None) and (int(rec['Int_AccLeader_kw_ID'])) != 0) else False
                account_manager_id = employees.filtered(lambda x: x.kw_id == int(rec['Int_AccMngr_kw_ID'])) if (rec['Int_AccMngr_kw_ID'] and not (int(rec['Int_AccMngr_kw_ID']) is None) and (int(rec['Int_AccMngr_kw_ID'])) != 0) else False
                reviewer_id = employees.filtered(lambda x: x.kw_id == int(rec['int_reviewer_id'])) if (rec['int_reviewer_id'] and not (int(rec['int_reviewer_id']) is None) and (int(rec['int_reviewer_id'])) != 0) else False
                sbu_head_id = employees.filtered(lambda x: x.kw_id == int(rec['int_sbu_head_id'])) if (rec['int_sbu_head_id'] and not (int(rec['int_sbu_head_id']) is None) and (int(rec['int_sbu_head_id'])) != 0) else False
                project_id = projects.filtered(lambda x : x.kw_id == int(rec['Int_Project_Id'])) if (rec['Int_Project_Id'] and not (int(rec['Int_Project_Id']) is None) and (int(rec['Int_Project_Id'])) != 0) else None
                if rec['Int_MileStone_ID'] not in billing_milestone_ids:
                    billing_create_params.append((rec['Vch_Sbu_Name'], rec['Vch_WOCode_Code'], rec['Vch_Wo_Name'], rec['dec_MileStone_Amt'], rec['Vch_MileStone_Details'], billing_plan_date,collection_plan_date,billing_target_date, rec['Int_MileStone_ID'],project_id.id if project_id else None,  project_manager_id.id if project_manager_id else None ,account_leader_id.id if account_leader_id else None,account_manager_id.id if account_manager_id else None,reviewer_id.id if reviewer_id else None ,sbu_head_id.id if sbu_head_id else None ,rec['UpDateBy'],last_updated_on,next_execution_time if next_execution_time else None))
                else:
                    billing_update_params.append((rec['Vch_Sbu_Name'], rec['Vch_WOCode_Code'], rec['Vch_Wo_Name'], rec['dec_MileStone_Amt'], rec['Vch_MileStone_Details'], billing_plan_date,collection_plan_date,billing_target_date, project_id.id if project_id else None,  project_manager_id.id if project_manager_id else None ,account_leader_id.id if account_leader_id else None,account_manager_id.id if account_manager_id else None,reviewer_id.id if reviewer_id else None ,sbu_head_id.id if sbu_head_id else None ,rec['UpDateBy'],last_updated_on,next_execution_time if next_execution_time else None,rec['Int_MileStone_ID']))
                    
                milestone_lst.append(rec['Int_MileStone_ID'])
                
        if billing_create_params:
            self.env.cr.executemany(billing_create_query, billing_create_params)
        if billing_update_params:
            self.env.cr.executemany(billing_update_query, billing_update_params)
        milestone_tuple = tuple(milestone_lst)
        self.env.cr.execute(f"update kw_billing_dashboard_port set active= False where kw_milestone_id not in {milestone_tuple}")
        












class KwPortletRecieved(models.Model):
    _name = 'kw_portlet_recieved_log'
    _order = 'id DESC'
    _rec_name = 'rec_id'

    rec_type = fields.Char('Type')
    rec_id = fields.Integer('Record ID')
    changed_date = fields.Date("Changed Opp/Debt/Bill Date")
    status = fields.Integer('Status')
    updated_by = fields.Many2one('hr.employee',string='Updated By')



    def update_recieved_data_in_model(self):
        recieved_data = self.env['kw_portlet_recieved_log'].search([('status','=',0)])
        opp_records = recieved_data.filtered(lambda x : x.rec_type == 'opp')
        debt_records = recieved_data.filtered(lambda x : x.rec_type == 'deb')
        bill_records = recieved_data.filtered(lambda x : x.rec_type == 'bill')
        opp_update_query = """UPDATE kw_opp_port SET expected_closing_date = %s WHERE opp_id = %s"""
        debt_update_query = """UPDATE kw_debtor_list_master SET expected_date = %s WHERE kw_invoice_id = %s"""
        bill_update_query = """UPDATE kw_billing_dashboard_port SET billing_target_date = %s WHERE kw_milestone_id = %s"""

        opp_update_params,debt_update_params,bill_update_params = [],[],[]

        if opp_records:
            for rec in opp_records:
                opp_update_params.append((rec.changed_date,rec.rec_id))
        if debt_records:
            for rec in debt_records:
                debt_update_params.append((rec.changed_date,rec.rec_id))
        if bill_records:
            for rec in bill_records:
                bill_update_params.append((rec.changed_date,rec.rec_id))

        if opp_update_params:
            self.env.cr.executemany(opp_update_query, opp_update_params)
            opp_records.write({'status':1})
        if debt_update_params:
            self.env.cr.executemany(debt_update_query, debt_update_params)
            debt_records.write({'status':1})
        if bill_update_params:
            self.env.cr.executemany(bill_update_query, bill_update_params)
            bill_records.write({'status':1})
            



