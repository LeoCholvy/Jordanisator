import json

## read json file
with open('agents_raw.json', 'r') as f:
    agents_data = json.load(f)
with open('maps_id_to_name.json', 'r') as f:
    maps_data = json.load(f)

# ## get agents names by uuid
# if not agents_data:
#     print("Erreur d'agents json")
#     exit(1)
# uuidToName: dict = {
#     agent['uuid']: agent['displayName']
#     for agent in agents_data
# }
#
# # save to .json file
# with open('agents_uuid_to_name.json', 'w') as f:
#     json.dump(uuidToName, f, indent=4)
# print("UUID to Name mapping saved to agents.json")

def format_tag(tag: str) -> str:
    if not tag:
        return tag
    result = tag[0].upper()
    for i in range(1, len(tag)):
        if tag[i-1] == " " or tag[i-1] == "/":
            result += tag[i].upper()
        else:
            result += tag[i].lower()
    return result

## get all tags
tags: list[str] = []
# agents
tags += [agent['displayName'] for agent in agents_data]
# abilities
tags += [ab['displayName'] for ag in agents_data for ab in ag['abilities']]
# maps
tags += list(maps_data.values())
# side
tags += ["Attacker", "Defender"]
# lower case everything excep for first letter and letters preceded by a space
formatted_tags = [format_tag(tag) for tag in tags]

# save to .json file
with open('tags.json', 'w') as f:
    json.dump(formatted_tags, f, indent=4)
print("Tags saved to tags.json")