import os
import warnings
import yaml
import toml
import json
import csv
import pickle
from typing import (IO, Dict, List, Any, Tuple)
from collections.abc import Iterable

from .exceptions import FileError


class FileHandler:
    """
    Handles basic read and write operations on supported file types.

    #### Supported File Types:
    .csv, .json, .txt, .html, .xml, .yml, .yaml, .js, .css, .md, .toml
    .doc, .docx, .pdf, .pickle, .pkl, .log, '.htm', '.xht', '.xhtml', 
    '.shtml' etc. Mostly text based file types.

    Usage Example:
    ```python
    import simple_file_handler as sfh

    # create a file handler object for a file named 'test.txt' in the current directory
    with sfh.FileHandler('test.txt') as hdl:
        hdl.write_to_file('Hello World!', mode='w')
        print(hdl.read_file('r'))

    # Output: Hello World!
    ```
    """
    def __init__(
            self, 
            filepath: str, 
            encoding: str = 'utf-8', 
            not_found_ok: bool = True, 
            exists_ok: bool = True, 
            allow_any: bool = False
        ):
        """
        Creates a FileHandler object for the specified file.

        On instantiation, the file is opened in 'a+' mode and stored in the `file` attribute.
        Remember to close the file object by calling the `close_file` method after use.

        :param str filepath: path to the file to be read or written to.
        :param str encoding: encoding to be used when reading or writing to the file. Defaults to 'utf-8'.
        :param bool not_found_ok: Whether to raise FileNotFoundError if file object specified by `filepath`
        cannot be found. If True, the file is created if it cannot be found and no exception is raised, otherwise,
        a `FileNotFoundError` is raised. Defaults to True.
        :param bool exist_ok: Whether to raise FileExistsError if file object specified by `filepath`
        already exists. If True, the already existent file is handled and no exception is raised, otherwise,
        a `FileExistsError` is raised. Defaults to True.
        :param bool allow_any: Whether to allow reading and writing to any file type. If True, the file type is not checked
        before reading or writing to the file. Defaults to False.
        """
        self._file: IO = None
        self.created_file = False
        self.filepath = os.path.abspath(filepath)
        self.encoding = encoding
        self.allow_any = allow_any
        
        if not os.path.exists(self.filepath):
            if not_found_ok is False:
                raise FileNotFoundError(f"File not found: {self.filepath}")
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True, mode=0o777)
            open(self.filepath, 'x').close()
            self.created_file = True

        else:
            if exists_ok is False:
                raise FileExistsError(f"File already exist: {self.filepath}")
        if not os.path.isfile(self.filepath):
            raise FileError(f"File not created: {self.filepath}. Check if the path points to a file.")
        # open file in append mode by default so it can be written into and read from 
        # even if the `open_file` method has not being called yet.
        self.open_file('a+')

    def __del__(self):
        try:
            self.close_file()
        except:
            pass

    def __repr__(self) -> str:
        return f"<FileHandler: path={self.filepath} mode={self.file.mode}>"
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        # Ensure that the file is closed when the context manager exits
        self.close_file()

    @property
    def file(self):
        """The file object being handled."""
        return self._file
    
    @property
    def file_exists(self) -> bool:
        """Returns True if the file exists, otherwise False."""
        return os.path.exists(self.filepath)

    @property
    def filetype(self) -> str:
        """Type of the handled file."""
        filetype = os.path.splitext(self.filepath)[-1].removeprefix('.').lower()
        if filetype in ('yaml', 'yml'):
            filetype = 'yaml'
        elif filetype in ('pickle', 'pkl'):
            filetype = 'pickle'
        return filetype

    @property
    def filename(self) -> str:
        """Name of the handled file, including its extension"""
        filename = os.path.basename(self.filepath)
        return filename.replace('\\', '')
    
    @property
    def file_basename(self) -> str:
        """Handled file name with its extension"""
        return os.path.splitext(self.filename)[0]

    @property
    def file_ext(self) -> str:
        """Handled file's extension."""
        return os.path.splitext(self.filename)[1]

    @property
    def file_dir(self) -> str:
        """Path to the directory containing the handled file."""
        return os.path.dirname(self.filepath)
    
    @property
    def file_content(self) -> str:
        """Content of the handled file (content returned is mostly non-byte type)"""
        content = self.read_file('r')
        return content

    @property
    def file_mode(self) -> str | None:
        """
        The mode the handled file is/was opened in.

        Returns None if the file is not yet accessible.
        """
        if not self.file:
            return None
        return self.file.mode
    
    @property
    def file_size(self) -> int:
        """Returns the size of the file in bytes."""
        return os.path.getsize(self.filepath)
    
    @property
    def closed(self) -> bool:
        """Returns True if the file is closed, otherwise False."""
        return self.file and self.file.closed

    @staticmethod
    def supported_types() -> Tuple[str]:
        '''
        Returns a tuple of supported file types.
        '''
        return (
        'txt', 'doc', 'docx', 'pdf', 'html', 'htm', 'xml',
         'js', 'css', 'md', 'json', 'csv', 'yaml', 'yml', 
         'toml', 'pickle', 'pkl', 'log', 'xht', 'xhtml', 'shtml',
        )


    def open_file(self, mode: str = 'a+') -> None:
        '''
        Opens the handled file in the specified mode. Default mode is 'a+'.
        
        :param mode (str): The mode to open the file in. Default is 'a+'
        '''
        mode = mode.lower()
        # Check if file is already open in the specified mode
        if not self.closed and self.file_mode == mode:
            return
        # Close file and reopen in the specified mode
        self.close_file()
        try:
            if 'b' in mode:
                self._file = open(self.filepath, mode=mode)
            else:
                self._file = open(self.filepath, mode=mode, encoding=self.encoding)
        except Exception as exc:
            raise FileError(
                "File cannot be opened."
            ) from exc


    def close_file(self) -> None:
        '''
        Closes the handled file if it is open.
        '''
        if self.file and not self.closed:
            self.file.close()
        return None


    def clear_file(self) -> None:
        """
        Empties handled file.

        The file still remains open in the mode it was 
        being used in, if it was open before the file was cleared.
        """
        was_closed = self.closed
        og_mode = self.file_mode
        self.open_file('w')
        self.file.write('')
        # Opens the file using mode before the the file was cleared to ensure that the file is 
        # still available for use in the initial user preferred mode
        if not was_closed:
            self.open_file(og_mode)
        return None


    def delete_file(self) -> None:
        '''Deletes the handled file.'''
        if not self.file_exists:
            warnings.warn(f"Cannot delete file. File does not exist: {self.filepath}")
            return
        try:
            self.close_file()
            os.remove(self.filepath)
            self._file = None
            self.file_path = None
        except Exception as exc:
            raise FileError(
                "File could not be deleted"
            ) from exc


    def make_copy(
            self, 
            destination: str, 
            filename: str = None, 
            suffix: str = "1"
        ) -> "FileHandler":
        '''
        Copies the file to the specified destination.

        :param destination (str): The path to the directory where the file will be copied to.
        :param filename (str): Preferred base name of the copied file. If None, 
        the base name of the original file is used.
        :param suffix (str): The suffix to be added to the filename in the case of a name conflict.
        :return: The `FileHandler` for the copy.
        '''
        if not isinstance(destination, str):
            raise TypeError("Invalid type for `destination`")
        if filename and not isinstance(filename, str):
            raise TypeError("Invalid type for `filename`")
        if not isinstance(suffix, str):
            raise TypeError("Invalid type for `suffix`")

        destination = os.path.abspath(destination)
        # check if destination is a file or directory
        if os.path.splitext(destination)[1]: # is directory
            raise FileError("Destination cannot be a file")

        if filename:
            filename = filename.replace('\\', '')
            if os.path.splitext(filename)[1]:
                raise FileError("`filename` cannot have an extension")
            filename = f"{filename}{self.file_ext}"
        
        try: 
            suffix = int(suffix)
        except ValueError:
            pass

        if isinstance(suffix, int) and suffix < 1:
            raise ValueError(
                "Invalid value for `suffix`. suffix must be non-zero and positive if it is numeric"
            )
        
        full_path = os.path.join(destination, filename or self.filename)
        already_exists = os.path.exists(full_path)
        c = 0
        while already_exists is True:
            c += 1
            if not filename:
                fname = f"{self.file_basename}_{suffix}{self.file_ext}"
            else:
                name, ext = os.path.splitext(filename)
                fname = f"{name}_{suffix}{ext}"

            full_path = os.path.join(destination, fname)
            already_exists = os.path.exists(full_path)
            if already_exists is False:
                break
            if isinstance(suffix, int):
                suffix += 1
            else:
                suffix = f"{suffix}_{c}"

        dst_hdl = FileHandler(
            filepath=full_path, 
            encoding=self.encoding,
            exists_ok=False
        )
       
        dst_hdl.write_to_file(self.read_file(), write_mode='w+')
        dst_hdl.close_file()
        return dst_hdl


    def move_file(self, destination: str) -> None:
        '''
        Moves the file to the specified destination.

        The handler automatically switches to handling the destination file.

        :param destination (str): The path to the directory where the file will be moved to.
        '''
        if not isinstance(destination, str):
            raise TypeError("Invalid type for `destination`")
        destination = os.path.abspath(destination)
        if destination == os.path.dirname(self.filepath):
            raise FileError(
                "File cannot be moved to the same directory as the original file"
            )
        
        dst_hdl = self.make_copy(destination)
        self.delete_file()
        self._file = dst_hdl.file
        self.filepath = dst_hdl.filepath
        return None
    

    def read_file(self, read_mode: str | None = "r+", **kwargs) -> Any:
        '''
        Although the `file_content` property of the handler may be sufficient
        to read content from a file for most use cases, this method reads the 
        file and returns the content using the specified `read_mode`.

        :param read_mode(str): The mode to be used to read the file. 
        If None, it reads in 'read(r+)' mode. Note that not all file 
        types support all modes so its best to use the default mode in such cases.
        :param kwargs: Additional keyword arguments to be passed to the underlying read method.

        Example:

        Without keyword arguments:
        ```python
        import simple_file_handler as sfh

        with sfh.FileHandler('test.yml') as hdl:
            print(hdl.read_file('r'))
        ```

        With keyword arguments:
        ```python
        import simple_file_handler as sfh

        with sfh.FileHandler('test.yml') as hdl:
            print(hdl.read_file('r', Loader=yaml.FullLoader))
        ```
        '''
        if not isinstance(read_mode, str):
            raise TypeError("Invalid type for `read_mode`")
        
        read_mode = read_mode.lower()
        if read_mode and any(map(lambda x: x in read_mode, ('w', 'a', 'x'))):
            raise FileError(f"Invalid read mode: '{read_mode}'")

        if self.filetype in self.supported_types() or self.allow_any is True:
            self.open_file(read_mode)
            try:
                return getattr(self, f'_read_{self.filetype}')(**kwargs)
            except AttributeError:
                return self.file.read()
        raise FileError(f"Unsupported File Type: '{self.filetype}'")

    
    def write_to_file(self, content: Any, write_mode: str | None = "a+", **kwargs) -> None:
        '''
        Writes the content to the file using the specified `write_mode`.

        NOTE: This method will always replace JSON file content with new content.
        To update a '.json' file use the `update_json` method.

        :param content (Any): The content to write to the file.
        :param write_mode(str): The mode to be used to write the file. 
        Note that not all file types support all modes so its best to 
        use the default mode in such cases.
        If None, it writes in append(a+) mode.
        To overwrite previous content use 'w' or 'wb'.
        :param kwargs: Additional keyword arguments to be passed to the underlying write method.

        Example:

        Without keyword arguments:
        ```python
        import simple_file_handler as sfh

        with sfh.FileHandler('test.json') as hdl: 
            data = {"test": "123"}
            hdl.write_to_file(data, 'w')
        ```

        With keyword arguments:
        ```python
        import simple_file_handler as sfh

        with sfh.FileHandler('test.json') as hdl:
            data = {"test": "123"}
            hdl.write_to_file(data, 'w', indent=4)
        ```
        '''
        if not isinstance(write_mode, str):
            raise TypeError("Invalid type for `write_mode`")

        write_mode = write_mode.lower()
        if write_mode and any(map(lambda x: x in write_mode, ('r', 'x'))):
            raise FileError(f"Invalid write mode: '{write_mode}'")

        if self.filetype in self.supported_types() or self.allow_any is True:
            self.open_file(write_mode)
            self._write_content(content, **kwargs)
            return
        raise FileError(F"Unsupported File Type: `{self.filetype}`")


    def _write_content(self, content: Any, **kwargs):
        try:
            return getattr(self, f'_write_{self.filetype}')(content, **kwargs)
        except AttributeError:
            self.file.write(content)
        return None
            

    def _read_json(self, **kwargs) -> Dict:
        '''
        Reads the file and returns the content as a dictionary.
        '''
        try:
            return json.load(self.file, **kwargs)
        except Exception as exc:
            raise FileError(
                'JSON file could not be loaded'
            ) from exc


    def _write_json(self, content: Dict, indent: int = 4, **kwargs) -> None:
        '''
        Writes new content to file after clearing previous content.

        :param content (Dict): JSON serializable content to write to the file
        '''
        if not isinstance(content, dict):
            raise TypeError('Invalid type for `content`')
        try:
            self.clear_file()
            _json = json.dumps(content, indent=indent, **kwargs)
            return self.file.write(_json)
        except Exception as exc:
            raise FileError(
                'File cannot be written into.'
            ) from exc

    
    def update_json(self, content: Dict, **kwargs):
        """
        Updates the content of JSON file with new content dict.
        Basically overwrites the file with the updated content.

        :param content (Dict): JSON serializable content to update the file with.
        """
        if self.filetype == 'json':
            try:
                file_content = self.read_file()
            except:
                file_content = {}
            file_content.update(content)
            return self.write_to_file(file_content, 'w', **kwargs)
        raise FileError(f"`update_json` cannot be used with '{self.filetype}' files.")


    def _write_csv(self, content: Iterable[Iterable], **kwargs) -> None:
        '''
        Writes the content to the file.

        :param content (List | Tuple): The content to write to the file
        '''
        if not isinstance(content, (list, set, tuple)):
            raise TypeError(f"Invalid type for `content`. Expected iterable got {type(content)}")
        kwargs_ = {
            # line terminator is set to '\n' to prevent extra 
            # blank lines from being added to the file
            "lineterminator": '\n',
            **kwargs
        }
        writer = csv.writer(self.file, **kwargs_)
        writer.writerows(content)
        return None


    def _read_csv(self, **kwargs) -> List:
        '''
        Reads the file and returns the content as a list.
        '''
        kwargs_ = {
            # line terminator is set to '\n' to prevent extra 
            # blank lines from being added to the file
            "lineterminator": '\n',
            **kwargs
        }
        try:
            reader = csv.reader(self.file, **kwargs_)
            return list(reader)
        except Exception as exc:
            raise FileError(
                'csv file could not be read.'
            ) from exc


    def _read_yaml(self, **kwargs) -> Dict: #
        '''
        Reads the file and returns the content as a dictionary.
        '''
        kwargs_ = {
            "Loader": yaml.FullLoader,
            **kwargs
        }
        try:
            return yaml.load(self.file, **kwargs_)
        except Exception as exc:
            raise FileError(
                'yaml file could not be loaded.'
            ) from exc

    
    def _write_yaml(self, content: dict, **kwargs) -> None: #
        '''
        Writes the content to the file.

        :param content (dict): The content to write to the file
        ''' 
        kwargs_ = {
            "default_flow_style": False,
            "encoding": self.encoding,
            **kwargs
        }
        yaml.dump(content, self.file, **kwargs_)
        return None


    def _read_pickle(self, **kwargs) -> Any:
        '''
        Reads the file and returns the content.
        '''
        try:
            self.open_file('rb+')
            return pickle.load(self.file, **kwargs)
        except Exception as exc:
            raise FileError(
                'pickle file could not be loaded.'
            ) from exc


    def _write_pickle(self, content: Any, **kwargs) -> None:
        '''
        Writes the content to the file.

        :param content (Any): The content to write to 
        the file (mostly byte content)
        '''
        # pkl = pickle.dumps(content).decode(self.encoding)
        # self.file.write(pkl)
        self.open_file('ab+')
        pickle.dump(content, self.file, **kwargs)
        return None


    def _read_toml(self, **kwargs) -> Dict:
        '''
        Reads the file and returns the content as a dictionary.
        '''
        try:
            return toml.load(self.file, **kwargs)
        except Exception as exc:
            raise FileError(
                'toml file could not be loaded.'
            ) from exc


    def _write_toml(self, content: dict, **kwargs) -> None:
        '''
        Writes the content to the file.

        :param content (dict): The content to write to the file
        '''
        toml.dump(content, self.file, **kwargs)
        return None


