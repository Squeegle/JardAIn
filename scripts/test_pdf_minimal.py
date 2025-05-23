"""
Minimal PDF generation test to debug WeasyPrint issues
"""

import weasyprint
import os
from pathlib import Path

def test_minimal_pdf():
    """Test minimal PDF generation"""
    
    print("🔍 Testing minimal PDF generation...")
    
    # Ensure directory exists
    Path("generated_plans").mkdir(exist_ok=True)
    
    # Simple HTML content
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test PDF</title>
        <style>
            body { font-family: Arial; padding: 20px; }
            h1 { color: green; }
        </style>
    </head>
    <body>
        <h1>🌱 Test Garden Plan PDF</h1>
        <p>This is a test to verify WeasyPrint is working correctly.</p>
        <ul>
            <li>Tomato</li>
            <li>Lettuce</li>
            <li>Carrots</li>
        </ul>
    </body>
    </html>
    """
    
    try:
        print("📝 Creating HTML document...")
        
        # Test different WeasyPrint approaches
        
        # Method 1: String-based
        try:
            print("🔄 Trying string-based approach...")
            html_doc = weasyprint.HTML(string=html_content)
            pdf_bytes = html_doc.write_pdf()
            
            with open("generated_plans/test_minimal.pdf", "wb") as f:
                f.write(pdf_bytes)
            
            print("✅ Method 1 (string-based) successful!")
            return True
            
        except Exception as e1:
            print(f"❌ Method 1 failed: {e1}")
            
            # Method 2: File-based
            try:
                print("🔄 Trying file-based approach...")
                temp_file = "generated_plans/temp_test.html"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                html_doc = weasyprint.HTML(filename=temp_file)
                pdf_bytes = html_doc.write_pdf()
                
                with open("generated_plans/test_minimal_v2.pdf", "wb") as f:
                    f.write(pdf_bytes)
                
                # Clean up
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                
                print("✅ Method 2 (file-based) successful!")
                return True
                
            except Exception as e2:
                print(f"❌ Method 2 also failed: {e2}")
                
                # Method 3: Check WeasyPrint version and API
                try:
                    print("🔍 Checking WeasyPrint version...")
                    print(f"WeasyPrint version: {weasyprint.__version__}")
                    
                    # Try the most basic approach
                    html_doc = weasyprint.HTML(string="<html><body><h1>Test</h1></body></html>")
                    pdf_bytes = html_doc.write_pdf()
                    
                    with open("generated_plans/test_basic.pdf", "wb") as f:
                        f.write(pdf_bytes)
                    
                    print("✅ Basic test successful - issue may be with complex HTML")
                    return False
                    
                except Exception as e3:
                    print(f"❌ Even basic test failed: {e3}")
                    print("🚨 WeasyPrint installation may have issues")
                    return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_minimal_pdf() 