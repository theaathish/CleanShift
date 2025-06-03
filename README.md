# CleanShift

A powerful standalone GUI application for Windows that cleans up and optimizes your system with an intuitive interface.

## 🚀 Quick Start

### One-Click Installation
1. Download `cleanshift.exe` from [Releases](https://github.com/theaathish/CleanShift/releases/latest)
2. Double-click to run - no installation required!
3. Enjoy a clean, optimized system

## ✨ Features

- **🖥️ Modern GUI**: Clean, intuitive interface inspired by modern design
- **📊 Dashboard**: Real-time drive status and system information
- **🧹 Smart Cleanup**: Remove temp files, browser cache, system junk
- **🔍 Disk Analysis**: Find large files and suggest optimizations
- **📦 App Management**: Move applications to free up C: drive space
- **🔧 Dev Environment Cleanup**: Clean Node.js, Python, and other dev tools
- **⚡ Standalone**: Single executable - no dependencies required

## 📖 How to Use

### Dashboard
- View drive space usage across all drives
- Quick system information and status
- One-click quick actions

### Clean Tab
- ✅ Temporary files cleanup
- ✅ Browser cache removal
- ✅ System cache optimization
- ✅ Recycle bin emptying
- ✅ RAM and DNS cache clearing

### Analyze Tab
- Scan any drive or folder for large files
- Get suggestions for space optimization
- Identify movable applications and data

### Move Apps Tab
- Find applications that can be moved to other drives
- Safe relocation with symbolic links
- Free up valuable C: drive space

### Dev Environments Tab
- Detect Node.js, Python, Java development environments
- Clean package caches and build artifacts
- Optimize development workspace

### Settings Tab
- Install to system for easy access
- Configure automatic cleanup preferences
- Manage application settings

## 🛡️ Safety Features

- **Preview Mode**: See what will be cleaned before taking action
- **System Protection**: Avoids critical system directories
- **Confirmation Prompts**: User confirmation for destructive operations
- **Symbolic Links**: Safe application moving without breaking functionality
- **Admin Detection**: Warns when administrator privileges are needed

## 🔧 System Requirements

- Windows 10/11
- No additional software required
- Administrator privileges recommended for full functionality

## 🛠️ For Developers

### Build from Source
```bash
# Clone repository
git clone https://github.com/theaathish/CleanShift.git
cd CleanShift

# Install build dependencies
pip install pyinstaller pillow psutil pywin32

# Build GUI executable
python build.py
```

### Project Structure
```
CleanShift/
├── cleanshift/
│   ├── main.py          # GUI entry point
│   ├── gui_app.py       # Main GUI application
│   ├── analyzer.py      # Disk analysis
│   ├── cleaner.py       # System cleanup
│   ├── mover.py         # File/app moving
│   ├── env_cleaner.py   # Dev environment cleanup
│   └── utils.py         # Utilities
├── assets/
│   ├── logo.png         # Application logo
│   └── icon.ico         # Window icon
└── build.py             # Build script
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## 🙏 Acknowledgments

Built with ❤️ for Windows users who want to keep their systems clean and optimized.
