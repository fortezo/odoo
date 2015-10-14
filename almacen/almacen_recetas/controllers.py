# -*- coding: utf-8 -*-
from openerp import http

# class MamamiaRecetas(http.Controller):
#     @http.route('/mamamia_recetas/mamamia_recetas/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mamamia_recetas/mamamia_recetas/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mamamia_recetas.listing', {
#             'root': '/mamamia_recetas/mamamia_recetas',
#             'objects': http.request.env['mamamia_recetas.mamamia_recetas'].search([]),
#         })

#     @http.route('/mamamia_recetas/mamamia_recetas/objects/<model("mamamia_recetas.mamamia_recetas"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mamamia_recetas.object', {
#             'object': obj
#         })