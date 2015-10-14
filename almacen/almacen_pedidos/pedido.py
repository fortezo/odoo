# -*- coding: utf-8 -*-
import time
from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import json
import openerp.addons.decimal_precision as dp

class pedido_orden(osv.osv):
	_name = 'pedido.orden'
	_description = 'Pedido'
	_inherit = ['mail.thread', 'ir.needaction_mixin']
	_order = 'fecha desc, id desc'


	def _amount_line_all(self, cr, uid, ids, field_names, arg, context=None):
		ordenes = self.browse(cr, uid, ids, context=context)
		res = dict([(i, {}) for i in ids])
		total = 0
		for order in ordenes:
			for detalles_object in order.detalles_ids:
				total = total+detalles_object.unitario*detalles_object.cantidad_solisitada
			res[order.id]['total'] = total
		return res
	
	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
        

		ctx = dict(context or {}, mail_create_nolog=True)
		ids = super(pedido_orden, self).create(cr, uid, vals, context=ctx)
        
		
		total = 0.0
		ordenes = self.browse(cr, uid, [ids], context=context)
		detalles = self.pool.get('pedido.orden.detalles',False)
		for order in ordenes:
			#config_finf = self.pool.get('pedido.configuraciones').search(cr, uid,[('company_id', '=', order.enpresa_envio_id.id)])[0]
			#config = self.pool.get('pedido.configuraciones').browse(cr, uid, config_finf, context=context)
			
			for detalles_object in order.detalles_ids:
				total = total+detalles_object.importe
				detalles.write(cr, uid, [detalles_object.id],{
					'company_id':order.company_id.id,
					'categoria_id':detalles_object.product_id.pos_categ_id.id,
					'importe':(detalles_object.product_id.list_price*detalles_object.cantidad_solisitada),
					'unitario':detalles_object.product_id.list_price
					}, context=context)
			self.write(cr, uid, [ids], {'total': total,'ordenado_user_id':uid,'fecha_ordenado':time.strftime("%Y-%m-%d %H:%M:%S")}, context=context)
		for order in self.browse(cr, uid, [ids], context=context):
				plantillas_ids = self.pool.get('pedido.plantilla').search(cr, uid,[('company_id', '=', order.company_id.id)])
				for plantilla in self.pool.get('pedido.plantilla').browse(cr, uid, plantillas_ids, context=context):
					self.pool.get('pedido.orden.detalles').create(cr, uid, 
						{'company_id':order.company_id.id,
						'pedido_id': order.id,
						'product_id': plantilla.product_id.id,
						'cantidad_solisitada':0,
						'plantilla_id':plantilla.id,
						'unitario':plantilla.product_id.list_price,
						'cantidad_surtida':0}, context=context)
        
		return ids
	_columns = {
		'name': fields.char('Folio'),
	    'fecha': fields.datetime('Fecha del documento',readonly=True),
	    'company_id': fields.many2one('res.company','Sucursal',readonly=True),
	    'user_id': fields.many2one('res.users','Responsable',readonly=True),
	    'state': fields.selection([('borrador', 'Borrador'),('ordenado', 'Ordenado'),('enproceso','En produccion'),('enviado', 'Enviado'),('recivido', 'Recibido'),('cancelado', 'Cancelado')], 'Status', copy=False),
	    
	    'fecha_ordenado': fields.datetime('Fecha orden',readonly=True),
	    'fecha_produccion': fields.datetime('Fecha produccin',readonly=True),
	    'fecha_enviado': fields.datetime('Fecha envio',readonly=True),
	    'fecha_recivido': fields.datetime('Fecha recibo',readonly=True),
	    
	    'ordenado_user_id': fields.many2one('res.users','Ordeno',readonly=True),
	    'produccion_user_id': fields.many2one('res.users','Producio',readonly=True),
	    'enviado_user_id': fields.many2one('res.users','Envio',readonly=True),
	    'recivido_user_id': fields.many2one('res.users','Recibió',readonly=True),

	    'detalles_ids': fields.one2many('pedido.orden.detalles','pedido_id','Productos del pedido'),
	    'notas': fields.html('Notas',),
        'total': fields.function(_amount_line_all, multi='pedido_orden_total', digits_compute=dp.get_precision('Product Price'), string='Total del Pedido', store=True),

	}
	_defaults = {
	    'state':'borrador',
	    'fecha':fields.datetime.now,
		'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
	    'user_id':lambda obj, cr, uid, context: uid,
	}
	def ordenar(self, cr, uid, ids, context=None):
		for order in self.browse(cr, uid, ids, context=context):
			self.pool.get('pedido.orden.detalles').write(cr, uid, [line.id for line in order.detalles_ids], {'state':'ordenado'}, context=context)
			
		#	for producto in self.pool.get('product.product').search(cr, uid,[('company_id', '=', order.company_id.id)]):
		#		self.pool.get('pedido.orden.detalles').create(cr, uid, {'company_id':order.company_id'pedido_id': pedido_id.id,'product_id': producto.id,'cantidad_solisitada':0,'cantidad_surtida':0}, context=context)
		
		folio = self.pool.get('ir.sequence').get(cr, uid, 'pedido.orden') or '/'
		return self.write(cr, uid, ids, {'name':folio,'state': 'ordenado','ordenado_user_id':uid,'fecha_ordenado':time.strftime("%Y-%m-%d %H:%M:%S")}, context=context)
	
	def enviar(self, cr, uid, ids, context=None):
		for order in self.browse(cr, uid, ids, context=context):
			self.pool.get('pedido.orden.detalles').write(cr, uid, [line.id for line in order.detalles_ids], {'state':'enviado'}, context=context)
		return self.write(cr, uid, ids, {'state': 'enviado','enviado_user_id':uid,'fecha_enviado':time.strftime("%Y-%m-%d %H:%M:%S")}, context=context)
	def produccion(self, cr, uid, ids, context=None):
		for order in self.browse(cr, uid, ids, context=context):
			self.pool.get('pedido.orden.detalles').write(cr, uid, [line.id for line in order.detalles_ids], {'state':'enproceso'}, context=context)
		return self.write(cr, uid, ids, {'state': 'enproceso','produccion_user_id':uid,'fecha_produccion':time.strftime("%Y-%m-%d %H:%M:%S")}, context=context)
	
	def recivir(self, cr, uid, ids, context=None):

		

		for order in self.browse(cr, uid, ids, context=context):
			self.pool.get('pedido.orden.detalles').write(cr, uid, [line.id for line in order.detalles_ids], {'state':'recivido'}, context=context)
		self.write(cr, uid, ids, {'state': 'recivido','recivido_user_id':uid,'fecha_recivido':time.strftime("%Y-%m-%d %H:%M:%S")}, context=context)
		self.create_picking_out(cr, uid, ids, context=context)
		return True
	def cancelar(self, cr, uid, ids, context=None):
		return self.write(cr, uid, ids, {'state': 'cancelado'}, context=context)
		
	def create_picking_out(self, cr, uid, ids, context=None):
		"""Create a picking for each order and validate it."""
		picking_obj = self.pool.get('stock.picking')
		partner_obj = self.pool.get('res.partner')
		move_obj = self.pool.get('stock.move')
		
		for order in self.browse(cr, uid, ids, context=context):
			config_finf = self.pool.get('pedido.configuraciones').search(cr, uid,[('company_id', '=', order.company_id.id)])
			if(len(config_finf)==0):
				raise osv.except_osv('Error!', 'No hay una operacion configurada')
			config = self.pool.get('pedido.configuraciones').browse(cr, uid, config_finf[0], context=context)
			
			addr = order.user_id.partner_id and partner_obj.address_get(cr, uid, [order.user_id.partner_id.id], ['delivery']) or {}
			picking_type = False
			picking_id = False
			picking_id = picking_obj.create(cr, uid, {
					'origin': order.name,
					'partner_id': addr.get('delivery',False),
					'date_done' : order.fecha_recivido,
			 		'picking_type_id': config.picking_type_id.id,
					'company_id': order.company_id.id,
					'move_type': 'direct',
					'note': order.notas or "",
					'invoice_state': 'none',
				}, context=context)
			self.write(cr, uid, [order.id], {'picking_id': picking_id}, context=context)
			
			src_id =config.picking_type_id.default_location_src_id.id
			destination_id = config.picking_type_id.default_location_dest_id.id
			
			move_list = []
			for line in order.detalles_ids:
				if line.product_id and line.product_id.type == 'service':
					continue

				move_list.append(move_obj.create(cr, uid, {
					'name': order.id,
					'product_uom': line.product_id.uom_id.id,
					'product_uos': line.product_id.uom_id.id,
					'picking_id': picking_id,
					'picking_type_id': config.picking_type_id.id,
					'product_id': line.product_id.id,
					'product_uos_qty': abs(line.cantidad_surtida),
					'product_uom_qty': abs(line.cantidad_surtida),
					'state': 'draft',
					'location_id': src_id if line.cantidad_surtida >= 0 else destination_id,
					'location_dest_id': destination_id if line.cantidad_surtida >= 0 else src_id,
				}, context=context))
                
			
				print 'action_confirm'
				picking_obj.action_confirm(cr, uid, [picking_id], context=context)
				print 'force_assign'
				picking_obj.force_assign(cr, uid, [picking_id], context=context)
				print 'action_done'
				picking_obj.action_done(cr, uid, [picking_id], context=context)
			
				print 'action_confirm'
				#move_obj.action_confirm(cr, uid, move_list, context=context)
				print 'force_assign'
				#move_obj.force_assign(cr, uid, move_list, context=context)
				print 'action_done'
				#move_obj.action_done(cr, uid, move_list, context=context)
		return True
