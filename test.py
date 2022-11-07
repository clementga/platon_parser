from urllib.parse import ParseResult
from dataclasses import asdict
import parsers.pl
import json

from utils import base_get_location

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)

testpath = 'test/test.pl'

parser = parsers.pl.PLParser(testpath, 0, 0, base_get_location, check_mandatory_keys=False)
output = parser.parse()


print(json.dumps(asdict(output), indent=2, cls=SetEncoder))

