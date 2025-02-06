# chatGPT-browser 🧠💬  
A **self-hosted web app** for browsing, searching, and analyzing **ChatGPT conversation exports**.  
Built with **Flask + SQLite**, it allows users to efficiently **paginate, search, and view** their chat history—including **text, images, audio, and code snippets**.

---

## 🚀 Features  
✅ **Fast & Local** – No cloud required, everything runs on your machine.  
✅ **Search & Pagination** – Browse **thousands of messages** without lag.  
✅ **Rich Media Support** – View **images, audio, file attachments, and code blocks**.  
✅ **Task & Automation Logs** – Displays structured logs from automated tasks.  
✅ **Conversation History Viewer** – Navigate long threads easily.  
✅ **File Serving API** – Automatically resolves **image & file links** from ChatGPT exports.  

---

## 🛠️ Installation  

### **1️⃣ Clone the Repo**
```sh
git clone https://github.com/actuallyrizzn/chatGPT-browser
cd chatGPT-browser
```

### **2️⃣ Install Dependencies**
Ensure you have Python 3.8+ installed, then run:
```sh
pip install -r requirements.txt
```

### **3️⃣ Set Up Your Chat Data**
The easiest way to not have to do a lot of customziation is to put these files in the same directory you expanded your export into. You will need to modify the absolute file path locations in your app.py and import_json.py.

### **4️⃣ Initialize the Database**
```sh
python import_json.py
```
This will parse `conversations.json` and insert it into `athena.db`.

### **5️⃣ Run the Web App**
```sh
python app.py
```
The app will be available at:
```
http://127.0.0.1:5000/
```

---

## 🖼️ Screenshots  
### 🔍 **Conversation Browser**  
![Conversations List](https://github.com/user-attachments/assets/ca2b7c20-0fa0-436b-be23-b300c7f9843a)


### 📝 **Message Viewer with Media Support**  
![Messages View](https://github.com/user-attachments/assets/619d52c7-821d-48e7-8349-74a24ba34ccd)


---

## ⚙️ Configuration  
Modify `app.py` to adjust:
- **`UPLOAD_FOLDER`** → Change where images/files are stored.
- **Database settings** (if migrating from SQLite).
- **Pagination settings** (`LIMIT 50 OFFSET X` for large datasets).

---

## 🏗️ Contributing  
1. **Fork this repository**  
2. **Create a feature branch**:  
   ```sh
   git checkout -b feature-name
   ```
3. **Commit your changes**  
   ```sh
   git commit -m "Added awesome feature"
   ```
4. **Push to your branch**  
   ```sh
   git push origin feature-name
   ```
5. **Create a Pull Request** 🎉  

---

## 📜 License  
MIT License – Feel free to use, modify, and distribute.  

---

## 🔥 Future Plans  
- **🔍 Full-Text Search**
- **📂 File Attachment Previews**
- **🔄 Syncing with Live Chat Data**
- **📊 Conversation Analytics & Trends**

💡 **Ideas? Issues?** Submit a [GitHub Issue](https://github.com/YOUR_GITHUB_USERNAME/athena-chat-explorer/issues).  

---

## ❤️ Support  
If you like this project, **star the repo ⭐** and consider contributing!  

---

### **🚀 Built With:**
- **Flask** – Backend Web Server
- **SQLite** – Lightweight Database
- **DataTables.js** – Dynamic Tables
- **Highlight.js** – Code Formatting  
```
