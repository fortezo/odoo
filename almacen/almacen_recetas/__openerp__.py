# -*- coding: utf-8 -*-
{
    'name': "Recetas de Mamamia",

    'summary': "Manegador de Recetas",

    'description': "Manegador de Recetas",

    'author': "Fortezo",
    'website': "http://www.fortezo.com.mx",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'recetas_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}