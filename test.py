from dataclasses import asdict
import json

from platonparser.parser.parser import parse_file
from platonparser.parser.utils import base_get_location, FullPath


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)

testpath = 'test/test.pl'
with open(testpath, 'rb') as file:
    output = parse_file(file.read(), FullPath(0, testpath), 0, base_get_location)

print(json.dumps(asdict(output), indent=2, cls=SetEncoder))