"""
Test script for PDF router endpoints
Tests all PDF-related API endpoints
"""

import asyncio
import httpx
import json
from typing import Dict, Any

# Base URL for the API
BASE_URL = "http://localhost:8000"

async def test_pdf_endpoints():
    """Test all PDF router endpoints"""
    
    print("🧪 Testing PDF Router Endpoints")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Health check
        print("1. 🔍 Testing PDF service health...")
        try:
            response = await client.get(f"{BASE_URL}/pdf/health")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Health: {result['status']}")
            else:
                print(f"   ❌ Health check failed")
        except Exception as e:
            print(f"   ❌ Health check error: {e}")
        
        print()
        
        # Test 2: Generate PDF
        print("2. 📄 Testing PDF generation...")
        try:
            pdf_request = {
                "zip_code": "K1A 0A6",
                "plant_names": ["Tomato", "Lettuce", "Carrots"],
                "custom_filename": "test_api_garden",
                "include_images": True,
                "include_calendar": True,
                "include_layout": True,
                "garden_size": "medium",
                "experience_level": "beginner"
            }
            
            print(f"   📋 Request: {pdf_request}")
            
            response = await client.post(
                f"{BASE_URL}/pdf/generate",
                json=pdf_request,
                timeout=120.0  # Increase timeout for PDF generation
            )
            
            print(f"   Status: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ PDF Generated: {result['pdf_info']['filename']}")
                print(f"   📏 Size: {result['pdf_info']['file_size_mb']} MB")
                print(f"   🌱 Plants: {len(result['garden_plan_summary']['plants'])}")
                print(f"   📍 Location: {result['garden_plan_summary']['location']}")
                print(f"   🔗 Download URL: {result['download_url']}")
                print(f"   👁️ View URL: {result['view_url']}")
                generated_filename = result['pdf_info']['filename']
            else:
                print(f"   ❌ PDF generation failed with status {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error details: {error_detail}")
                except:
                    print(f"   Raw response: {response.text}")
                generated_filename = None
                
        except Exception as e:
            print(f"   ❌ PDF generation error: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            generated_filename = None
        
        print()
        
        # Test 3: List PDFs
        print("3. 📚 Testing PDF listing...")
        try:
            response = await client.get(f"{BASE_URL}/pdf/list")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Found {result['pdf_count']} PDFs")
                print(f"   📊 Total size: {result['total_size_mb']} MB")
                if result['pdfs']:
                    print("   📁 Recent files:")
                    for pdf in result['pdfs'][:3]:  # Show first 3
                        print(f"     - {pdf['filename']} ({pdf['size_mb']} MB)")
            else:
                print(f"   ❌ Listing failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Listing error: {e}")
        
        print()
        
        # Test 4: PDF Statistics
        print("4. 📊 Testing PDF statistics...")
        try:
            response = await client.get(f"{BASE_URL}/pdf/stats")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                stats = result['statistics']
                print(f"   ✅ Total files: {stats['total_files']}")
                print(f"   📏 Average size: {stats['average_size_mb']} MB")
                print(f"   📈 Recent files (24h): {stats['recent_files_24h']}")
            else:
                print(f"   ❌ Statistics failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Statistics error: {e}")
        
        print()
        
        # Test 5: Download PDF (if we generated one)
        if generated_filename:
            print(f"5. 📥 Testing PDF download ({generated_filename})...")
            try:
                response = await client.get(f"{BASE_URL}/pdf/download/{generated_filename}")
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    print(f"   ✅ Download successful")
                    print(f"   📏 Content length: {len(response.content)} bytes")
                    print(f"   📄 Content type: {response.headers.get('content-type', 'unknown')}")
                else:
                    print(f"   ❌ Download failed: {response.text}")
            except Exception as e:
                print(f"   ❌ Download error: {e}")
        else:
            print("5. ⏭️  Skipping download test (no PDF generated)")
        
        print()
        print("🎉 PDF Router testing completed!")

if __name__ == "__main__":
    print("🚀 Make sure the FastAPI server is running on localhost:8000")
    print("   Run: uvicorn main:app --reload")
    print()
    
    try:
        asyncio.run(test_pdf_endpoints())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}") 