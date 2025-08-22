# OpenCV-HandBot

A real-time robotic hand simulation controlled by your own hand movements using MediaPipe, OpenCV, and PyBullet. The project maps real hand position, orientation, and finger states to a robotic hand URDF model, enabling natural teleoperation of a virtual robot hand.

# HandBot Teleoperation

Control a simulated robotic hand in real time using your own hand gestures!  
This project uses **MediaPipe** for hand tracking, **OpenCV** for camera input, and **PyBullet** for physics-based simulation of a custom URDF robotic hand model.

## Features

- Real-time hand tracking via webcam using [MediaPipe Hands](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker).
- Maps **hand position** and **orientation** directly to the robotic hand’s wrist joint.
- Each finger joint is mapped to open/close gestures:
  - Detects finger state (`open` / `closed`) with MediaPipe landmarks.
  - Supports **special finger combinations** (e.g., index + thumb pinch).
- Ensures the palm stays **upright** in simulation, avoiding noisy Z-axis roll from MediaPipe.
- Physics-based simulation with [PyBullet](https://pybullet.org/wordpress/).
- Easy setup using `requirements.py` (creates `requirements.txt` and virtual environment).

