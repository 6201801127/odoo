{
    'name'      :'Training',
    'summary'   :"Training Plan Preparation.",
    'author'    :"PMIS Tech Team",
    'category'  :'training',
    'version'   :'14.0.0.1',

    'depends'   :['base','project'],

    'data':[
        'security/ir.model.access.csv',
        'views/training_views.xml',
        'views/category_views.xml',
        'views/menu_views.xml',
    ],

    'installable':True,
    'application':True,
}   