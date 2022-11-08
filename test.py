from dataclasses import asdict
import json

from parser import parse_file
from utils import base_get_location


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)

testpath = 'test/blah.pl'

output = parse_file(testpath, 0, 0, base_get_location)


print(json.dumps(asdict(output), indent=2, cls=SetEncoder))

