import requests
import json

def get_agents_json():
    url = "https://valorant-api.com/v1/agents"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erreur : {response.status_code}")
        return None

if __name__ == "__main__":
    agents_data = get_agents_json().get('data')
    print(agents_data[0].get('abilities'))

    ## save the raw json data to a file
    with open('agents_raw.json', 'w') as f:
        json.dump(agents_data, f, indent=4)
    print("Raw JSON data saved to agents_raw.json")