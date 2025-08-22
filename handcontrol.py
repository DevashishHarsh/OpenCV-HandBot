import cv2
import mediapipe as mp
import numpy as np
import pybullet as p
import pybullet_data
import time


def lerp(a, b, t):
    temp = []
    for i in range(3):
        temp.append(a[i] + (b[i] - a[i]) * t) 
    return temp

def finger_is_closed(landmarks, tip_id, pip_id):
    return landmarks[tip_id].y > landmarks[pip_id].y

def thumb_is_closed(landmarks):
    return landmarks[4].x < landmarks[2].x



# Initialize PyBullet
physicsClient = p.connect(p.GUI)
p.setGravity(0, 0, -9.81)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
planeId = p.loadURDF("plane.urdf")

# Load your robot
robot_id = p.loadURDF("Handbot/HandBot.urdf", [0, 0, 1], useFixedBase=True)

# Get end-effector index
end_effector_index = 4  # <-- Replace with your actual EE joint index
up_vector = [0, 0, 1]
rest_pose = [0.0] * 20
rest_pose[0] = 3.14

joint_map = {
    "pinky":  [5,6,7],
    "ring":   [8,9,10],
    "middle": [11,12,13],
    "index":  [14,15,16],
    "thumb":  [17,18,19]
}

# Joint presets
joint_targets = {
    "pinky":  [(0, 0, 0), (1.1,1.5,1.2)],
    "ring":   [(0, 0, 0), (1.5, 1.5, 1)],
    "middle": [(0, 0, 0), (1.5, 1.5, 1.2)],
    "index":  [(0, 0, 0), (1.5, 1.15, 1)],
    "thumb":  [(0, 0, 0), (1.5, -1.5, -1.5)],
}



# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=1,
                       min_detection_confidence=0.7,
                       min_tracking_confidence=0.7)

mp_drawing = mp.solutions.drawing_utils

# OpenCV webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        continue

    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:

            lm = hand_landmarks.landmark

            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get wrist base (landmark 0)
            
            wrist = lm[0]
            x = wrist.x
            y = wrist.y
            z = wrist.z  # z is relative depth

            calc_x = -(x-0.5)*0.8

            calc_z = (1-y)*1.8

            x_world = np.clip(calc_x,-0.4,0.4)
            y_world = -0.25
            z_world = np.clip(calc_z,0.5,0.9)

            link_state = p.getLinkState(robot_id, 4)

            current_pos = link_state[4]  # if it's not already a list
            target_pos = [-x_world, y_world, z_world]
            alpha = 0.8  # smoothing factor (0.0 = no movement, 1.0 = instant jump)
            smoothed_pos = lerp(current_pos, target_pos, alpha)
            
            upright_quat = p.getQuaternionFromEuler([0, 0, 0])

            joint_positions = p.calculateInverseKinematics(
                robot_id,
                end_effector_index,
                smoothed_pos,
                targetOrientation=upright_quat,
                restPoses=rest_pose,
                jointDamping=[0.1] * 20
            )
        

            state = {}
            state['pinky'] = finger_is_closed(lm, 20, 18)
            state['ring'] = finger_is_closed(lm, 16, 14)
            state['middle'] = finger_is_closed(lm, 12, 10)
            state['index'] = finger_is_closed(lm, 8, 6)
            state['thumb'] = thumb_is_closed(lm)

            # Set joint angles
            for finger, joints in joint_map.items():
                closed = state[finger]
                if finger == "index" and state['thumb'] == False and closed:
                    values = (1.5, 1.5, 1) 
                elif finger == "pinky" and state['ring'] == False and closed:
                    values = (1.5, 1.5, 0.45)
                elif closed:
                    values = joint_targets[finger][1]
                else:
                    values = joint_targets[finger][0]

                for i, val in zip(joints, values):
                    p.setJointMotorControl2(robot_id, i, p.POSITION_CONTROL, targetPosition=val)

            exclude_fingers = set(range(5, 20))


            for i in range(len(joint_positions)):
                if i in exclude_fingers:
                    continue  # skip finger joints
                p.setJointMotorControl2(robot_id,
                            i,
                            p.POSITION_CONTROL,
                            targetPosition=joint_positions[i])
                



    # Show webcam feed
    image = cv2.flip(image, 1)
    cv2.imshow("Hand Tracking", image)

    p.resetDebugVisualizerCamera(
    cameraDistance=2,
    cameraYaw=180,
    cameraPitch=-30,
    cameraTargetPosition=[0, 0, 0]
)

    p.stepSimulation()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
p.disconnect()
