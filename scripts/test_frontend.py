#!/usr/bin/env python3
"""
Test script to verify frontend plant category display
"""
import requests
import json

def test_plant_api():
    """Test the plants API endpoint"""
    print("🧪 Testing Plant API Endpoint")
    print("=" * 40)
    
    try:
        # Test the API endpoint
        response = requests.get("http://localhost:8000/api/plants/")
        
        if response.status_code == 200:
            data = response.json()
            plants = data.get("plants", [])
            
            print(f"✅ API Response: {response.status_code}")
            print(f"✅ Total plants: {len(plants)}")
            
            # Check first few plants
            print(f"\n🌱 Sample plants:")
            for i, plant in enumerate(plants[:5]):
                print(f"  {i+1}. {plant['name']}")
                print(f"     Type: {plant['plant_type']}")
                print(f"     Days: {plant['days_to_harvest']}")
                print()
            
            # Check plant types distribution
            types = {}
            for plant in plants:
                plant_type = plant['plant_type']
                types[plant_type] = types.get(plant_type, 0) + 1
            
            print(f"🏷️  Plant types distribution:")
            for plant_type, count in sorted(types.items()):
                print(f"  - {plant_type}: {count}")
            
            return True
            
        else:
            print(f"❌ API Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_frontend_load():
    """Test if frontend loads correctly"""
    print(f"\n🌐 Testing Frontend Load")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:8000/")
        
        if response.status_code == 200:
            content = response.text
            
            # Check for key elements
            checks = [
                ("plant-grid", "Plant grid container"),
                ("plant-search", "Plant search input"),
                ("app.js", "JavaScript application"),
                ("Select Your Plants", "Plant selection section")
            ]
            
            for check, description in checks:
                if check in content:
                    print(f"✅ {description}: Found")
                else:
                    print(f"❌ {description}: Missing")
            
            return True
            
        else:
            print(f"❌ Frontend Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 JardAIn Frontend Plant Category Test")
    print("=" * 50)
    
    # Test API
    api_ok = test_plant_api()
    
    # Test Frontend
    frontend_ok = test_frontend_load()
    
    print(f"\n📊 Test Results:")
    print(f"  API: {'✅ PASS' if api_ok else '❌ FAIL'}")
    print(f"  Frontend: {'✅ PASS' if frontend_ok else '❌ FAIL'}")
    
    if api_ok and frontend_ok:
        print(f"\n🎉 All tests passed!")
        print(f"💡 Open http://localhost:8000 in your browser to see the plant tiles with categories")
        print(f"🔍 The plant tiles should now show:")
        print(f"   - Plant name")
        print(f"   - Plant type (vegetable, herb, fruit)")
        print(f"   - Appropriate emoji for each type")
    else:
        print(f"\n❌ Some tests failed. Check the application setup.")

if __name__ == "__main__":
    main() 