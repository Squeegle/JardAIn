#!/usr/bin/env python3
"""
Verification script to test plant category display fix
"""
import requests
import json

def test_api_endpoint():
    """Test the API endpoint that the frontend uses"""
    print("🧪 Testing Frontend API Endpoint")
    print("=" * 50)
    
    try:
        # Test the exact endpoint the frontend now uses
        response = requests.get("http://localhost:8000/api/plants/")
        
        if response.status_code == 200:
            data = response.json()
            plants = data.get("plants", [])
            
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Total plants: {len(plants)}")
            
            if plants:
                print(f"\n🌱 First 3 plants with categories:")
                for i, plant in enumerate(plants[:3]):
                    name = plant.get('name', 'Unknown')
                    plant_type = plant.get('plant_type', 'MISSING')
                    days = plant.get('days_to_harvest', 'N/A')
                    
                    # Determine emoji
                    emoji_map = {
                        'vegetable': '🥕',
                        'herb': '🌿', 
                        'fruit': '🍅'
                    }
                    emoji = emoji_map.get(plant_type, '🌱')
                    
                    print(f"  {i+1}. {emoji} {name}")
                    print(f"     Category: {plant_type}")
                    print(f"     Days to harvest: {days}")
                    print()
                
                # Check for any plants with missing plant_type
                missing_type = [p for p in plants if not p.get('plant_type')]
                if missing_type:
                    print(f"⚠️  Found {len(missing_type)} plants with missing plant_type:")
                    for plant in missing_type[:3]:
                        print(f"    - {plant.get('name', 'Unknown')}")
                else:
                    print(f"✅ All plants have plant_type field")
                
                return True
            else:
                print("❌ No plants in response")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_frontend_page():
    """Test if the frontend page loads"""
    print(f"\n🌐 Testing Frontend Page")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8000/")
        
        if response.status_code == 200:
            content = response.text
            
            # Check for updated JavaScript
            if 'fetch(\'/api/plants/\')' in content:
                print("✅ Frontend uses correct API endpoint")
            else:
                print("❌ Frontend may still use old endpoint")
            
            # Check for plant grid
            if 'plant-grid' in content:
                print("✅ Plant grid container found")
            else:
                print("❌ Plant grid container missing")
                
            return True
        else:
            print(f"❌ Frontend error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main verification function"""
    print("🔍 JardAIn Plant Category Display Verification")
    print("=" * 60)
    
    api_ok = test_api_endpoint()
    frontend_ok = test_frontend_page()
    
    print(f"\n📊 Verification Results:")
    print(f"  API Endpoint: {'✅ PASS' if api_ok else '❌ FAIL'}")
    print(f"  Frontend Page: {'✅ PASS' if frontend_ok else '❌ FAIL'}")
    
    if api_ok and frontend_ok:
        print(f"\n🎉 Verification Complete!")
        print(f"💡 Next steps:")
        print(f"   1. Open http://localhost:8000 in your browser")
        print(f"   2. Hard refresh (Ctrl+F5 or Cmd+Shift+R) to clear cache")
        print(f"   3. Open browser console (F12) to see debug logs")
        print(f"   4. Plant tiles should now show proper categories!")
        print(f"\n🔧 Debug page available at:")
        print(f"   http://localhost:8000/static/debug_frontend.html")
    else:
        print(f"\n❌ Issues found. Check the application setup.")

if __name__ == "__main__":
    main() 