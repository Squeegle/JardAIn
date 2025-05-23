#!/usr/bin/env python3
"""
Test the location service with both US zip codes and Canadian postal codes.
"""

import sys
import os
import asyncio

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_location_service():
    """Test location service with various postal codes"""
    
    print("🌍 Testing Location Service (US & Canada)")
    print("=" * 60)
    
    try:
        from services.location_service import location_service
        
        # Test cases: [postal_code, expected_country, description]
        test_cases = [
            ("90210", "🇺🇸", "Beverly Hills, CA (US)"),
            ("K1A 0A6", "🇨🇦", "Ottawa, ON (Canada)"), 
            ("10001", "🇺🇸", "New York, NY (US)"),
            ("M5V 3A8", "🇨🇦", "Toronto, ON (Canada)"),
            ("V6B 1A1", "🇨🇦", "Vancouver, BC (Canada)"),
            ("33101", "🇺🇸", "Miami, FL (US)"),
            ("H3A 0G4", "🇨🇦", "Montreal, QC (Canada)"),
            ("98101", "🇺🇸", "Seattle, WA (US)")
        ]
        
        for postal_code, flag, description in test_cases:
            print(f"\n{flag} Testing: {postal_code} ({description})")
            print("-" * 40)
            
            try:
                location_info = await location_service.get_location_info(postal_code)
                
                print(f"📍 Location: {location_info.city}, {location_info.state}")
                print(f"🌡️  Zone: {location_info.usda_zone}")
                print(f"❄️  Last Frost: {location_info.last_frost_date}")
                print(f"🍂 First Frost: {location_info.first_frost_date}")
                print(f"📅 Growing Season: {location_info.growing_season_days} days")
                print(f"🌤️  Climate: {location_info.climate_type}")
                
            except Exception as e:
                print(f"❌ Error testing {postal_code}: {e}")
        
        print("\n" + "=" * 60)
        print("🎉 Location service test completed!")
        
        # Test the country detection separately
        print("\n🔍 Testing Country Detection:")
        test_detections = [
            "90210",      # US
            "K1A 0A6",    # Canada with space
            "K1A0A6",     # Canada without space
            "M5V3A8",     # Canada without space
            "10001",      # US
            "invalid"     # Invalid
        ]
        
        for code in test_detections:
            country, cleaned = location_service._detect_country_and_validate(code)
            flag = "🇺🇸" if country == "us" else "🇨🇦"
            print(f"  {code} → {flag} {cleaned}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_location_service())
    sys.exit(0 if success else 1)