"""An API for handling marine experiments."""

from datetime import datetime

from flask import Flask, jsonify, request
from psycopg2 import sql

from database_functions import get_db_connection, get_subjects, get_experiments, delete_experiment_by_id, insert_experiment


app = Flask(__name__)

"""
For testing reasons; please ALWAYS use this connection. 
- Do not make another connection in your code
- Do not close this connection
"""
conn = get_db_connection("marine_experiments")


def verify_type(type: str) -> bool:
    if type is None:
        return True
    return type.lower() in {"intelligence", "obedience", "aggression"}


def verify_score(score_over: str) -> bool:
    if score_over is None:
        return True
    try:
        score_over = int(score_over)
    except:
        return False
    return  score_over >= 0 and score_over <= 100


def verify_subject_id(subject_id: str) -> bool:
    if not subject_id:
        return False
    for i in str(subject_id):
        if i not in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            return False
    try:
        subject_id = int(subject_id)
    except:
        return False
    return True


@app.get("/")
def home():
    """Returns an informational message."""
    return jsonify({
        "designation": "Project Armada",
        "resource": "JSON-based API",
        "status": "Classified"
    })


@app.get("/subject")
def subject():
    """Returns an informational message."""
    subjects = get_subjects(conn)
    return subjects, 200


@app.route("/experiment", methods = ["GET", "POST"])
def experiment():
    """Returns an informational message."""
    if request.method == "GET":
        type = request.args.get("type")
        score_over =  request.args.get("score_over")
        if not verify_type(type):
            return {"error": "Invalid value for 'type' parameter"}, 400
        if not verify_score(score_over):
            return {"error": "Invalid value for 'score_over' parameter"}, 400
        experiments = get_experiments(type, score_over, conn)
        return experiments, 200    
    if request.method == "POST":
        data = request.json
        score = data.get("score", None)
        experiment_type = data.get("experiment_type", None)
        subject_id = data.get("subject_id", None)
        experiment_date = data.get("experiment_date", None)
        if not score:
            return {"error": "Request missing key 'score'."}, 400
        if not experiment_type:
            return {"error": "Request missing key 'experiment_type'."}, 400
        if not subject_id:
            return {"error": "Request missing key 'subject_id'."}, 400
        if not verify_subject_id(subject_id):
            return {"error": "Invalid value for 'subject_id' parameter."}, 400
        if not verify_type(experiment_type):
            return {"error": "Invalid value for 'experiment_type' parameter."}, 400
        if not verify_score(score):
            return {"error": "Invalid value for 'score' parameter."}, 400
        experiment = insert_experiment(subject_id, score, experiment_type, experiment_date, conn)
        return experiment, 201


@app.route("/experiment/<id>", methods=["DELETE"])
def delete_experiment(id):
    if not id.isnumeric():
        return {"error": "ID must be an integer"}, 400
    experiment = delete_experiment_by_id(id, conn)
    if not experiment:
        return {"error": f"Unable to locate experiment with ID {id}."}, 404
    return experiment, 200


if __name__ == "__main__":
    app.config["DEBUG"] = True
    app.config["TESTING"] = True

    app.run(port=8000, debug=True)

    conn.close()
