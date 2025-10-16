from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from enum import Enum
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rules_db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Scenario(str, Enum):
    positive = "positive"
    negative = "negative"
    borderline = "borderline"

class RuleType(str, Enum):
    transaction_amount = "transaction amount"
    country = "country"
    frequency = "frequency"

class Direction(str, Enum):
    greater_than = "greater than"
    less_than = "less than"


class Tenant(db.Model):
    __tablename__ = 'tenants'
    tenant_id = db.Column(db.Integer, primary_key=True)
    tenant_name = db.Column(db.String, nullable=False)

class Rule(db.Model):
    __tablename__ = 'rules'
    rule_id = db.Column(db.Integer, primary_key=True)
    rule_name = db.Column(db.String, unique=True, nullable=False)
    rule_description = db.Column(db.String)

    # New fields
    rule_type = db.Column(db.String)  
    prohibited_country = db.Column(db.String, nullable=True)
    frequency = db.Column(db.Integer, nullable=True)
    direction = db.Column(db.String, nullable=True)  
    threshold = db.Column(db.Float, nullable=True)

    parameters = db.Column(db.Text)  # store as JSON string

class TenantRule(db.Model):
    __tablename__ = 'tenant_rules'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.tenant_id'))
    rule_id = db.Column(db.Integer, db.ForeignKey('rules.rule_id'))
    parameters = db.Column(db.Text)  # tenant-specific params

    tenant = db.relationship('Tenant', backref=db.backref('tenant_rules', cascade="all, delete-orphan"))
    rule = db.relationship('Rule', backref=db.backref('tenant_rules', cascade="all, delete-orphan"))


with app.app_context():
    db.create_all()

    # Only seed data if tables are empty
    if not Tenant.query.first():

        tenant1 = Tenant(tenant_name="Alpha Bank")
        tenant2 = Tenant(tenant_name="Beta Fintech")
        tenant3 = Tenant(tenant_name="Gamma Payments")

        db.session.add_all([tenant1, tenant2, tenant3])
        db.session.commit()

        rules_data = [
            {
                "rule_name": "High Transaction Amount",
                "rule_description": "Flags transactions above threshold",
                "rule_type": "transaction amount",
                "direction": "greater than",
                "threshold": 10000.0,
                "parameters": {"currency": "USD"}
            },
            {
                "rule_name": "Prohibited Country Transaction",
                "rule_description": "Blocks transactions to high-risk countries",
                "rule_type": "country",
                "prohibited_country": "Iran",
                "parameters": {"severity": "high"}
            },
            {
                "rule_name": "Frequent Transactions",
                "rule_description": "Flags if transactions exceed frequency limit",
                "rule_type": "frequency",
                "direction": "greater than",
                "frequency": 5,
                "parameters": {"window": "1 day"}
            },
            {
                "rule_name": "Low Transaction Amount",
                "rule_description": "Flags suspiciously small transactions",
                "rule_type": "transaction amount",
                "direction": "less than",
                "threshold": 5.0,
                "parameters": {"alert_level": "low"}
            }
        ]

        rules = []
        for r in rules_data:
            rule = Rule(
                rule_name=r["rule_name"],
                rule_description=r["rule_description"],
                rule_type=r["rule_type"],
                prohibited_country=r.get("prohibited_country"),
                frequency=r.get("frequency"),
                direction=r.get("direction"),
                threshold=r.get("threshold"),
                parameters=json.dumps(r["parameters"])
            )
            rules.append(rule)
        db.session.add_all(rules)
        db.session.commit()

        # --- Tenant Rules (link tenants to rules) ---
        tenant_rules = [
            TenantRule(tenant_id=tenant1.tenant_id, rule_id=rules[0].rule_id, parameters=json.dumps({"active": True})),
            TenantRule(tenant_id=tenant1.tenant_id, rule_id=rules[1].rule_id, parameters=json.dumps({"risk": "high"})),
            TenantRule(tenant_id=tenant1.tenant_id, rule_id=rules[2].rule_id, parameters=json.dumps({"limit": 5})),

            TenantRule(tenant_id=tenant2.tenant_id, rule_id=rules[1].rule_id, parameters=json.dumps({"risk": "medium"})),
            TenantRule(tenant_id=tenant2.tenant_id, rule_id=rules[2].rule_id, parameters=json.dumps({"limit": 10})),
            TenantRule(tenant_id=tenant2.tenant_id, rule_id=rules[3].rule_id, parameters=json.dumps({"enabled": True})),

            TenantRule(tenant_id=tenant3.tenant_id, rule_id=rules[0].rule_id, parameters=json.dumps({"currency": "SGD"})),
            TenantRule(tenant_id=tenant3.tenant_id, rule_id=rules[2].rule_id, parameters=json.dumps({"window": "12h"})),
            TenantRule(tenant_id=tenant3.tenant_id, rule_id=rules[3].rule_id, parameters=json.dumps({"alert_level": "moderate"})),
        ]

        db.session.add_all(tenant_rules)
        db.session.commit()

        print("Sample data addded")


