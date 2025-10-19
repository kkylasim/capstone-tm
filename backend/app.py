from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

from db import db, Tenant, Rule, Country, TenantRule  
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

@app.route('/tenants', methods=['GET'])
def get_tenants():
    tenants = [t.tenant_name for t in Tenant.query.all()]
    return jsonify({"tenants": tenants})

@app.route('/tenant-rules', methods=['POST'])
def get_tenant_rules():
    data = request.get_json()
    tenant_name = data.get('tenant', 'CN')

    tenant = Tenant.query.filter_by(tenant_name=tenant_name).first()
    tenant_rules = TenantRule.query.filter_by(tenant_id=tenant.tenant_id).all()
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



# import openai

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
