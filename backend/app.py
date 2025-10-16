from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import openai
from dotenv import load_dotenv
import os, io, csv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Set your OpenAI API key from the environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()

@app.route('/api/generate-data-gpt', methods=['GET'])
def generate_data():
    # Extract query parameters
    tenant_id = request.args.get('tenant_id')
    transaction_date = request.args.get('transaction_date')
    scenario = request.args.get('scenario')
    rule = request.args.get('rule')

    # Validate required parameters
    if not all([tenant_id, transaction_date, scenario, rule]):
        return jsonify({"error": "Missing required parameters"}), 400

    # Define the prompt for ChatGPT
    my_prompt = f"""
    Your task is to generate transaction data in a text file format that fulfil the criteria below. There are 4 inputs to help you generate the data: 
    1) Tenant ID. The country code to generate from. For example, SG for singapore. 
    2) Transaction date. Transaction date is when the transaction should start or occur from. 
    3) Scenario: The scenario should be the polarity of the data generated. There are 3 types of scenarios, namely positive, negative and borderline. For example, if scenario is positive, and the rule is ">$10000 for 7 consecutive days", then you will need to generate 7 rows of data that has transaction amount >$10000. If scenario is negative, and the rule is ">$10000 for 7 consecutive days", then you will need to generate 7 rows of data that has at least one transaction amount <=$10000. If scenario is borderline, and the rule is ">$10000 for 7 consecutive days", then you will need to generate 7 rows of data that has at least one transaction amount =$10000. 
    4) Rule. The type of transactions to generate. For example, a. If the transaction amount if > $100K b. If the transaction made to country is Iran c. If 3 ATM (source system) withdrawals made in 3 consecutive days with transaction amount more than $5K d. If money sent to 10 times to the same country where amount is less than $100

    Output format: 
    Your output must be a text file that contain the following information: 
    CN - Tenant/Country 
    20320331 - Transaction date/business data
    ATC0000000079 - Transaction ID 
    AML-FTF-ALL-ALL-A-D07-FTR - Rule ID 
    8000 - Amount of transaction 
    CNY - Currency of transactions 
    RBK - Retail banking source system CN-CN - From Country - To Country 

    Example output is: CN20320331ATC0000000079~##~CN~##~CN1021523002118CNY~##~8000~##~~##~positive AML-FTF-ALL-ALL-A-D07-FTR 0320331~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~TCOECDEGEN~##~~##~~##~CNMNTXN99~##~~##~20320331124925~##~UOB~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~6000~##~CNY~##~~##~~##~~##~~##~~##~~1~##~~##~~##~~##~~##~~##~RBK~##~~##~110~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~CN_CN~##~~##~~##~~##~~##~~##~4832~##~~##~~##~~##~~##~C~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~

    Strictly generate the data based on the information below. 
    Tenant ID: {tenant_id} 
    Transaction date: {transaction_date} 
    Scenario: {scenario} 
    Rule: {rule}
    """
    app.logger.info(f"Generated prompt: {my_prompt}") 

    try:
        # Call the ChatGPT API
        response = client.responses.create(
            model="gpt-5-mini",  # Use the appropriate engine
            input=my_prompt
        )

        # Extract the generated text
        generated_data = response.output_text
        app.logger.info(f"API response:\n{response.output_text}")

        # Return the generated data as JSON
        return jsonify({"results": generated_data})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/config', methods=['GET'])
def get_config():
    tenants = ["Tenant 1", "Tenant 2", "Tenant 3"]

    rules = [
        {"name": "Option A", "description": "Enables feature A."},
        {"name": "Option B", "description": "Enables feature B."},
        {"name": "Option C", "description": "Test scenario C."},
        {"name": "Option D", "description": "Special configuration D."}
    ]

    return jsonify({
        "tenants": tenants,
        "rules": rules
    })

@app.route('/generate-data', methods=['POST'])
def generate_data():
    data = request.get_json()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name', 'Score', 'Status'])
    writer.writerow(['Alice', 95, 'Pass'])
    writer.writerow(['Bob', 80, 'Pass'])
    writer.writerow(['Eve', 60, 'Borderline'])

    csv_data = output.getvalue()
    output.close()

    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=data.csv'}
    )

if __name__ == "__main__":
    app.run(debug=True)
