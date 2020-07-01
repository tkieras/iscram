
SUPPORTED_LOGIC = set(["and", "or"])


def validate_logic(logic_type):
	return logic_type in SUPPORTED_LOGIC
		

def validate_risk(r):
	if (r < 0.0) or (r > 1.0):
		return False
	else:
		return True

def validate_cost(c):
	if c < 0:
		return False
	else:
		return True