# Contributing to Forensic Workstation Builder

Thank you for your interest in contributing! 🎉

## Getting Started

1. **Fork** the repository
2. **Clone** your fork:
   ```bash
   git clone https://github.com/your-username/forensic-workstation-builder.git
   cd forensic-workstation-builder
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Run the app**:
   ```bash
   python main.py
   ```

---

## 🛠️ Code Style

- Follow **PEP 8** guidelines
- Use **meaningful variable names**
- Add **docstrings** to functions and classes
- Keep functions **small and focused** (Single Responsibility Principle)

---

## 🧪 Adding a New Tool

To add a new tool to the catalogue:

1. **Create a JSON manifest** in `data/tools/`:
   ```json
   {
     "id": "tool_id",
     "name": "Tool Name",
     "description": "Brief description",
     "category": "Category",
     "version": "1.0.0",
     "supported_os": ["windows", "linux"],
     "install_method": "installer|portable|archive|python_package",
     "download_url": "https://example.com/download",
     "sha256": "",
     "dependencies": [],
     "file_name": "installer.exe",
     "requires_admin": false,
     "source": "official"
   }
   ```

2. **Sign the manifest**:
   ```bash
   python sign_manifests.py
   ```

3. **Test the installation**:
   ```bash
   python cli.py install tool_id
   ```

---

## 🐛 Reporting Issues

1. Go to the **Issues** tab
2. Click **"New Issue"**
3. Use the template:
   - **Title**: Clear and descriptive
   - **Description**: What happened? Expected behavior?
   - **Steps**: How to reproduce
   - **Screenshots**: If applicable

---

## 📝 Pull Request Process

1. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**

3. **Commit**:
   ```bash
   git commit -m "feat: your feature description"
   ```

4. **Push**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request**:
   - Go to the repository
   - Click **"Pull Requests"** → **"New Pull Request"**
   - Select your branch
   - Write a description
   - Submit!

---

## 📄 License

This project is **MIT Licensed**. By contributing, you agree to the same license.

---

## 💬 Questions?

Feel free to open an issue or reach out!

**Happy coding!** 🚀
```
