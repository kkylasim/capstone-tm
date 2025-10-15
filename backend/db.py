from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3, json

app = FastAPI(title="AML Rule Manager")

# ---------- Database setup ----------
def get_connection():
    conn = sqlite3.connect("rules_db.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS tenants (
        tenant_id INTEGER PRIMARY KEY AUTOINCREMENT,
        tenant_name TEXT
    );
    CREATE TABLE IF NOT EXISTS rules (
        rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
        rule_name TEXT,
        rule_description TEXT,
        parameters TEXT
    );
    CREATE TABLE IF NOT EXISTS tenant_rules (
        tenant_id INTEGER,
        rule_id INTEGER,
        parameters TEXT,
        FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
        FOREIGN KEY (rule_id) REFERENCES rules(rule_id)
    );
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- Models ----------
class RuleCreate(BaseModel):
    tenant_id: int
    rule_name: str
    rule_description: str
    parameters: dict  

# ---------- Endpoints ----------

@app.post("/rules")
def create_rule(rule: RuleCreate):
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Check if rule already exists globally
    cursor.execute("SELECT rule_id FROM rules WHERE rule_name = ?", (rule.rule_name,))
    existing_rule = cursor.fetchone()

    if existing_rule:
        rule_id = existing_rule["rule_id"]
    else:
        cursor.execute(
            "INSERT INTO rules (rule_name, rule_description, parameters) VALUES (?, ?, ?)",
            (rule.rule_name, rule.rule_description, json.dumps(rule.parameters))
        )
        rule_id = cursor.lastrowid

    # 2. Link tenant and rule
    cursor.execute(
        "INSERT INTO tenant_rules (tenant_id, rule_id, parameters) VALUES (?, ?, ?)",
        (rule.tenant_id, rule_id, json.dumps(rule.parameters))
    )

    conn.commit()
    conn.close()
    return {"message": "Rule created successfully", "rule_id": rule_id}


@app.get("/rules/{tenant_id}")
def get_rules_for_tenant(tenant_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.rule_id, r.rule_name, r.rule_description, tr.parameters
        FROM tenant_rules tr
        JOIN rules r ON tr.rule_id = r.rule_id
        WHERE tr.tenant_id = ?
    """, (tenant_id,))
    rules = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"tenant_id": tenant_id, "rules": rules}


@app.post("/tenants")
def create_tenant(tenant_name: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tenants (tenant_name) VALUES (?)", (tenant_name,))
    conn.commit()
    conn.close()
    return {"message": f"Tenant '{tenant_name}' created successfully"}

