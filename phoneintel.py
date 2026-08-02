"""PhoneIntel — free phone-number validation via numverify API.

Free tier: 100 requests/month after a free API key (https://numverify.com).
Returns validity, country, carrier and line type — NOT the owner's identity
(name/age/address requires paid data-broker services).
"""

import os
import requests


class PhoneIntel:
    def __init__(self, phone):
        self.phone = phone
        self.result = {}

    def query(self):
        api_key = os.environ.get("NUMVERIFY_API_KEY", "")
        if not api_key:
            self.result = {
                "phone": self.phone,
                "error": "No NUMVERIFY_API_KEY set — demo mode. "
                         "Get a free key at https://numverify.com",
            }
            return self.result

        url = "http://apilayer.net/api/validate"
        params = {"access_key": api_key, "number": self.phone}
        try:
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            if data.get("valid"):
                self.result = {
                    "phone": self.phone,
                    "valid": True,
                    "country": data.get("country_name", "Unknown"),
                    "location": data.get("location", "N/A"),
                    "carrier": data.get("carrier", "Unknown"),
                    "line_type": data.get("line_type", "Unknown"),
                }
            else:
                self.result = {"phone": self.phone, "valid": False,
                               "error": data.get("error", {}).get("info", "invalid number")}
        except Exception as e:
            self.result = {"phone": self.phone, "error": str(e)}
        return self.result
      
