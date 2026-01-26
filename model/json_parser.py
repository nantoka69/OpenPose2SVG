import json

class ParserError(Exception):
    """Generic exception for the parser layer."""
    pass

class PoseJsonParser:
    def parse_pose_json(self, json_string):
        """
        Parses the input JSON string and returns a tuple (object, pretty_string).
        Catches all exceptions and rethrows them as a ParserError.
        """
        try:
            data = json.loads(json_string)
            pretty_json = json.dumps(data, indent=4)
            return data, pretty_json
        except Exception as e:
            raise ParserError(f"Failed to parse JSON: {str(e)}")
