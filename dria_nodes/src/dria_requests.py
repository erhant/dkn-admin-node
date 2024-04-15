import requests


class DriaClient:
    def __init__(self, auth):
        self.auth = auth
        self.base_url = "http://0.0.0.0:8002"  # Assuming the base URL is the same as in the provided context

    def get_jobs(self):
        headers = {"Authorization": f"Bearer {self.auth}"}
        response = requests.get(f"{self.base_url}/jobs", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError("Failed to get jobs")

    def is_available(self):
        headers = {"Authorization": f"Bearer {self.auth}"}
        response = requests.get(f"{self.base_url}/current_jobs", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError("Failed to get jobs")
