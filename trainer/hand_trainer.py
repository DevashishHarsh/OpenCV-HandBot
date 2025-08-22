import cv2 as c
import mediapipe as mp
import traininghand as train
import pickle
import os
import subprocess
import time
import threading

# --- Ensure paths are relative to the script file, not current working dir ---
base_dir = os.path.abspath(os.path.dirname(__file__)) if "__file__" in globals() else os.getcwd()
training_data_dir = os.path.join(base_dir, "training_data")
os.makedirs(training_data_dir, exist_ok=True)
data_file = os.path.join(training_data_dir, "hand_positions.pkl")
# -------------------------------------------------------------------------

# Setting up MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7)

# Load existing data if file exists
if os.path.exists(data_file):
    with open(data_file, "rb") as f:
        gesture_data = pickle.load(f)
    print("[INFO] Loaded existing dataset.")
else:
    gesture_data = {}
    print("[INFO] Starting new dataset.")

# Start webcam
cap = c.VideoCapture(0)

pose_name = input("Pose name: ")
if pose_name not in gesture_data:
    gesture_data[pose_name] = []

print("[INFO] Press 's' to save current hand pose")
print("[INFO] Press 'a' to automatically save pose at regular intervals")
print("[INFO] Press 'n' to move to next gesture")
print("[INFO] Press 'esc' to exit and save data")

autosave = 1
stopautosave = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip and convert color
    frame = c.flip(frame, 1)
    rgb = c.cvtColor(frame, c.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    c.putText(frame, f"Current Pose: {pose_name}", (10, 30), c.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
    c.imshow("Hand Capture", frame)

    def manualsave():
        # Only call when results.multi_hand_landmarks exists
        hand_landmark = results.multi_hand_landmarks[0]
        adjusted_list = train.adjusted_range(hand_landmark)
        adjusted_pos = train.adjusted_positions(adjusted_list)
        train.add_to_gesture(pose_name, adjusted_pos, gesture_data)

    def automaticsave(name):
        global autosave, stopautosave
        autosave = 0
        if stopautosave:
            print("[INFO] Autosaving stopped mid process. Validate and Trim the dataset")
            print()

        for i in range(100):
            # check again in case hand lost mid autosave
            if not (results and results.multi_hand_landmarks):
                print("[WARN] Hand lost during autosave, aborting autosave loop.")
                break
            hand_landmark = results.multi_hand_landmarks[0]
            adjusted_list = train.adjusted_range(hand_landmark)
            adjusted_pos = train.adjusted_positions(adjusted_list)
            train.add_to_gesture(pose_name, adjusted_pos, gesture_data)
            time.sleep(1)
        autosave = 1
        print(f"[INFO] Finished saving up to 100 points for {name} pose.")

    key = c.waitKey(1)
    if key == 27:  # ESC
        stopautosave = 1
        print("[INFO] Exiting and saving...")
        break

    elif key == ord('s') and results and results.multi_hand_landmarks:
        manualsave()

    elif key == ord('n'):
        pose_name = input("Pose name: ")
        if pose_name not in gesture_data:
            gesture_data[pose_name] = []

    elif key == ord('a') and results and results.multi_hand_landmarks and autosave:
        print("----- Autosaving started. Please keep the hand pose in the webcam view.--------")
        threading.Thread(target=automaticsave, args=(pose_name,), daemon=True).start()

# Save data to file
with open(data_file, "wb") as f:
    pickle.dump(gesture_data, f)
print("[INFO] Dataset saved to", data_file)
print()

run_check = input("Do you want to open the file checker ( y/n ) : ")
if run_check.lower() == "y":
    checker_path = os.path.join(base_dir, "file_checker.py")
    # If file_checker.py is in the same folder, run it; otherwise fallback to just calling 'python file_checker.py'
    if os.path.exists(checker_path):
        subprocess.run(["python", checker_path])
    else:
        subprocess.run(["python", "file_checker.py"])

cap.release()
c.destroyAllWindows()
