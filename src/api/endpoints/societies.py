from flask import g, jsonify, request, current_app, url_for
from flask_restplus import Resource

from api.utils.auth import token_required, roles_required
from api.utils.helpers import find_society
from ..models import Society


class SocietyResource(Resource):
    """To contain CRUD endpoints for Society."""

    @token_required
    @roles_required(["Success Ops"])
    def post(self):
        """Create a society."""
        try:
            payload = request.get_json()
        except Exception as e:
            response = jsonify({
                "status": "fail",
                "message": "Name, color_scheme and logo url required"})
            response.status_code = 400
            return response

        # if payload exists
        try:
            name = payload["name"]
            color_scheme = payload["colorScheme"]
            logo = payload["logo"]
            photo = payload["photo"]
        except Exception as e:
            response = jsonify({
                "status": "fail",
                "message": "Name, color scheme and logo are required"
                           " to create a society."
                })
            response.status_code = 400
            return response

        # if no errors occur in assigning above
        society = Society(
            name=name, color_scheme=color_scheme, logo=logo, photo=photo
        )
        society.save()
        response = jsonify({
            "status": "success",
            "data": society.serialize(),
            "message": "Society created successfully."
        })
        response.status_code = 201
        return response

    @token_required
    def get(self, society_id=None):
        """Get Society(ies) details."""
        if society_id:
            society = Society.query.get(society_id)
            return find_society(society)
        else:
            _page = request.args.get('page')
            _limit = request.args.get('limit')
            page = int(_page or current_app.config['DEFAULT_PAGE'])
            limit = int(_limit or current_app.config['PAGE_LIMIT'])
            search_term = request.args.get('q')

            if search_term:
                society = Society.query.filter_by(name=search_term).first()
                return find_society(society)

            # if no search term has been passed, return all societies in DB
            societies = Society.query

            societies = societies.paginate(
                page=page,
                per_page=limit,
                error_out=False
            )
            if societies.items:
                previous_url = None
                next_url = None
                if societies.has_next:
                    next_url = url_for(request.endpoint, limit=limit,
                                       page=page+1, _external=True)
                if societies.has_prev:
                    previous_url = url_for(request.endpoint, limit=limit,
                                           page=page-1, _external=True)

                societies_list = []
                for _society in societies.items:
                    society = _society.serialize()
                    societies_list.append(society)

                response = jsonify({
                    "status": "success",
                    "data": {"societies": societies_list,
                             "count": len(societies.items),
                             "nextUrl": next_url,
                             "previousUrl": previous_url,
                             "currentPage": societies.page},
                    "message": "Society fetched successfully."
                })
                response.status_code = 200
                return response
            else:
                response = jsonify({
                    "status": "success",
                    "data": {"societies": [],
                             "count": 0},
                    "message": "There are no societies."
                })
                response.status_code = 404
                return response

    @token_required
    @roles_required(["Success Ops"])
    def put(self, society_id=None):
        """Edit Society details."""
        try:
            payload = request.get_json()
        except Exception as e:
            response = jsonify({
                "status": "fail",
                "errors": e,
                "message": "Name, color_scheme and logo url required"})
            response.status_code = 400
            return response

        if payload:
            if not society_id:
                # if society_id is not passed
                response = jsonify({
                    "status": "fail",
                    "message": "Society to be edited must be provided"})
                response.status_code = 400
                return response

            society = Society.query.get(society_id)
            if society:
                try:
                    name = payload["name"]
                    color_scheme = payload["colorScheme"]
                    logo = payload["logo"] or None
                    photo = payload["photo"]or None
                    if name:
                        society.name = name
                    if color_scheme:
                        society.color = color_scheme
                    if photo:
                        society.photo = logo
                    if logo:
                        society.logo = photo
                    society.save()
                    response = jsonify({
                        "data": {"path": society.serialize()},
                        "status": "success",
                        "message": "Society edited successfully."
                    })
                    response.status_code = 200
                    return response
                except Exception as e:
                    response = jsonify({"errors": e,
                                        "module": "Society Module"})
                    response.status_code = 500
                    return response
            else:
                response = jsonify({"status": "fail",
                                    "message": "Society does not exist."})
                response.status_code = 404
            return response

    @token_required
    @roles_required(["Success Ops"])
    def delete(self, society_id=None):
        """Delete Society."""
        if not society_id:
            response = jsonify({"status": "fail",
                                "message": "Society id must be provided."})
            response.status_code = 400
            return response
        society = Society.query.get(society_id)
        if not society:
            response = jsonify({"status": "fail",
                                "message": "Society does not exist."})
            response.status_code = 404
            return response
        else:
            society.delete()
            response = jsonify({"status": "success",
                                "message": "Society deleted successfully."})
            response.status_code = 200
            return response
