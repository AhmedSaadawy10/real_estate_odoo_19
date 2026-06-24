import json
import math
from urllib.parse import parse_qs

from odoo import http
from odoo.http import request


def valid_response(data, pagination_info, status):
    response_body = {
        'message': 'success',
        'data': data
    }
    if pagination_info:
        response_body['pagination_info'] = pagination_info
    return request.make_json_response(response_body, status=status)


def invalid_response(error, status):
    response_body = {
        'error': error,
    }
    return request.make_json_response(response_body, status=status)


class PropertyApi(http.Controller):

    @http.route("/api/property", methods=["POST"], type="http", auth="none", csrf=False)
    def post_properties(self):
        args = request.httprequest.data.decode() #بعمل ريكويست واخد الداتا في شكل json
        vals = json.loads(args) #طبعا محتاج احولها ل dict عشان اعرف استخدمها ف كرييت الريكورد او اعمل check علي فيلد معين
        print(vals)
        # do not forget the validation layer
        # يعني لو عند فيلد required لازم اتاكد انه مبعوت مع الداتا
        if not vals.get('name'):
            return request.make_json_response({
                "message": "Name Is Required",
            }, status=400)
        try:
            res = request.env['real.estate'].create(vals)
            print(res)
            if res:
                return request.make_json_response({
                    "status": "success",
                    "message": "Property Created Successfully",
                    "id": res.id,
                    "name": res.name,
                }, status=201)
        except Exception as error:
            print(error)
            return request.make_json_response({
                "status": error,
                "message": "Property Creation Failed",
            }, status=400)

    @http.route("/api/property/<int:property_id>", methods=["PUT"], type="http", auth="none", csrf=False)
    def update_property(self, property_id):
        property_id = request.env['real.estate'].sudo().search([('id', '=', property_id)])
        if not property_id:
            return request.make_json_response({
                "message": "Property Not Found",
            }, status=404)
        print(property_id)
        args = request.httprequest.data.decode()
        vals = json.loads(args)
        print(vals)
        property_id.write(vals)
        print(property_id.state)
        return request.make_json_response({
            "status": "success",
            "message": "Property Updated Successfully",
            "id": property_id.id,
            "name": property_id.name,
        }, status=200)

    @http.route("/api/property/<int:property_id>", methods=["GET"], type="http", auth="none", csrf=False)
    def get_property(self, property_id):
        try:
            property_id = request.env['real.estate'].sudo().search([('id', '=', property_id)])
            if not property_id:
                return invalid_response("Property Not Found", status=404)
            return request.make_json_response({
                "status": "success",
                "message": "Property Found Successfully",
                "id": property_id.id,
                "name": property_id.name,
                "description": property_id.description,
            }, status=200)
        except Exception as error:
            print(error)

    @http.route("/api/properties", methods=["GET"], type="http", auth="none", csrf=False)
    def get_property_list(self):
        try:
            params = parse_qs(request.httprequest.query_string.decode('utf-8'))
            print(params)
            property_domain = []
            page = offset = None
            limit = 0
            if params:
                if params.get('limit'):
                    limit = int(params.get('limit')[0])
                if params.get('page'):
                    page = int(params.get('page')[0])
                if params.get('state'):
                    property_domain.append(('state', '=', params.get('state')[0]))
                print(property_domain)
                if params.get('name'):
                    property_domain.append(('name', 'ilike', params.get('name')[0]))
            if page:
                offset = (page * limit) - limit
            property_count_ids = request.env['real.estate'].sudo().search_count(property_domain)
            print(property_count_ids)
            property_ids = request.env['real.estate'].sudo().search(property_domain, offset=offset, limit=limit, order='id desc')
            print(property_ids)

            if not property_ids:
                return request.make_json_response({
                    "error": "there are no records",
                }, status=404)
            data = [{
                "status": "success",
                "message": "Properties Found Successfully",
                "id": property_id.id,
                "name": property_id.name,
                "description": property_id.description,
            } for property_id in property_ids]
            pagination_info = {
                "total": property_count_ids,
                "page": page if page else 1,
                "pages": math.ceil(property_count_ids / limit) if limit else 1,
                "offset": offset,
                "limit": limit
            }
            print(data)
            return valid_response(data, pagination_info, status=200)

        except Exception as error:
            print(error)

    @http.route("/api/property/<int:property_id>", methods=["DELETE"], type="http", auth="none", csrf=False)
    def delete_property(self, property_id):
        try:
            property_id = request.env['real.estate'].sudo().search([('id', '=', property_id)])
            if not property_id:
                return request.make_json_response({
                    "error": "Property Not Found",
                }, status=404)
            property_id.unlink()
            return request.make_json_response({
                "status": "success",
                "message": "Property Deleted Successfully",
            }, status=200)
        except Exception as error:
            print(error)

    @http.route("/api/property/json", methods=["POST"], type="json", auth="none", csrf=False)
    def post_property_json(self):
        args = request.httprequest.data.decode()
        vals = json.loads(args)
        print(vals)
        res = request.env['real.estate'].create(vals)
        print(res)
        if res:
            return [{
                "status": "success",
                "message": "Property Json Created Successfully",
            }]
