import requests
import json

def get_agents_json():
    url = "https://valorant-api.com/v1/maps"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erreur : {response.status_code}")
        return None

if __name__ == "__main__":
    maps_datas_data = get_agents_json().get('data')

    ## save the raw json data to a file
    with open('maps_raw.json', 'w') as f:
        json.dump(maps_datas_data, f, indent=4)
    print("Raw JSON data saved to agents_raw.json")