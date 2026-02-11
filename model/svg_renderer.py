import math
DEFAULT_CANVAS_WIDTH = 400
DEFAULT_CANVAS_HEIGHT = 400

from .keypoints import KeyPoint

class SVGRenderer:
    """
    Class to render OpenPose JSON data into SVG format.
    The OpenPose format consists of a list of pose data entries at the top level.
    This renderer uses the first entry from the list for the entire rendering process.
    """
    KEYPOINT_MARKER_COLORS = ['#00ff00', '#ff0000', '#0000ff']

    def render(self, pose_json_data):
        """
        Renders the given pose JSON data into an SVG string.
        Extracts the first entry from the input list and uses it for rendering.
        
        Args:
            pose_json_data: The parsed OpenPose JSON data.
            
        Returns:
            str: The rendered SVG as a string.
        """
        
        if not pose_json_data:
            raise Exception("No pose data found")
        pose_data = pose_json_data[0]

        header = self._generate_svg_header(pose_data)
        
        people_svg_content = []
        for person in pose_data.get('people', []):
            # Parse different keypoint sets
            pose_keypoints = self.__parse_keypoints(person.get('pose_keypoints_2d', []))
            face_keypoints = self.__parse_keypoints(person.get('face_keypoints_2d', []))
            left_hand_keypoints = self.__parse_keypoints(person.get('hand_left_keypoints_2d', []))
            right_hand_keypoints = self.__parse_keypoints(person.get('hand_right_keypoints_2d', []))
            
            # Render each set
            people_svg_content.append(self.__render_pose(pose_keypoints))
            people_svg_content.append(self.__render_face(face_keypoints))
            people_svg_content.append(self.__render_hand_left(left_hand_keypoints))
            people_svg_content.append(self.__render_hand_right(right_hand_keypoints))
            
        footer = self._generate_svg_footer()
        
        return header + "".join(people_svg_content) + footer

    def __parse_keypoints(self, keypoint_array):
        """
        Groups a flat array of numbers into KeyPoint objects.
        Each keypoint is represented by 3 consecutive values: x, y, probability.
        """
        keypoints = []
        for i in range(0, len(keypoint_array), 3):
            if i + 2 < len(keypoint_array):
                keypoints.append(KeyPoint(
                    x=keypoint_array[i],
                    y=keypoint_array[i+1],
                    score=keypoint_array[i+2]
                ))
        return keypoints

    def __render_pose(self, keypoints):
        return self.__draw_bezier_loop(400,400,450,450,"#0000ff") + self.__draw_bezier_loop(100,100,100,600,"#ff0000")

    def __render_face(self, keypoints):
        """Internal method to render the face. Placeholder for now."""
        return ""

    def __render_hand_left(self, keypoints):
        """Internal method to render the left hand. Placeholder for now."""
        return ""

    def __render_hand_right(self, keypoints):
        """Internal method to render the right hand. Placeholder for now."""
        return ""


    def _generate_svg_header(self, pose_data):
        width = pose_data.get('canvas_width', DEFAULT_CANVAS_WIDTH)
        height = pose_data.get('canvas_height', DEFAULT_CANVAS_HEIGHT)

        print(f"SVG Header: Canvas size {width}x{height}")
        
        defs = self.__define_markers()
        
        return f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">\n{defs}'

    def __define_markers(self):
        """
        Defines circular markers for a set of sample colors from MARKER_COLORS.
        Returns the <defs> section as a string.
        """
        markers = []
        for color in self.KEYPOINT_MARKER_COLORS:
            marker = f"""
		<marker id="marker_{color}" viewBox="0 0 20 20" refX="10" refY="10" markerWidth="20" markerHeight="20">
			<circle cx="10" cy="10" r="9" style="fill:{color};"/>
		</marker>"""
            markers.append(marker)
            
        return f"\t<defs>{''.join(markers)}\n\t</defs>"

    def _generate_svg_footer(self):
        return "</svg>"

    def __draw_bezier_loop(self, x1, y1, x2, y2, color):
        """
        Draws a bezier curve from (x1, y1) to (x2, y2) and back to (x1, y1).
        Handles of length 10 are orthogonal to the line connecting the two points.
        The loop is filled with the specified color.
        """
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx*dx + dy*dy)
        
        if length < 0.001:
            return ""
        
        # Unit orthogonal vector (nx, ny)
        nx = -dy / length
        ny = dx / length
        
        # Offset for handles
        ox = nx * 10
        oy = ny * 10
        
        # Control points for forward curve
        cp1x, cp1y = x1 + ox, y1 + oy
        cp2x, cp2y = x2 + ox, y2 + oy
        
        # Control points for return curve
        cp3x, cp3y = x2 - ox, y2 - oy
        cp4x, cp4y = x1 - ox, y1 - oy
        
        return f'<path d="M {x1},{y1} C {cp1x},{cp1y} {cp2x},{cp2y} {x2},{y2} C {cp3x},{cp3y} {cp4x},{cp4y} {x1},{y1}" style="fill:{color};stroke:none" marker-start="url(#marker_{color})" marker-mid="url(#marker_{color})" marker-end="url(#marker_{color})" />'

