# CleanShift

A powerful standalone CLI utility for Windows that cleans up and offloads software packages from the C: drive to other available drives to free up space.

## 🚀 Quick Installation (One Command)

### Option 1: Direct Download & Install
```batch
curl -L https://github.com/theaathish/CleanShift/raw/main/install.bat -o install.bat && install.bat
```

### Option 2: PowerShell Install
```powershell
iwr -useb https://github.com/theaathish/CleanShift/raw/main/install.ps1 | iex
```

### Option 3: Manual Download
1. Download `cleanshift.exe` from [Releases](https://github.com/theaathish/CleanShift/releases/latest)
2. Run as administrator: `cleanshift.exe install`
3. Use globally: `cleanshift <command>`

## ✨ Features

- **🔍 Disk Analysis**: Scan C: drive and identify large folders
- **🧹 Smart Cleanup**: Remove temp files, browser caches, system caches  
- **📦 Package Moving**: Move folders to other drives with symbolic links
- **📊 Drive Status**: Monitor disk space across all drives
- **🔒 Safety First**: Dry run mode and system directory protection
- **⚡ Standalone**: No dependencies - single executable file

## 📖 Usage

### Check Drive Status
```bash
cleanshift status
```

### Analyze Large Folders
```bash
cleanshift analyze --min-size 500
```

### Clean Temporary Files
```bash
cleanshift clean --temp-files --browser-cache --dry-run
```

### Move Large Folders
```bash
cleanshift move --source "C:\Users\Username\Downloads" --target-drive D:
```

## 🛠️ Build from Source

```bash
# Clone repository
git clone https://github.com/theaathish/CleanShift.git
cd CleanShift

# Install build dependencies
pip install pyinstaller

# Build standalone executable
python build.py
```

## 🔧 Commands

| Command | Description |
|---------|-------------|
| `cleanshift status` | Show disk space for all drives |
| `cleanshift analyze` | Find large folders on C: drive |
| `cleanshift clean` | Remove temporary/cache files |
| `cleanshift move` | Move folders to other drives |
| `cleanshift install` | Install to system PATH |

## 🛡️ Safety Features

- Administrator privilege warnings
- Dry run mode for testing
- System directory protection  
- Confirmation prompts for destructive operations
- Automatic symbolic link creation

## 📋 Requirements

- Windows 10/11
- Administrator privileges (recommended)
- No additional dependencies needed

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.
