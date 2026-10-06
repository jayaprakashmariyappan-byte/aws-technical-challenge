"""
Scalable Web App — Flask + Gunicorn
Reads configuration from environment variables (injected by User Data from SSM).
"""
import os
import logging
import boto3
import pymysql
from flask import Flask, jsonify, request

# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ── DB config from environment ─────────────────────────────────────────────
DB_CONFIG = {
    "host":     os.environ.get("DB_HOST", "localhost"),
    "user":     os.environ.get("DB_USER", "dbadmin"),
    "password": os.environ.get("DB_PASS", ""),
    "database": os.environ.get("DB_NAME", "appdb"),
    "connect_timeout": 5,
    "cursorclass": pymysql.cursors.DictCursor,
}

S3_BUCKET = os.environ.get("S3_BUCKET", "")
AWS_REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")


def get_db():
    """Return a fresh PyMySQL connection."""
    return pymysql.connect(**DB_CONFIG)


# ── Routes ─────────────────────────────────────────────────────────────────

@app.route("/health")
def health():
    """ALB / Route 53 health check endpoint."""
    return jsonify(status="ok"), 200


@app.route("/")
def index():
    return jsonify(
        message="Scalable Web Application on AWS",
        environment=os.environ.get("ENV", "prod"),
        region=AWS_REGION,
    ), 200


@app.route("/db-check")
def db_check():
    """Verify database connectivity."""
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("SELECT VERSION() AS version")
            row = cur.fetchone()
        conn.close()
        return jsonify(db="connected", version=row["version"]), 200
    except Exception as exc:
        logger.exception("DB connectivity check failed")
        return jsonify(db="error", detail=str(exc)), 500


@app.route("/items", methods=["GET"])
def list_items():
    """List items from the database."""
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM items LIMIT 100")
            rows = cur.fetchall()
        conn.close()
        return jsonify(items=rows), 200
    except Exception as exc:
        logger.exception("Failed to list items")
        return jsonify(error=str(exc)), 500


@app.route("/items", methods=["POST"])
def create_item():
    """Create a new item."""
    data = request.get_json(force=True)
    name = data.get("name", "").strip()
    if not name:
        return jsonify(error="'name' is required"), 400
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO items (name, created_at) VALUES (%s, NOW())",
                (name,),
            )
            conn.commit()
            item_id = cur.lastrowid
        conn.close()
        return jsonify(id=item_id, name=name), 201
    except Exception as exc:
        logger.exception("Failed to create item")
        return jsonify(error=str(exc)), 500


@app.route("/s3-assets")
def list_s3_assets():
    """List static assets in S3 (demonstrates IAM role access)."""
    if not S3_BUCKET:
        return jsonify(error="S3_BUCKET not configured"), 500
    try:
        s3 = boto3.client("s3", region_name=AWS_REGION)
        resp = s3.list_objects_v2(Bucket=S3_BUCKET, MaxKeys=20)
        keys = [obj["Key"] for obj in resp.get("Contents", [])]
        return jsonify(bucket=S3_BUCKET, assets=keys), 200
    except Exception as exc:
        logger.exception("Failed to list S3 assets")
        return jsonify(error=str(exc)), 500


# ── DB schema bootstrap ────────────────────────────────────────────────────

def init_db():
    """Create tables if they don't exist (runs once on startup)."""
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id         INT AUTO_INCREMENT PRIMARY KEY,
                    name       VARCHAR(255) NOT NULL,
                    created_at DATETIME NOT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            conn.commit()
        conn.close()
        logger.info("DB schema initialised")
    except Exception as exc:
        logger.warning("DB init skipped (DB may not be ready yet): %s", exc)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8000, debug=False)
