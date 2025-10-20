import pandas as pd
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timedelta
from enum import Enum
import random

'''
Fields needed:
Tenant/Country - code of country usually, CN
Transaction date - yyyymmdd, 20320331
Transaction ID - id, ATC0000000079
Rule ID - AML-FTF-ALL-ALL-A-D07-FTR
Amount of transaction - 8000
Currency of transactions - CNY
Retail banking source system - RBK
From country-To country - CN-CN
'''


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

class TransactionInput(BaseModel):
    '''
    tenant: required, selected by user
    transaction_date: required, selected by user
    scenario: required, selected by user
    rule_id: required, selected by user
    rule: required, selected by user
    rule_type: required, queried from db by by rule_id
    frequency: optional only required for frequency rules, queried from db by rule_id
    direction: optional only required for amount/frequency rules, queried from db by rule_id
    threshold: optional only required for amount/frequency rules, queried from db by rule_id

    db will have
    tenant
    rule_id
    rule_type
    frequency
    direction
    threshold
    '''
    tenant: str = Field(..., description="Tenant or country code (e.g., 'CN')")
    transaction_date: datetime = Field(..., description="Base transaction date (YYYYMMDD or datetime)")
    scenario: Scenario
    rule_id: str = Field(..., description="Rule ID (e.g., 'AML-FTF-ALL-ALL-A-D07-FTR')")
    rule: str = Field(..., description="Human-readable rule description")
    rule_type: RuleType
    frequency: int | None = Field(None, description="Frequency for frequency rules")
    direction: Direction | None = Field(None, description="Direction for amount/frequency rules")
    threshold: float | None = Field(None, description="Threshold for amount/frequency rules")

    @field_validator("transaction_date", mode="before")
    def parse_transaction_date(cls, v):
        if isinstance(v, datetime):
            return v
        try:
            return datetime.strptime(v, "%Y%m%d")
        except Exception:
            raise ValueError("transaction_date must be a datetime or 'YYYYMMDD' string")

    @field_validator("direction")
    def check_direction(cls, v, values):
        if values.data.get("rule_type") in [RuleType.country]:
            if v is not None:
                raise ValueError("Direction must be empty for country rules.")
        elif values.data.get("rule_type") in [RuleType.transaction_amount, RuleType.frequency]:
            if v is None:
                raise ValueError("Direction must be provided for transaction amount or frequency rules.")
        return v

    def sample_data():
        input_rules = [
          # Transaction amount rule
          TransactionInput(
              tenant="CN",
              transaction_date="20320331",
              scenario=Scenario.positive,
              rule_id = '1',
              rule_type=RuleType.transaction_amount,
              direction=Direction.greater_than,
              threshold=100000,
              rule="Transaction amount greater than 100k"
          ),
          # Country rule
          TransactionInput(
              tenant="CN",
              transaction_date="20320331",
              scenario=Scenario.boundary,
              rule_id='2',
              rule_type=RuleType.country,
              rule="Transaction made to Iran"
              #prohibited_country="IR"
          ),
          # Frequency rule
          TransactionInput(
              tenant="CN",
              transaction_date="20320331",
              scenario=Scenario.positive,
              rule_id='3',
              rule_type=RuleType.frequency,
              frequency=3,
              direction=Direction.greater_than,
              threshold=5000,
              rule="3 ATM withdrawals > 5k in 3 days"
          ),
        ]
        return input_rules
    

