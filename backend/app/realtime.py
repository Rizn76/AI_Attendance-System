def run():
    import streamlit as st
    import cv2
    import os
    import numpy as np
    import sqlite3
    from datetime import datetime
    from PIL import Image



    # ---------------- DB ----------------
    conn = sqlite3.connect("attendance.db", check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            date TEXT,
            time TEXT
        )
    """)
    conn.commit()

    BASE_DIR = os.path.dirname(__file__)
    DATASET_DIR = os.path.join(BASE_DIR, "dataset")
    os.makedirs(DATASET_DIR, exist_ok=True)

    MODEL_PATH = os.path.join(BASE_DIR, "trainer.yml")
    LABELS_PATH = os.path.join(BASE_DIR, "labels.npy")

    mode = st.radio("Mode", ["Register", "Train Model", "Attendance"])

    # ================= REGISTER =================
    if mode == "Register":
        name = st.text_input("Enter Name")

        if st.button("Capture Images"):
            if name == "":
                st.warning("Enter name")
                return

            person_dir = os.path.join(DATASET_DIR, name)
            os.makedirs(person_dir, exist_ok=True)

            cap = cv2.VideoCapture(0)
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )

            st.info("Capturing 20 face images...")

            count = 0
            while count < 20:
                ret, frame = cap.read()
                if not ret:
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)

                for (x, y, w, h) in faces:
                    face = gray[y:y+h, x:x+w]
                    face = cv2.resize(face, (200, 200))
                    cv2.imwrite(os.path.join(person_dir, f"{count}.jpg"), face)
                    count += 1

            cap.release()
            st.success("✅ Registration done")

    # ================= TRAIN =================
    elif mode == "Train Model":

        if st.button("Train Now"):

            faces = []
            labels = []
            label_map = {}
            current_label = 0

            for person in os.listdir(DATASET_DIR):
                person_path = os.path.join(DATASET_DIR, person)

                if not os.path.isdir(person_path):
                    continue

                label_map[current_label] = person

                for img_name in os.listdir(person_path):
                    img_path = os.path.join(person_path, img_name)

                    img = Image.open(img_path).convert('L')
                    img_np = np.array(img, 'uint8')

                    faces.append(img_np)
                    labels.append(current_label)

                current_label += 1

            if len(faces) == 0:
                st.error("No data found")
                return

            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.train(faces, np.array(labels))

            recognizer.save(MODEL_PATH)
            np.save(LABELS_PATH, label_map)

            st.success("✅ Model trained")

    # ================= ATTENDANCE =================
    elif mode == "Attendance":

        if not os.path.exists(MODEL_PATH):
            st.error("Train model first!")
            return

        start_camera = st.checkbox("Start Camera")

        if start_camera:

            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.read(MODEL_PATH)
            label_map = np.load(LABELS_PATH, allow_pickle=True).item()

            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )

            cap = cv2.VideoCapture(0)
            frame_placeholder = st.empty()
            status_placeholder = st.empty()

            today = datetime.now().date()

            while start_camera:
                ret, frame = cap.read()
                if not ret:
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)

                for (x, y, w, h) in faces:
                    face = gray[y:y+h, x:x+w]
                    face = cv2.resize(face, (200, 200))

                    label, confidence = recognizer.predict(face)

                    if confidence < 60:
                        name = label_map[label]

                        # CHECK DB
                        check = conn.execute(
                            "SELECT * FROM attendance WHERE name=? AND date=?",
                            (name, today)
                        ).fetchone()

                        if check is None:
                            now = datetime.now()

                            conn.execute(
                                "INSERT INTO attendance (name, date, time) VALUES (?, ?, ?)",
                                (name, today, now.strftime("%H:%M:%S"))
                            )
                            conn.commit()

                            status_placeholder.success(f"✅ {name} marked present")

                        else:
                            status_placeholder.info(f"ℹ️ {name} already marked today")

                        cv2.putText(frame, name, (x, y-10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)
                    else:
                        cv2.putText(frame, "Unknown", (x, y-10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)

                    cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)

                frame_placeholder.image(frame, channels="BGR")

            cap.release()