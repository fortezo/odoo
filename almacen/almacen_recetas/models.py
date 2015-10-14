# -*- coding: utf-8 -*-
import time
from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import json
import openerp.addons.decimal_precision as dp

class recetas_recetas(osv.osv):
	_name = 'recetas.recetas'
	_description = 'Recetas de productos'
	_columns = {
	    'product_id': fields.many2one('product.template','Padre'),
	    'sub_product_id': fields.many2one('product.product','Sub-producto'),
	    'editable': fields.boolean('Editable'),
	    'cantidad':fields.float('Cantidad',),
		
	}
class recetas_esquema(osv.osv):
	_name = 'recetas.esquema'
	_description = 'Esquema de productos'
	_columns = {
	    'product_id': fields.many2one('product.product','Padre'),
	    'sub_product_id': fields.many2one('product.product','Hijo'),
		
	}
class recetas_aplicada(osv.osv):
	_name = 'recetas.pos.lines'
	_description = 'Recetas aplicada al TPV'
	_columns = {
	    'pos_order_line_id': fields.many2one('pos.order.line','Linea del TPV'),
	    'sub_product_id': fields.many2one('product.product','Sub-Producto'),
		
	}
class recetas_product_tipo(osv.osv):
	_name = 'recetas.product.tipo'
	_description = 'Tipo de productos para recetas'
	_columns = {
		'name': fields.char('Nombre'),
		'codigo': fields.char('Codigo'),
		
	}
class product_product(osv.osv):
	_name = 'product.template'
	_inherit = 'product.template'
	_columns = {
	    'recetas_product_tipo_id': fields.many2one('recetas.product.tipo','Tipo de productos para recetas'),
		'recetas_recetas_ids': fields.one2many('recetas.recetas','product_id','Receta'),
	}
class pos_order_line(osv.osv):
	#_name = 'pos.order.line'
	_inherit = 'pos.order.line'
	_columns = {
	    'recetas_aplicada_ids': fields.one2many('recetas.pos.lines','pos_order_line_id','Sub-Productos desc'),
	    'productos_ids': fields.one2many('pos.order.line','sub_pos_order_line_id','Sub-Productos'),
	    'sub_pos_order_line_id': fields.many2one('pos.order.line','Padre'),

	}
	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
        
		ctx = dict(context or {}, mail_create_nolog=True)
		ids = super(pos_order_line, self).create(cr, uid, vals, context=ctx)
        
		linea = self.pool.get('pos.order.line').browse(cr, uid, [ids], context=context)[0]

		sun_lines  = self.pool.get('pos.order.line')
		map_ids = self.pool.get('recetas.recetas').search(cr, uid,[('product_id', '=', linea.product_id.product_tmpl_id.id)])
		for map_ in self.pool.get('recetas.recetas').browse(cr, uid, map_ids, context=context):
			vals['product_id']=map_.sub_product_id.id
			vals['sub_pos_order_line_id']=ids
			vals['price_unit']=0
			sun_lines.create(cr, uid, vals, context=context)
			
		return ids