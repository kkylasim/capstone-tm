from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

from db import db, Tenant, Rule, Country, TenantRule, seed_db
from fake import Data, TransactionInput, Scenario, RuleType, Direction

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rules_db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
seed_db(app)

@app.route('/tenants', methods=['GET'])
def get_tenants():
    tenants = [t.tenant_name for t in Tenant.query.all()]
    return jsonify({"tenants": tenants})

@app.route('/tenant-rules', methods=['POST'])
def get_tenant_rules():
    data = request.get_json()
    tenant_name = data.get('tenant', 'China')

    tenant = Tenant.query.filter_by(tenant_name=tenant_name).first()
    tenant_rules = TenantRule.query.filter_by(tenant_id=tenant.tenant_code).all()
    rule_ids = [tr.rule_id for tr in tenant_rules]

    rules = Rule.query.filter(Rule.rule_id.in_(rule_ids)).all()
    rules_data = [{"id": r.rule_id, "name": r.rule_name, "description": r.rule_description} for r in rules]

    return jsonify({"rules": rules_data})

@app.route('/generate-data', methods=['POST'])
def generate_data():
    """
    Output format: 
    Your output must be a text file that contain the following information: 
    CN - Tenant/Country 
    20320331 - Transaction date/business data
    ATC0000000079 - Transaction ID 
    AML-FTF-ALL-ALL-A-D07-FTR - Rule ID 
    8000 - Amount of transaction 
    CNY - Currency of transactions 
    RBK - Retail banking source system CN-CN - From Country - To Country 
    """
    data = request.get_json()
    print(data)

    tenant = data.get('tenant', 'CN')
    transaction_date = data.get('transaction_date', '20320331')
    scenario = data.get('scenario', 'positive')
    rules = data.get('rules', [])

    countries = Country.query.all()
    risk_dict = {
        tier: [c.country_code for c in countries if c.risk_tier == tier]
        for tier in {"high", "medium", "low"}
    }
    country_codes = {c.country_name: c.country_code for c in countries}
    inputs = []
    for name in rules:
        rule = Rule.query.filter(Rule.rule_name==name).first()
        if not rule:
            return jsonify({"error": f"Rule ID {name} not found"}), 404

        txn_input = TransactionInput(
            tenant=tenant,
            transaction_date=transaction_date,
            scenario=Scenario(scenario.lower()),
            rule_id=str(rule.rule_id),
            rule=rule.rule_description or rule.rule_name,
            rule_type=RuleType(rule.rule_type),
            frequency=rule.frequency,
            direction=Direction(rule.direction) if rule.direction else None,
            threshold=rule.threshold,
        )
        inputs.append(txn_input)
    df = Data.generate_dataset(inputs, risk_dict, country_codes)
    results = df.to_dict(orient='records')
    return jsonify({"results": results})


if __name__ == "__main__":
    app.run(debug=True)


