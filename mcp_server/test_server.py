import sys
from pprint import pprint

# Ensure the script can import local modules
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import get_inventory, get_active_rentals, get_rental_history, audit_inventory


def run_tests():
    print("==================================================")
    print("      MCP SERVER TOOL INTEGRATION TESTS          ")
    print("==================================================")
    
    # 1. Test get_inventory
    print("\n--- Testing get_inventory() ---")
    inventory = get_inventory()
    print(f"Total equipment items in inventory: {len(inventory)}")
    if inventory:
        print("Sample item:")
        pprint(inventory[0])
    else:
        print("Warning: Inventory is empty!")

    # 2. Test get_active_rentals
    print("\n--- Testing get_active_rentals() ---")
    active_rentals = get_active_rentals()
    print(f"Total active rentals: {len(active_rentals)}")
    if active_rentals:
        print("Sample active rental:")
        pprint(active_rentals[0])
    
    # 3. Test get_rental_history
    print("\n--- Testing get_rental_history() ---")
    # Use equipment ID from inventory or default to 1
    target_eq_id = inventory[0]["id"] if inventory else 1
    print(f"Fetching rental history for equipment_id={target_eq_id}...")
    history = get_rental_history(target_eq_id)
    print(f"Total rental records for item {target_eq_id}: {len(history)}")
    if history:
        print("Sample history record:")
        pprint(history[0])

    # 4. Test audit_inventory
    print("\n--- Testing audit_inventory() ---")
    findings = audit_inventory()
    print(f"Total audit findings: {len(findings)}")
    if findings:
        print("Audit findings:")
        pprint(findings)
    else:
        print("No audit findings found (inventory is healthy).")

    print("\n==================================================")
    print("        ALL INTEGRATION TESTS COMPLETED           ")
    print("==================================================")


if __name__ == "__main__":
    run_tests()
