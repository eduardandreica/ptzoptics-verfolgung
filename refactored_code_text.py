# imports
import cv2
import mediapipe as mp
from mediapipe.python.solutions import pose as mp_pose
import time
import keyboard
from http_commands import PtzCommands  # Assuming http_commands.py exists

# --- Configuration ---
# Camera settings
CAMERA_CONFIG = {
    1: {"ip": "192.168.1.37", "source": 1},
    2: {"ip": "192.168.1.245", "source": 2},
}
DEFAULT_CAMERA_ID = 2

# Frame processing settings
FRAME_WIDTH = 1120
FRAME_HEIGHT = 630
PROCESSING_WIDTH = 140  # Smaller size for faster MediaPipe processing
PROCESSING_HEIGHT = 80

# Tracking box ratios
LEFT_LINE_RATIO = 0.35
RIGHT_LINE_RATIO = 0.65
TOP_LINE_RATIO = 0.2
BOTTOM_LINE_RATIO = 0.45

# Colors (BGR format)
COLORS = {
    "BLUE": (255, 0, 0),
    "WHITE": (255, 255, 255),
    "RED": (0, 0, 255),
    "GREEN": (0, 255, 0),
    "YELLOW": (0, 175, 175)
}
# ---------------------


class CameraTracker:
    def __init__(self):
        # MediaPipe setup
        self.mp_pose = mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_complexity=0
        )

        # State variables
        self.cam = None
        self.ptz_controller = None
        self.tracking_enabled = True
        self.movement_state = "stop"
        self.key_toggle_pressed = False  # For 'f' key debounce

        # FPS calculation
        self.prev_time = time.time()
        self.fps = 0

        # Initial setup
        self.window_name = "Gesichtsverfolgung"
        cv2.namedWindow(self.window_name)
        self._select_camera(DEFAULT_CAMERA_ID)

    def _select_camera(self, camera_id):
        """Releases the current camera and initializes a new one."""
        if camera_id not in CAMERA_CONFIG:
            print(f"Error: Camera ID {camera_id} not in CONFIG.")
            return

        if self.cam:
            self.cam.release()
            print(f"Released camera.")

        config = CAMERA_CONFIG[camera_id]
        self.cam = cv2.VideoCapture(config["source"])
        if not self.cam.isOpened():
            print(f"Error: Could not open camera source {config['source']}")
            return
            
        self.ptz_controller = PtzCommands(config["ip"])
        print(f"Selected camera {camera_id} at {config['ip']}")

    def _handle_keyboard_input(self):
        """
        Handles all keyboard input for camera switching, tracking toggle, and exit.
        Returns True if the program should quit, False otherwise.
        """
        # Check for window close or ESC key
        key = cv2.waitKey(1)
        if key == 27 or cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) < 1:
            return True  # Signal to quit

        # Toggle tracking with 'f' key
        if keyboard.is_pressed('f'):
            if not self.key_toggle_pressed:
                self.tracking_enabled = not self.tracking_enabled
                self.key_toggle_pressed = True
        else:
            self.key_toggle_pressed = False

        # Camera selection
        if keyboard.is_pressed("1"):
            self._select_camera(1)
        if keyboard.is_pressed("2"):
            self._select_camera(2)

        return False  # Signal to continue

    def _calculate_fps(self):
        """Calculates and updates the FPS."""
        curr_time = time.time()
        self.fps = int(1 / (curr_time - self.prev_time))
        self.prev_time = curr_time

    def _process_frame(self, frame):
        """Processes the frame for pose detection and draws landmarks."""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Process a smaller, resized image for performance
        frame_small = cv2.resize(frame_rgb, (PROCESSING_WIDTH, PROCESSING_HEIGHT))
        results = self.mp_pose.process(frame_small)

        if results.pose_landmarks:
            # Draw landmarks on the *original* frame
            for i, landmark in enumerate(results.pose_landmarks.landmark):
                x = int(landmark.x * FRAME_WIDTH)
                y = int(landmark.y * FRAME_HEIGHT)
                
                # Highlight the nose (landmark 0)
                color = COLORS["RED"] if i == 0 else COLORS["BLUE"]
                cv2.circle(frame, (x, y), 5, color, -1)
                
        return results.pose_landmarks

    def _update_tracking_logic(self, landmarks, lines):
        """Contains all logic for moving the PTZ camera based on target position."""
        left_line, right_line, top_line, bottom_line = lines

        # Stop moving if tracking is disabled or no person is detected
        if not self.tracking_enabled or not landmarks:
            if self.movement_state != "stop":
                self.ptz_controller.stop()
                self.movement_state = "stop"
            return

        # Get target coordinates (using nose landmark 0)
        target_x = landmarks.landmark[0].x * FRAME_WIDTH
        target_y = landmarks.landmark[0].y * FRAME_HEIGHT

        # Determine new movement state
        new_state = "stop"
        
        # Diagonal movements
        if target_x < left_line and target_y < top_line:
            new_state = "linksoben"  # Original func name
        elif target_x > right_line and target_y < top_line:
            new_state = "rechtsoben"
        elif target_x < left_line and target_y > bottom_line:
            new_state = "linksunten"
        elif target_x > right_line and target_y > bottom_line:
            new_state = "rechtsunten"
            
        # Vertical movements
        elif target_y < top_line and left_line < target_x < right_line:
            new_state = "oben"
        elif target_y > bottom_line and left_line < target_x < right_line:
            new_state = "unten"
            
        # Horizontal movements
        elif target_x < left_line and top_line < target_y < bottom_line:
            new_state = "links"
        elif target_x > right_line and top_line < target_y < bottom_line:
            new_state = "rechts"
        
        # Stop (target is inside the box)
        else:
            new_state = "stop"

        # Only send a command if the state has changed
        if new_state != self.movement_state:
            # Get the correct function from the controller object
            # e.g., self.ptz_controller.links(1) or self.ptz_controller.stop()
            move_function = getattr(self.ptz_controller, new_state)
            
            if new_state == "stop":
                move_function()
            else:
                move_function(1)  # All movement commands seem to take '1'
                
            self.movement_state = new_state

    def _draw_overlay(self, frame, lines):
        """Draws all informational text and lines on the frame."""
        img_h, img_w, _ = frame.shape
        left_line, right_line, top_line, bottom_line = lines

        # Draw tracking box
        cv2.line(frame, (int(left_line), 0), (int(left_line), img_h), COLORS["WHITE"], 2)
        cv2.line(frame, (int(right_line), 0), (int(right_line), img_h), COLORS["WHITE"], 2)
        cv2.line(frame, (0, int(top_line)), (img_w, int(top_line)), COLORS["WHITE"], 2)
        cv2.line(frame, (0, int(bottom_line)), (img_w, int(bottom_line)), COLORS["WHITE"], 2)

        # Draw text
        cv2.putText(frame, '[ESC] zum beenden', (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS["WHITE"], 1)

        track_text = '[f] wird verfolgt' if self.tracking_enabled else '[f] wird nicht verfolgt'
        track_color = COLORS["RED"] if self.tracking_enabled else COLORS["WHITE"]
        cv2.putText(frame, track_text, (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, track_color, 1)

        cv2.putText(frame, f'FPS: {self.fps}', (20, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS["GREEN"], 2)

        # Display the final frame
        cv2.imshow(self.window_name, frame)

    def cleanup(self):
        """Stops the camera and closes all windows."""
        print("Cleaning up...")
        if self.ptz_controller:
            self.ptz_controller.stop()
        if self.cam:
            self.cam.release()
        cv2.destroyAllWindows()

    def run(self):
        """The main loop of the application."""
        while True:
            success, frame = self.cam.read()
            if not success:
                print("Skipped frame")
                continue

            frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
            
            # Calculate line positions for this frame size
            lines = (
                LEFT_LINE_RATIO * FRAME_WIDTH,
                RIGHT_LINE_RATIO * FRAME_WIDTH,
                TOP_LINE_RATIO * FRAME_HEIGHT,
                BOTTOM_LINE_RATIO * FRAME_HEIGHT
            )

            # Core logic
            landmarks = self._process_frame(frame)
            self._update_tracking_logic(landmarks, lines)

            # Info display
            self._calculate_fps()
            self._draw_overlay(frame, lines)

            # Handle input and check for exit
            if self._handle_keyboard_input():
                break

        self.cleanup()


# --- Main execution ---
if __name__ == "__main__":
    try:
        tracker = CameraTracker()
        tracker.run()
    except Exception as e:
        print(f"An error occurred: {e}")
        # Ensure cleanup happens even on error
        if 'tracker' in locals():
            tracker.cleanup()
