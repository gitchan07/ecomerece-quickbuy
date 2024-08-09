from flask import Blueprint, request, jsonify
from connection.connector import connection
from sqlalchemy.orm import sessionmaker
from models.Categories import Categories
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError

category_routes = Blueprint("category_routes", __name__)

Session = sessionmaker(bind=connection)


# Routes


@category_routes.route("/testing", methods=["GET"])
def test_connection():
    try:
        with Session() as session:
            category = session.query(Categories).first()
            response = {
                "message": "good connection",
                "dict": category.to_dict() if category else "No categories available",
            }
            return jsonify(response), 200
    except Exception as e:
        return jsonify({"message": "connection failed", "error": str(e)}), 500


@category_routes.route("/", methods=["POST"])
@jwt_required()
def create_category():
    if not request.is_json:
        return jsonify({"message": "Request must be JSON"}), 415

    try:
        data = request.get_json()
        response, status = create_new_category(data)
        return jsonify(response), status
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500


@category_routes.route("/", methods=["GET"])
@jwt_required()
def get_categories():
    try:
        response, status = get_all_categories()
        return jsonify(response), status
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500


@category_routes.route("/<int:category_id>", methods=["GET"])
@jwt_required()
def get_category(category_id):
    try:
        response, status = get_category_by_id(category_id)
        return jsonify(response), status
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500


@category_routes.route("/<int:category_id>", methods=["PUT"])
@jwt_required()
def update_category(category_id):
    if not request.is_json:
        return jsonify({"message": "Request must be JSON"}), 415

    try:
        data = request.get_json()
        response, status = update_existing_category(category_id, data)
        return jsonify(response), status
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500


@category_routes.route("/<int:category_id>", methods=["DELETE"])
@jwt_required()
def delete_category(category_id):
    try:
        response, status = delete_existing_category(category_id)
        return jsonify(response), status
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500


# Utility Functions


def create_new_category(data):
    session = None
    try:
        session = Session()
        new_category = Categories(name=data["name"])
        session.add(new_category)
        session.commit()
        return {
            "message": "Category created successfully",
            "category": {"id": new_category.id, "name": new_category.name},
        }, 201
    except SQLAlchemyError as e:
        session.rollback()
        return {"message": "Fail to create category", "error": str(e)}, 500
    finally:
        if session:
            session.close()


def get_all_categories():
    try:
        with Session() as session:
            product_id = request.args.get("product_id")  # correct this implementtation
            categories = session.query(Categories).all()
            category_list = [
                {
                    "id": category.id,
                    "name": category.name,
                    "created_at": category.created_at,
                    "updated_at": category.updated_at,
                }
                for category in categories
            ]
            return {"categories": category_list}, 200
    except SQLAlchemyError as e:
        return {"message": "Fail to retrieve categories", "error": str(e)}, 500


def get_category_by_id(category_id):
    try:
        with Session() as session:
            category = session.query(Categories).filter_by(id=category_id).first()
            if category is None:
                return {"message": "Category not found"}, 404
            return {
                "category": {
                    "id": category.id,
                    "name": category.name,
                    "created_at": category.created_at,
                    "updated_at": category.updated_at,
                }
            }, 200
    except SQLAlchemyError as e:
        return {"message": "Fail to retrieve category", "error": str(e)}, 500


def update_existing_category(category_id, data):
    session = None
    try:
        session = Session()
        category = session.query(Categories).filter_by(id=category_id).first()
        if category is None:
            return {"message": "Category not found"}, 404
        category.name = data["name"]
        session.commit()
        return {
            "message": "Category updated successfully",
            "category": {"id": category.id, "name": category.name},
        }, 200
    except SQLAlchemyError as e:
        session.rollback()
        return {"message": "Fail to update category", "error": str(e)}, 500
    finally:
        if session:
            session.close()


def delete_existing_category(category_id):
    session = None
    try:
        session = Session()
        category = session.query(Categories).filter_by(id=category_id).first()

        if category is None:
            print(f"Category ID {category_id} not found")
            return jsonify({"message": "Category not found"}), 404

        session.delete(category)
        session.commit()
        print(f"Category ID {category_id} deleted successfully")
        return jsonify({"message": "Category deleted successfully"}), 200
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Failed to delete category ID {category_id}: {str(e)}")
        return jsonify({"message": "Fail to delete category", "error": str(e)}), 500
    finally:
        if session:
            session.close()
