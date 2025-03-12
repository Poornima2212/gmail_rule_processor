from rule_engine import load_rules, process_rule
from authenticate import authenticate
from googleapiclient.discovery import build

def run_rules():
    # Authenticates and builds Gmail service
    creds = authenticate()
    service = build('gmail', 'v1', credentials=creds)
    
    # Load available rules from the rules file 
    rules = load_rules()
    print("\n Which rule do you want to apply?")
    for idx, rule in enumerate(rules, start=1):
        print(f"{idx}. {rule['name']}")
    
    choice = int(input("\n Enter your choice: "))
    if choice < 1 or choice > len(rules):
        print("Invalid choice!")
        return
    selected_rule_name = rules[choice - 1]["name"]
    print(f"Applying Rule: {selected_rule_name}")
    
    # Process the selected rule using the rule engine
    process_rule(selected_rule_name, service)
    
    print("Task Completed Successfully!")

if __name__ == "__main__":
    run_rules()
