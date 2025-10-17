from flask import Flask, jsonify, request
from flask_cors import CORS
# import openai
from dotenv import load_dotenv
import os
import json

from db import db, Tenant, Rule, TenantRule  
from fake import Data, TransactionInput, Scenario, RuleType, Direction

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rules_db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

## Initialising tables ##
with app.app_context():
    db.create_all()

## Helper for seeding data ##
def seed_data():
    """Helper to seed tenants and rules."""
    Tenant.query.delete()
    Rule.query.delete()
    TenantRule.query.delete()
    db.session.commit()

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

    return "Database seeded successfully!"



@app.route('/api/hello')
def hello():
    return jsonify({"message": "Hello from Flask backend!"})


@app.route('/config', methods=['GET'])
def get_config():
    # tenants = ["Tenant 1", "Tenant 2", "Tenant 3"]

    # rules = [
    #     {"name": "Option A", "description": "Enables feature A."},
    #     {"name": "Option B", "description": "Enables feature B."},
    #     {"name": "Option C", "description": "Test scenario C."},
    #     {"name": "Option D", "description": "Special configuration D."}
    # ]

    # return jsonify({
    #     "tenants": tenants,
    #     "rules": rules
    # })
    tenants = [t.tenant_name for t in Tenant.query.all()]
    rules = [{"id": r.rule_id, "name": r.rule_name, "description": r.rule_description} for r in Rule.query.all()]
    return jsonify({"tenants": tenants, "rules": rules})

@app.route('/seed', methods=['POST'])
def seed_database():
    """HTTP endpoint to seed DB."""
    msg = seed_data()
    return jsonify({"message": msg})

@app.route('/generate-data', methods=['POST'])
def generate_data():
    data = request.get_json()

    tenant = data.get('tenant', 'CN')
    transaction_date = data.get('transaction_date', '20320331')
    scenario = data.get('scenario', 'positive')
    rules = data.get('rules', [])

    #     Output format: 
    #     Your output must be a text file that contain the following information: 
    #     CN - Tenant/Country 
    #     20320331 - Transaction date/business data
    #     ATC0000000079 - Transaction ID 
    #     AML-FTF-ALL-ALL-A-D07-FTR - Rule ID 
    #     8000 - Amount of transaction 
    #     CNY - Currency of transactions 
    #     RBK - Retail banking source system CN-CN - From Country - To Country 
    inputs = []
    for id in rules:
        rule = Rule.query.get(id)
        if not rule:
            return jsonify({"error": f"Rule ID {id} not found"}), 404
        #TEMP Prohibited country
        prob_temp = 'PK'
        txn_input = TransactionInput(
            tenant=tenant,
            transaction_date=transaction_date,
            scenario=Scenario(scenario),
            rule_id=str(rule.rule_id),
            rule=rule.rule_description or rule.rule_name,
            rule_type=RuleType(rule.rule_type),
            prohibited_country=prob_temp,
            frequency=rule.frequency,
            direction=Direction(rule.direction) if rule.direction else None,
            threshold=rule.threshold,
        )
        inputs.append(txn_input)
    df = Data.generate_dataset(inputs)
    results = df.to_dict(orient='records')
    return jsonify({"results": results})


    # mock_data = []
    # for idx, rule_id in enumerate(rules):
    #     mock_data.append({
    #         "tenant": tenant,
    #         "transaction_date": transaction_date,
    #         "transaction_id": f"ATC00000000{79 + idx}",
    #         "rule_id": rule_id,
    #         "amount": str(8000 + idx * 2000),
    #         "currency": "CNY",
    #         "source_system": "RBK",
    #         "from_to_country": "CN_CN" if idx % 2 == 0 else "CN_SG",
    #         "scenario": scenario
    #     })

    # return jsonify({"results": mock_data})

@app.cli.command("seed")
def seed():
    """Command line: flask --app app.py seed"""
    with app.app_context():
        print(seed_data())


if __name__ == "__main__":
    app.run(debug=True)



# Set your OpenAI API key from the environment variable
# openai.api_key = os.getenv("OPENAI_API_KEY")
# client = openai.OpenAI()

# @app.route('/api/generate-data-gpt', methods=['GET'])
# def generate_data():
#     # Extract query parameters
#     tenant_id = request.args.get('tenant_id')
#     transaction_date = request.args.get('transaction_date')
#     scenario = request.args.get('scenario')
#     rule = request.args.get('rule')

#     # Validate required parameters
#     if not all([tenant_id, transaction_date, scenario, rule]):
#         return jsonify({"error": "Missing required parameters"}), 400

#     # Define the prompt for ChatGPT
#     my_prompt = f"""
#     Your task is to generate transaction data in a text file format that fulfil the criteria below. There are 4 inputs to help you generate the data: 
#     1) Tenant ID. The country code to generate from. For example, SG for singapore. 
#     2) Transaction date. Transaction date is when the transaction should start or occur from. 
#     3) Scenario: The scenario should be the polarity of the data generated. There are 3 types of scenarios, namely positive, negative and borderline. For example, if scenario is positive, and the rule is ">$10000 for 7 consecutive days", then you will need to generate 7 rows of data that has transaction amount >$10000. If scenario is negative, and the rule is ">$10000 for 7 consecutive days", then you will need to generate 7 rows of data that has at least one transaction amount <=$10000. If scenario is borderline, and the rule is ">$10000 for 7 consecutive days", then you will need to generate 7 rows of data that has at least one transaction amount =$10000. 
#     4) Rule. The type of transactions to generate. For example, a. If the transaction amount if > $100K b. If the transaction made to country is Iran c. If 3 ATM (source system) withdrawals made in 3 consecutive days with transaction amount more than $5K d. If money sent to 10 times to the same country where amount is less than $100

#     Output format: 
#     Your output must be a text file that contain the following information: 
#     CN - Tenant/Country 
#     20320331 - Transaction date/business data
#     ATC0000000079 - Transaction ID 
#     AML-FTF-ALL-ALL-A-D07-FTR - Rule ID 
#     8000 - Amount of transaction 
#     CNY - Currency of transactions 
#     RBK - Retail banking source system CN-CN - From Country - To Country 

#     Example output is: CN20320331ATC0000000079~##~CN~##~CN1021523002118CNY~##~8000~##~~##~positive AML-FTF-ALL-ALL-A-D07-FTR 0320331~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~TCOECDEGEN~##~~##~~##~CNMNTXN99~##~~##~20320331124925~##~UOB~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~6000~##~CNY~##~~##~~##~~##~~##~~##~~1~##~~##~~##~~##~~##~~##~RBK~##~~##~110~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~CN_CN~##~~##~~##~~##~~##~~##~4832~##~~##~~##~~##~~##~C~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~

#     Strictly generate the data based on the information below. 
#     Tenant ID: {tenant_id} 
#     Transaction date: {transaction_date} 
#     Scenario: {scenario} 
#     Rule: {rule}
#     """
#     app.logger.info(f"Generated prompt: {my_prompt}") 

#     try:
#         # Call the ChatGPT API
#         response = client.responses.create(
#             model="gpt-5-mini",  # Use the appropriate engine
#             input=my_prompt
#         )

#         # Extract the generated text
#         generated_data = response.output_text
#         app.logger.info(f"API response:\n{response.output_text}")

#         # Return the generated data as JSON
#         return jsonify({"results": generated_data})

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500