@app.route('/tenants', methods=['POST'])
def create_tenant():
    data = request.get_json()
    tenant_name = data.get('tenant_name')
    if not tenant_name:
        return jsonify({"error": "tenant_name is required"}), 400

    tenant = Tenant(tenant_name=tenant_name)
    db.session.add(tenant)
    db.session.commit()
    return jsonify({"message": f"Tenant '{tenant_name}' created successfully", "tenant_id": tenant.tenant_id})


@app.route('/rules', methods=['POST'])
def create_rule():
    data = request.get_json()

    tenant_id = data.get('tenant_id')
    rule_name = data.get('rule_name')
    rule_description = data.get('rule_description')
    rule_type = data.get('rule_type')
    prohibited_country = data.get('prohibited_country')
    frequency = data.get('frequency')
    direction = data.get('direction')
    threshold = data.get('threshold')
    parameters = data.get('parameters', {})

    # Check tenant exists
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return jsonify({"error": f"Tenant {tenant_id} not found"}), 404

    # Check if rule exists globally
    rule = Rule.query.filter_by(rule_name=rule_name).first()
    if not rule:
        rule = Rule(
            rule_name=rule_name,
            rule_description=rule_description,
            rule_type=rule_type,
            prohibited_country=prohibited_country,
            frequency=frequency,
            direction=direction,
            threshold=threshold,
            parameters=json.dumps(parameters)
        )
        db.session.add(rule)
        db.session.commit()

    # Link tenant and rule
    tenant_rule = TenantRule(
        tenant_id=tenant_id,
        rule_id=rule.rule_id,
        parameters=json.dumps(parameters)
    )
    db.session.add(tenant_rule)
    db.session.commit()

    return jsonify({"message": "Rule created successfully", "rule_id": rule.rule_id})


@app.route('/rules/<int:tenant_id>', methods=['GET'])
def get_rules_for_tenant(tenant_id):
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return jsonify({"error": f"Tenant {tenant_id} not found"}), 404

    tenant_rules = TenantRule.query.filter_by(tenant_id=tenant_id).all()
    rules = []

    for tr in tenant_rules:
        rule = Rule.query.get(tr.rule_id)
        rule_data = {
            "rule_id": rule.rule_id,
            "rule_name": rule.rule_name,
            "rule_description": rule.rule_description,
            "rule_type": rule.rule_type,
            "prohibited_country": rule.prohibited_country,
            "frequency": rule.frequency,
            "direction": rule.direction,
            "threshold": rule.threshold,
            "parameters": json.loads(tr.parameters)
        }

        # Include rule_id in parameters for clarity
        rule_data["parameters"]["rule_id"] = rule.rule_id

        rules.append(rule_data)

    return jsonify({"tenant_id": tenant_id, "rules": rules})



if __name__ == '__main__':
    app.run(debug=True)
