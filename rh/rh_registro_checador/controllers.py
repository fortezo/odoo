# -*- coding: utf-8 -*-
from openerp import http

# class MamamiaChecador(http.Controller):
#     @http.route('/mamamia_checador/mamamia_checador/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mamamia_checador/mamamia_checador/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mamamia_checador.listing', {
#             'root': '/mamamia_checador/mamamia_checador',
#             'objects': http.request.env['mamamia_checador.mamamia_checador'].search([]),
#         })

#     @http.route('/mamamia_checador/mamamia_checador/objects/<model("mamamia_checador.mamamia_checador"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mamamia_checador.object', {
#             'object': obj
#         })