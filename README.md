# TFT Overlay

Modified version of https://github.com/ufanYavas/LoL-TFT-Champion-Masking.

Instead of text recognition, this TFT overlay uses cv2 image matching method. 

### Current version
Set 4

### Creating custom composition
- Open mainwindow.py
- Edit `comp` variable in line 12

Example:
```python
comp = {
    "CompName1": ["champname1", "champname2", "champname3"],
    "CompName2": ["champname4", "champname5", "champname6"]
    }
```

Make sure champion names are written in lower case

### Game settings
- Resolution: 1920x1080
- Window Mode: Borderless

### Running overlay
- `pip install -r requirements.txt --user`
- `python mainwindow.py`