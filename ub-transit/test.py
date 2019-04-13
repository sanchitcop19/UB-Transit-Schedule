import json
from lambda_function import get_transit
location_index = {
    'creekside': 0,
    'creekside village': 0,
    'moody terrace': 1
}
intent = json.loads(json.dumps(
    {'slots': {'location': {'value': 'creekside'}, 'vehicle': {'value': 'shuttle'}}, 'name': 'test'}))
get_transit(intent, None)
