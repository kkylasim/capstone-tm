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

        rule_data["parameters"]["rule_id"] = rule.rule_id

        rules.append(rule_data)

    return jsonify({"tenant_id": tenant_id, "rules": rules})


if __name__ == '__main__':
    app.run(debug=True)
