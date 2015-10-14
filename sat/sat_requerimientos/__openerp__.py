# -*- coding: utf-8 -*-
{
    'name': "Sat Mexico",

    'summary': "Modulo de requerimientos del sat",

    'description': "Modulo de requerimientos del sat",

    'author': "Fortezo",
    'website': "http://www.fortezo.com.mx",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account_voucher'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'templates.xml',
        'views/report_invoice.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}