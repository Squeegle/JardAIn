"""
Debug PDF naming conflicts and WeasyPrint installation
"""

def debug_pdf_imports():
    """Check for PDF class conflicts"""
    
    print("🔍 Debugging PDF import conflicts...")
    print("=" * 50)
    
    # Check what's in the global namespace
    import sys
    
    print("📦 Checking imported modules with 'pdf' in name:")
    for module_name in sys.modules:
        if 'pdf' in module_name.lower():
            print(f"   - {module_name}")
    
    print("\n🔍 Testing WeasyPrint imports step by step:")
    
    # Test imports one by one
    try:
        print("1. Importing weasyprint...")
        import weasyprint
        print(f"   ✅ WeasyPrint version: {weasyprint.__version__}")
    except Exception as e:
        print(f"   ❌ WeasyPrint import failed: {e}")
        return
    
    try:
        print("2. Checking WeasyPrint.HTML class...")
        html_class = weasyprint.HTML
        print(f"   ✅ HTML class: {html_class}")
    except Exception as e:
        print(f"   ❌ HTML class access failed: {e}")
        return
    
    try:
        print("3. Creating simple HTML object...")
        html_obj = weasyprint.HTML(string="<html><body>test</body></html>")
        print(f"   ✅ HTML object created: {type(html_obj)}")
    except Exception as e:
        print(f"   ❌ HTML object creation failed: {e}")
        return
    
    try:
        print("4. Checking write_pdf method...")
        write_pdf_method = html_obj.write_pdf
        print(f"   ✅ write_pdf method: {write_pdf_method}")
    except Exception as e:
        print(f"   ❌ write_pdf method access failed: {e}")
        return
    
    try:
        print("5. Attempting PDF generation...")
        pdf_bytes = html_obj.write_pdf()
        print(f"   ✅ PDF generated! Size: {len(pdf_bytes)} bytes")
    except Exception as e:
        print(f"   ❌ PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🔍 Checking for PDF class conflicts:")
    
    # Check if there's a conflicting PDF class
    try:
        import builtins
        if hasattr(builtins, 'PDF'):
            print("   ⚠️ Found PDF in builtins!")
            
        # Check globals
        if 'PDF' in globals():
            print(f"   ⚠️ Found PDF in globals: {globals()['PDF']}")
            
        # Check if we accidentally imported a PDF class from somewhere
        import sys
        for module_name, module in sys.modules.items():
            if module and hasattr(module, 'PDF'):
                print(f"   📦 Module {module_name} has PDF class: {getattr(module, 'PDF')}")
                
    except Exception as e:
        print(f"   Error checking for conflicts: {e}")

if __name__ == "__main__":
    debug_pdf_imports() 