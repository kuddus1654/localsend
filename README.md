
# Local Send - Ultimate File Sharing & Streaming 🚀

A futuristic, high-performance local file sharing and media streaming application. Share files, stream videos, and chat across devices on your local network with ease.

## ✨ Key Features

### 📂 File Sharing & OTT
-   **Ultra-Fast Transfer**: Share files, images, and videos instantly between devices.
-   **Media Streaming**: Stream movies and music directly in the browser without downloading.
-   **Clipboard Sharing**: Share text content across devices instantly.

### 🛡️ Admin & Security
-   **Host Control**: Only the host can see connected peers and detailed logs.
-   **User Blocking**: Ban unwanted devices with a single click. Blocked users cannot view, download, or share files.
-   **Activity Logs**: Track who is downloading, uploading, or viewing files.
-   **Secure**: Password-protected login system.

### 💻 Cross-Platform
-   Works seamlessly on **Windows, macOS, Linux, Android, and iOS**.
-   **Responsive Design**: A beautiful, neon-themed interface that adapts to any screen size.

---

## 🚀 Getting Started

### Option 1: Run the Executable (Windows)
1.  Download or locate `dist/LocalSend.exe`.
2.  Double-click to run.
3.  The specific URL (e.g., `http://192.168.1.5:8000`) will be displayed and the browser will open.
4.  Open that URL on any device connected to the same Wi-Fi.

### Option 2: Run from Source (Developers)
1.  **Install Python 3.x**.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the application:
    ```bash
    python app.py
    ```

---

## 📖 Admin Guide

### Accessing Admin Controls
1.  Log in as the Host.
2.  Click the **"👥 Network"** button in the navbar.
3.  *(Note: This button is hidden for all other clients).*

### Blocking Users
1.  Open the **Network** modal.
2.  Find the connected user in the list.
3.  Toggle the switch to **OFF**. The user is now blocked from all actions.

### Viewing Logs
1.  Open the **Network** modal.
2.  Scroll down to **Activity Logs**.
3.  You can see real-time updates for:
    -   File Uploads/Downloads
    -   File Views (Streaming)
    -   Clipboard Sharing
    -   User Joins/Leaves

### Shutting Down
To close the server completely, click your **Profile Icon** -> **Logout** (or click Logout in the menu). This will terminate the application window.

---

## ❓ Troubleshooting

-   **"Site can't be reached"**: Ensure both devices are on the **same Wi-Fi**. Check your firewall settings to allow Python/LocalSend.
-   **No "Network" Button**: Only the Host computer can see this button.
-   **Video Buffering**: Ensure you have a strong Wi-Fi signal.
 <button class="nav-tab" onclick="openTab(event, 'wan-share')">🌍 Remote Share</button>