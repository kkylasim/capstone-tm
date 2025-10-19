from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from enum import Enum
import json
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rules_db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Scenario(str, Enum):
    positive = "positive"
    negative = "negative"
    boundary = "boundary"


class RuleType(str, Enum):
    transaction_amount = "transaction amount"
    country = "country"
    frequency = "frequency"
    composite = "composite"


class Direction(str, Enum):
    greater_than = "greater than"
    less_than = "less than"


class Tenant(db.Model):
    __tablename__ = 'tenants'
    tenant_id = db.Column(db.Integer, primary_key=True)
    tenant_code = db.Column(db.String, unique=True, nullable=False)
    tenant_name = db.Column(db.String, nullable=False)


class Rule(db.Model):
    __tablename__ = 'rules'
    rule_id = db.Column(db.Integer, primary_key=True)
    rule_name = db.Column(db.String, unique=True, nullable=False)
    rule_description = db.Column(db.String)
    rule_type = db.Column(db.String)
    frequency = db.Column(db.Integer, nullable=True)
    direction = db.Column(db.String, nullable=True)
    threshold = db.Column(db.Float, nullable=True)
    parameters = db.Column(db.Text)  # store as JSON string


class Country(db.Model):
    __tablename__ = 'countries'
    country_id = db.Column(db.Integer, primary_key=True)
    country_code = db.Column(db.String, unique=True, nullable=False)
    country_name = db.Column(db.String, unique=True, nullable=False)
    risk_tier = db.Column(db.String, nullable=False)  # e.g., high, medium, low


# class RuleCountry(db.Model):
#     __tablename__ = 'rule_countries'
#     id = db.Column(db.Integer, primary_key=True)
#     rule_id = db.Column(db.Integer, db.ForeignKey('rules.rule_id'))
#     country_id = db.Column(db.Integer, db.ForeignKey('countries.country_id'))

#     rule = db.relationship('Rule', backref=db.backref('rule_countries', cascade="all, delete-orphan"))
#     country = db.relationship('Country', backref=db.backref('rule_countries', cascade="all, delete-orphan"))


class TenantRule(db.Model):
    __tablename__ = 'tenant_rules'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.tenant_id'))
    rule_id = db.Column(db.Integer, db.ForeignKey('rules.rule_id'))
    #parameters = db.Column(db.Text)
    #tenant = db.relationship('Tenant', backref=db.backref('tenant_rules', cascade="all, delete-orphan"))
    #rule = db.relationship('Rule', backref=db.backref('tenant_rules', cascade="all, delete-orphan"))

