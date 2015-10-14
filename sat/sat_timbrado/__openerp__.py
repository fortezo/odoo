# -*- coding: utf-8 -*-
{
    'name': "Timbrado de fortezo",

    'summary': "Modulo de timbrado de fortezo",

    'description': "Modulo de timbrado de fortezo",

    'author': "Fortezo",
    'website': "http://www.fortezo.com.mx",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'PAQ',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
    'installable': True,
    'auto_install': False,

}
