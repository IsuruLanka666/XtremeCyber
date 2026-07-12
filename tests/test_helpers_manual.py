from core.helpers import parse_port_range, validate_target


print(validate_target("192.168.1.1"))
print(validate_target("example.com"))
print(parse_port_range("22,80,443"))
print(parse_port_range("20-25,80,443"))