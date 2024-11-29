"""Functions that interact with the database."""

from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection
from datetime import datetime


def format_subjects(subjects: list[dict]) -> list[dict]:
    subjects_formatted = []
    for subject in subjects:
        date_str = subject["date_of_birth"].strftime("%Y-%m-%d")
        subjects_formatted.append({
            "subject_id": subject["subject_id"],
            "subject_name": subject["subject_name"],
            "species_name": subject["species_name"],
            "date_of_birth": date_str
        })
    return subjects_formatted


def format_experiments(experiments: list[dict], score_over:str ) -> list[dict]:
    experiments_formatted = []
    for experiment in experiments:
        score_percentage = float((experiment["score"] / experiment["max_score"]) * 100)
        if score_percentage > int(score_over):
            date_str = experiment["experiment_date"].strftime("%Y-%m-%d")
            experiments_formatted.append({
                "experiment_id": experiment["experiment_id"],
                "subject_id": experiment["subject_id"],
                "species": experiment["species_name"],
                "experiment_date": date_str,
                "experiment_type": experiment["type_name"],
                "score": f'{(score_percentage/100):.2%}'
                    })
    return experiments_formatted


def get_db_connection(dbname,
                      password="postgres") -> connection:
    """Returns a DB connection."""

    return connect(dbname=dbname,
                   host="localhost",
                   port=5432,
                   password=password,
                   cursor_factory=RealDictCursor)


def get_subjects(conn) -> list[dict]:
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM subject
        JOIN species USING (species_id)
        ORDER BY subject.date_of_birth DESC;
         """)
    subjects = cur.fetchall()
    cur.close()
    return format_subjects(subjects)


def get_experiments(type: str, score_over: int, conn) -> list[dict]:
    if not score_over:
        score_over = 0
    if not type:
        type = ''
    else:
        type = type.lower()
    cur = conn.cursor()
    cur.execute(f"""
            SELECT experiment.experiment_id, experiment.subject_id, species.species_name, experiment.experiment_date, experiment_type.type_name, experiment.score, experiment_type.max_score
            FROM experiment
            JOIN subject USING (subject_id)
            JOIN species USING (species_id)
            JOIN experiment_type USING(experiment_type_id)
            WHERE experiment_type.type_name LIKE '%{type}%'
            ORDER BY experiment.experiment_date DESC
            ;
         """)
    experiments = cur.fetchall()
    cur.close()
    return format_experiments(experiments, score_over)


def delete_experiment_by_id(id: int, conn) -> dict | None:
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM experiment
        WHERE experiment_id = %s
        RETURNING experiment_id, experiment_date
        ;""",
        [id])
    experiment = cur.fetchall()
    if experiment:
        experiment = experiment[0]
        correct_date = experiment["experiment_date"].strftime("%Y-%m-%d")
        formatted_experiment = {
        "experiment_id": experiment["experiment_id"],
        "experiment_date": correct_date
        }
        cur.close()
        conn.commit()
        return formatted_experiment
    cur.close()
    conn.commit()
    return experiment


def insert_experiment(subject_id, score, experiment_type, experiment_date, conn) -> dict:
    if not experiment_date:
        experiment_date = datetime.now().strftime("%Y-%m-%d")
    cur = conn.cursor()
    cur.execute( """
        SELECT experiment_type_id
        FROM experiment_type
        WHERE type_name = %s
                 """, [experiment_type.lower()])
    experiment_type__id = cur.fetchone().get("experiment_type_id")
    cur.execute("""
        INSERT INTO experiment (subject_id, experiment_type_id, experiment_date, score )
        VALUES (%s, %s, %s, %s)
        RETURNING *
        ;
        """,
        [subject_id, experiment_type__id, experiment_date, score])
    experiment = cur.fetchall()
    if experiment:
        experiment = experiment[0]
        correct_date = experiment["experiment_date"].strftime("%Y-%m-%d")
        formatted_experiment = {
            "experiment_id": experiment["experiment_id"],
            "subject_id": experiment["subject_id"],
            "experiment_type_id": experiment["experiment_type_id"],
            "experiment_date": correct_date,
            "score": experiment["score"]
            }
        cur.close()
        conn.commit()
        return formatted_experiment
    cur.close()
    return experiment
