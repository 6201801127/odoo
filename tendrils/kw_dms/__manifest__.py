{
    "name": "Kwantify DMS", 
    "summary": """Document Management System""",
    "version": '1.0',  
    "category": 'Document Management',    
    "depends": [
        
        "kw_dms_utils",
        "kw_web_searchpanel",
        "kw_dms_preview",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        # "actions/file.xml",
        "template/assets.xml",
        "template/onboarding.xml",
        "views/menu.xml",
        "views/tag.xml",
        "views/category.xml",
        "views/file.xml",
        "views/directory.xml",
        "views/storage.xml",
        "views/res_config_settings.xml",
        # 'views/directory_download.xml',

        ##security
        "views/access_groups.xml",

         ##dms Access security groups
        "views/dms_access/access_groups.xml",
        "views/dms_access/directory.xml",

        ##DMS Thumbnails
         "views/dms_thumbnail/storage.xml",
         "data/ir_cron.xml",

         ##DMS Versioning
         "views/dms_version/storage.xml",
         "views/dms_version/file.xml",

         ##Download log
        #  "views/dms_download_log/file_download_log.xml",
         "views/dms_download_log/directory.xml",
        #  "views/dms_download_log/directory_download_log.xml",

         ##DMS Tree View
          "views/dms_tree_view/documents.xml",
          "template/dms_tree_view/assets.xml",

          ##DMS Integration
        #   "views/dms_integration/directory.xml",
          "views/dms_integration/file.xml",
          "views/dms_integration/res_config_settings.xml",

          ##DMS Revision
          "views/dms_revision_history/file.xml",
          "views/dms_revision_history/storage.xml",

        ##default integration storages and groups
          "data/kwdms_integration_folder_data.xml",

        ##digi sign
        "views/dms_digi_esign/file.xml",

        ##public access
        "views/dms_public_access/file.xml",
         
         
    ],
    "demo": [
       
    ],
    "qweb": [
        "static/src/xml/*.xml",
        "static/src/xml/tree_view/*.xml",
        "static/src/xml/digi_sign/*.xml",
    ],
    "images": [
        'static/description/banner.png'
    ],
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "application": True,
    "installable": True,
    'auto_install': False,
    "post_load": "_patch_system",
}