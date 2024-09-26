from odoo import fields,models#,api

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

    cancelled_by = fields.Char(string='Cancelled By')
    cancelled_by_dept = fields.Char(string='Cancelled Dept.')
    cancelled_by_jobpos = fields.Char(string='Cancelled Designation')
    cancelled_by_branch = fields.Char(string='Cancelled Branch')
    cancelled_date = fields.Date(string='Cancelled Date')

    rejected_by = fields.Char(string='Rejected By')
    rejected_by_dept = fields.Char(string='Rejected Dept.')
    rejected_by_jobpos = fields.Char(string='Rejected Designation')
    rejected_by_branch = fields.Char(string='Rejected Branch')
    rejected_date = fields.Date(string='Rejected Date')

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

    put_in_shelf_user = fields.Char(string='Put in Shelf User')
    put_in_shelf_dept = fields.Char(string='Put in Shelf Dept.')
    put_in_shelf_job_pos = fields.Char(string='Put in Shelf Designation')
    put_in_shelf_branch = fields.Char(string='Put in Shelf Branch')
    put_in_shelf_date = fields.Date(string='Put in Shelf Date')

    transferred_from = fields.Char(string='transferred From)')
    transferred_from_dept = fields.Char(string='transferred Dept.')
    transferred_from_jobpos = fields.Char(string='transferred Designation')
    transferred_from_branch = fields.Char(string='transferred Branch')

    transferred_by = fields.Char(string='transferred From')
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
                                     ('pulled_from_shelf',"Pulled from Shelf"),
                                     ('put_in_shelf','Put File in Departmental Shelf'),
                                     ('put_in_own_shelf','Put File in Own Shelf'),
                                     ('file_created', 'File Created'),
                                     ('correspondence_forwarded', 'Correspondence Forwarded'),
                                     ('file_forwarded', 'File Forwarded'),
                                     ('correspondence_transferred', 'Correspondence Transferred'),
                                     ('file_transferred', 'File Transferred'),
                                     ('correspondence_pulled', 'Correspondence Pulled'),
                                     ('file_pulled', 'File Pulled'),
                                     ('assigned_to_file', 'Assigned To File'),

                                     ('submit_file_close', 'File Close Submitted'),
                                     ('cancel_file_close', 'File Close Cancelled'),
                                     ('file_closed', 'File Close Approved'),
                                     ('file_close_reject', 'File Close Rejected'),

                                     ('submit_file_repoen', 'File Reopen Submitted'),
                                     ('cancel_file_repoen', 'File Reopen Cancelled'),
                                     ('file_repoened', 'File Reopen Approved'),
                                     ('file_repoen_reject', 'File Reopen Rejected'),

                                     ('correspondence_send_bank', 'Correspondence Sent Back'),
                                     ('file_send_bank', 'File Sent Back'),
                                     ], string='Action Taken')