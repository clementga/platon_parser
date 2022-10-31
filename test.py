from urllib.parse import ParseResult
from dataclasses import asdict
import parsers.pl
import json

from get_location import get_location

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)

testpath = 'test/test.pl'

parser = parsers.pl.PLParser(testpath, 0, 0, get_location)
output = parser.parse()


print(json.dumps(asdict(output), indent=2, cls=SetEncoder))

