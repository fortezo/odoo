# -*- coding: utf-8 -*-
{
    'name': "Clientes en el menu de TPV ",

    'summary': "Clientes en el menu de terminal de punto de ve tas",

    'description': "Clientes en el menu de terminal de punto de ve tas",

    'author': "Fortezo",
    'website': "http://www.fortezo.com.mx",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
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
}