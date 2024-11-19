from flask import Flask, jsonify, request, Response
from decimal import Decimal, InvalidOperation
from db.database import connect_db
import json

def decimal_serializer(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def init_routes(app):
    
    @app.route('/')
    def index():
        """
        Returns the list of available routes
        """
        routes_info = {
            "routes": [
            "GET /vehicles",
            "GET /vehicles/<vin>",
            "POST /create_vehicle",
            "PUT /update_vehicle/<vin>",
            "DELETE /delete_vehicle/<vin>"
            ]
        }
        return Response(
            json.dumps(routes_info, indent=4),
            mimetype='application/json'
        )

    @app.route('/vehicles', methods=['GET'])
    def get_all_vehicles():
        """
        Returns a list of all vehicles in the database
        """
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Vehicle;")
            vehicles = cursor.fetchall()
            response_data = {"Vehicles": vehicles}
            cursor.close()
            conn.close()

            return Response(
                json.dumps(response_data, indent=4, default=decimal_serializer),
                mimetype='application/json'
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 400


    @app.route('/vehicles/<string:vin>', methods=['GET'])
    def get_specific_vehicle(vin):
        """
        Returns a specific vehicle based on the VIN
        """
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Vehicle WHERE vin = %s;", (vin,))
            vehicle = cursor.fetchone()
            response_data = {"Vehicle": vehicle}
            cursor.close()
            conn.close()
            if vehicle:
                return Response(
                    json.dumps(response_data, indent=4, default=decimal_serializer),
                    mimetype='application/json'
                )
            else:
                raise Exception("Vehicle not found")
        except Exception as e:
            return jsonify({"error": str(e)}), 400


    @app.route('/create_vehicle', methods=['POST'])
    def create_vehicle():
        """
        Creates a new vehicle in the database
        """
        try:
            if not request.is_json:
                return jsonify({"error": "Request body must be in JSON representation"}), 400

            data = request.get_json()

            required_fields = [
                'vin', 'manufacturer_name', 'horse_power', 'model_name',
                'model_year', 'purchase_price', 'fuel_type'
            ]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({
                    "error": "Missing required fields",
                    "missing_fields": missing_fields
                }), 422

            if 'model_year' in data and not isinstance(data['model_year'], int):
                return jsonify({
                    "error": "Invalid data type for model_year",
                    "details": "model_year must be an integer"
                }), 422

            if 'horse_power' in data and not isinstance(data['horse_power'], int):
                return jsonify({
                    "error": "Invalid data type for horse_power",
                    "details": "horse_power must be an integer"
                }), 422

            if 'purchase_price' in data:
                try:
                    data['purchase_price'] = Decimal(data['purchase_price'])
                except (InvalidOperation, ValueError):
                    return jsonify({
                        "error": "Invalid data type for purchase_price",
                        "details": "purchase_price must be a float represented as a string or the number itself"
                    }), 422


            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Vehicle (vin, manufacturer_name, description, horse_power, model_name, model_year, purchase_price, fuel_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data['vin'],
                data['manufacturer_name'],
                data.get('description'),
                data['horse_power'],
                data['model_name'],
                data['model_year'],
                data['purchase_price'],
                data['fuel_type']
            ))
            cursor.execute("SELECT * FROM Vehicle WHERE vin = %s;", (data['vin'],))
            new_vehicle = cursor.fetchone()
            response_data = {"Vehicle": new_vehicle}
            conn.commit()
            cursor.close()
            conn.close()

            return Response(
                json.dumps(response_data, indent=4, default=decimal_serializer),
                mimetype='application/json'
            )

        except Exception as e:
            return jsonify({"error": str(e)}), 400


    @app.route('/update_vehicle/<string:vin>', methods=['PUT'])
    def update_vehicle(vin):
        """
        Updates an existing vehicle in the database based on the VIN
        """
        try:
            if not request.is_json:
                return jsonify({"error": "Request body must be in JSON representation"}), 400

            data = request.get_json()

            if not data:
                return jsonify({"error": "No data provided for update"}), 400
            if 'model_year' in data and not isinstance(data['model_year'], int):
                return jsonify({"error": "Invalid data type for model_year. Must be an integer."}), 422
            if 'horse_power' in data and not isinstance(data['horse_power'], int):
                return jsonify({"error": "Invalid data type for horse_power. Must be an integer."}), 422
            if 'purchase_price' in data:
                try:
                    data['purchase_price'] = Decimal(data['purchase_price'])
                except (InvalidOperation, ValueError):
                    return jsonify({
                        "error": "Invalid data type for purchase_price",
                        "details": "purchase_price must be a float represented as a string or the number itself"
                    }), 422

            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Vehicle WHERE vin = %s;", (vin,))
            existing_vehicle = cursor.fetchone()

            if not existing_vehicle:
                cursor.close()
                conn.close()
                return jsonify({"error": f"Vehicle not found"}), 404

            update_fields = []
            update_values = []
            for field in ['manufacturer_name', 'description', 'horse_power', 'model_name', 'model_year', 'purchase_price', 'fuel_type']:
                if field in data:
                    update_fields.append(f"{field} = %s")
                    update_values.append(data[field])

            if not update_fields:
                return jsonify({"error": "No valid fields provided for update"}), 422

            update_values.append(vin)
            cursor.execute(f"""
                UPDATE Vehicle
                SET {', '.join(update_fields)}
                WHERE vin = %s;
            """, tuple(update_values))
            cursor.execute("SELECT * FROM Vehicle WHERE vin = %s;", (vin,))
            updated_vehicle = cursor.fetchone()
            response_data = {"Vehicle": updated_vehicle}
            conn.commit()
            cursor.close()
            conn.close()

            return Response(
                json.dumps(response_data, indent=4, default=decimal_serializer),
                mimetype='application/json'
            )

        except Exception as e:
            return jsonify({"error": str(e)}), 400


    @app.route('/delete_vehicle/<string:vin>', methods=['DELETE'])
    def delete_vehicle(vin):
        """
        Deletes a vehicle from the database based on the VIN
        """
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Vehicle WHERE vin = %s RETURNING vin;", (vin,))
            deleted_vin = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            if deleted_vin:
                return '', 204
            else:
                return jsonify({"error": "Vehicle not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 400
