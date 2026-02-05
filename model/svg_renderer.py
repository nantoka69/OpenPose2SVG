class SVGRenderer:
    """Class to render OpenPose JSON data into SVG format."""

    def render(self, pose_json_data):
        """
        Renders the given pose JSON data into an SVG string.
        Currently ignores the input and returns a simple triangle.
        
        Args:
            pose_json_data (dict): The parsed OpenPose JSON data.
            
        Returns:
            str: The rendered SVG as a string.
        """
        # A simple SVG displaying a blue triangle
        svg_content = """<svg width="400" height="400" xmlns="http://www.w3.org/2000/svg">
  <polygon points="200,50 350,350 50,350" style="fill:lime;stroke:purple;stroke-width:5" />
  <text x="150" y="380" font-family="Arial" font-size="20" fill="black">SVG Triangle</text>
</svg>"""
        return svg_content
