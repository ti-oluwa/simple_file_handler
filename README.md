## simple_file_handler

The `FileHandler` class provides an interface to perform most file operations easily and intuitively. All you need is the file path.

```python
import simple_file_handler as sfh

# Create a file handler object
with sfh.FileHandler('path/to/file.txt') as hdl:
    # Read the handled file's content
    data = hdl.read_file(mode='r')
    # Write to the handled file
    hdl.write_file(b'Hello World!', mode='ab')
    # Make a copy of the handled file
    copy_hdl = hdl.copy_file('path/to/directory', filename='file_copy')
    # Delete the handled file
    hdl.delete_file()
```

## Installation

Do a pip install from the command line:

```bash
pip install simple-file-handler
```
