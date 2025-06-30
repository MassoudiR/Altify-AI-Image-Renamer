import requests
from utils.config import Config  
class DPClient:
    LOGIN_URL = "https://dp.localetmoi.fr/localfr-api/generate-user-token"
    PARTNER_URL = "https://api.local.fr/api/partners?customerCode={code}&properties[]=id"
    DETAILS_URL = "https://api.local.fr{partner_id}"
    COMPANY_URL = "https://dp.localetmoi.fr/api/salesforce/account/{code}"

    def __init__(self):
        self.token = None
        self.config = Config() 

    def login(self):
        username = self.config.get_dp_username()
        password = self.config.get_dp_password()
        creds = {"username": username, "password": password}


        if not username or not password:
            return False

        try:
            r = requests.post(self.LOGIN_URL, json=creds, timeout=5)
            r.raise_for_status()
            self.token = r.json().get("access_token")
            return bool(self.token)
        except:
            return False

    def get_headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    def get_info(self, code):
        if not self.token and not self.login():
            return False, "Login failed"

        try:
            # Get partner ID
            r = requests.get(self.PARTNER_URL.format(code=code), headers=self.get_headers(), timeout=5)
            r.raise_for_status()
            partner_id = r.json().get("hydra:member", [{}])[0].get("@id")

            # Get mainLocality and company code
            r = requests.get(self.DETAILS_URL.format(partner_id=partner_id), headers=self.get_headers(), timeout=5)
            r.raise_for_status()
            data = r.json()
            
            main_locality = data.get("mainLocality")
            seo_keywords_list = data.get("sites")[0].get("seoKeywords")
            seo_keywords = " , ".join(seo_keywords_list[:5])


            company_code = data.get("company")

            # Get industry and code APE
            headers = {
                **self.get_headers(),
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            r = requests.get(self.COMPANY_URL.format(code=company_code), headers=headers, timeout=5)
            r.raise_for_status()
            company = r.json()
            name = company.get("Name")
            industry = company.get("Industry")
            code_ape = company.get("Libell_code_APE__c")
            billing_city = company.get("BillingCity")

            return True, {
                "name": name,
                "mainLocality": main_locality,
                "industry": industry,
                "Libell_code_APE__c": code_ape,
                "seoKeywords": seo_keywords,
                "billingCity": billing_city
            }

        except Exception as e:
            return False, str(e)


