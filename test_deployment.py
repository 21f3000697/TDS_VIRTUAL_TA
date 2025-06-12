import requests
import json

def test_deployed_api():
    # The base URL of your deployed application
    base_url = "https://tds-virtual-ta-n3hk.onrender.com"
    
    print("\nTesting root endpoint (GET request)...")
    try:
        root_response = requests.get(base_url)
        print(f"Root endpoint status: {root_response.status_code}")
    except Exception as e:
        print(f"Root endpoint check failed: {str(e)}")

    # Test API endpoint with question
    print("\nTesting question API endpoint...")
    api_url = f"{base_url}/api/"  # Note the /api/ endpoint!
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "question": "How do I calculate tokens?"
    }
    
    print(f"\nSending POST request to: {api_url}")
    print(f"Request headers: {headers}")
    print(f"Request body: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(api_url, headers=headers, json=data)
        print(f"\nResponse status code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API call successful!")
            print(f"Response body: {json.dumps(response.json(), indent=2)}")
        else:
            print("❌ API call failed!")
            print(f"Error response: {response.text}")
            print("\nCommon issues:")
            print("1. Make sure you're using the /api/ endpoint")
            print("2. Make sure you're sending a POST request")
            print("3. Make sure your request has the correct headers and JSON body")
            print("\nExample curl command:")
            print(f'''curl -X POST "{api_url}" \\
    -H "Content-Type: application/json" \\
    -H "Accept: application/json" \\
    -d '{{"question": "How do I calculate tokens?"}}\'''')
    except Exception as e:
        print(f"API request failed: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Check if the service is running")
        print("2. Verify the URL is correct")
        print("3. Check your internet connection")
        print(f"4. Try accessing the docs at: {base_url}/docs")

if __name__ == "__main__":
    test_deployed_api() 