from urllib.parse import ParseResult
from dataclasses import asdict
import parsers.pl

testpath = 'platon_parser/test/test.pl'

parser = parsers.pl.PLParser(testpath, 0)
output = parser.parse()
print(asdict(output))