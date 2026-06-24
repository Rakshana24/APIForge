import os
import shutil
from app import run_api_forge

def main():
    requirement = (
        "An inventory management system for managing warehouse inventory. "
        "It has three models: Item, Stock, and Transaction. "
        "Items have a name (string), description (string), category (string), price (float), and low_stock_threshold (integer). "
        "Stock tracks the quantity (integer) and location (string) for each item, referencing the Item model. "
        "Transactions track stock changes including stock_id (integer), transaction_type (string, e.g., ADD, REMOVE), quantity (integer), and date (datetime). "
        "The application should have endpoints to manage items, manage stock levels, view stock reports, list transactions, and get alerts for low stock items. "
        "Authentication is NOT required."
    )
    answers = (
        "Item, Stock, and Transaction models. No authentication/login. "
        "The /alerts/low_stock endpoint should alert low stock items."
    )

    if os.path.exists("generated_project"):
        shutil.rmtree("generated_project")
        
    if os.path.exists("repair_observability.log"):
        os.remove("repair_observability.log")

    print("Running APIForge for Inventory Management...")
    try:
        success = run_api_forge(requirement, answers=answers)
        print(f"\nExecution finished! Success: {success}")
    except Exception as e:
        print(f"\nExecution failed with error: {e}")

if __name__ == "__main__":
    main()
