from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    ocr_transaction_id = fields.Many2one('ocr.transactions', string='OCR', readonly=True)
    customer_id = fields.Many2one('res.partner', readonly=True, string='Customer')
    to_correct = fields.Boolean("For correction portal", default=False)
    is_ocr = fields.Boolean('De OCR')
    ocr_delivery_invoice = fields.Boolean(string='Es Gestor OCR',
                                          default=lambda self: self.env.user.company_id.ocr_delivery_company)
    ocr_upload_status = fields.Selection(string='OCR Status', related='ocr_transaction_id.ocr_upload_id.state')
    ocr_combination_image = fields.Binary("Img to show on wizard")
    ocr_transaction_error = fields.Char(string='OCR Error', related='ocr_transaction_id.transaction_error')

    def post_correction_form(self):

        self.to_correct = True

        return {'type': 'ir.actions.act_url',
                'url': '/invoice/correction',
                'target': 'current',
                }

    def invoice_combination_wizard(self):

        if self.ocr_transaction_id:
            view_id = self.env.ref('ocr_transactions.invoice_combination_view').id

            return {
                'name': _("Combinar Facturas"),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'ocr.invoice.combination',
                'view_id': view_id,
                'target': 'new',
                'context': {
                    'default_ocr_transaction_id': self.ocr_transaction_id.id,
                    'default_invoice_id_link': self.ocr_transaction_id.invoice_id.id,
                    #'default_attachment_datas': self.message_main_attachment_id.datas,
                    'default_attachment_datas': self.ocr_combination_image,
                    'default_original_ocr_transaction_id': self.ocr_transaction_id.id,
                }
            }

    def send_through(self):
        for record in self:
            if not record.message_main_attachment_id:
                raise ValidationError(
                    'No hay adjunto para enviar a OCR')
            else:
                ocr_upload = record.env['ocr.uploads'].create({
                    'name': str(record.env.user.name) + " - " + \
                            str(datetime.utcnow().strftime('%d-%m-%Y')),
                    'type': 'recibida',
                    'attachment_ids': [(6, 0, [record.message_main_attachment_id.id])],
                    'invoice_origin_id': record.id,
                })
                if ocr_upload:
                    ocr_upload.prepare_ocr_post_transactions_from_invoice()
                    record.ocr_transaction_id = ocr_upload.ocr_transaction_ids[0]
                    record.ocr_transaction_id.invoice_id = record.id
                    record.is_ocr = True

    def create_invoice_lines_from_ocr(self):
        for record in self:
            partner_id = record.partner_id
            # Comprobamos que el partner tiene asignadas cuentas contables por defecto para crear las líneas de factura:
            if (not partner_id.ocr_sale_account_id.id) or (not partner_id.ocr_purchase_account_id.id):
                raise ValidationError(
                    'Asigne los productos o cuentas contables por defecto para OCR en la ficha de esta empresa, antes de intentar crear las líneas de factura.')

            # Inicializando:
            base_iva21 = 0
            base_iva10 = 0
            base_iva4 = 0

            # Diccionario de impuestos para ventas:
            if record.move_type in ['out_invoice', 'out_refund']:
                # Si hay producto en la configuración OCR del partner, se utiliza; en otro caso sólo la cuenta contable:
                producto = partner_id.ocr_sale_product_id
                if (producto.property_account_income_id.id):
                    cc = producto.property_account_income_id.id
                    descrip = producto.name
                elif (not producto.property_account_income_id.id) and (
                producto.categ_id.property_account_income_categ_id.id):
                    cc = producto.categ_id.property_account_income_categ_id.id
                    descrip = producto.name
                else:
                    cc = partner_id.ocr_sale_account_id.id
                    descrip = partner_id.ocr_sale_account_id.name

                taxiva21 = self.env['ocr.dictionary'].search([('name', '=', 'IVA21'), ('type', '=', 'out_invoice')]).tax_id
                taxiva10 = self.env['ocr.dictionary'].search([('name', '=', 'IVA10'), ('type', '=', 'out_invoice')]).tax_id
                taxiva4 = self.env['ocr.dictionary'].search([('name', '=', 'IVA4'), ('type', '=', 'out_invoice')]).tax_id
                taxiva0 = self.env['ocr.dictionary'].search([('name', '=', 'IVA0'), ('type', '=', 'out_invoice')]).tax_id
                # Diccionario de retenciones para ventas:
                taxret19 = self.env['ocr.dictionary'].search([('name', '=', 'IRPF19'), ('type', '=', 'out_invoice')]).tax_id
                taxret15 = self.env['ocr.dictionary'].search([('name', '=', 'IRPF15'), ('type', '=', 'out_invoice')]).tax_id
                taxret7 = self.env['ocr.dictionary'].search([('name', '=', 'IRPF7'), ('type', '=', 'out_invoice')]).tax_id
                taxret2 = self.env['ocr.dictionary'].search([('name', '=', 'IRPF2'), ('type', '=', 'out_invoice')]).tax_id

            # Diccionario de impuestos para compras:
            elif record.move_type in ['in_invoice', 'in_refund']:
                # Si hay producto en la configuración OCR del partner, se utiliza; en otro caso sólo la cuenta contable:
                producto = partner_id.ocr_purchase_product_id
                if (producto.property_account_expense_id.id):
                    cc = producto.property_account_expense_id.id
                    descrip = producto.name
                elif (not producto.property_account_expense_id.id) and (
                producto.categ_id.property_account_expense_categ_id.id):
                    cc = producto.categ_id.property_account_expense_categ_id.id
                    descrip = producto.name
                else:
                    cc = partner_id.ocr_purchase_account_id.id
                    descrip = partner_id.ocr_purchase_account_id.name

                taxiva21 = self.env['ocr.dictionary'].search([('name', '=', 'IVA21'), ('type', '=', 'in_invoice')]).tax_id
                taxiva10 = self.env['ocr.dictionary'].search([('name', '=', 'IVA10'), ('type', '=', 'in_invoice')]).tax_id
                taxiva4 = self.env['ocr.dictionary'].search([('name', '=', 'IVA4'), ('type', '=', 'in_invoice')]).tax_id
                taxiva0 = self.env['ocr.dictionary'].search([('name', '=', 'IVA0'), ('type', '=', 'in_invoice')]).tax_id
                # Diccionario de retenciones para compras:
                taxret19 = self.env['ocr.dictionary'].search([('name', '=', 'IRPF19'), ('type', '=', 'in_invoice')]).tax_id
                taxret15 = self.env['ocr.dictionary'].search([('name', '=', 'IRPF15'), ('type', '=', 'in_invoice')]).tax_id
                taxret7 = self.env['ocr.dictionary'].search([('name', '=', 'IRPF7'), ('type', '=', 'in_invoice')]).tax_id
                taxret2 = self.env['ocr.dictionary'].search([('name', '=', 'IRPF2'), ('type', '=', 'in_invoice')]).tax_id

            # Valores:
            subtotal = self.env['ocr.values'].search(
                [('ocr_transaction_id', '=', record.ocr_transaction_id.id), ('name', '=', 'SubTotal')])
            total = self.env['ocr.values'].search(
                [('ocr_transaction_id', '=', record.ocr_transaction_id.id), ('name', '=', 'TOTAL')])
            iva21 = self.env['ocr.values'].search(
                [('ocr_transaction_id', '=', record.ocr_transaction_id.id), ('name', '=', 'IVA21')])
            iva10 = self.env['ocr.values'].search(
                [('ocr_transaction_id', '=', record.ocr_transaction_id.id), ('name', '=', 'IVA10')])
            iva4 = self.env['ocr.values'].search(
                [('ocr_transaction_id', '=', record.ocr_transaction_id.id), ('name', '=', 'IVA4')])
            iva0 = self.env['ocr.values'].search(
                [('ocr_transaction_id', '=', record.ocr_transaction_id.id), ('name', '=', 'IVA0')])
            ret19 = self.env['ocr.values'].search(
                [('ocr_transaction_id', '=', record.ocr_transaction_id.id), ('name', '=', 'IRPF19')])
            ret15 = self.env['ocr.values'].search(
                [('ocr_transaction_id', '=', record.ocr_transaction_id.id), ('name', '=', 'IRPF15')])
            ret7 = self.env['ocr.values'].search(
                [('ocr_transaction_id', '=', record.ocr_transaction_id.id), ('name', '=', 'IRPF7')])
            ret2 = self.env['ocr.values'].search(
                [('ocr_transaction_id', '=', record.ocr_transaction_id.id), ('name', '=', 'IRPF2')])
            BaseImponible0 = self.env['ocr.values'].search(
                [('ocr_transaction_id', '=', record.ocr_transaction_id.id), ('name', '=', 'BaseImponible0')])
            BaseImponible4 = self.env['ocr.values'].search(
                [('ocr_transaction_id', '=', record.ocr_transaction_id.id), ('name', '=', 'BaseImponible4')])
            BaseImponible10 = self.env['ocr.values'].search(
                [('ocr_transaction_id', '=', record.ocr_transaction_id.id), ('name', '=', 'BaseImponible10')])
            BaseImponible21 = self.env['ocr.values'].search(
                [('ocr_transaction_id', '=', record.ocr_transaction_id.id), ('name', '=', 'BaseImponible21')])

            # Cálculo de bases imponibles POR IVA (ESTO ES UN PROBLEMA PORQUE LOS REDONDEOS SE MULTIPLICAN POR 5 para el 21% y por 10 para 10%):
            if subtotal.id:  neto = float(subtotal.value)
            if iva21.id:  base_iva21 = float(BaseImponible21.value)
            if iva10.id:  base_iva10 = float(BaseImponible10.value)
            if iva4.id:   base_iva4 = float(BaseImponible4.value)

            # Cálculo de bases imponibles POR RETENCIONES (para desviaciones por decimales se considera la opción de que sea por el neto completo):
            if (ret19.id) and (subtotal.id):
                irpf19_del_neto = round(neto * 19 / 100, 2)
                if (float(ret19.value) == irpf19_del_neto):
                    base_ret19 = neto
                else:
                    base_ret19 = round(float(ret19.value) * 100 / 19, 2)
            if (ret15.id) and (subtotal.id):
                irpf15_del_neto = round(neto * 15 / 100, 2)
                if (float(ret15.value) == irpf15_del_neto):
                    base_ret15 = neto
                else:
                    base_ret15 = round(float(ret15.value) * 100 / 15, 2)
            if (ret7.id) and (subtotal.id):
                irpf7_del_neto = round(neto * 7 / 100, 2)
                if (float(ret7.value) == irpf7_del_neto):
                    base_ret7 = neto
                else:
                    base_ret7 = round(float(ret7.value) * 100 / 19, 2)
            if (ret2.id) and (subtotal.id):
                irpf2_del_neto = round(neto * 2 / 100, 2)
                if (float(ret2.value) == irpf2_del_neto):
                    base_ret2 = neto
                else:
                    base_ret2 = round(float(ret2.value) * 100 / 2, 2)

            # Cálculo de retenciones al 19%:
            if (ret19.id) and (base_ret19 > 0):
                if (base_iva21 >= base_ret19):
                    # crear línea con base de retención y dejar base restante para otra línea:
                    impuestos = [taxiva21.id, taxret19.id]
                    record['invoice_line_ids'] = [
                        (0, 0, {'product_id': producto.id, 'name': descrip or producto.name, 'account_id': cc,
                                'partner_id': partner_id.id, 'price_unit': base_ret19, 'tax_ids': [(6, 0, impuestos)]}),
                        (0, 0, {'name': descrip or '/', 'account_id': partner_id.ocr_purchase_account_id.id,
                                'partner_id': partner_id.id, 'exclude_from_invoice_tab': True})]
                    base_iva21 -= base_ret19
                    neto -= base_ret19
                    base_ret19 = 0

                # Lo mismo por si es iva10
                if (base_iva10 >= base_ret19) and (base_ret19 > 0):
                    # crear línea con base de retención y dejar base restante para otra línea:
                    impuestos = [taxiva10.id, taxret19.id]
                    record['invoice_line_ids'] = [
                        (0, 0, {'product_id': producto.id, 'name': descrip or producto.name, 'account_id': cc,
                                'partner_id': partner_id.id, 'price_unit': base_ret19, 'tax_ids': [(6, 0, impuestos)]}),
                        (0, 0, {'name': descrip or '/', 'account_id': partner_id.ocr_purchase_account_id.id,
                                'partner_id': partner_id.id, 'exclude_from_invoice_tab': True})]
                    base_iva10 -= base_ret19
                    neto -= base_ret19
                    base_ret19 = 0
                # Lo mismo por si es iva4 para 19
                if (base_iva4 >= base_ret19) and (base_ret19 > 0):
                    # crear línea con base de retención y dejar base restante para otra línea:
                    impuestos = [taxiva4.id, taxret19.id]
                    record['invoice_line_ids'] = [
                        (0, 0, {'product_id': producto.id, 'name': descrip or producto.name, 'account_id': cc,
                                'partner_id': partner_id.id, 'price_unit': base_ret19, 'tax_ids': [(6, 0, impuestos)]}),
                        (0, 0, {'name': descrip or '/', 'account_id': partner_id.ocr_purchase_account_id.id,
                                'partner_id': partner_id.id, 'exclude_from_invoice_tab': True})]
                    base_iva4 -= base_ret19
                    neto -= base_ret19

            # Cálculo de retenciones al 15%:
            if (ret15.id) and (base_ret15 > 0):
                if (base_iva21 >= base_ret15):
                    # crear línea con base de retención y dejar base restante para otra línea:
                    impuestos = [taxiva21.id, taxret15.id]
                    record['invoice_line_ids'] = [
                        (0, 0, {'product_id': producto.id, 'name': descrip or producto.name, 'account_id': cc,
                                'partner_id': partner_id.id, 'price_unit': base_ret15, 'tax_ids': [(6, 0, impuestos)]}),
                        (0, 0, {'name': descrip or '/', 'account_id': partner_id.ocr_purchase_account_id.id,
                                'partner_id': partner_id.id, 'exclude_from_invoice_tab': True})]
                    base_iva21 -= base_ret15
                    neto -= base_ret15
                    base_ret15 = 0
                # Lo mismo por si es iva10
                if (base_iva10 >= base_ret15) and (base_ret15 > 0):
                    # crear línea con base de retención y dejar base restante para otra línea:
                    impuestos = [taxiva10.id, taxret15.id]
                    record['invoice_line_ids'] = [
                        (0, 0, {'product_id': producto.id, 'name': descrip or producto.name, 'account_id': cc,
                                'partner_id': partner_id.id, 'price_unit': base_ret15, 'tax_ids': [(6, 0, impuestos)]}),
                        (0, 0, {'name': descrip or '/', 'account_id': partner_id.ocr_purchase_account_id.id,
                                'partner_id': partner_id.id, 'exclude_from_invoice_tab': True})]
                    base_iva10 -= base_ret15
                    neto -= base_ret15
                    base_ret15 = 0
                # Lo mismo por si es iva4 para 15
                if (base_iva4 >= base_ret15) and (base_ret15 > 0):
                    # crear línea con base de retención y dejar base restante para otra línea:
                    impuestos = [taxiva4.id, taxret15.id]
                    record['invoice_line_ids'] = [
                        (0, 0, {'product_id': producto.id, 'name': descrip or producto.name, 'account_id': cc,
                                'partner_id': partner_id.id, 'price_unit': base_ret15, 'tax_ids': [(6, 0, impuestos)]}),
                        (0, 0, {'name': descrip or '/', 'account_id': partner_id.ocr_purchase_account_id.id,
                                'partner_id': partner_id.id, 'exclude_from_invoice_tab': True})]
                    base_iva4 -= base_ret15
                    neto -= base_ret15

            # Cálculo de retenciones al 7%:
            if (ret7.id) and (base_ret7 > 0):
                if (base_iva21 >= base_ret7):
                    # crear línea con base de retención y dejar base restante para otra línea:
                    impuestos = [taxiva21.id, taxret7.id]
                    record['invoice_line_ids'] = [
                        (0, 0, {'product_id': producto.id, 'name': descrip or producto.name, 'account_id': cc,
                                'partner_id': partner_id.id, 'price_unit': base_ret7, 'tax_ids': [(6, 0, impuestos)]}),
                        (0, 0, {'name': descrip or '/', 'account_id': partner_id.ocr_purchase_account_id.id,
                                'partner_id': partner_id.id, 'exclude_from_invoice_tab': True})]
                    base_iva21 -= base_ret7
                    neto -= base_ret7
                    base_ret7 = 0
                # Lo mismo por si es iva10
                if (base_iva10 >= base_ret7) and (base_ret7 > 0):
                    # crear línea con base de retención y dejar base restante para otra línea:
                    impuestos = [taxiva10.id, taxret7.id]
                    record['invoice_line_ids'] = [
                        (0, 0, {'product_id': producto.id, 'name': descrip or producto.name, 'account_id': cc,
                                'partner_id': partner_id.id, 'price_unit': base_ret7, 'tax_ids': [(6, 0, impuestos)]}),
                        (0, 0, {'name': descrip or '/', 'account_id': partner_id.ocr_purchase_account_id.id,
                                'partner_id': partner_id.id, 'exclude_from_invoice_tab': True})]
                    base_iva10 -= base_ret7
                    neto -= base_ret7
                    base_ret7 = 0
                # Lo mismo por si es iva4 para 7
                if (base_iva4 >= base_ret7) and (base_ret7 > 0):
                    # crear línea con base de retención y dejar base restante para otra línea:
                    impuestos = [taxiva4.id, taxret7.id]
                    record['invoice_line_ids'] = [
                        (0, 0, {'product_id': producto.id, 'name': descrip or producto.name, 'account_id': cc,
                                'partner_id': partner_id.id, 'price_unit': base_ret7, 'tax_ids': [(6, 0, impuestos)]}),
                        (0, 0, {'name': descrip or '/', 'account_id': partner_id.ocr_purchase_account_id.id,
                                'partner_id': partner_id.id, 'exclude_from_invoice_tab': True})]
                    base_iva4 -= base_ret7
                    neto -= base_ret7

            # Cálculo de retenciones al 2%:
            if (ret2.id) and (base_ret2 > 0):
                if (base_iva21 >= base_ret2):
                    # crear línea con base de retención y dejar base restante para otra línea:
                    impuestos = [taxiva21.id, taxret2.id]
                    record['invoice_line_ids'] = [
                        (0, 0, {'product_id': producto.id, 'name': descrip or producto.name, 'account_id': cc,
                                'partner_id': partner_id.id, 'price_unit': base_ret2, 'tax_ids': [(6, 0, impuestos)]}),
                        (0, 0, {'name': descrip or '/', 'account_id': partner_id.ocr_purchase_account_id.id,
                                'partner_id': partner_id.id, 'exclude_from_invoice_tab': True})]
                    base_iva21 -= base_ret2
                    neto -= base_ret2
                    base_ret2 = 0
                # Lo mismo por si es iva10
                if (base_iva10 >= base_ret2) and (base_ret2 > 0):
                    # crear línea con base de retención y dejar base restante para otra línea:
                    impuestos = [taxiva10.id, taxret2.id]
                    record['invoice_line_ids'] = [
                        (0, 0, {'product_id': producto.id, 'name': descrip or producto.name, 'account_id': cc,
                                'partner_id': partner_id.id, 'price_unit': base_ret2, 'tax_ids': [(6, 0, impuestos)]}),
                        (0, 0,
                         {'name': descrip or '/', 'account_id': partner_id.ocr_purchase_account_id.id, 'partner_id': partner_id.id,
                          'exclude_from_invoice_tab': True})]
                    base_iva10 -= base_ret2
                    neto -= base_ret2
                    base_ret2 = 0
                # Lo mismo por si es iva4 para 2
                if (base_iva4 >= base_ret2) and (base_ret2 > 0):
                    # crear línea con base de retención y dejar base restante para otra línea:
                    impuestos = [taxiva4.id, taxret2.id]
                    record['invoice_line_ids'] = [
                        (0, 0, {'product_id': producto.id, 'name': descrip or producto.name, 'account_id': cc,
                                'partner_id': partner_id.id, 'price_unit': base_ret2, 'tax_ids': [(6, 0, impuestos)]}),
                        (0, 0, {'name': descrip or '/', 'account_id': partner_id.ocr_purchase_account_id.id,
                                'partner_id': partner_id.id, 'exclude_from_invoice_tab': True})]
                    base_iva4 -= base_ret2
                    neto -= base_ret2

            # Líneas de impuestos estándar, sin retención:
            if (taxiva21.id) and (base_iva21 > 0):
                impuestos = [taxiva21.id]
                record['invoice_line_ids'] = [
                    (0, 0, {'product_id': producto.id, 'name': descrip or producto.name, 'account_id': cc,
                            'partner_id': partner_id.id, 'price_unit': base_iva21, 'tax_ids': [(6, 0, impuestos)]}),
                    (0, 0, {'name': descrip or '/', 'account_id': partner_id.ocr_purchase_account_id.id,
                            'partner_id': partner_id.id, 'exclude_from_invoice_tab': True})]
                neto -= base_iva21
            if (taxiva10.id) and (base_iva10 > 0):
                impuestos = [taxiva10.id]
                record['invoice_line_ids'] = [
                    (0, 0, {'product_id': producto.id, 'name': descrip or producto.name, 'account_id': cc,
                            'partner_id': partner_id.id, 'price_unit': base_iva10, 'tax_ids': [(6, 0, impuestos)]}),
                    (0, 0, {'name': descrip or '/', 'account_id': partner_id.ocr_purchase_account_id.id,
                            'partner_id': partner_id.id, 'exclude_from_invoice_tab': True})]
                neto -= base_iva10
            if (taxiva4.id) and (base_iva4 > 0):
                impuestos = [taxiva4.id]
                record['invoice_line_ids'] = [
                    (0, 0, {'product_id': producto.id, 'name': descrip or producto.name, 'account_id': cc,
                            'partner_id': partner_id.id, 'price_unit': base_iva4, 'tax_ids': [(6, 0, impuestos)]}),
                    (0, 0, {'name': descrip or '/', 'account_id': partner_id.ocr_purchase_account_id.id,
                            'partner_id': partner_id.id, 'exclude_from_invoice_tab': True})]
                neto -= base_iva4

            # Caso de línea sin impuestos y sin detectar IVA0%:
            if (subtotal.id) and (neto > 0):
                impuestos = [taxiva0.id]
                record['invoice_line_ids'] = [
                    (0, 0, {'product_id': producto.id, 'name': descrip or producto.name, 'account_id': cc,
                            'partner_id': partner_id.id, 'price_unit': neto, 'tax_ids': [(6, 0, impuestos)]}),
                    (0, 0, {'name': descrip or '/', 'account_id': partner_id.ocr_purchase_account_id.id,
                            'partner_id': partner_id.id, 'exclude_from_invoice_tab': True})]

            # Reculcalate Taxes
            # if record.invoice_line_ids.ids:
            #  record.compute_taxes()





