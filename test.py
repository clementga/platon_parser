from urllib.parse import ParseResult
from dataclasses import asdict
import parsers.pl

from get_location import get_location

testpath = 'test/test.pl'

parser = parsers.pl.PLParser(testpath, 0, 0, get_location)
output = parser.parse()
print(asdict(output))