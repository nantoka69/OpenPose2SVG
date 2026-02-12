import math
DEFAULT_CANVAS_WIDTH = 400
DEFAULT_CANVAS_HEIGHT = 400
DEFAULT_COLOR = "#cccccc"
FACE_KEYPOINT_COLOR = "#ffffff"
POSE_BONE_ALPHA_VALUE = "0.6"

from .keypoints import KeyPoint
from .pose_keypoint_colors import POSE_KEYPOINT_COLORS
from .pose_bone_colors import POSE_BONE_COLORS

class SVGRenderer:
    """
    Class to render OpenPose JSON data into SVG format.
    The OpenPose format consists of a list of pose data entries at the top level.
    This renderer uses the first entry from the list for the entire rendering process.
    """
    
    def __init__(self, pose_json_data):
        """
        Initializes the renderer with OpenPose JSON data.
        Validates the data and extracts the first entry for rendering.
        """
        if not pose_json_data:
            raise Exception("No pose data found")
        self.pose_json_data = pose_json_data
        self.pose_data = pose_json_data[0]
        self.__extract_canvas_size()


    def render(self):
        """
        Renders the stored pose data into an SVG string.
        
        Returns:
            str: The rendered SVG as a string.
        """
        header = self.__generate_svg_header()
        background = self.__generate_background()
        
        people_svg_content = []
        for person in self.pose_data.get('people', []):
            # Parse different keypoint sets
            pose_keypoints = self.__parse_keypoints(person.get('pose_keypoints_2d', []))
            face_keypoints = self.__parse_keypoints(person.get('face_keypoints_2d', []))
            left_hand_keypoints = self.__parse_keypoints(person.get('hand_left_keypoints_2d', []))
            right_hand_keypoints = self.__parse_keypoints(person.get('hand_right_keypoints_2d', []))

            print(f"Pose Keypoints: {len(pose_keypoints)}")
            print(f"Face Keypoints: {len(face_keypoints)}")
            print(f"Left Hand Keypoints: {len(left_hand_keypoints)}")
            print(f"Right Hand Keypoints: {len(right_hand_keypoints)}")
            
            # Render each set
            people_svg_content.append(self.__render_pose(pose_keypoints))
            people_svg_content.append(self.__render_face(face_keypoints))
            people_svg_content.append(self.__render_hand_left(left_hand_keypoints))
            people_svg_content.append(self.__render_hand_right(right_hand_keypoints))
            
        footer = self.__generate_svg_footer()
        
        return header + background + "".join(people_svg_content) + footer

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
        """
        Renders the pose body keypoints and connections (bones).
        """
        if not keypoints:
            return ""
            
        svg_elements = []
        for idx1, idx2 in POSE_BONE_COLORS.keys():
            svg_elements.append(self.__draw_pose_bone(keypoints, idx1, idx2))
            
        return "".join(svg_elements)

    def __render_face(self, keypoints):
        """
        Renders the face keypoints as filled white circles without stroke.
        The circles are encapsulated in a <g id="head"> group.
        """
        if not keypoints:
            return ""
            
        svg_elements = []
        for kp in keypoints:
            if kp.score > 0:
                x, y = self.__scale_head_keypoint_if_needed(kp.x, kp.y)
                svg_elements.append(f'<circle cx="{x}" cy="{y}" r="2" style="fill:{FACE_KEYPOINT_COLOR};stroke:none" />')
                
        if not svg_elements:
            return ""
            
        return f'\t<g id="head">\n\t\t{"".join(svg_elements)}\n\t</g>\n'

    def __render_hand_left(self, keypoints):
        """Internal method to render the left hand. Placeholder for now."""
        return ""

    def __render_hand_right(self, keypoints):
        """Internal method to render the right hand. Placeholder for now."""
        return ""


    def __extract_canvas_size(self):
        """
        Extracts canvas dimensions from the pose data and stores them as attributes.
        """
        self.width = self.pose_data.get('canvas_width', DEFAULT_CANVAS_WIDTH)
        self.height = self.pose_data.get('canvas_height', DEFAULT_CANVAS_HEIGHT)

        print(f"SVG Header: Canvas size {self.width}x{self.height}")


    def __generate_svg_header(self):        
        defs = self.__define_markers()
        
        return f'<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">\n{defs}'


    def __define_markers(self):
        """
        Defines circular markers for all colors used in the pose rendering.
        Returns the <defs> section as a string.
        """
        unique_colors = set(POSE_KEYPOINT_COLORS)
        unique_colors.update(POSE_BONE_COLORS.values())
        unique_colors.add(DEFAULT_COLOR)
        
        markers = []
        for color in sorted(unique_colors):
            marker = f"""
		<marker id="marker_{color}" viewBox="0 0 20 20" refX="10" refY="10" markerWidth="20" markerHeight="20">
			<circle cx="10" cy="10" r="9" style="fill:{color};fill-opacity:{POSE_BONE_ALPHA_VALUE};stroke:none;"/>
		</marker>"""
            markers.append(marker)
            
        return f"\t<defs>{''.join(markers)}\n\t</defs>"

    def __generate_background(self):
        """
        Generates a black background rectangle matching the canvas size.
        The rectangle is encapsulated in an SVG group.
        """
        return f'\t<g id="background">\n\t\t<rect width="{self.width}" height="{self.height}" fill="black" />\n\t</g>\n'

    def __generate_svg_footer(self):
        return "</svg>"

    def __draw_pose_bone(self, keypoints, idx1, idx2):
        """
        Draws a bone between two keypoints if they exist and have a score > 0.
        Uses predefined colors for the bone and the markers but make them semi-transparent.
        """
        if idx1 >= len(keypoints) or idx2 >= len(keypoints):
            return ""
            
        kp1 = keypoints[idx1]
        kp2 = keypoints[idx2]
        
        if kp1.score <= 0 or kp2.score <= 0:
            return ""
            
        x1, y1 = kp1.x, kp1.y
        x2, y2 = kp2.x, kp2.y
        
        # Scale if coordinates are normalized (between 0 and 1)
        x1, y1, x2, y2 = self.__scale_coordinates_if_needed(x1, y1, x2, y2)
            
        # Get bone color
        bone_color = POSE_BONE_COLORS.get((idx1, idx2))
        if not bone_color:
            # Try reverse tuple if not found
            bone_color = POSE_BONE_COLORS.get((idx2, idx1), DEFAULT_COLOR)
            
        # Get marker colors
        color1 = POSE_KEYPOINT_COLORS[idx1] if idx1 < len(POSE_KEYPOINT_COLORS) else DEFAULT_COLOR
        color2 = POSE_KEYPOINT_COLORS[idx2] if idx2 < len(POSE_KEYPOINT_COLORS) else DEFAULT_COLOR
        
        return self.__draw_bezier_loop(x1, y1, color1, x2, y2, color2, bone_color)

    def __scale_coordinates_if_needed(self, x1, y1, x2, y2):
        """
        Scales coordinates if they are normalized (between 0 and 1).
        returnsscaled x1, y1, x2, y2.
        """
        if 0.0 <= x1 <= 1.0 and 0.0 <= y1 <= 1.0 and 0.0 <= x2 <= 1.0 and 0.0 <= y2 <= 1.0:
            x1 *= self.width
            y1 *= self.height
            x2 *= self.width
            y2 *= self.height
        return x1, y1, x2, y2

    def __scale_head_keypoint_if_needed(self, x, y):
        """
        Scales a single head (face) keypoint if the coordinates are normalized.
        Returns scaled x, y.
        """
        if 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0:
            x *= self.width
            y *= self.height
        return x, y

    def __draw_bezier_loop(self, x1, y1, color1, x2, y2, color2, fill_color):
        """
        Draws a bezier curve from (x1, y1) to (x2, y2) and back to (x1, y1).
        Handles of length 10 are orthogonal to the line connecting the two points.
        The loop is filled with fill_color.
        Markers at the points are colored with color1 and color2.
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
        
        return f'<path d="M {x1},{y1} C {cp1x},{cp1y} {cp2x},{cp2y} {x2},{y2} C {cp3x},{cp3y} {cp4x},{cp4y} {x1},{y1}" style="fill:{fill_color};fill-opacity:{POSE_BONE_ALPHA_VALUE};stroke:none" marker-start="url(#marker_{color1})" marker-mid="url(#marker_{color2})" marker-end="url(#marker_{color1})" />'

