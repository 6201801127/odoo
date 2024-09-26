{
    "name": "PMIS Theme",
    "summary": "PMIS Theme",
    "category": "Theme/Backend",
	"description": """
		PMIS Theme
    """,
    "installable": True,
    "depends": [
        'web',
        'web_responsive',
        'pims_debranding',
        'auth_signup',
    ],
    "data": [
        'views/assets.xml',
		'views/res_company_view.xml',
		'views/users.xml',
        'views/login.xml',
    ],
}
