#!/usr/bin/env python3
"""
Simple JSON Linter - Easy to use and configure
"""

import json
import sys
import re


class SimpleLinter:
    """A simple, easy-to-use JSON linter"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.line_map = {}
    
    def lint_file(self, filename):
        """Lint a JSON file and print results"""
        self.errors = []
        self.warnings = []
        self.line_map = {}
        
        # Load and parse JSON with line tracking
        try:
            with open(filename, 'r') as f:
                content = f.read()
                data = json.loads(content)
                self._build_line_map(content)
        except FileNotFoundError:
            print(f"❌ Error: File '{filename}' not found")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON - {e.msg} at line {e.lineno}")
            return False
        
        # Run basic validations
        self._check_structure(data)
        self._check_content(data)
        
        # Print results
        self._print_results()
        
        return len(self.errors) == 0
    
    def _build_line_map(self, content):
        """Build a map of array indices to line numbers"""
        lines = content.split('\n')
        current_item = -1
        
        for line_num, line in enumerate(lines, 1):
            # Look for opening braces that start new objects
            if '{' in line and current_item == -1:
                current_item = 0
                self.line_map[current_item] = line_num
            elif '{' in line and current_item >= 0:
                current_item += 1
                self.line_map[current_item] = line_num
            # Reset when we find the end of an object
            elif '}' in line and ',' in line:
                # This object is done, next one will be incremented
                pass
    
    def _get_line_info(self, index):
        """Get line number for an array index"""
        line_num = self.line_map.get(index, None)
        return f" (line {line_num})" if line_num else ""
    
    def _check_structure(self, data):
        """Check basic JSON structure"""
        if not isinstance(data, list):
            self.errors.append("JSON should be an array")
            return
        
        if len(data) == 0:
            self.warnings.append("Array is empty")
        
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                line_info = self._get_line_info(i)
                self.errors.append(f"Item {i} should be an object{line_info}")
    
    def _check_content(self, data):
        """Check content of JSON objects"""
        if not isinstance(data, list):
            return
        
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                continue
            
            # Get tagKey and line info for better error messages
            tag_key = item.get("tagKey", f"Item {i}")
            line_info = self._get_line_info(i)
            
            # Check required keys
            if "tagKey" not in item:
                self.errors.append(f"Missing 'tagKey' at position {i}{line_info}")
            if "value" not in item:
                self.errors.append(f"Missing 'value' for '{tag_key}'{line_info}")
            
            # Check for empty values
            if "tagKey" in item and not item["tagKey"].strip():
                self.warnings.append(f"Empty 'tagKey' at position {i}{line_info}")
            if "value" in item and not item["value"].strip():
                self.warnings.append(f"Empty 'value' for '{tag_key}'{line_info}")
            
            # Check specific tag key values
            self._check_specific_tag_values(item, i, line_info)
    
    def _check_specific_tag_values(self, item, index, line_info):
        """Check specific validation rules for different tag keys"""
        tag_key = item.get("tagKey", "")
        value = item.get("value", "")
        
        # Route to specific validation functions
        if tag_key == "Data Classification":
            self._validate_data_classification(value, line_info)
        elif tag_key == "Business Groups":
            self._validate_business_groups(value, line_info)
        elif tag_key == "Owning Business group":
            self._validate_owning_business_group(value, line_info)
        elif tag_key == "Environment":
            self._validate_environment(value, line_info)
        # Add more tag key validations here as needed
    
    def _validate_data_classification(self, value, line_info):
        """Validate Data Classification values"""
        valid_values = ["DCL1", "DCL2", "DCL3", "DCL4"]
        if value and value not in valid_values:
            self.warnings.append(f"Invalid Data Classification '{value}' (should be one of: {', '.join(valid_values)}){line_info}")
    
    def _validate_business_groups(self, value, line_info):
        """Validate Business Groups values"""
        if value and len(value) < 2:
            self.warnings.append(f"Business Groups value '{value}' is too short (minimum 2 characters){line_info}")
        
        # Example: Check for valid business group codes
        valid_prefixes = ["gip", "eng", "ops", "fin"]
        if value and not any(value.lower().startswith(prefix) for prefix in valid_prefixes):
            self.warnings.append(f"Business Groups '{value}' should start with one of: {', '.join(valid_prefixes)}{line_info}")
    
    def _validate_owning_business_group(self, value, line_info):
        """Validate Owning Business group values"""
        if value and len(value) < 5:
            self.warnings.append(f"Owning Business group '{value}' is too short (minimum 5 characters){line_info}")
        
        # Example: Check for proper capitalization
        if value and not any(word[0].isupper() for word in value.split() if word):
            self.warnings.append(f"Owning Business group '{value}' should have proper capitalization{line_info}")
    
    def _validate_environment(self, value, line_info):
        """Validate Environment values"""
        valid_environments = ["dev", "development", "staging", "stage", "prod", "production"]
        if value and value.lower() not in valid_environments:
            self.warnings.append(f"Invalid Environment '{value}' (should be one of: {', '.join(valid_environments)}){line_info}")
    
    def _print_results(self):
        """Print linting results"""
        if not self.errors and not self.warnings:
            print("✅ No issues found!")
            return
        
        if self.errors:
            print(f"❌ {len(self.errors)} Error(s):")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print(f"⚠️  {len(self.warnings)} Warning(s):")
            for warning in self.warnings:
                print(f"  • {warning}")


def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python simple_linter.py <json_file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    linter = SimpleLinter()
    success = linter.lint_file(filename)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
