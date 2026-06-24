from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class PropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Offers Made For Real Estate'
    _order = "price desc"
    _sql_constraints = [
        ('check_offer_price', 'CHECK(price > 0)', 'The Offer price must be strictly positive'),

    ]

    price = fields.Float(required=True)
    status = fields.Selection([
        ('accepted', 'Accepted'),
        ('refused', 'Refused')
    ],
        default='refused',
        copy=False,
        required=True,
    )
    property_id = fields.Many2one('real.estate', required=True)
    property_type_id = fields.Many2one(
        'estate.property.type',
        string='Property Type',
        related='property_id.property_type_id',
        store=True,
    )
    partner_id = fields.Many2one('res.partner', required=True)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(
        compute='_compute_date_deadline',
        inverse='_inverse_date_deadline',
        store=True
    )

    @api.model
    def create(self, vals):
        property_id = self.env['real.estate'].browse(vals['property_id'])

        # Raise an error if there is an existing offer with a higher or equal amount
        existing_offers = property_id.offer_ids.filtered(lambda o: o.price >= vals['price'])
        if existing_offers:
            raise UserError("An offer with a higher or equal amount already exists.")

        # Set the property state to 'Offer Received'
        property_id.state = 'received'

        return super().create(vals)

    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for property in self:
            property.date_deadline = fields.Date.today() + relativedelta(days=property.validity)

    def _inverse_date_deadline(self):
        for rec in self:
            rec.validity = (rec.date_deadline - fields.Date.today()).days

    def action_accept(self):
        self.ensure_one()
        if "accepted" in self.property_id.offer_ids.mapped('status') and self.status == "accepted":
            raise UserError("An offer is already accepted for this property.")
        self.status = "accepted"
        self.property_id.selling_price = self.price
        self.property_id.buyer_id = self.partner_id

    def action_refuse(self):
        self.ensure_one()
        if self.status == "accepted":
            raise UserError("An accepted offer cannot be refused.")
        self.status = "refused"