with app.app_context():
    db.drop_all()
    db.create_all()

    # Seed only if empty
    if not Tenant.query.first():
        # tenant1 = Tenant(tenant_name="Alpha Bank")
        # tenant2 = Tenant(tenant_name="Beta Fintech")
        # tenant3 = Tenant(tenant_name="Gamma Payments")

        uob_tenants = [
            ('AU', "Australia"),
            ('BN', "Brunei"),
            ('CA', "Canada"),
            ('CN', "Mainland China"),
            ('FR', "France"),
            ('HK', "Hong Kong"),
            ('IN', "India"),
            ('ID', "Indonesia"),
            ('JP', "Japan"),
            ('MY', "Malaysia"),
            ('MM', "Myanmar"),
            ('PH', "Philippines"),
            ('SG', "Singapore"),
            ('KR', "South Korea"),
            ('TW', "Taiwan"),
            ('TH', "Thailand"),
            ('GB', "United Kingdom"),
            ('US', "United States of America"),
            ('VN', "Vietnam")
        ]
        tenants = [Tenant(tenant_code=code, tenant_name=name) for code, name in uob_tenants]

        db.session.add_all(tenants)
        db.session.commit()

        # ---- Seed Rules ----
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
            },
            {
                "rule_name": "Frequent Transaction Above Threshold",
                "rule_description": "Flags frequent transactions above a certain amount",
                "rule_type": "composite",
                "direction": "greater than",
                "frequency": 5,
                "threshold": 5000.0,
                "parameters": {"window": "1 day", "currency": "USD"}
            }
        ]

        rules = []
        for r in rules_data:
            rule = Rule(
                rule_name=r["rule_name"],
                rule_description=r["rule_description"],
                rule_type=r["rule_type"],
                frequency=r.get("frequency"),
                direction=r.get("direction"),
                threshold=r.get("threshold"),
                parameters=json.dumps(r["parameters"])
            )
            rules.append(rule)
        db.session.add_all(rules)
        db.session.commit()

        # ---- Seed Countries ----
        # countries_data = [
        #     {"country_name": "North Korea", "risk_tier": "high"},
        #     {"country_name": "Iran", "risk_tier": "high"},
        #     {"country_name": "Syria", "risk_tier": "high"},
        #     {"country_name": "Singapore", "risk_tier": "low"},
        #     {"country_name": "Malaysia", "risk_tier": "medium"}
        # ]

        countries_data = [
            # High-risk countries
            {"country_code": "KP", "country_name": "North Korea", "risk_tier": "high"},
            {"country_code": "IR", "country_name": "Iran", "risk_tier": "high"},
            {"country_code": "SY", "country_name": "Syria", "risk_tier": "high"},
            {"country_code": "AF", "country_name": "Afghanistan", "risk_tier": "high"},
            {"country_code": "IQ", "country_name": "Iraq", "risk_tier": "high"},
            {"country_code": "VE", "country_name": "Venezuela", "risk_tier": "high"},
            {"country_code": "SO", "country_name": "Somalia", "risk_tier": "high"},
            {"country_code": "LY", "country_name": "Libya", "risk_tier": "high"},
            {"country_code": "YE", "country_name": "Yemen", "risk_tier": "high"},
            {"country_code": "SD", "country_name": "Sudan", "risk_tier": "high"},
            {"country_code": "SS", "country_name": "South Sudan", "risk_tier": "high"},
            {"country_code": "HT", "country_name": "Haiti", "risk_tier": "high"},
            {"country_code": "CD", "country_name": "Democratic Republic of the Congo", "risk_tier": "high"},
            {"country_code": "CF", "country_name": "Central African Republic", "risk_tier": "high"},
            {"country_code": "ML", "country_name": "Mali", "risk_tier": "high"},

            # Medium-risk countries
            {"country_code": "MY", "country_name": "Malaysia", "risk_tier": "medium"},
            {"country_code": "TH", "country_name": "Thailand", "risk_tier": "medium"},
            {"country_code": "IN", "country_name": "India", "risk_tier": "medium"},
            {"country_code": "ID", "country_name": "Indonesia", "risk_tier": "medium"},
            {"country_code": "PH", "country_name": "Philippines", "risk_tier": "medium"},
            {"country_code": "CN", "country_name": "China", "risk_tier": "medium"},
            {"country_code": "MM", "country_name": "Myanmar", "risk_tier": "medium"},
            {"country_code": "VN", "country_name": "Vietnam", "risk_tier": "medium"},
            {"country_code": "BR", "country_name": "Brazil", "risk_tier": "medium"},
            {"country_code": "RU", "country_name": "Russia", "risk_tier": "medium"},

            # Low-risk countries
            {"country_code": "SG", "country_name": "Singapore", "risk_tier": "low"},
            {"country_code": "AU", "country_name": "Australia", "risk_tier": "low"},
            {"country_code": "CA", "country_name": "Canada", "risk_tier": "low"},
            {"country_code": "JP", "country_name": "Japan", "risk_tier": "low"},
            {"country_code": "DE", "country_name": "Germany", "risk_tier": "low"},
            {"country_code": "US", "country_name": "United States of America", "risk_tier": "low"},
            {"country_code": "GB", "country_name": "United Kingdom", "risk_tier": "low"},
            {"country_code": "KR", "country_name": "South Korea", "risk_tier": "low"},
            {"country_code": "HK", "country_name": "Hong Kong", "risk_tier": "low"},
            {"country_code": "FR", "country_name": "France", "risk_tier": "low"},
            {"country_code": "TW", "country_name": "Taiwan", "risk_tier": "low"},
            {"country_code": "NZ", "country_name": "New Zealand", "risk_tier": "low"}
        ]

        countries = []
        for c in countries_data:
            country = Country(country_code=c["country_code"], 
                              country_name=c["country_name"], 
                              risk_tier=c["risk_tier"])
            countries.append(country)
        db.session.add_all(countries)
        db.session.commit()

        # rule_country_links = [
        #     {"rule": rules[1], "country": countries[0]},  # NK
        #     {"rule": rules[1], "country": countries[1]},  # Iran
        #     {"rule": rules[1], "country": countries[2]},  # Syria
        # ]

        # for link in rule_country_links:
        #     db.session.add(RuleCountry(rule=link["rule"], country=link["country"]))
        # db.session.commit()

         # TenantRule(tenant_id=tenants[0].tenant_id, rule_id=rules[0].rule_id, parameters=json.dumps({"active": True})),
        # TenantRule(tenant_id=tenants[0].tenant_id, rule_id=rules[1].rule_id, parameters=json.dumps({"risk": "high"})),
        # TenantRule(tenant_id=tenants[0].tenant_id, rule_id=rules[2].rule_id, parameters=json.dumps({"limit": 5})),

        # TenantRule(tenant_id=tenants[1].tenant_id, rule_id=rules[1].rule_id, parameters=json.dumps({"risk": "medium"})),
        # TenantRule(tenant_id=tenants[1].tenant_id, rule_id=rules[2].rule_id, parameters=json.dumps({"limit": 10})),
        # TenantRule(tenant_id=tenants[1].tenant_id, rule_id=rules[3].rule_id, parameters=json.dumps({"enabled": True})),

        # TenantRule(tenant_id=tenants[2].tenant_id, rule_id=rules[0].rule_id, parameters=json.dumps({"currency": "SGD"})),
        # TenantRule(tenant_id=tenants[2].tenant_id, rule_id=rules[2].rule_id, parameters=json.dumps({"window": "12h"})),
        # TenantRule(tenant_id=tenants[2].tenant_id, rule_id=rules[3].rule_id, parameters=json.dumps({"alert_level": "moderate"})),
        tenant_rules = []
        for tenant_code, tenant_name in uob_tenants:
            selected_rules = random.sample(range(1, len(rules)+1), random.randint(2, len(rules)))
            for r in selected_rules:
                curr = TenantRule(tenant_id=tenant_code, rule_id=r)
                tenant_rules.append(curr)

        db.session.add_all(tenant_rules)
        db.session.commit()

        print("✅ Sample data added.")


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


@app.route('/rules/<int:tenant_id>', methods=['GET'])
def get_rules_for_tenant(tenant_id):
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return jsonify({"error": f"Tenant {tenant_id} not found"}), 404

    tenant_rules = TenantRule.query.filter_by(tenant_id=tenant_id).all()
    rules = []

    for tr in tenant_rules:
        rule = Rule.query.get(tr.rule_id)
        linked_countries = [
            {"country_name": rc.country.country_name, "risk_tier": rc.country.risk_tier}
            for rc in rule.rule_countries
        ]

        rule_data = {
            "rule_id": rule.rule_id,
            "rule_name": rule.rule_name,
            "rule_description": rule.rule_description,
            "rule_type": rule.rule_type,
            "direction": rule.direction,
            "threshold": rule.threshold,
            "frequency": rule.frequency,
            "countries": linked_countries,
            "parameters": json.loads(tr.parameters)
        }
        rule_data["parameters"]["rule_id"] = rule.rule_id

        rules.append(rule_data)

    return jsonify({"tenant_id": tenant_id, "rules": rules})


if __name__ == '__main__':
    app.run(debug=True)
