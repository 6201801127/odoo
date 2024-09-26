from odoo import fields,api,models


class FileTracker(models.Model):
    _name="file.tracker.report"
    _description="File Tracking Report"

    name = fields.Char(string='Name')
    number = fields.Char(string='Number')
    type = fields.Char(string='Type')


    created_by = fields.Char(string='Created By')
    created_by_dept = fields.Char(string='Create Department')
    created_by_jobpos = fields.Char(string='Create Designation')
    created_by_branch = fields.Char(string='Create Branch')
    create_date = fields.Date(string='Create Date')



    assigned_by = fields.Char(string='Asgn. By')
    assigned_by_dept = fields.Char(string='Asgn. Dept.')
    assigned_by_jobpos = fields.Char(string='Asgn. Designation')
    assigned_by_branch = fields.Char(string='Asgn. Branch')
    assigned_date = fields.Date(string='Asgn. Date')




    closed_by = fields.Char(string='Closed By')
    closed_by_dept = fields.Char(string='Closed Dept.')
    closed_by_jobpos = fields.Char(string='Closed Designation')
    closed_by_branch = fields.Char(string='Closed Branch')
    close_date = fields.Date(string='Closed Date')



    repoen_by = fields.Char(string='Reopen By')
    repoen_by_dept = fields.Char(string='Reopen Dept.')
    repoen_by_jobpos = fields.Char(string='Reopen Designation')
    repoen_by_branch = fields.Char(string='Reopen Branch')
    repoen_date = fields.Date(string='Reopen Date')



    forwarded_by = fields.Char(string='Fwd. By')
    forwarded_by_dept = fields.Char(string='Fwd. Dept.')
    forwarded_by_jobpos = fields.Char(string='Fwd. Designation')
    forwarded_by_branch = fields.Char(string='Fwd. Branch')


    forwarded_date = fields.Date(string='Fwd. Date')

    forwarded_to_user = fields.Char(string='Fwd. To')
    forwarded_to_dept = fields.Char(string='Fwd. To Dept.')
    job_pos = fields.Char(string='Fwd. to Designation')
    forwarded_to_branch = fields.Char(string='Fwd. To Branch')


    pulled_by = fields.Char(string='Pulled From)')
    pulled_by_dept = fields.Char(string='Pulled Dept.')
    pulled_by_jobpos = fields.Char(string='Pulled Designation')
    pulled_by_branch = fields.Char(string='Pulled Branch')


    pulled_date = fields.Date(string='Pulled Date')

    pulled_to_user = fields.Char(string='Pulled To User')
    pulled_to_dept = fields.Char(string='Pulled To Dept.')
    pulled_to_job_pos = fields.Char(string='Pulled to Designation')
    pulled_to_branch = fields.Char(string='Pulled To Branch')



    transferred_from = fields.Char(string='transferred From)')
    transferred_from_dept = fields.Char(string='transferred Dept.')
    transferred_from_jobpos = fields.Char(string='transferred Designation')
    transferred_from_branch = fields.Char(string='transferred Branch')

    transferred_by = fields.Char(string='transferred From)')
    transferred_by_dept = fields.Char(string='transferred Dept.')
    transferred_by_jobpos = fields.Char(string='transferred Designation')
    transferred_by_branch = fields.Char(string='transferred Branch')

    transferred_date = fields.Date(string='transferred Date')

    transferred_to_user = fields.Char(string='transferred To User')
    transferred_to_dept = fields.Char(string='transferred To Dept.')
    transferred_to_job_pos = fields.Char(string='transferred to Designation')
    transferred_to_branch = fields.Char(string='transferred To Branch')



    remarks = fields.Char(string='Remarks')
    details = fields.Char(string='Details')
    action_taken = fields.Selection([('correspondence_created', 'Correspondence Created'),
                                     ('file_created', 'File Creates'),
                                     ('correspondence_forwarded', 'Correspondence Forwarded'),
                                     ('file_forwarded', 'File Forwarded'),
                                     ('correspondence_transferred', 'Correspondence Transferred'),
                                     ('file_transferred', 'File Transferred'),
                                     ('correspondence_pulled', 'Correspondence Pulled'),
                                     ('file_pulled', 'File Pulled'),
                                     ('assigned_to_file', 'Assigned To File'),
                                     ('file_closed', 'File Closed'),
                                     ('file_repoened', 'File Reopened'),
                                     ], string='Action Taken')