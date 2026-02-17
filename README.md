IDNT – IT Device Naming Tool

**IDNT** (IT Device Naming Tool) is a lightweight desktop application written in Python that generates standardized device names based on organizational codes.

It provides a simple graphical interface for IT staff to quickly build consistent, policy-compliant device names using predefined entity, department, division, and device type codes.

Author: Billy Watts
Version: 0.001
Date: 01/24/2026

---

## ✨ Features

* Graphical interface built with Tkinter (no external dependencies)
* Dropdown selection for:
  * Entity
  * Department
  * Division
  * Device Type
* Manual input fields for:
  * Deployment year
  * Technician ID
* Real-time device name preview
* One-click clipboard copy
* CSV-driven configuration (no code changes required to update codes)
* Fallback sample data if CSV files are missing

---

## 🧱 Device Name Format

Generated device names follow this structure:

```
<Entity><Department><Division><Type><YearDigit><TechID>
```

Example:

```
LPWADMWK600A7
```

Where:

| Component  | Example | Description                                    |
| ---------- | ------- | ---------------------------------------------- |
| Entity     | L       | Organization level (e.g., County, City, State) |
| Department | PW      | Department code                                |
| Division   | ADM     | Division code                                  |
| Type       | WK      | Device type (Workstation, Laptop, etc.)        |
| Year Digit | 6       | Last digit of deployment year (e.g., 2026 → 6) |
| TechID     | 00A7    | Technician identifier                          |

---

## 📂 Configuration via CSV

IDNT loads dropdown values from CSV files located in the same directory as `idnt.py`.

Expected format:

```
Label,Code
```

Example (`department.csv`):

```
Department,Code
Public Works,PW
Finance,FIN
```

### Required CSV Files

* `entity.csv`
* `department.csv`
* `division.csv`
* `type.csv`

If any file is missing, IDNT automatically loads sample fallback data.

---

## 🚀 Installation & Usage

### Requirements

* Python 3.x
* Tkinter (included with most Python installations)

### Run the Application

```bash
python3 idnt.py
```

On Windows:

```bash
python idnt.py
```

No additional packages are required.

---

## 🖥️ Interface Overview

* Top row: Dropdowns and input fields
* Middle row: Large visual breakdown of each code component
* Bottom display: Final generated device name
* "Copy" button: Copies generated name to clipboard
* Press **Enter** in the TechID field to auto-copy

---

## 🔧 Customization

To adapt IDNT to your organization:

1. Edit the CSV files.
2. Add or modify Label/Code pairs.
3. Restart the application.

No code modification required.

---

## 📋 Behavior Notes

* The last digit of the deployment year is automatically extracted.
* Active input fields are highlighted visually.
* The window title updates dynamically to show the generated device name.
* Clicking the author email opens the project webpage.

---

## 📦 Example Use Case

An IT technician deploying a workstation in:

* County entity
* Public Works department
* Administration division
* Device type: Workstation
* Deployed in 2026
* Technician ID: 00A7

Would generate:

```
LPWADMWK600A7
```

---

## 🛠 Future Improvements (Potential Roadmap)

* Validation for TechID format
* Export to CSV
* Batch name generation
* Dark mode theme
* Packaged executable build

---

## 📄 License
GNU GPL V2
IDNT – IT Device Naming Tool

**IDNT** (IT Device Naming Tool) is a lightweight desktop application written in Python that generates standardized device names based on organizational codes.

It provides a simple graphical interface for IT staff to quickly build consistent, policy-compliant device names using predefined entity, department, division, and device type codes.

Author: Billy Watts
Version: 0.001
Date: 01/24/2026

---

## ✨ Features

* Graphical interface built with Tkinter (no external dependencies)
* Dropdown selection for:
  * Entity
  * Department
  * Division
  * Device Type
* Manual input fields for:
  * Deployment year
  * Technician ID
* Real-time device name preview
* One-click clipboard copy
* CSV-driven configuration (no code changes required to update codes)
* Fallback sample data if CSV files are missing

---

## 🧱 Device Name Format

Generated device names follow this structure:

```
<Entity><Department><Division><Type><YearDigit><TechID>
```

Example:

```
LPWADMWK600A7
```

Where:

| Component  | Example | Description                                    |
| ---------- | ------- | ---------------------------------------------- |
| Entity     | L       | Organization level (e.g., County, City, State) |
| Department | PW      | Department code                                |
| Division   | ADM     | Division code                                  |
| Type       | WK      | Device type (Workstation, Laptop, etc.)        |
| Year Digit | 6       | Last digit of deployment year (e.g., 2026 → 6) |
| TechID     | 00A7    | Technician identifier                          |

---

## 📂 Configuration via CSV

IDNT loads dropdown values from CSV files located in the same directory as `idnt.py`.

Expected format:

```
Label,Code
```

Example (`department.csv`):

```
Department,Code
Public Works,PW
Finance,FIN
```

### Required CSV Files

* `entity.csv`
* `department.csv`
* `division.csv`
* `type.csv`

If any file is missing, IDNT automatically loads sample fallback data.

---

## 🚀 Installation & Usage

### Requirements

* Python 3.x
* Tkinter (included with most Python installations)

### Run the Application

```bash
python3 idnt.py
```

On Windows:

```bash
python idnt.py
```

No additional packages are required.

---

## 🖥️ Interface Overview

* Top row: Dropdowns and input fields
* Middle row: Large visual breakdown of each code component
* Bottom display: Final generated device name
* "Copy" button: Copies generated name to clipboard
* Press **Enter** in the TechID field to auto-copy

---

## 🔧 Customization

To adapt IDNT to your organization:

1. Edit the CSV files.
2. Add or modify Label/Code pairs.
3. Restart the application.

No code modification required.

---

## 📋 Behavior Notes

* The last digit of the deployment year is automatically extracted.
* Active input fields are highlighted visually.
* The window title updates dynamically to show the generated device name.
* Clicking the author email opens the project webpage.

---

## 📦 Example Use Case

An IT technician deploying a workstation in:

* County entity
* Public Works department
* Administration division
* Device type: Workstation
* Deployed in 2026
* Technician ID: 00A7

Would generate:

```
LPWADMWK600A7
```

---

## 🛠 Future Improvements (Potential Roadmap)

* Validation for TechID format
* Export to CSV
* Batch name generation
* Dark mode theme
* Packaged executable build

---

## 📄 License
GNU GPL V3
https://www.gnu.org/licenses/
