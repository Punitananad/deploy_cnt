#!/usr/bin/env python3
"""
Fix app.py encoding and remove email verification
"""

def fix_app_py():
    """Clean app.py and remove email verification"""
    
    # Read the problematic file with error handling
    try:
        with open('app.py', 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except:
        with open('app.py', 'r', encoding='latin-1') as f:
            content = f.read()
    
    # Remove email verification functions
    import re
    
    # Remove issue_signup_otp function
    content = re.sub(r'def issue_signup_otp\(.*?\n(?=def|\n@|\nclass|\n#|\Z)', 
                     '# Email verification removed\n\n', content, flags=re.DOTALL)
    
    # Remove verify_signup_otp function  
    content = re.sub(r'def verify_signup_otp\(.*?\n(?=def|\n@|\nclass|\n#|\Z)', 
                     '', content, flags=re.DOTALL)
    
    # Remove email verification routes
    content = re.sub(r'@app\.route\("/verify-email".*?\n(?=@|\ndef|\nclass|\n#|\Z)', 
                     '', content, flags=re.DOTALL)
    
    content = re.sub(r'@app\.route\("/verify-email/resend".*?\n(?=@|\ndef|\nclass|\n#|\Z)', 
                     '', content, flags=re.DOTALL)
    
    # Clean up multiple newlines
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Write clean file
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed app.py - removed email verification and encoding issues")

if __name__ == "__main__":
    fix_app_py()