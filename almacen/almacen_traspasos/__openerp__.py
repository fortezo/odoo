# -*- coding: utf-8 -*-
{
    'name': "Traspasos",

    'summary': "Traspasos entre almacenes",

    'description': """
        Traspasos entre almacenes
    """,

    'author': "Fortezo",
    'website': "http://www.fortezo.com.mx",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','sales_team','account_voucher', 'procurement', 'report'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'traspasos_view.xml',
        'traspaso_report.xml',
        'views/traspaso.xml',
        'folios.xml',
        'traspasos_data.xml',
        'traspasos_configuraciones.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}