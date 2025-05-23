"""
Completely isolated WeasyPrint test
"""

# Fresh Python interpreter test
if __name__ == "__main__":
    print("🧪 Isolated WeasyPrint test...")
    
    # Clear any potential imports
    import sys
    modules_to_remove = [m for m in sys.modules.keys() if 'pdf' in m.lower() or 'weasy' in m.lower()]
    for module in modules_to_remove:
        if module in sys.modules:
            del sys.modules[module]
    
    try:
        # Fresh import
        import weasyprint
        
        print(f"✅ WeasyPrint imported: {weasyprint.__version__}")
        
        # Create HTML
        html = weasyprint.HTML(string="<html><head><title>Test</title></head><body><h1>Hello World</h1></body></html>")
        print("✅ HTML object created")
        
        # Generate PDF
        pdf_data = html.write_pdf()
        print(f"✅ PDF generated: {len(pdf_data)} bytes")
        
        # Save to file
        with open("test_isolated.pdf", "wb") as f:
            f.write(pdf_data)
        print("✅ PDF saved successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc() 