{
    'name': 'Arduino Controller',
    'version': '1.0',
    'category': 'hardware',
    'author': 'ItOpen',
    'description': 'Control Arduino from OpenERP',
    'website': 'http://www.itopen.it',
    'depends': ['base'],
    'data' : [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'arduinocontroller_views.xml',
    ],
    'external_dependencies' : {
            'python': ['pyfirmata']
    },
    'active': False,
    'installable': True,
}
