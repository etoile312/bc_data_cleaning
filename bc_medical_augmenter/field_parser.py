import json

class FieldRuleParser:
    def __init__(self, rule_path):
        with open(rule_path, 'r', encoding='utf-8') as f:
            self.rules = json.load(f)
    def get_field_defs(self):
        return self.rules.get('fields', {})
    
    def get_logic_rules(self):
        return self.rules.get('logic', [])

    def get_linked_fields(self, field):
        return self.rules.get('links', {}).get(field, [])
    def get_field_options(self, field):
        return self.rules.get('fields', {}).get(field, {}).get('options', [])
    def get_default(self, field):
        return self.rules.get('fields', {}).get(field, {}).get('default', None) 