
{
    "name": "Kwantify DMS Preview", 
    "summary": """File Preview Dialog""",
    "version": "1.0",
    "category": "Extra Tools",
    
    "contributors": [
       
    ],
    "depends": [
        "kw_dms_utils",
    ],
    "data": [
        "template/assets.xml",

        "template/image_preview/assets.xml",
        # "template/ms_office_preview/assets.xml",
        "template/open_document_preview/assets.xml",
        "template/csv_preview/assets.xml",        
        "template/markdown_preview/assets.xml", 
        "template/rst_preview/assets.xml",
        "template/text_preview/assets.xml",
        "template/video_preview/assets.xml",
        "template/audio_preview/assets.xml",

        # "views/res_config_settings_view.xml",
    ],
    "demo": [
    ],
    "qweb": [
        "static/src/xml/*.xml",
        "static/image_preview/src/xml/*.xml",
        # "static/ms_office_preview/src/xml/*.xml",
        "static/open_document_preview/src/xml/*.xml",
        "static/csv_preview/src/xml/*.xml",
        "static/markdown_preview/src/xml/*.xml",
        "static/rst_preview/src/xml/*.xml",
        "static/text_preview/src/xml/*.xml",
        "static/video_preview/src/xml/*.xml",
        "static/audio_preview/src/xml/*.xml",
    ],
    "images": [
        'static/description/banner.png'
    ],
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "application": False,
    "installable": True,
    
}
