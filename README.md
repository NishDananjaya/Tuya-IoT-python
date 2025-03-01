# Tuya API Application

A custom application to connect and manage IoT devices using the Tuya API. This project is a pilot project to understand the tuya API and it's Applications

---

## 🚀 Features

- Connect IoT devices to Tuya's cloud platform.
- Perform device configuration and control via API calls.
- User-friendly interface for managing devices.

---

## 🛠️ Technology Stack

- **Language:** Python
- **API:** Tuya IoT Cloud API
- **Protocols:** HTTP
- **Platform:** ESP32 IoT devices, Tuya-enabled devices

---

## 📋 Requirements

- Tuya platform supported IoT device
- Tuya Developer Account
- Python 3.8+
- Internet Connection


---

## ⚙️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/NishDananjaya/tuya_API_Application.git
   cd tuya_API_Application

2. **Create a python virtual enviorenment**
   ```python
   python -m venv [your envioronment name]

3. **Install the requirements**
   ```bash
   pip install -r requirements.txt

4. **Crteat a .env file**

    Add following keys 

     - TUYA_ACCESS_ID= 
     - TUYA_ACCESS_KEY= 
     - TUYA_BASE_URL=
     - DEVICE_ID =

    put the fields empty   

---

## 🧿 Future Implementations

- [ ] **Automatically Update Device Status**  
  Real-time updates for device status without manual refresh.
- [ ] **Enhanced User-Friendly GUI**  
  - Automatically display device configurations upon selection.
- [ ] **Scene Management**  
  Add support for creating and managing scenes.
- [ ] **4-Gang Switch Features**  
  - Countdown timer
  - Schedule timer
  - Cycle settings
  - Switch inching
  - Backlight control

---

##  🔗 Uselful links

- [tinyTuya](https://github.com/jasonacox/tinytuya)
- [LocalTuya](https://github.com/rospogrigio/localtuya)
- [Watch Demo](https://drive.google.com/file/d/1RyJzB9uqz2N0TjDua1W7kBAy3JFcULY8/view?usp=drive_link)
