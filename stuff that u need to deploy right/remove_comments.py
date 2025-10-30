
import os
import re
import sys
from pathlib import Path

def remove_python_comments(content):
    """Remove comments from Python code while preserving functionality"""
    lines = content.split('\n')
    result_lines = []
    in_multiline_string = False
    multiline_quote = None
    
    for line in lines:
        original_line = line
        stripped = line.strip()
        
        
        if not stripped:
            result_lines.append(line)
            continue
            
        
        if not in_multiline_string:
            
            if '"""' in line or "'''" in line:
                
                triple_double = line.find('"""')
                triple_single = line.find("'''")
                
                if triple_double != -1 and (triple_single == -1 or triple_double < triple_single):
                    multiline_quote = '"""'
                    quote_pos = triple_double
                elif triple_single != -1:
                    multiline_quote = "'''"
                    quote_pos = triple_single
                else:
                    quote_pos = -1
                
                if quote_pos != -1:
                    
                    before_quote = line[:quote_pos].strip()
                    if (not before_quote or 
                        before_quote.endswith(':') or 
                        re.match(r'^\s*(def|class|async\s+def)\s+', original_line)):
                        
                        
                        end_pos = line.find(multiline_quote, quote_pos + 3)
                        if end_pos != -1:
                            
                            if not before_quote:
                                continue  
                            else:
                                
                                result_lines.append(line[:quote_pos].rstrip())
                                continue
                        else:
                            
                            in_multiline_string = True
                            if not before_quote:
                                continue  
                            else:
                                
                                result_lines.append(line[:quote_pos].rstrip())
                                continue
        else:
            
            if multiline_quote in line:
                end_pos = line.find(multiline_quote)
                in_multiline_string = False
                multiline_quote = None
                
                continue
            else:
                
                continue
        
        
        if '
            
            in_string = False
            string_char = None
            i = 0
            while i < len(line):
                char = line[i]
                if not in_string:
                    if char in ['"', "'"]:
                        in_string = True
                        string_char = char
                    elif char == '
                        
                        line = line[:i].rstrip()
                        break
                else:
                    if char == string_char and (i == 0 or line[i-1] != '\\'):
                        in_string = False
                        string_char = None
                i += 1
        
        
        if line.strip() or not original_line.strip():
            result_lines.append(line)
    
    return '\n'.join(result_lines)

def remove_php_comments(content):
    """Remove comments from PHP code"""
    lines = content.split('\n')
    result_lines = []
    in_multiline_comment = False
    
    for line in lines:
        if in_multiline_comment:
            if '*/' in line:
                
                end_pos = line.find('*/')
                line = line[end_pos + 2:]
                in_multiline_comment = False
            else:
                continue
        
        
        if '//' in line:
            comment_pos = line.find('//')
            line = line[:comment_pos].rstrip()
        
        
        if '/*' in line:
            start_pos = line.find('/*')
            if '*/' in line[start_pos:]:
                
                end_pos = line.find('*/', start_pos)
                line = line[:start_pos] + line[end_pos + 2:]
            else:
                
                line = line[:start_pos].rstrip()
                in_multiline_comment = True
        
        
        if '
            comment_pos = line.find('
            line = line[:comment_pos].rstrip()
        
        result_lines.append(line)
    
    return '\n'.join(result_lines)

def process_file(file_path):
    """Process a single file to remove comments"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        if file_path.suffix == '.py':
            content = remove_python_comments(content)
        elif file_path.suffix == '.php':
            content = remove_php_comments(content)
        else:
            print(f"Skipping {file_path} - unsupported file type")
            return False
        
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Processed: {file_path}")
            return True
        else:
            print(f"No changes: {file_path}")
            return False
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to process all files"""
    root_dir = Path('.')
    
    
    python_files = list(root_dir.rglob('*.py'))
    php_files = list(root_dir.rglob('*.php'))
    
    all_files = python_files + php_files
    
    print(f"Found {len(python_files)} Python files and {len(php_files)} PHP files")
    
    processed_count = 0
    for file_path in all_files:
        if process_file(file_path):
            processed_count += 1
    
    print(f"\nProcessed {processed_count} files successfully")

if __name__ == "__main__":
    main()
