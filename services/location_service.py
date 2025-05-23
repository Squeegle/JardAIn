"""
Location service - handles location lookup, climate data, and growing zones.
Supports both US zip codes and Canadian postal codes with appropriate climate data.
"""

import httpx
import asyncio
import re
from typing import Optional, Dict, Any, Tuple
from datetime import date, datetime
from models.garden_plan import LocationInfo
from config import settings

class LocationService:
    """
    Service for location-based climate and growing information
    Supports both United States and Canada
    """
    
    def __init__(self):
        self.client = httpx.AsyncClient()
    
    def _detect_country_and_validate(self, postal_code: str) -> Tuple[str, str]:
        """
        Detect if postal code is US zip code or Canadian postal code
        Returns (country_code, cleaned_postal_code)
        """
        # Clean the input
        cleaned = postal_code.strip().upper().replace(" ", "")
        
        # Canadian postal code pattern: L#L #L# (e.g., K1A0A6)
        canadian_pattern = r'^[A-Z]\d[A-Z]\d[A-Z]\d$'
        
        # US zip code patterns: ##### or #####-#### 
        us_zip_pattern = r'^\d{5}(-\d{4})?$'
        
        # Check Canadian pattern first (after removing spaces)
        if re.match(canadian_pattern, cleaned):
            # Reformat to standard Canadian format with space
            formatted = f"{cleaned[:3]} {cleaned[3:]}"
            return "ca", formatted
        
        # Check US zip code (take only first 5 digits)
        if re.match(us_zip_pattern, postal_code.strip()):
            return "us", postal_code.strip()[:5]
        
        # Try to detect based on length and content
        if len(cleaned) == 6 and any(c.isalpha() for c in cleaned):
            # Likely Canadian without space
            formatted = f"{cleaned[:3]} {cleaned[3:]}"
            return "ca", formatted
        elif len(postal_code.strip()) == 5 and postal_code.strip().isdigit():
            return "us", postal_code.strip()
        
        # Default to US if uncertain
        return "us", postal_code.strip()
    
    async def get_location_info(self, postal_code: str) -> LocationInfo:
        """
        Get comprehensive location information for garden planning
        Supports both US zip codes and Canadian postal codes
        """
        
        # Detect country and validate format
        country, cleaned_code = self._detect_country_and_validate(postal_code)
        
        # Start with basic location info
        location_info = LocationInfo(zip_code=cleaned_code)
        
        try:
            # Get basic location data (city, province/state) from postal code
            basic_info = await self._get_basic_location_info(cleaned_code, country)
            if basic_info:
                location_info.city = basic_info.get('city')
                location_info.state = basic_info.get('state')  # Province for Canada
            
            # Get hardiness zone (different systems for US vs Canada)
            zone_info = await self._get_hardiness_zone(cleaned_code, country)
            if zone_info:
                location_info.usda_zone = zone_info
            
            # Get frost dates and growing season info
            frost_info = await self._get_frost_dates(cleaned_code, country, location_info.state)
            if frost_info:
                location_info.last_frost_date = frost_info.get('last_frost')
                location_info.first_frost_date = frost_info.get('first_frost')
                location_info.growing_season_days = frost_info.get('growing_days')
            
            # Determine climate type
            location_info.climate_type = self._determine_climate_type(location_info, country)
            
            country_flag = "🇺🇸" if country == "us" else "🇨🇦"
            print(f"📍 {country_flag} Location info for {cleaned_code}: {location_info.city}, {location_info.state} (Zone {location_info.usda_zone})")
            
        except Exception as e:
            print(f"❌ Error getting location info for {cleaned_code}: {e}")
        
        return location_info
    
    async def _get_basic_location_info(self, postal_code: str, country: str) -> Optional[Dict[str, Any]]:
        """
        Get basic location info (city, state/province) from postal/zip code
        Uses multiple fallback methods for comprehensive coverage
        """
        try:
            # Primary method: zippopotam.us API
            url = f"http://api.zippopotam.us/{country}/{postal_code}"
            response = await self.client.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'city': data['places'][0]['place name'],
                    'state': data['places'][0]['state'],  # Province for Canada
                    'state_code': data['places'][0]['state abbreviation'],
                    'latitude': float(data['places'][0]['latitude']),
                    'longitude': float(data['places'][0]['longitude']),
                    'country': country.upper()
                }
        except Exception as e:
            print(f"⚠️  Primary location API failed: {e}")
        
        # Fallback for Canadian postal codes: Use known major city mappings
        if country == "ca":
            return self._get_canadian_fallback_location(postal_code)
        
        return None
    
    def _get_canadian_fallback_location(self, postal_code: str) -> Optional[Dict[str, Any]]:
        """
        Fallback location data for Canadian postal codes when API fails
        Uses first letter (Forward Sortation Area) to determine region
        """
        try:
            first_letter = postal_code[0].upper()
            
            # Major Canadian city mappings by FSA
            canadian_locations = {
                'A': {'city': 'St. Johns', 'state': 'Newfoundland and Labrador', 'state_code': 'NL'},
                'B': {'city': 'Halifax', 'state': 'Nova Scotia', 'state_code': 'NS'},
                'C': {'city': 'Charlottetown', 'state': 'Prince Edward Island', 'state_code': 'PE'},
                'E': {'city': 'Moncton', 'state': 'New Brunswick', 'state_code': 'NB'},
                'G': {'city': 'Quebec City', 'state': 'Quebec', 'state_code': 'QC'},
                'H': {'city': 'Montreal', 'state': 'Quebec', 'state_code': 'QC'},
                'J': {'city': 'Sherbrooke', 'state': 'Quebec', 'state_code': 'QC'},
                'K': {'city': 'Ottawa', 'state': 'Ontario', 'state_code': 'ON'},
                'L': {'city': 'Hamilton', 'state': 'Ontario', 'state_code': 'ON'},
                'M': {'city': 'Toronto', 'state': 'Ontario', 'state_code': 'ON'},
                'N': {'city': 'London', 'state': 'Ontario', 'state_code': 'ON'},
                'P': {'city': 'Sudbury', 'state': 'Ontario', 'state_code': 'ON'},
                'R': {'city': 'Winnipeg', 'state': 'Manitoba', 'state_code': 'MB'},
                'S': {'city': 'Saskatoon', 'state': 'Saskatchewan', 'state_code': 'SK'},
                'T': {'city': 'Calgary', 'state': 'Alberta', 'state_code': 'AB'},
                'V': {'city': 'Vancouver', 'state': 'British Columbia', 'state_code': 'BC'},
                'X': {'city': 'Yellowknife', 'state': 'Northwest Territories', 'state_code': 'NT'},
                'Y': {'city': 'Whitehorse', 'state': 'Yukon', 'state_code': 'YT'},
            }
            
            location_data = canadian_locations.get(first_letter)
            if location_data:
                print(f"🇨🇦 Using fallback location data for {postal_code}")
                return {
                    'city': location_data['city'],
                    'state': location_data['state'],
                    'state_code': location_data['state_code'],
                    'latitude': 45.0,  # Approximate Canadian latitude
                    'longitude': -75.0,  # Approximate Canadian longitude
                    'country': 'CA'
                }
        except Exception as e:
            print(f"❌ Canadian fallback location failed: {e}")
        
        return None
    
    async def _get_hardiness_zone(self, postal_code: str, country: str) -> Optional[str]:
        """
        Get hardiness zone for the postal code
        Uses USDA zones for US, Canadian zones for Canada
        """
        if country == "us":
            return await self._get_us_hardiness_zone(postal_code)
        else:
            return await self._get_canadian_hardiness_zone(postal_code)
    
    async def _get_us_hardiness_zone(self, zip_code: str) -> Optional[str]:
        """
        Get USDA hardiness zone for US zip code
        """
        try:
            zip_num = int(zip_code)
            
            # Simplified zone mapping based on common zip code ranges
            if 1000 <= zip_num <= 9999:  # Northeast (New England)
                return "4a-6b"
            elif 10000 <= zip_num <= 19999:  # Northeast (NY, PA, NJ)
                return "5a-7a"
            elif 20000 <= zip_num <= 26999:  # Mid-Atlantic (MD, DC, VA)
                return "6a-8a"
            elif 27000 <= zip_num <= 28999:  # Southeast (NC)
                return "6b-8a"
            elif 29000 <= zip_num <= 31999:  # Southeast (SC, GA)
                return "7a-9a"
            elif 32000 <= zip_num <= 34999:  # Southeast (FL)
                return "8b-11"
            elif 35000 <= zip_num <= 36999:  # Southeast (AL, TN)
                return "6b-8a"
            elif 37000 <= zip_num <= 38999:  # Southeast (KY, WV)
                return "5b-7a"
            elif 39000 <= zip_num <= 39999:  # Mississippi
                return "7a-9a"
            elif 40000 <= zip_num <= 41999:  # Kentucky
                return "6a-7a"
            elif 42000 <= zip_num <= 45999:  # Ohio, Indiana
                return "5a-6b"
            elif 46000 <= zip_num <= 47999:  # Indiana, Michigan
                return "5a-6a"
            elif 48000 <= zip_num <= 49999:  # Michigan
                return "4a-6a"
            elif 50000 <= zip_num <= 52999:  # Iowa, Minnesota
                return "3a-5a"
            elif 53000 <= zip_num <= 54999:  # Wisconsin
                return "3a-5a"
            elif 55000 <= zip_num <= 56999:  # Minnesota, North Dakota
                return "2a-4a"
            elif 57000 <= zip_num <= 57999:  # South Dakota
                return "3a-4b"
            elif 58000 <= zip_num <= 58999:  # North Dakota
                return "2a-4a"
            elif 59000 <= zip_num <= 59999:  # Montana
                return "3a-5a"
            elif 60000 <= zip_num <= 62999:  # Illinois
                return "5a-6a"
            elif 63000 <= zip_num <= 65999:  # Missouri, Arkansas
                return "6a-7b"
            elif 66000 <= zip_num <= 67999:  # Kansas
                return "5a-7a"
            elif 68000 <= zip_num <= 69999:  # Nebraska
                return "4a-5b"
            elif 70000 <= zip_num <= 71999:  # Louisiana
                return "8a-10a"
            elif 72000 <= zip_num <= 72999:  # Arkansas
                return "6b-8a"
            elif 73000 <= zip_num <= 74999:  # Oklahoma
                return "6a-8a"
            elif 75000 <= zip_num <= 79999:  # Texas
                return "7a-10a"
            elif 80000 <= zip_num <= 81999:  # Colorado
                return "3a-6a"
            elif 82000 <= zip_num <= 83999:  # Wyoming, Idaho
                return "3a-6a"
            elif 84000 <= zip_num <= 84999:  # Utah
                return "4a-7a"
            elif 85000 <= zip_num <= 86999:  # Arizona
                return "7a-10b"
            elif 87000 <= zip_num <= 88999:  # New Mexico
                return "4a-8a"
            elif 89000 <= zip_num <= 89999:  # Nevada
                return "5a-9a"
            elif 90000 <= zip_num <= 96999:  # California
                return "8a-11"
            elif 97000 <= zip_num <= 97999:  # Oregon
                return "6a-9a"
            elif 98000 <= zip_num <= 99999:  # Washington
                return "5a-9a"
            else:
                return "6a-7a"  # Default zone
                
        except ValueError:
            return "6a-7a"  # Default for invalid zip codes
    
    async def _get_canadian_hardiness_zone(self, postal_code: str) -> Optional[str]:
        """
        Get Canadian hardiness zone for Canadian postal code
        Based on first letter of postal code (Forward Sortation Area)
        """
        try:
            # Canadian postal codes: first letter indicates general region
            first_letter = postal_code[0].upper()
            
            # Mapping based on Canadian hardiness zones
            # Note: Canadian zones are generally colder than equivalent US zones
            zone_mapping = {
                'A': '4a-6a',    # Newfoundland, Labrador
                'B': '5a-7a',    # Nova Scotia, New Brunswick
                'C': '6a-8a',    # Prince Edward Island
                'E': '4a-6a',    # New Brunswick
                'G': '3a-5a',    # Eastern Quebec
                'H': '4a-6a',    # Montreal area, Quebec
                'J': '3a-5a',    # Western Quebec
                'K': '4a-6a',    # Eastern Ontario (Ottawa)
                'L': '5a-7a',    # Central Ontario
                'M': '6a-7a',    # Toronto area
                'N': '4a-6a',    # Southwestern Ontario
                'P': '2a-4a',    # Northern Ontario
                'R': '2a-4a',    # Manitoba
                'S': '1a-3a',    # Saskatchewan
                'T': '2a-4a',    # Alberta
                'V': '6a-9a',    # British Columbia (varies greatly)
                'X': '0a-2a',    # Northwest Territories, Nunavut
                'Y': '0a-1a',    # Yukon
            }
            
            return zone_mapping.get(first_letter, '4a-6a')  # Default to moderate zone
            
        except (IndexError, AttributeError):
            return '4a-6a'  # Default zone
    
    async def _get_frost_dates(self, postal_code: str, country: str, province_state: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get first and last frost dates for the location
        Different patterns for US vs Canada
        """
        if country == "us":
            return await self._get_us_frost_dates(postal_code, province_state)
        else:
            return await self._get_canadian_frost_dates(postal_code, province_state)
    
    async def _get_us_frost_dates(self, zip_code: str, state: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get frost dates for US locations
        """
        try:
            zip_num = int(zip_code)
            current_year = datetime.now().year
            
            # Basic frost date estimation based on US climate patterns
            if 1000 <= zip_num <= 19999:  # Northeast
                last_frost = date(current_year, 4, 15)
                first_frost = date(current_year, 10, 15)
            elif 20000 <= zip_num <= 34999:  # Southeast
                last_frost = date(current_year, 3, 15)
                first_frost = date(current_year, 11, 15)
            elif 35000 <= zip_num <= 39999:  # Deep South
                last_frost = date(current_year, 2, 28)
                first_frost = date(current_year, 12, 1)
            elif 40000 <= zip_num <= 56999:  # Midwest
                last_frost = date(current_year, 4, 30)
                first_frost = date(current_year, 10, 1)
            elif 57000 <= zip_num <= 59999:  # Northern Plains
                last_frost = date(current_year, 5, 15)
                first_frost = date(current_year, 9, 15)
            elif 60000 <= zip_num <= 69999:  # Central
                last_frost = date(current_year, 4, 15)
                first_frost = date(current_year, 10, 15)
            elif 70000 <= zip_num <= 79999:  # South Central
                last_frost = date(current_year, 3, 1)
                first_frost = date(current_year, 11, 30)
            elif 80000 <= zip_num <= 89999:  # Mountain West
                last_frost = date(current_year, 5, 1)
                first_frost = date(current_year, 9, 30)
            elif 90000 <= zip_num <= 96999:  # California
                last_frost = date(current_year, 2, 1)
                first_frost = date(current_year, 12, 15)
            else:  # Pacific Northwest
                last_frost = date(current_year, 3, 15)
                first_frost = date(current_year, 11, 1)
            
            growing_days = (first_frost - last_frost).days
            
            return {
                'last_frost': last_frost,
                'first_frost': first_frost,
                'growing_days': growing_days
            }
            
        except Exception as e:
            print(f"❌ Error calculating US frost dates: {e}")
            return None
    
    async def _get_canadian_frost_dates(self, postal_code: str, province: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get frost dates for Canadian locations
        Generally shorter growing seasons than US
        """
        try:
            first_letter = postal_code[0].upper()
            current_year = datetime.now().year
            
            # Canadian frost dates by region (generally more conservative/shorter seasons)
            frost_patterns = {
                'A': (date(current_year, 5, 20), date(current_year, 9, 30)),   # Newfoundland
                'B': (date(current_year, 5, 1), date(current_year, 10, 15)),   # Nova Scotia
                'C': (date(current_year, 4, 25), date(current_year, 10, 20)),  # PEI
                'E': (date(current_year, 5, 10), date(current_year, 10, 1)),   # New Brunswick
                'G': (date(current_year, 5, 15), date(current_year, 9, 25)),   # Eastern Quebec
                'H': (date(current_year, 5, 5), date(current_year, 10, 5)),    # Montreal
                'J': (date(current_year, 5, 20), date(current_year, 9, 20)),   # Western Quebec
                'K': (date(current_year, 5, 1), date(current_year, 10, 1)),    # Ottawa
                'L': (date(current_year, 4, 20), date(current_year, 10, 15)),  # Central Ontario
                'M': (date(current_year, 4, 15), date(current_year, 10, 20)),  # Toronto
                'N': (date(current_year, 4, 25), date(current_year, 10, 10)),  # SW Ontario
                'P': (date(current_year, 6, 1), date(current_year, 9, 1)),     # Northern Ontario
                'R': (date(current_year, 5, 25), date(current_year, 9, 20)),   # Manitoba
                'S': (date(current_year, 5, 30), date(current_year, 9, 15)),   # Saskatchewan
                'T': (date(current_year, 5, 20), date(current_year, 9, 25)),   # Alberta
                'V': (date(current_year, 3, 15), date(current_year, 11, 1)),   # BC (varies)
                'X': (date(current_year, 6, 15), date(current_year, 8, 20)),   # Northwest Territories
                'Y': (date(current_year, 6, 20), date(current_year, 8, 15)),   # Yukon
            }
            
            last_frost, first_frost = frost_patterns.get(first_letter, 
                (date(current_year, 5, 15), date(current_year, 9, 30)))  # Default
            
            growing_days = (first_frost - last_frost).days
            
            return {
                'last_frost': last_frost,
                'first_frost': first_frost,
                'growing_days': growing_days
            }
            
        except Exception as e:
            print(f"❌ Error calculating Canadian frost dates: {e}")
            return None
    
    def _determine_climate_type(self, location: LocationInfo, country: str) -> str:
        """
        Determine general climate type based on location data
        Accounts for generally colder Canadian climate
        """
        if not location.usda_zone:
            return "cold" if country == "ca" else "temperate"
        
        zone = location.usda_zone.lower()
        
        # Canadian zones are generally shifted colder
        if country == "ca":
            if any(z in zone for z in ["0", "1", "2", "3"]):
                return "arctic"
            elif any(z in zone for z in ["4", "5"]):
                return "cold"
            elif any(z in zone for z in ["6", "7"]):
                return "temperate"
            elif any(z in zone for z in ["8", "9"]):
                return "warm"
            else:
                return "cold"
        else:
            # US zones
            if any(z in zone for z in ["2", "3", "4"]):
                return "cold"
            elif any(z in zone for z in ["5", "6", "7"]):
                return "temperate"
            elif any(z in zone for z in ["8", "9"]):
                return "warm"
            elif any(z in zone for z in ["10", "11"]):
                return "tropical"
            else:
                return "temperate"
    
    async def close(self):
        """
        Close the HTTP client
        """
        await self.client.aclose()

# Global instance
location_service = LocationService()