# -*- coding: utf-8 -*-
import requests, json
import logging
from datetime import date
from odoo import models, fields, api,_
from pathlib import Path
from odoo.exceptions import ValidationError


class JobPositionsSync(models.Model):
    _inherit = "kw_hr_job_positions"

    file_path = Path(r'/home/localadmin/odoo-dev/odoo/kwantify-odoo/kw_career_sync/static/src/log/log.txt')
    
    def prepar_data(self,job_lists):
        payload = {"method": "syncJobOpenings", "data": []}
        for job in job_lists:
            payload["data"].append({
                "id": job.id,
                "title": job.title if job.title else "",
                "location": [loc.id for loc in job.address_id] if job.address_id else [],
                "department_id": job.department_id.id if job.department_id else "",
                "code": job.job_code if job.job_code else "",
                "description": job.description if job.description else "",
                "publish_date": str(job.job_publish_date) if job.job_publish_date else "",
                "publish_status": 1 if job.website_published else 0,
                "expiration": str(job.expiration) if job.expiration else "",
                "no_of_post": job.no_of_recruitment if job.no_of_recruitment else "",
                "qualification": [qual.id for qual in job.qualification] if job.qualification else [],
                "min_exp_year": job.min_exp_year if job.min_exp_year else 0,
                "max_exp_year": job.max_exp_year if job.max_exp_year else 0,
                "job_category": job.emp_category_id.id if job.emp_category_id else "",
                "industry_type": job.industry_type.id if job.industry_type else "",
                "travel": 1 if job.travel else 0,
                "summary": job.summary if job.summary else "",
                "candidate_profile": job.candidate_profile if job.candidate_profile else "",
                "job_image": job.attachment_url if job.attachment else "",
                "set_homepage": 1 if job.on_homepage else 0,
                "walk_in": job.walk_in and 1 or 0,
                "campus_drive": job.campus_drive and 1 or 0,
                "hide_in_website": job.hide_in_website and 1 or 0,
            })
        return payload
    
    def prepar_usa_data(self,job_lists):
        # payload = {"method": "syncJobOpenings", "data": []}
        qualification = self.env['kw_qualification_master'].search([])
        jobdata ={}
        payload = []
        master_data =  [{"id": qual.id, "name": qual.name,
                                             "code": qual.code if qual.code else "",
                                             "sequence": qual.sequence if qual.sequence else "",
                                             "campus_drive": qual.campus_drive and 1 or 0} for qual in qualification]
        for job in job_lists:
            payload.append({
                "jobid": job.id if job.id else "",
                "code": job.job_code if job.job_code else "",
                "designation": job.title if job.title else "",
                "vacancies": job.no_of_recruitment if job.no_of_recruitment else "",
                "experienceFrom": job.min_exp_year if job.min_exp_year else 0,
                "experienceTo": job.max_exp_year if job.max_exp_year else 0,
                "candidateProfile": job.candidate_profile if job.candidate_profile else "",
                "jobDescription": job.description if job.description else "",
                "qualification": ','.join([str(qual.id) for qual in job.qualification]) if job.qualification else [],
                "qualification_name": ','.join([str(qual.name) for qual in job.qualification]) if job.qualification else [],
                "jobstartDate": str(job.job_publish_date.date()) if job.job_publish_date else "",
                "joblastDate": str(job.expiration) if job.expiration else "",
                "jobSnippet": job.summary if job.summary else "",
                "PublishStatus": 1 if job.website_published else 0,
                "job_location_name": ','.join([str(loc.name) for loc in job.address_id]) if job.address_id else [],
                "job_location_id": ','.join([str(loc.id) for loc in job.address_id]) if job.address_id else [],
            })
        jobdata = {"jobdata":payload if payload else [],"us_qualification_master":master_data}
        return jobdata
    

    @api.model
    def sync_job_lists(self):
        # print('sync_ job lis called')
        curr_date = date.today()
        job_lists = self.env["kw_hr_job_positions"].search(
            ['&', ("website_published", "=", True), ("expiration", '>=', curr_date)])
        if len(job_lists) >= 0:
            global_opening = job_lists.filtered(lambda x: x.opening_for == 'global') if job_lists else []
            america_opening = job_lists.filtered(lambda x: x.opening_for == 'america') if job_lists else []
            africa_opening = job_lists.filtered(lambda x: x.opening_for == 'africa') if job_lists else []
            log = self.env["kw_recruitment_career_sync_log"].sudo()
            
            # payload = self.prepar_data(job_lists)
            # nested if elif condition for sync
            if len(global_opening)>=0 or len(africa_opening)>=0:
                payload = self.prepar_data(global_opening)
                data = json.dumps(payload)
                try:
                    res = log.create({
                        "name": "Global Job Sync",
                        "payload": data,
                        'status': 'Initiated'
                    })
                    # print(f"Prepared payload inside job opening sync is {payload}")
                    url = self.env["ir.config_parameter"].sudo().get_param("kw_recruitment_career_sync_system_parameter")
                    # print("URL is", url)
                    if not url:
                        console_api_url = self.env["ir.config_parameter"].sudo().get_param("kwantify_console_service_api_url")
                        # url = "http://192.168.103.229/CSM/api/consoleServices"
                        url = console_api_url
                    
                    key = self.env["ir.config_parameter"].sudo().get_param("kw_auth.enable_sync_logging")
                    if key == 'True':
                        self.log_file(self.file_path, 'Global Job List Sync', url, payload)

                    # response_obj = requests.post(url, headers={"Content-Type": "application/json"}, data=data, timeout=30)
                    response_obj = requests.post(url, headers={"Content-Type": "application/json"}, data=data, timeout=30)
                    content = response_obj.content
                    # print("Content is ",content)
                    resp = json.loads(content.decode("utf-8"))

                    # print(f"Response after request GLOBAL to sync job opening {resp}")
                    if resp['status'] == '200':
                        res.write({
                            'status': 'Success'
                        })
                        # print("Job opening sync Successful.")
                        self.env.user.notify_success(message='Sync successful.')
                except Exception as e:
                    # print("Error : no response from career server", e)
                    res.write({
                        'status': 'Failed'
                    })
                    self.env.user.notify_info(message=f'An error occurred while Global job opening sync.{e}')
            if len(america_opening) >=0:
                payload = self.prepar_usa_data(america_opening)
                data = json.dumps(payload)
                try:
                    res = log.create({
                        "name": "American Job Sync",
                        "payload": data,
                        'status': 'Initiated'
                    })
                    print(f"Prepared payload inside america job opening sync is {payload}")
                    url = self.env["ir.config_parameter"].sudo().get_param("kw_recruitment_career_sync_america_system_parameter")
                    # print("URL is====================", url)
                    if not url:
                        console_api_url = self.env["ir.config_parameter"].sudo().get_param("kwantify_console_service_api_url")
                        # url = "http://192.168.103.229/CSM/api/consoleServices"
                        url = console_api_url
                    
                    key = self.env["ir.config_parameter"].sudo().get_param("kw_auth.enable_sync_logging")
                    if key == 'True':
                        self.log_file(self.file_path, 'American Job List Sync', url, payload)
                    # print("in log file--------------------------")
                    # response_obj = requests.post(url, headers={"Content-Type": "application/json"}, data=data, timeout=30)
                    response_obj = requests.post(url, headers={"Content-Type": "application/json"}, data=data, timeout=30)
                    content = response_obj.content
                    resp = json.loads(content.decode("utf-8"))

                    # print(f"Response after request to USA sync job opening {resp}")
                    if resp['status'] == '200':
                        res.write({
                            'status': 'Success'
                        })
                        self.env.user.notify_success(message='Sync successful.')
                except Exception as e:
                    # print("Error : no response from career server", e)
                    res.write({
                        'status': 'Failed'
                    })
                    self.env.user.notify_info(message=f'An error occurred while American job opening sync.{e}')
        else:
            self.env.user.notify_info(message='No jobs found to sync.')
        
            
    @api.model
    def sync_job_master(self):
        location = self.env["kw_recruitment_location"].search([])
        qualification = self.env['kw_qualification_master'].search([])
        job_category = self.env['kw_job_category'].search([])
        industry_type = self.env['kw_industry_type'].search([])
        skill_data = self.env['kw_skill_master'].search([])
        institute_data = self.env['res.partner'].search([('institute', '=', True)])

        payload = {"method": "syncJobMasterData",
                   "data": {"location": [], "qualification": [], "job_category": [], "industry_type": [], "skill": [],
                            "institute": []}}
        payload["data"]["location"] = [{"id": loc.id, "name": loc.name} for loc in location]
        payload["data"]["qualification"] = [{"id": qual.id, "name": qual.name,
                                             "code": qual.code if qual.code else "",
                                             "sequence": qual.sequence if qual.sequence else "",
                                             "campus_drive": qual.campus_drive and 1 or 0} for qual in qualification]
        payload["data"]["job_category"] = [{"id": job.id, "name": job.name} for job in job_category]
        payload["data"]["industry_type"] = [{"id": ind.id, "name": ind.name} for ind in industry_type]
        payload["data"]["skill"] = [{"id": skill.id, "name": skill.name} for skill in skill_data]
        payload["data"]["institute"] = [{"id": inst.id, "name": inst.name} for inst in institute_data]

        log = self.env["kw_recruitment_career_sync_log"].sudo()
        data = json.dumps(payload)
        # us_data = json.dumps(payload["data"]["qualification"])
        res = log.create({
            "name": "Master Sync",
            "payload": data,
            'status': "Initiated",
        })
        # print("Prepared payload is", data)
        # for gloabal
        try:
            url = self.env["ir.config_parameter"].sudo().get_param("kw_recruitment_career_sync_system_parameter")
            if not url:
                console_api_url = self.env["ir.config_parameter"].sudo().get_param("kwantify_console_service_api_url")
                # url = "http://192.168.103.229/CSM/api/consoleServices"
                url = console_api_url
            
            key = self.env["ir.config_parameter"].sudo().get_param("kw_auth.enable_sync_logging")
            if key == 'True':
                self.log_file(self.file_path,'Master Sync',url,payload)
            # print("URL is",url)
            # print("URL is",url)
            response_obj = requests.post(url, headers={"Content-Type": "application/json"}, data=data, timeout=30)
            # print("response obj is",response_obj)
            content = response_obj.content
            # print("Content is ", content)
            resp = json.loads(content.decode("utf-8"))
            # print(f"Response after request to sync job master{resp}")
            if resp['status'] == '200':
                res.write({
                    'status': "Success",
                })
                # print("Sync Successful.")
                self.env.user.notify_success(message='Master sync successful.')
        except Exception as e:
            # print("Error : no response from career server", e)
            res.write({
                'status': "Failed",
            })
            self.env.user.notify_info(message='An error occurred while master sync.')
            self.env.user.notify_info(message=f'An error occurred while master sync.{e}')
        
        # except Exception as e:
        #     # print("Error : no response from career server", e)
        #     res.write({
        #         'status': "Failed",
        #     })
        #     self.env.user.notify_info(message='An error occurred while USA master sync.')
            #     self.env.user.notify_info(message=f'An error occurred while USA master sync.{e}')

    def log_file(self, fname, name, payload, URL):
        with open(fname, "a") as myfile:
            myfile.write("------------------------------------------\n")
            myfile.write(f"Name : {name}\n")
            myfile.write(f"URL : {URL}\n")
            myfile.write(f"Payload : {payload}\n")
            myfile.write("------------------------------------------\n")

        txt = open(fname)
        # print(txt.read())
