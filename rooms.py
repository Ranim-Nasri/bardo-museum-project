from flask import Blueprint, request, jsonify
from models import Room, db

rooms_bp = Blueprint('rooms', __name__, url_prefix='/rooms')

@rooms_bp.route('/', methods=['POST'])
def add_rooms():
    data = request.json
    try:
        if isinstance(data, list):
            rooms = [Room(**r) for r in data]
            db.session.add_all(rooms)
        else:
            room = Room(**data)
            db.session.add(room)
        db.session.commit()
        return jsonify({"message": "Rooms added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@rooms_bp.route('/', methods=['GET'])
def get_rooms():
    rooms = Room.query.all()  # Fetch all rooms from the database
    # Return the room details in JSON format
    return jsonify([{
        "id": room.id,
        "name": room.name,
        "level": room.level,
        "type": room.type,
        "connections": room.connections
    } for room in rooms]), 200

@rooms_bp.route('/<int:room_id>/connections', methods=['GET'])
def get_room_connections(room_id):
    try:
        room = Room.query.get(room_id)
        if room:
            connections = room.connections_list  # Assuming `connections_list` gives a list of connected room names
            return jsonify(connections), 200
        else:
            return jsonify({"error": "Room not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rooms_bp.route('/<int:room_id>', methods=['GET'])
def get_room_by_id(room_id):
    try:
        room = Room.query.get(room_id)  # Fetch the room from the database by ID

        if room:
            return jsonify({
                "id": room.id,
                "name": room.name,
                "level": room.level,
                "type": room.type,
                "connections": room.connections
            }), 200
        else:
            return jsonify({"error": "Room not found"}), 404  # Room not found

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Server error

@rooms_bp.route('/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    try:
        # Get the data to update the room
        data = request.get_json()

        # Find the room to update
        room = Room.query.get(room_id)

        if not room:
            return jsonify({"error": "Room not found"}), 404

        # Update room attributes
        room.name = data.get("name", room.name)
        room.level = data.get("level", room.level)
        room.type = data.get("type", room.type)
        room.connections_list = data.get("connections", room.connections_list)

        # Commit the changes
        db.session.commit()
        return jsonify({"message": "Room updated successfully", "room": room.name}), 200

    except Exception as e:
        db.session.rollback()  # Rollback the transaction if there's an error
        return jsonify({"error": str(e)}), 400  # Return the error message
    
@rooms_bp.route('/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    try:
        # Find the room to delete
        room = Room.query.get(room_id)

        if not room:
            return jsonify({"error": "Room not found"}), 404

        # Delete the room
        db.session.delete(room)
        db.session.commit()
        return jsonify({"message": "Room deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()  # Rollback the transaction if there's an error
        return jsonify({"error": str(e)}), 400  # Return the error message
