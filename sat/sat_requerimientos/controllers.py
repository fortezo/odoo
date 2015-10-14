# -*- coding: utf-8 -*-
from openerp import http

# class SatFacturacion(http.Controller):
#     @http.route('/sat_facturacion/sat_facturacion/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sat_facturacion/sat_facturacion/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sat_facturacion.listing', {
#             'root': '/sat_facturacion/sat_facturacion',
#             'objects': http.request.env['sat_facturacion.sat_facturacion'].search([]),
#         })

#     @http.route('/sat_facturacion/sat_facturacion/objects/<model("sat_facturacion.sat_facturacion"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sat_facturacion.object', {
#             'object': obj
#         })