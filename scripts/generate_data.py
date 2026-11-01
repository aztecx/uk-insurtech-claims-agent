import os
import random
import pandas as pd
from faker import Faker


# Initializing the Faker but with the UK locale for authentic British names and data
fake = Faker("en_GB")
Faker.seed(42)
random.seed(42)

def generate_mock_policies(num_rows=60):
    """Generates realistic UK insurance policy records with standard tiers and edge cases."""
    coverage_types = [
        'Comprehensive Auto',
        'Third Party Auto',
        'Home Buildings & Contents',
        'Home Buildings Only'
    ]
    deductible_options = [100.0, 250.0, 500.0, 1000.0]
    policies = []

    for i in range (1, num_rows + 1):
        # Generate UK Style policy ID format (POL-UK-1001 ...etc)
        policy_id = f"POL-UK-{i:04d}"
        client_name = fake.name()
        coverage_type = random.choice(coverage_types)
        deductible = random.choice(deductible_options)

        # 80/20 ratio for active and expired to test agent rejection logic
        if (random.random() < 0.8):
            status = "Active"
        else:
            status = "Expired"

        policies.append({
            "policy_id": policy_id,
            "client_name": client_name,
            "coverage_type": coverage_type,
            "deductible": deductible,
            "status": status
        })
        

    # Inject deliberate edge cases for testing agent resilience
    edge_cases = [
        {"policy_id": "POL-UK-9999", "client_name": "Test User (Expired)", "coverage_type": "Comprehensive Auto", "deductible": 500.0, "status": "Expired"},
        {"policy_id": "POL-UK-8888", "client_name": "Boundary Test User", "coverage_type": "Home Buildings & Contents", "deductible": 250.0, "status": "Active"}
    ]
    policies.extend(edge_cases)
    
    return pd.DataFrame(policies)


def generate_mock_ledger():
    """Generates a preliminary financial payout ledger for reconciliation simulation."""
    ledger_data = [
        {"transaction_id": "TXN-9001", "policy_id": "POL-UK-0001", "payout_amount": 450.0, "status": "Reconciled"},
        {"transaction_id": "TXN-9002", "policy_id": "POL-UK-0005", "payout_amount": 1200.0, "status": "Reconciled"}
    ]
    return pd.DataFrame(ledger_data)

if __name__ == "__main__":
    # Ensuring the data directory exists to begin with
    os.makedirs("data", exist_ok=True)
    
    # Generate the DFs
    df_policies = generate_mock_policies(60)
    df_ledger = generate_mock_ledger()
    
    # Save to CSV files inside the data/ folder
    policies_path = "data/policies.csv"
    ledger_path = "data/ledger.csv"
    
    df_policies.to_csv(policies_path, index=False)
    df_ledger.to_csv(ledger_path, index=False)

    print("===================\n")
    print(f"Success! Generated {len(df_policies)} UK policies at '{policies_path}'")
    print(f"Success! Generated initial ledger at '{ledger_path}'")
    print("\n==================")