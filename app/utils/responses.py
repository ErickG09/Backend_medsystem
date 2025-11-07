from flask import jsonify

def ok(data=None, **kwargs):
    payload = {"status": "ok"}
    if data is not None:
        payload["data"] = data
    payload.update(kwargs)
    return jsonify(payload), 200

def created(data=None, **kwargs):
    payload = {"status": "created"}
    if data is not None:
        payload["data"] = data
    payload.update(kwargs)
    return jsonify(payload), 201

def error(message="error", status=400, **kwargs):
    payload = {"message": message}
    payload.update(kwargs)
    return jsonify(payload), status
