import sqlite3

from flask import current_app, g


def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()


def init_db():
    db = get_db()

    # check if db is already initialised
    if "versions" in get_tables():
        return

    print(" * Initialising database")

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def get_tables():
    db = get_db()

    return [
        row["name"].lower()
        for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        ).fetchall()
    ]


def add_versions(pipeline_id, sesquencescape_version, limber_version):
    db = get_db()

    db.executescript(
        "INSERT INTO versions (pipeline_id, sequencescape_version, sequencescape_url, limber_version, limber_url) VALUES ('{}', '{}', '{}', '{}', '{}');".format(
            pipeline_id,
            sesquencescape_version[0],
            sesquencescape_version[1],
            limber_version[0],
            limber_version[1],
        )
    )
    db.commit()


def get_versions(pipeline_id=None, limit=20):
    db = get_db()

    if pipeline_id:
        return db.execute(
            "SELECT * FROM versions WHERE pipeline_id = ? ORDER BY created_at DESC LIMIT ?;",
            (pipeline_id, limit),
        ).fetchone()

    return db.execute(
        "SELECT * FROM versions ORDER BY created_at DESC LIMIT ?;",
        (limit,),
    ).fetchall()
