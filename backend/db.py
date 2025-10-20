from flask import request, jsonify
from flask_sqlalchemy import SQLAlchemy
from enum import Enum
import json
import random

db = SQLAlchemy()

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


class TenantRule(db.Model):
    __tablename__ = 'tenant_rules'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.tenant_id'))
    rule_id = db.Column(db.Integer, db.ForeignKey('rules.rule_id'))


def seed_db(app):
    """Create tables and seed sample data when the application starts.

    Call this from the main application after `db.init_app(app)` so the
    database is created and seeded exactly once by the single Flask app.
    """
    with app.app_context():
        # create tables if they don't exist
        db.create_all()

        # Seed only if empty
        if not Tenant.query.first():
            uob_tenants = [
                ('AU', "Australia"),
                ('BN', "Brunei"),
                ('CA', "Canada"),
                ('CN', "China"),
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
                {"country_code": "BN", "country_name": "Brunei", "risk_tier": "medium"},

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

            tenant_rules = []
            for tenant_code, tenant_name in uob_tenants:
                selected_rules = random.sample(range(1, len(rules)+1), random.randint(2, len(rules)))
                for r in selected_rules:
                    curr = TenantRule(tenant_id=tenant_code, rule_id=r)
                    tenant_rules.append(curr)

            db.session.add_all(tenant_rules)
            db.session.commit()

            print("✅ Sample data added.")
