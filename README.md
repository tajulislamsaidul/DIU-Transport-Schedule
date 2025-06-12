
---

# 🚍 DIU Transport Schedule Viewer 🗓️

A user-friendly desktop application built with Python and Tkinter to **view, manage, and export** transport route schedules for DIU (Daffodil International University). Easily load transport schedules from Excel, browse routes, save favorites, and export route details to PDF.

---

## ✨ Features

* 📂 **Load Transport Schedule**
  Import route data from Excel (.xlsx or .xls) files containing DIU transport schedules.

* 🔍 **View Route Details**
  Display detailed route info including route number, name, description, start & departure times.

* ⭐ **Save Favorite Routes**
  Save frequently used routes for quick, convenient access.

* 📄 **Export to PDF**
  Export detailed route info with embedded route maps to professional PDF files.

* 🌗 **Light & Dark Theme**
  Toggle UI themes with a smooth fade effect for comfortable viewing day or night.

---

## 🖼️ Demo

 ![Image Alt](https://github.com/tajulislamsaidul/DIU-Transport-Schedule/blob/67b1e9ecd17953270d9caf771fdcbc5f07c73044/DEMO/2.png)

---

## 📹 Video Walkthrough

![Image](https://github.com/user-attachments/assets/a773a498-bba7-4f52-a4d8-0fa068d4dc25)

Watch the full video tutorial to get started and explore all features:


*Click the image above to watch on DEMO video.*

---

## ⚙️ Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/tajulislamsaidul/diu-transport-schedule-viewer.git
   cd diu-transport-schedule-viewer
   ```

2. **Install dependencies**
   Ensure Python 3.7+ is installed, then run:

   ```bash
   pip install pandas reportlab pillow requests
   ```

---

## ▶️ Usage

1. Run the application:

   ```bash
   python main.py
   ```

2. Use **Browse** to select your transport schedule Excel file.

3. Click **Load Schedule** to import routes.

4. Select a route from the dropdown and click **Show Route Details**.

5. Add routes to favorites for quick access.

6. Export route details to PDF via the **Export to PDF** button.

7. Toggle Light/Dark mode with the theme button.

---

## 📝 Excel File Format

* Should contain a sheet with route data including columns: Route No, Route Name, Route Details, Start Times, Departure Times, and optionally Route Map URLs.
* The app auto-detects the appropriate sheet and data start row.

---

## 📦 Dependencies

* `pandas` — for data handling
* `tkinter` — GUI framework (included with Python)
* `reportlab` — PDF generation
* `Pillow` — image processing
* `requests` — fetching map images

---

## 🤝 Contributing

Contributions welcome! Feel free to open issues or submit pull requests to improve the app.

---

## 📬 Contact

Created and maintained by **Tajul Islam Saidul**.
Feel free to reach out for questions, suggestions, or collaboration:

[![Email](https://img.shields.io/badge/Email-tajulislam2103@gmail.com-blue?style=for-the-badge&logo=gmail)](mailto:tajulislam2103@gmail.com)
[![GitHub](https://img.shields.io/badge/GitHub-tajulislamsaidul-181717?style=for-the-badge&logo=github)](https://github.com/tajulislamsaidul)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-View_Profile-0A66C2?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/md-tajul-islam-saidul-86b2bb348?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app)



---

Thank you for using the **DIU Transport Schedule Viewer**! 🚍📅

---
