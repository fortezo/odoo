# -*- coding: utf-8 -*-
from openerp import http

# class MamamiaPedidos(http.Controller):
#     @http.route('/mamamia_pedidos/mamamia_pedidos/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mamamia_pedidos/mamamia_pedidos/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mamamia_pedidos.listing', {
#             'root': '/mamamia_pedidos/mamamia_pedidos',
#             'objects': http.request.env['mamamia_pedidos.mamamia_pedidos'].search([]),
#         })

#     @http.route('/mamamia_pedidos/mamamia_pedidos/objects/<model("mamamia_pedidos.mamamia_pedidos"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mamamia_pedidos.object', {
#             'object': obj
#         })