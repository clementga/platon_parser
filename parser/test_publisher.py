import json

from parser import parse_file
from utils import base_get_location

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)

output = parse_file("test/test.pl", 0, 0, base_get_location)

exercise = dict()

exercise['cid'] = 0
exercise['author'] = output.data['author']
exercise['version'] = output.data['version']
exercise['process'] = output.data

print(json.dumps(exercise, indent=2, cls=SetEncoder))