class Data:
    template = '''
    {From}{TransactionDate}{TransactionID}~##~{From}~##~{From}1021523002118{Currency}~##~{Amount}~##~~##~{Scenario}
    {RuleID}{TransactionDate}~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~TCOECDEGEN~##~~##~~##~CNMNTXN99~##~~##~{TransactionDate}~##~UOB~##~~##~~##~~##~~##~~
    ##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~6000~##~CNY~##~~##~~##~~##~~##~~##~~1~##~~##~~##~~##~~##~~##~RBK~##~~##~110~##~~
    #~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~{FromTo}~##~~##~~##~~##~~##~~##~4832~##~~##~~##~~##~~##~C~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~
    '''

    def generate_transaction(input_data: TransactionInput, risk_dict: dict, country_codes: dict):
        """Generate a fake transaction based on the provided input data."""
        # -------------------------- #
        # Extracting data from input #
        # -------------------------- #
        tenant = input_data.tenant
        base_date = input_data.transaction_date
        scenario = input_data.scenario.value
        rule_id = input_data.rule_id
        rule = input_data.rule
        rule_type = input_data.rule_type.value
        direction = input_data.direction.value if input_data.direction else None
        frequency = input_data.frequency
        threshold = input_data.threshold

        # -------------------------- #
        # Frequency RuleType Special #
        # -------------------------- #
        if rule_type == "frequency" or rule_type == "composite":
            # Frequency means multiple transactions
            num_txns = frequency
            base_amount = 10000

            if scenario == "positive":
                num_txns = random.randint(frequency + 2, frequency + 5)
            elif scenario == "boundary":
                num_txns = random.randint(frequency - 1, frequency + 1)
            else:  
                num_txns = random.randint(1, frequency - 2)

            transactions = []
            for i in range(num_txns):
                txn_date = (base_date + timedelta(days=i)).strftime("%Y%m%d")
                transaction_id = f"ATC{random.randint(1000000000, 9999999999)}"
                currency = random.choice(["CNY", "USD", "EUR", "SGD"])
                source_system = "ATM"
                from_country = country_codes[tenant]
                to_country = random.choice(["CN", "US", "SG", "DE"])

                amount = random.uniform(base_amount * 0.95, base_amount * 1.05)
                if rule_type == "composite":
                    if scenario == "positive":
                        amount = random.uniform(threshold * 1.1, threshold * 1.5)
                    elif scenario == "boundary":
                        amount = random.uniform(threshold * 0.95, threshold * 1.05)
                    else:
                        amount = random.uniform(threshold * 0.1, threshold * 0.9)

                transactions.append({
                    "Tenant": tenant,
                    "TransactionDate": txn_date,
                    "TransactionID": transaction_id,
                    "RuleID": rule_id,
                    "Amount": round(amount, 2),
                    "Currency": currency,
                    "SourceSystem": source_system,
                    "FromTo": f"{from_country}-{to_country}",
                    "From": from_country,
                    "To": to_country,
                    "Scenario": scenario
                })
            return transactions  # multiple rows


        # ------------------------------------------------------- #
        # Initialising random parameters for generated transation #
        # ------------------------------------------------------- #
        transaction_id = f"ATC{random.randint(1000000000, 9999999999)}"
        currency = random.choice(["CNY", "USD", "EUR", "SGD"])
        source_system = random.choice(["RBK", "ATM", "MOB", "IBK"])
        from_country = country_codes[tenant]
        
        # ---------- #
        # Rule Logic #
        # ---------- #
        if rule_type == "transaction amount":
            to_country = random.choice(["CN", "IR", "US", "SG", "DE"])
            if threshold is None:
                threshold = 100000
            if direction == "greater than":
                if scenario == "positive":
                    amount = random.uniform(threshold * 1.1, threshold * 1.5)
                elif scenario == "boundary":
                    amount = random.uniform(threshold * 0.9, threshold * 1.1)
                else:
                    amount = random.uniform(threshold * 0.1, threshold * 0.9)
            elif direction == "less than":
                if scenario == "positive":
                    amount = random.uniform(threshold * 0.1, threshold * 0.9)
                elif scenario == "boundary":
                    amount = random.uniform(threshold * 0.9, threshold * 1.1)
                else:
                    amount = random.uniform(threshold * 1.1, threshold * 1.5)

        elif rule_type == "country":
            if scenario == "positive":
                to_country = random.choice(risk_dict['high'])
            elif scenario == "boundary":
                to_country = random.choice(risk_dict['medium'])
            else:
                to_country = random.choice(risk_dict['low'])
            amount = random.uniform(5000, 50000)
        else:
            amount = random.uniform(1000, 100000)

        txn_date = base_date

        return {
            "Tenant": tenant,
            "TransactionDate": txn_date.strftime("%Y%m%d"),
            "TransactionID": transaction_id,
            "RuleID": rule_id,
            "Amount": round(amount, 2),
            "Currency": currency,
            "SourceSystem": source_system,
            "FromTo": f"{from_country}-{to_country}",
            "From": from_country,
            "To": to_country,
            "Scenario": scenario
        }

    def generate_dataset(inputs: list[TransactionInput], risk_dict: dict, country_codes: dict, write_path: str = None) -> pd.DataFrame:
        """Generate a dataset of fake transactions for all rule inputs."""
        n_per_rule = random.randint(3, 5)
        all_txns = []
        for inp in inputs:
            if inp.rule_type.value == 'frequency' or inp.rule_type.value == 'composite':
                all_txns.extend(Data.generate_transaction(inp, risk_dict, country_codes))
            else:
                for _ in range(n_per_rule):
                    all_txns.append(Data.generate_transaction(inp, risk_dict, country_codes))
        res = pd.DataFrame(all_txns)
        if write_path:
            Data.write_dataset(res, write_path)
        return res
    
    ## Not in use ##
    def write_dataset(df: pd.DataFrame, filename: str):
        """Write the dataset to a text file in the specified format."""
        with open(filename, 'w') as output:
            outstr = "\n".join(df.apply(lambda row: Data.template.format(**row), axis=1))
            output.write(outstr)

if __name__ == "__main__":
    # For quick testing
    sample_inputs = TransactionInput.sample_data()
    df = Data.generate_dataset(sample_inputs)
    print(df.head(20))



"""
Tables avail:

t1
tenant_id
tenant_name

t2
rule_id
rule_name
rule_description
rule_query

t3
tenant_id
rule_id

t4
id
tenant_id
customer_id
txn_date
amount
country
source_system

t5
alert_id
tenant_id
rule_id
customer_id
txn_date
description
"""