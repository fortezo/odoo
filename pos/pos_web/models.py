from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import StringIO
import base64
import csv
import time
import pytz, datetime

class pos_order_line():
    _name = 'pos.order.line'
    _inherit = "pos.order.line"
    _columns = {
        'sub_productos': fields.one2many(
            'pos.order.line',
            'o2m_field_id',
            'Promociones',
        ),
        'o2m_field_id': fields.integer(
            'Producto Padre',
        )
    }
pos_order_line()

class pos_order(osv.Model):
    _name = 'pos.order'
    _inherit = "pos.order"
    _columns = {
        'repartidorid': fields.many2one('res.partner','Repartidor',),  
        'horainicio': fields.datetime('Hora Inicio',),
        'horapreparacion': fields.datetime('Hora Preparacion',),
        'horaenvio': fields.datetime('Hora Envio',),
        'horafinal': fields.datetime('Hora Final',),

        #'pizza_state':fields.selection('Status',[('ordenado','Ordenado'),('cocina','En Cocina'),('horno','En Horno'),('disponible','Disponible'),('reparto','En Reparto'),('entregado','Entregado'),('cancel','Cancelado'),('modificado','Modificado'),('cancel','Cancelado'),],  index=True, readonly=True, default='ordenado',),
        'active': fields.boolean(
                'Activo',
            ),
        #'servicio':fields.selection('Servicio',[('domicilo','A Domicilio'),('aqui','Para Comer Aqui'),('llevar','Para Llevar'),('pasaporella','Pasa Por Ella'),], index=True, readonly=True, default='aqui',),
        'tipocambio':fields.float('Tipo Cambio',),
        #abono
        'canceladorid': fields.many2one('res.partner','Cancelo',),
        'horacancela': fields.datetime('Hora Cancela',),
        'modificacionid': fields.many2one('res.partner','Modifico',),
        'corterepartidor_id': fields.many2one('pizza.sesion','Corte de Repartidor',),
        'referencia_cliente': fields.text('Referencia de Cliente',),
        'ticket_data': fields.text('Ticket',),
    }

  #? estacion integer,
  #-descuento integer DEFAULT 0,
  #-pago smallint,
  #descuentop integer NOT NULL DEFAULT 0,
  #descuentoe numeric(10,2) DEFAULT 0.00,
  #numerocontrol character varying(20) DEFAULT '0'::character varying,
  #horareg timestamp without time zone,
 