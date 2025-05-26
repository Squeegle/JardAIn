#!/usr/bin/env python3
"""
WeasyPrint Test Script for Railway Deployment
Tests that WeasyPrint can generate PDFs successfully
"""

import sys
import tempfile
import os

def test_weasyprint():
    """Test WeasyPrint installation and PDF generation"""
    try:
        from weasyprint import HTML, CSS
        print("✅ WeasyPrint imported successfully")
        
        # Test basic HTML to PDF conversion
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>WeasyPrint Test</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                h1 { color: #2e7d32; }
            </style>
        </head>
        <body>
            <h1>🌱 JardAIn Garden Planner</h1>
            <p>WeasyPrint is working correctly!</p>
            <p>This is a test PDF generated during deployment.</p>
        </body>
        </html>
        """
        
        # Create temporary file for PDF output
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            pdf_path = tmp_file.name
        
        # Generate PDF
        HTML(string=html_content).write_pdf(pdf_path)
        
        # Check if PDF was created and has content
        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
            print(f"✅ PDF generated successfully: {os.path.getsize(pdf_path)} bytes")
            os.unlink(pdf_path)  # Clean up
            return True
        else:
            print("❌ PDF generation failed - file not created or empty")
            return False
            
    except ImportError as e:
        print(f"❌ WeasyPrint import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ WeasyPrint test failed: {e}")
        return False

def test_dependencies():
    """Test that all required dependencies are available"""
    dependencies = [
        'weasyprint',
        'pydyf', 
        'pillow',
        'cssselect2',
        'html5lib'
    ]
    
    print("🔍 Testing PDF generation dependencies...")
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - MISSING")
            return False
    
    return True

if __name__ == "__main__":
    print("🧪 Testing WeasyPrint installation...")
    
    # Test dependencies
    deps_ok = test_dependencies()
    
    # Test WeasyPrint functionality
    weasyprint_ok = test_weasyprint()
    
    if deps_ok and weasyprint_ok:
        print("🎉 All WeasyPrint tests passed!")
        sys.exit(0)
    else:
        print("💥 WeasyPrint tests failed!")
        sys.exit(1) 