# -*- coding: utf-8 -*-
import time
from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import json
import openerp.addons.decimal_precision as dp

class traspasos_documento(osv.osv):
	_name = 'traspasos.documento'
	_description = 'Ordenen de Traspaso'
	_inherit = ['mail.thread', 'ir.needaction_mixin']
	_order = 'fecha desc, id desc'
	_track = {
        'state': {
            'traspasos.mt_traspaso_enviado': lambda self, cr, uid, obj, ctx=None: obj.state in ['sent'],
            'traspasos.mt_traspaso_canceladoa': lambda self, cr, uid, obj, ctx=None: obj.state in ['cancel'],
        },'traspasos.mt_traspaso_recibida': lambda self, cr, uid, obj, ctx=None: obj.state in ['recibe'],
    }
	def _user_company_id(self, cr, uid, ids, field_names, arg, context=None):
		ordenes = self.browse(cr, uid, ids, context=context)
		res = dict([(i, {}) for i in ids])
		

		for order in ordenes:
			user = self.pool.get('res.users',False).browse(cr, uid, uid, context=context)[0]
			res[order.id]['user_company_id.id'] = user.company_id.id
			print '-----------------------'
			print user.company_id.id
		return res
	def filter_user_company_id(self, cr, uid, ids, field_names, arg, context=None):
		#ordenes = self.browse(cr, uid, ids, context=context)
		res = dict([(i, {}) for i in [uid]])
		

		user = self.pool.get('res.users',False).browse(cr, uid, uid, context=context)[0]
		res[uid]['user_company_id.id'] = user.company_id.id
		print '-----------------------'
		print user.company_id.id
		return res
	def _sendto_company_id(self, cr, uid, ids, field_names, arg, context=None):
		ordenes = self.browse(cr, uid, ids, context=context)
		res = dict([(i, {}) for i in ids])
		

		for order in ordenes:
			res[order.id]['sendto_company_id.id'] = order.enpresa_resivir_id.id
		return res
	def filtro_sendto_company_id(self, cr, uid, ids, field_names, arg, context=None):
		print '----------'
		print context
		ordenes = self.browse(cr, uid, ids, context=context)
		res = dict([(i, {}) for i in ids])
		

		for order in ordenes:
			res[order.id]['sendto_company_id.id'] = order.enpresa_resivir_id.id
		return res

	def _amount_line_all(self, cr, uid, ids, field_names, arg, context=None):
		ordenes = self.browse(cr, uid, ids, context=context)
		res = dict([(i, {}) for i in ids])
		total = 0
		for order in ordenes:
			for detalles_object in order.order_line:
				total = total+detalles_object.unitario*detalles_object.cantidad
			res[order.id]['total'] = total
		return res
	_columns = {
		'name': fields.char('Documento',copy=False),
	    'enpresa_envio_id': fields.many2one('res.company','Emisor', readonly=True),
	    'partner_id': fields.many2one('res.partner','Receptor',readonly=True, states={'draft': [('readonly', False)]}),
        'enpresa_resivir_id': fields.many2one('res.company','Empresa Receptora',readonly=True, states={'draft': [('readonly', False)]}),
        'envio_id': fields.many2one('res.users', 'Envio',copy=False, readonly=True),
        'envioa_id': fields.many2one('res.users', 'Enviado a',readonly=True, states={'draft': [('readonly', False)]}),
        'envio_fecha': fields.datetime('Fecha de envio',copy=False, readonly=True),
        'fecha': fields.datetime('Fecha del documento',copy=False, readonly=True),
        'recivo_fecha': fields.datetime('Fecha de recibo',copy=False, readonly=True),
        'notas': fields.html('Notas',copy=False,readonly=True, states={'draft': [('readonly', False)]}),
        'order_line': fields.one2many('traspasos.documento.productos', 'docunemto_id', 'Productos del traspaso', readonly=True, states={'draft': [('readonly', False)]}, copy=True),
        #'total':fields.float('Total del Traspaso', readonly=True),
        'total': fields.function(_amount_line_all, multi='traspasos_documento_total', digits_compute=dp.get_precision('Product Price'), string='Total del Traspaso', store=True),

        'ubicacion_destino_id': fields.many2one('stock.location','Localidad Destino',readonly=True, states={'sent': [('readonly', False)]},domain=[('usage', '=', 'internal')]),
        'user_company_id': fields.function(_user_company_id,type='integer', method=True,string='company user', store=False,fnct_search=filter_user_company_id),
        'sendto_company_id': fields.function(_sendto_company_id,type='integer', method=True,string='company sen to', store=False,fnct_search=filtro_sendto_company_id),
        
		'state': fields.selection([
            ('draft', 'Borrador'),
            ('sent', 'Enviada'),
            ('cancel', 'Cancelada'),
            ('recibe', 'Recibida')
            ], 'Status', readonly=True, copy=False),

	}
        
	_defaults = {
		'state':'draft',
		'fecha':fields.datetime.now,
		'enpresa_envio_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }
	
		
	def enviar(self, cr, uid, ids, context=None):

		self.create_picking_out(cr, uid, ids, context=context)

		total = 0.0
		ordenes = self.browse(cr, uid, ids, context=context)
		detalles = self.pool.get('traspasos.documento.productos',False)
		for order in ordenes:
			config_finf = self.pool.get('traspasos.configuraciones').search(cr, uid,[('company_id', '=', order.enpresa_envio_id.id)])[0]
			config = self.pool.get('traspasos.configuraciones').browse(cr, uid, config_finf, context=context)
			
			for detalles_object in order.order_line:
				total = total+detalles_object.importe
				detalles.write(cr, uid, [detalles_object.id],{
					'state':'sent',
					'enpresa_envio_id':order.enpresa_envio_id.id,
					'enpresa_resivir_id':order.partner_id.company_id.id,
					'categoria_id':detalles_object.product_id.pos_categ_id.id,
					'importe':(detalles_object.product_id.list_price*detalles_object.cantidad),
					'unitario':detalles_object.product_id.list_price
					}, context=context)
			
		self.write(cr, uid, ids, {'total': total,'enpresa_resivir_id':order.partner_id.company_id.id,'envio_id':config.users_id.id}, context=context)

		folio = self.pool.get('ir.sequence').get(cr, uid, 'traspasos.documento') or '/'
		return self.write(cr, uid, ids, {'name':folio,'state': 'sent','envio_id':uid,'envio_fecha':time.strftime("%Y-%m-%d %H:%M:%S")}, context=context)
	def recivir(self, cr, uid, ids, context=None):
		for order in self.browse(cr, uid, ids, context=context):
			self.pool.get('traspasos.documento.productos').write(cr, uid, [line.id for line in order.order_line], {'state':'recibe'}, context=context)
		return self.write(cr, uid, ids, {'state': 'recibe','envioa_id':uid,'recivo_fecha':time.strftime("%Y-%m-%d %H:%M:%S")}, context=context)
	
	def cancelar(self, cr, uid, ids, context=None):
		for order in self.browse(cr, uid, ids, context=context):
			self.pool.get('traspasos.documento.productos').write(cr, uid, [line.id for line in order.order_line], {'state':'cancel'}, context=context)
		return self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
	
	def create_picking_out(self, cr, uid, ids, context=None):
		"""Create a picking for each order and validate it."""
		picking_obj = self.pool.get('stock.picking')
		partner_obj = self.pool.get('res.partner')
		move_obj = self.pool.get('stock.move')
		
		for order in self.browse(cr, uid, ids, context=context):
			config_finf = self.pool.get('traspasos.configuraciones').search(cr, uid,[('company_id', '=', order.enpresa_envio_id.id)])[0]
			print order.enpresa_envio_id.id
			config = self.pool.get('traspasos.configuraciones').browse(cr, uid, config_finf, context=context)
			
			addr = order.partner_id and partner_obj.address_get(cr, uid, [order.partner_id.id], ['delivery']) or {}
			picking_type = False
			picking_id = False
			picking_id = picking_obj.create(cr, uid, {
					'origin': order.name,
					'partner_id': addr.get('delivery',False),
					'date_done' : order.envio_fecha,
			 		'picking_type_id': config.picking_type_id.id,
					'company_id': order.enpresa_envio_id.id,
					'move_type': 'direct',
					'note': order.notas or "",
					'invoice_state': 'none',
				}, context=context)
			self.write(cr, uid, [order.id], {'picking_id': picking_id}, context=context)
			
			src_id =config.picking_type_id.default_location_src_id.id
			destination_id = config.picking_type_id.default_location_dest_id.id
			
			move_list = []
			for line in order.order_line:
				if line.product_id and line.product_id.type == 'service':
					continue

				move_list.append(move_obj.create(cr, uid, {
					'name': order.id,
					'product_uom': line.product_id.uom_id.id,
					'product_uos': line.product_id.uom_id.id,
					'picking_id': picking_id,
					'picking_type_id': config.picking_type_id.id,
					'product_id': line.product_id.id,
					'product_uos_qty': abs(line.cantidad),
					'product_uom_qty': abs(line.cantidad),
					'state': 'draft',
					'location_id': src_id if line.cantidad >= 0 else destination_id,
					'location_dest_id': destination_id if line.cantidad >= 0 else src_id,
				}, context=context))
                
			
				print 'action_confirm'
				#picking_obj.action_confirm(cr, uid, [picking_id], context=context)
				print 'force_assign'
				#picking_obj.force_assign(cr, uid, [picking_id], context=context)
				print 'action_done'
				#picking_obj.action_done(cr, uid, [picking_id], context=context)
			
				print 'action_confirm'
				move_obj.action_confirm(cr, uid, move_list, context=context)
				print 'force_assign'
				move_obj.force_assign(cr, uid, move_list, context=context)
				print 'action_done'
				move_obj.action_done(cr, uid, move_list, context=context)
		return True
class traspasos_configuraciones(osv.osv):
	_name = 'traspasos.configuraciones'
	_columns = {
	    'company_id': fields.many2one('res.company','Sucursal'),
	    'picking_type_id': fields.many2one('stock.picking.type','Operacion'),
        'users_id': fields.many2one('res.users', 'Encargado'),

	}
class traspasos_documento_productos(osv.osv):
	_name = 'traspasos.documento.productos'
	_order = 'fecha desc, id desc'
	_rec_name = "product_id"
	def onchange_qty(self, cr, uid, ids, product, cantidad, context=None):
		result = {}
		prod = self.pool.get('product.product').browse(cr, uid, product, context=context)
		result['importe'] = (prod.list_price*cantidad)
		self.write(cr, uid, ids, {'importe': result['importe']}, context=context)
		return {'value': result}
	def onchange_unitario(self, cr, uid, ids, product, unitario,cantidad, context=None):
		result = {}
		prod = self.pool.get('product.product').browse(cr, uid, product, context=context)
		result['unitario'] = unitario
		result['importe'] = (unitario*cantidad)
		self.write(cr, uid, ids, {'importe': result['importe']}, context=context)
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
			res[line.id]['importe'] = line.unitario*line.cantidad
		return res
	_columns = {
		'enpresa_envio_id': fields.many2one('res.company','Emisor'),
	    'enpresa_resivir_id': fields.many2one('res.company','Receptor'),
        'docunemto_id': fields.many2one('traspasos.documento','Trapaso'),
        'product_id': fields.many2one('product.product', 'Producto'),
        'cantidad':fields.float('Cantidad'),
        'categoria_id': fields.many2one('pos.category','Categoria',),
        'fecha': fields.datetime('Fecha',readonly=True),
        #'importe':fields.float('Importe',readonly=True),
        'importe': fields.function(_amount_line_all, multi='traspasos_documento_productos_total', digits_compute=dp.get_precision('Product Price'), string='Importe', store=True),

        'unitario':fields.float('Inporte Unitario'),
        'state': fields.selection([
            ('draft', 'Borrador'),
            ('sent', 'Enviada'),
            ('cancel', 'Cancelada'),
            ('recibe', 'Recibida')
            ], 'Status', readonly=True, copy=False),
	}
	_defaults = {
	    'state':'draft',
	    'fecha':fields.datetime.now,
	}
	