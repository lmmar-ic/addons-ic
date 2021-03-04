from odoo import _, api, fields, models

import logging
_logger = logging.getLogger(__name__)


class SaleOrderSets(models.Model):
    _inherit = 'sale.order'

    def _get_lines_count(self):
        results = self.env['sale.order.line'].search([
            ('order_id', '=', self.id),
            ('display_type', '=', 'line_section')]
        )
        self.section_lines_count = len(results)

    section_lines_count = fields.Integer('Lines', compute=_get_lines_count)

    def action_view_sections(self):
        action = self.env.ref(
            'sale_order_multisection.action_view_sections').read()[0]
        return action


