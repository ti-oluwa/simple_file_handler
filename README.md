## simple_file_handler

The `FileHandler` class provides an interface to perform most file operations easily and intuitively. All you need is the file path.

```python
import simple_file_handler as sfh

# Use in a with statement to ensure the file is closed after use
with sfh.FileHandler('path/to/file.txt') as hdl:
    try:
        # Read the handled file's content
        data = hdl.read_file(mode='r')
        # Write to the handled file
        hdl.write_file(b'Hello World!', mode='ab')
        # Make a copy of the handled file
        copy_hdl = hdl.make_copy('path/to/directory', filename='file_copy')
        print(copy_hdl.file_path)
        # Delete the handled file
        hdl.delete_file()
    except sfh.FileError as exc:
        print(exc)
```

## Installation

Do a pip install from the command line:

```bash
pip install simple-file-handler
```