class pedido_configuraciones(osv.osv):
	_name = 'pedido.configuraciones'
	_description = 'Configuracion de Pedidos'
	_columns = {
	    'company_id': fields.many2one('res.company','Sucursal'),
	    'picking_type_id': fields.many2one('stock.picking.type','Operacion'),
        'users_id': fields.many2one('res.users', 'Encargado'),

	}
class pedido_orden_detalles(osv.osv):
	_name = 'pedido.orden.detalles'
	_order = 'fecha desc, id desc'
	_description = 'Producto de pedidos'
	def onchange_qty(self, cr, uid, ids, product, cantidad, context=None):
		result = {}
		prod = self.pool.get('product.product').browse(cr, uid, product, context=context)
		result['importe'] = (prod.list_price*cantidad)
		result['cantidad_solisitada']=cantidad
		for detalle in self.pool.get('pedido.orden.detalles').browse(cr, uid, ids, context=context):
			#valida la configuracion de multiplos
			if (detalle.plantilla_id.multriplos!=0):
				res_float = (cantidad/detalle.plantilla_id.multriplos)
				res_int = int(cantidad/detalle.plantilla_id.multriplos)
				if(res_float!=res_int):
					result['cantidad_solisitada'] = 0
			#validacion para afectar a terceros
			if (detalle.plantilla_id.afectara_id!=False):
				obj_detalles = self.pool.get('pedido.orden.detalles')
				terseros_id = obj_detalles.search(cr, uid,[('product_id', '=', detalle.plantilla_id.afectara_id.id)])
				result_canridad = (detalle.plantilla_id.afectara_cantidad*cantidad)
				obj_detalles.write(cr, uid, terseros_id, {'importe': result['importe'],'cantidad_solisitada':result_canridad}, context=context)
			
					#raise osv.except_osv('Error!', 'Solo multiplos de: '+str(detalle.plantilla_id.multriplos))
					

		self.write(cr, uid, ids, {'importe': result['importe'],'cantidad_solisitada':cantidad}, context=context)
		return {'value': result}
	def onchange_product_id(self, cr, uid, ids, product_id, cantidad=0, context=None):
		result = {}
		prod = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
		result['importe'] = (prod.list_price*cantidad)
		result['unitario'] = prod.list_price
		self.write(cr, uid, ids, {'importe': result['importe'],'categoria_id':prod.pos_categ_id.id}, context=context)
		return {'value': result}
	def _amount_line_all(self, cr, uid, ids, field_names, arg, context=None):
		res = dict([(i, {}) for i in ids])
		for line in self.browse(cr, uid, ids, context=context):
			res[line.id]['importe'] = line.unitario*line.cantidad_solisitada
		return res
	_columns = {
		'company_id': fields.many2one('res.company','Sucursal'),
        'pedido_id': fields.many2one('pedido.orden','Pedido'),
        'product_id': fields.many2one('product.product', 'Producto',readonly=True),
        'plantilla_id': fields.many2one('pedido.plantilla', 'Plantilla',readonly=True),
        'cantidad_solisitada':fields.float('Cantidad Solisitada'),
        'cantidad_surtida':fields.float('Cantidad Surtida'),
        'categoria_id': fields.many2one('pos.category','Categoria',),
        'fecha': fields.datetime('Fecha',readonly=True),
        'importe': fields.function(_amount_line_all, multi='traspasos_documento_productos_total', digits_compute=dp.get_precision('Product Price'), string='Importe', store=True),

        'unitario':fields.float('Precio'),
        'state': fields.selection([('borrador', 'Borrador'),('ordenado', 'Ordenado'),('enproceso','En produccion'),('enviado', 'Enviado'),('recivido', 'Recibido'),('cancelado', 'Cancelado')], 'Status', readonly=True, copy=False),
	}
	_defaults = {
	    'state':'borrador',
	    'fecha':fields.datetime.now,
	}
class pedido_plantilla(osv.osv):
	_name = 'pedido.plantilla'
	_description = 'plantilla de productos para pedidos'
	_columns = {
		'company_id': fields.many2one('res.company','Sucursal'),
		'product_id': fields.many2one('product.product', 'Producto'),
		'multriplos':fields.float('Solo multiplos de'),
		'afectara_id': fields.many2one('product.product', 'Afectar a otro producto'),
		'afectara_cantidad':fields.float('Afectar Cantidad',help='la regla debe multiplicar las cantidades del sub-producto que se colocaron en el producto principal', ),
	
	}