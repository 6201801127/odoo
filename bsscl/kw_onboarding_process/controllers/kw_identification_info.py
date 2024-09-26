# -*- coding: utf-8 -*-
import base64, re

from odoo import http


class Identificationinfo:

    # #read work information data from DB
    def getIdentificationdetailsfromDB(self, enroll_data):
        idendict = {}
        if enroll_data:
            for record in enroll_data.identification_ids:
                for data in record:
                    if data.name == '1':
                        idendict['txtpan'] = data.doc_number
                        idendict['pandtdoi'] = data.date_of_issue.strftime('%d-%b-%Y') if data.date_of_issue else ""
                        idendict['pandtdoe'] = data.date_of_expiry.strftime('%d-%b-%Y') if data.date_of_expiry else ""
                        idendict['panddlrenewal'] = str(data.renewal_sts)
                        idendict['flpandocument'] = data.doc_number
                        idendict['panfilename'] = data.filename
                    if data.name == '2':
                        idendict['txtpassport'] = data.doc_number
                        idendict['passdtdoi'] = data.date_of_issue.strftime('%d-%b-%Y') if data.date_of_issue else ""
                        idendict['passdtdoe'] = data.date_of_expiry.strftime('%d-%b-%Y') if data.date_of_expiry else ""
                        idendict['passddlrenewal'] = str(data.renewal_sts)
                        idendict['flpassportdocument'] = data.uploaded_doc
                        idendict['passportfilename'] = data.filename
                    if data.name == '3':
                        idendict['txtdl'] = data.doc_number
                        idendict['dldtdoi'] = data.date_of_issue.strftime('%d-%b-%Y') if data.date_of_issue else ""
                        idendict['dldtdoe'] = data.date_of_expiry.strftime('%d-%b-%Y') if data.date_of_expiry else ""
                        idendict['dlddlrenewal'] = str(data.renewal_sts)
                        idendict['dlfldldocument'] = data.uploaded_doc
                        idendict['dlfilename'] = data.filename
                    if data.name == '4':
                        idendict['txtvoterid'] = data.doc_number
                        idendict['vdtdoi'] = data.date_of_issue.strftime('%d-%b-%Y') if data.date_of_issue else ""
                        idendict['vdtdoe'] = data.date_of_expiry.strftime('%d-%b-%Y') if data.date_of_expiry else ""
                        idendict['vddlrenewal'] = str(data.renewal_sts)
                        idendict['vflvoteriddocument'] = data.uploaded_doc
                        idendict['voterfilename'] = data.filename
                    if data.name == '5':
                        idendict['txtaadhaar'] = data.doc_number
                        idendict['adtdoi'] = data.date_of_issue.strftime('%d-%b-%Y') if data.date_of_issue else ""
                        idendict['adtdoe'] = data.date_of_expiry.strftime('%d-%b-%Y') if data.date_of_expiry else ""
                        idendict['addlrenewal'] = str(data.renewal_sts)
                        idendict['flaadhaardocument'] = data.uploaded_doc
                        idendict['aadhaarfilename'] = data.filename

        return idendict

    # save work information information to database
    def saveIdentificationInfo(self, enrollment_data, **kw):
        try:
            employee_data = {'identification_ids': []}
            indentification_db_data = []
            edited_identification_data = []
            posted_identification_info = []

            if enrollment_data.identification_ids:
                indentification_db_data = enrollment_data.identification_ids
                # print(indentification_db_data)
            # temp_data   = dict()

            if kw['txtpan'] != "":
                # pan details
                temp_data = dict()
                panfilename = kw['hiddenpanname']
                temp_data = {'name': '1',
                             'doc_number': kw['txtpan'],
                             'uploaded_doc': base64.encodestring(kw['flpandocument'].read()) if kw['flpandocument'] else '',
                             'filename': panfilename}

                posted_identification_info.append(temp_data)
                # for population data after error
                kw['panfilename'] = panfilename

            if kw['txtpassport'] != "":
                # passport details
                temp_data = dict()

                passrenewaldt = True if kw['passddlrenewal'] == "True" else False
                passfilename = kw['hiddenpasportname']

                if kw['passdtdoi']:
                    pass_dti_string = kw['passdtdoi']
                    sp_list = pass_dti_string.split("-")
                    pass_dti_new_string = f'{sp_list[2]}-{sp_list[1]}-{sp_list[0]}'

                if kw['passdtdoe']:
                    pass_dte_string = kw['passdtdoe']
                    sp_list = pass_dte_string.split("-")
                    pass_dte_new_string = f'{sp_list[2]}-{sp_list[1]}-{sp_list[0]}'
                    # 'date_of_issue': kw['passdtdoi'] kw['passdtdoe']

                temp_data = {'name': '2',
                             'doc_number': kw['txtpassport'],
                             'date_of_issue': pass_dti_new_string if kw['passdtdoi'] else None,
                             'date_of_expiry': pass_dte_new_string if kw['passdtdoe'] else None,
                             'renewal_sts': passrenewaldt,
                             'uploaded_doc': base64.encodestring(kw['flpassportdocument'].read()) if kw['flpassportdocument'] else '',
                             'filename': passfilename}

                posted_identification_info.append(temp_data)
                # for population data after error
                kw['passportfilename'] = passfilename

            if kw['txtdl'] != "":
                # Dl details
                temp_data = dict()
                dlrenewaldt = True if kw['dlddlrenewal'] == "True" else False
                dlfilename = kw['hiddendlname']

                if kw['dldtdoi']:
                    dl_dti_string = kw['dldtdoi']
                    sp_list = dl_dti_string.split("-")
                    dl_dti_new_string = f'{sp_list[2]}-{sp_list[1]}-{sp_list[0]}'

                if kw['dldtdoe']:
                    dl_dte_string = kw['dldtdoe']
                    sp_list = dl_dte_string.split("-")
                    dl_dte_new_string = f'{sp_list[2]}-{sp_list[1]}-{sp_list[0]}'
                    # 'date_of_issue': kw['dldtdoi'] kw['dldtdoe']

                temp_data = {'name': '3',
                             'doc_number': kw['txtdl'],
                             'date_of_issue': dl_dti_new_string if kw['dldtdoi'] else None,
                             'date_of_expiry': dl_dte_new_string if kw['dldtdoe'] else None,
                             'renewal_sts': dlrenewaldt,
                             # 'renewal_sts': dlrenewaldt,
                             'uploaded_doc': base64.encodestring(kw['dlfldldocument'].read()) if kw['dlfldldocument'] else '',
                             'filename': dlfilename}

                posted_identification_info.append(temp_data)
                kw['dlfilename'] = dlfilename

            if kw['txtvoterid'] != "":
                # voter details
                temp_data = dict()
                voterfilename = kw['hiddenvotername']
                temp_data = {'name': '4',
                             'doc_number': kw['txtvoterid'],
                             'uploaded_doc': base64.encodestring(kw['vflvoteriddocument'].read()) if kw['vflvoteriddocument'] else '',
                             'filename': voterfilename}

                posted_identification_info.append(temp_data)
                kw['voterfilename'] = voterfilename

            if kw['txtaadhaar'] != "":
                # aadhar details
                temp_data = dict()
                aadharfilename = kw['hiddenaadhaarname']
                temp_data = {'name': '5',
                             'doc_number': kw['txtaadhaar'],
                             'uploaded_doc': base64.encodestring(kw['flaadhaardocument'].read()) if kw['flaadhaardocument'] else '',
                             'filename': aadharfilename}

                posted_identification_info.append(temp_data)
                kw['aadhaarfilename'] = aadharfilename

            if len(posted_identification_info) > 0:
                for post_info in posted_identification_info:
                    # print(post_info)
                    if post_info['name']:
                        if post_info['uploaded_doc'] == b'':
                            del post_info['uploaded_doc']
                            del post_info['filename']

                        filtered_edit_data = enrollment_data.identification_ids.filtered(lambda r: r.name == post_info['name'])
                        
                        if filtered_edit_data:
                            employee_data['identification_ids'].append([1, filtered_edit_data.id, post_info])
                            edited_identification_data.append(filtered_edit_data.id)
                        else:
                            employee_data['identification_ids'].append([0, 0, post_info])
            # print(employee_data)

            if edited_identification_data:
                filtered_del_data = enrollment_data.identification_ids.filtered(lambda r: r.id not in edited_identification_data)
                if filtered_del_data:
                    for del_data in filtered_del_data:
                        employee_data['identification_ids'].append([2, del_data.id, False])

            if 'draft' not in kw:
                employee_data['state'] = '2'
                employee_data['create_full_profile'] = True

            # update the data in database
            enrollment_data.sudo().write(employee_data)

            # after saving into db, return data frm db
            resdata = self.getIdentificationdetailsfromDB(enrollment_data)
            resdata['success_msg'] = 'Identification details saved successfully'

            if 'draft' in kw:
                resdata['draft'] = kw['draft']
            return resdata

        except Exception as e:
            http.request._cr.rollback()
            kw['err_msg'] = str(e)
            return kw
