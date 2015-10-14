# -*- coding: utf-8 -*-
from openerp import http

# class FacturaGlobal(http.Controller):
#     @http.route('/factura_global/factura_global/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/factura_global/factura_global/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('factura_global.listing', {
#             'root': '/factura_global/factura_global',
#             'objects': http.request.env['factura_global.factura_global'].search([]),
#         })

#     @http.route('/factura_global/factura_global/objects/<model("factura_global.factura_global"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('factura_global.object', {
#             'object': obj
#         })