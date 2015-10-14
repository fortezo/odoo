# -*- coding: utf-8 -*-
{
    'name': "mamamia pedidos",

    'summary': "Control de pedidos",

    'description': "Control de pedidos",

    'author': "Fortezo",
    'website': "http://www.fortezo.com.mx",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account_voucher', 'procurement', 'report'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'pedido_view.xml',
        'folios.xml',
        'pedido_reporte.xml',
        'documentos/pedido.xml',
        'reportes_view.xml',
        'config.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}