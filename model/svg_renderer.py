DEFAULT_CANVAS_WIDTH = 400
DEFAULT_CANVAS_HEIGHT = 400

class SVGRenderer:
    """
    Class to render OpenPose JSON data into SVG format.
    The OpenPose format consists of a list of pose data entries at the top level.
    This renderer uses the first entry from the list for the entire rendering process.
    """

    def render(self, pose_json_data):
        """
        Renders the given pose JSON data into an SVG string.
        Extracts the first entry from the input list and uses it for rendering.
        
        Args:
            pose_json_data: The parsed OpenPose JSON data.
            
        Returns:
            str: The rendered SVG as a string.
        """
        # OpenPose format has a list of pose data at the top level.
        # We use only the first entry for this project.
        pose_data = pose_json_data[0] if pose_json_data else {}

        header = self._generate_svg_header(pose_data)
        
        # A simple SVG displaying a blue triangle
        sample_body = """
  <polygon points="200,50 350,350 50,350" style="fill:lime;stroke:purple;stroke-width:5" />
  <text x="150" y="380" font-family="Arial" font-size="20" fill="black">SVG Triangle</text>
"""
        footer = self._generate_svg_footer()
        
        return header + sample_body + footer

    def _generate_svg_header(self, pose_data):
        width = pose_data.get('canvas_width', DEFAULT_CANVAS_WIDTH)
        height = pose_data.get('canvas_height', DEFAULT_CANVAS_HEIGHT)

        print(f"SVG Header: Canvas size {width}x{height}")
        
        return f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'

    def _generate_svg_footer(self):
        return "</svg>"

