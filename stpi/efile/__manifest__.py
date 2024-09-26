# -*- coding: utf-8 -*-
{
    'name': "Smart Office",

    'summary': """
            Smart Office
             """,

    'description': """
        Smart Office
    """,

    'author': "Sachin Burnawal",
    'website': "https://theerpstore.com/",
    'category': 'Smart Office',
    'version': '0.1',

    'depends': ['mail', 'muk_dms', 'muk_dms_actions', ],

    'data': [
        'data/data.xml',
        # 'views/load_ifrme_widget.xml',
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/doc_receive_type.xml',
        'data/dem_file.xml',
        # 'security/ir_rule.xml',
        'views/folder.xml',
        'wizard/filewizard.xml',
        'wizard/folderwizard.xml',
        'wizard/pull_into.xml',
        'wizard/pull_into_file.xml',
        'wizard/outgoing_letters.xml',
        'wizard/incoming_letters.xml',
        'wizard/create_folder_wizard.xml',
        'wizard/outgoing_files.xml',
        'wizard/incoming_files.xml',
        'wizard/assign_folder_wizard.xml',
        'wizard/file_exception_wizard_view.xml',
        'wizard/report_wizard.xml',
        'wizard/add_reference.xml',
        'wizard/write_correspondence.xml',
        'wizard/pull_into_my_inbox.xml',
        'wizard/pull_into_my_inbox_file.xml',
        'wizard/edit_doc_dispatch.xml',
        'wizard/edit_doc_dispatch_mode.xml',
        'wizard/send_back_file.xml',
        'wizard/send_back.xml',
        'views/department_job.xml',
        'views/file_tracking_information.xml',
        'views/add_letter.xml',
        'views/in_out_letter_view.xml',
        # 'views/letters_view.xml',
        'views/add_files.xml',

        'views/files_view.xml',
        'views/wizard.xml',
        'views/templates.xml',
        'views/master.xml',
        'views/see_file.xml',
        'views/file_exception.xml',
        'views/report.xml',
        'views/document_dispatch.xml',
        'report/dispatch_document.xml',

    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'demo': [
    ],
    # 'installable': True,
    'application': True,
}
