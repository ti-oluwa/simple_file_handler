import unittest
import os

from simple_file_handler.handler import FileHandler, FileError



class FileHandlerTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.read_modes = ("r", "r+")
        cls.read_bytes_modes = ("rb", "rb+")
        cls.write_modes = ("w", "a", "a+", "w+")
        cls.write_bytes_modes = ("wb", "ab", "ab+", "wb+")
        cls.forbidden_modes = ("x", "xb", "x+", "xb+")
        cls.file_dir = os.path.abspath('tests/fixtures')
        cls.txt_file_path = os.path.abspath(f'{cls.file_dir}/test.txt')
        cls.moved_dir = os.path.abspath(f"{cls.file_dir}/moved")


    @classmethod
    def tearDownClass(cls):
        for item in os.listdir(cls.file_dir):
            if os.path.isdir(f"{cls.file_dir}/{item}"):
                for file in os.listdir(f"{cls.file_dir}/{item}"):
                    os.remove(f"{cls.file_dir}/{item}/{file}")
                os.rmdir(f"{cls.file_dir}/{item}")
            else:
                os.remove(f"{cls.file_dir}/{item}")


    def test_init(self):
        file_hdl = FileHandler(self.txt_file_path)
        self.assertTrue(file_hdl.filepath == self.txt_file_path)
        self.assertTrue(file_hdl.filename == 'test.txt')
        self.assertTrue(file_hdl.filetype == 'txt')
        self.assertTrue(file_hdl.file_exists)
        self.assertFalse(file_hdl.closed)
        with self.assertRaises(TypeError):
            FileHandler(1)
        file_hdl.close_file()
            

    def test_exists_ok_on_init(self):
        hdl = None
        try:
            with FileHandler(f"{self.file_dir}/exists.txt", exists_ok=True) as file_hdl:
                hdl = file_hdl
                pass

            with self.assertRaises(FileExistsError):
                with FileHandler(f"{self.file_dir}/exists.txt", exists_ok=False):
                    pass
        finally:
            if hdl:  
                hdl.delete_file()


    def test_not_found_ok_on_init(self):
        with FileHandler(f"{self.file_dir}/not_found.txt", not_found_ok=True) as file_hdl:
            try:
                # Ensure that the file was created if it didn't exist
                self.assertTrue(file_hdl.created_file and file_hdl.file_exists)
                # Delete the file which should have already been created by the context manager
            finally:
                file_hdl.delete_file()

        with self.assertRaises(FileNotFoundError):
            with FileHandler(f"{self.file_dir}/not_found.txt", not_found_ok=False):
                pass
    

    def test_allow_any(self):
        with FileHandler(f"{self.file_dir}/any.csharp", allow_any=True) as file_hdl:
            try:
                file_hdl.read_file("r")
                file_hdl.write_to_file("test", "w")
            finally:
                file_hdl.delete_file()
            
        with FileHandler(f"{self.file_dir}/any.csharp", allow_any=False) as file_hdl:
            try:
                with self.assertRaises(FileError):
                    file_hdl.read_file("r")
                with self.assertRaises(FileError):
                    file_hdl.write_to_file("test", "w")
            finally:
                file_hdl.delete_file()


    def test_forbidden_modes(self):
        with FileHandler(self.txt_file_path) as file_hdl:
            for mode in self.forbidden_modes:
                with self.assertRaises(FileError):
                    file_hdl.read_file(mode)
                with self.assertRaises(FileError):
                    file_hdl.write_to_file("test", mode)
                

    def test_context_usage(self):
        hdl = None
        with FileHandler(self.txt_file_path) as file_hdl:
            hdl = file_hdl            
            self.assertFalse(file_hdl.closed)
        # Context manager should have closed the file on exit
        self.assertTrue(hdl.closed)


    def test_supported_types(self):
        with FileHandler(self.txt_file_path) as file_hdl:
            self.assertIsInstance(file_hdl.supported_types(), tuple)


    def test_open_file(self):
        with FileHandler(self.txt_file_path) as file_hdl:
            # Open is called on instantiation
            self.assertFalse(file_hdl.closed)
            self.assertTrue(file_hdl.file.readable())
            self.assertTrue(file_hdl.file.writable())


    def test_close_file(self):
        file_hdl = FileHandler(self.txt_file_path)
        file_hdl.close_file()
        self.assertTrue(file_hdl.closed)

    
    def test_delete_file(self):
        with FileHandler(f"{self.file_dir}/delete.txt") as file_hdl:
            file_hdl.delete_file()
            self.assertFalse(file_hdl.file_exists)

    
    def test_clear_file(self):
        with FileHandler(self.txt_file_path) as file_hdl:
            og_mode = file_hdl.file_mode
            file_hdl.clear_file()
            self.assertTrue(file_hdl.file_mode == og_mode)
            self.assertTrue(file_hdl.file_content == "")
            self.assertTrue(file_hdl.file_size == 0)


    def test_read_file(self):
        with FileHandler(self.txt_file_path) as file_hdl:
            with self.assertRaises(TypeError):
                file_hdl.read_file(1)

            for mode in self.read_modes:
                content = file_hdl.read_file(mode)
                self.assertTrue(file_hdl.file_mode, mode)
                self.assertIsInstance(content, str)

            for mode in self.read_bytes_modes:
                content = file_hdl.read_file(mode)
                self.assertTrue(file_hdl.file_mode, mode)
                self.assertIsInstance(content, bytes)

            for mode in (*self.write_modes, *self.write_bytes_modes):
                with self.assertRaises(FileError):
                    file_hdl.read_file(mode)

  
    def test_write_to_file(self):
        with FileHandler(self.txt_file_path) as file_hdl:
            with self.assertRaises(TypeError):
                file_hdl.write_to_file("test", 1)

            for mode in self.write_modes:
                file_hdl.write_to_file("test", mode)
                self.assertTrue(file_hdl.file_mode, mode)
                if mode in ("w", "w+"):
                    self.assertTrue(file_hdl.file_content, "test")

            for mode in self.write_bytes_modes:
                file_hdl.write_to_file(b"test", mode)
                self.assertTrue(file_hdl.file_mode, mode)
                if mode in ("wb", "wb+"):
                    self.assertTrue(file_hdl.file_content, b"test")

            for mode in (*self.read_modes, *self.read_bytes_modes):
                with self.assertRaises(FileError):
                    file_hdl.write_to_file("test", mode)
    

    def test_make_copy(self):
        with FileHandler(self.txt_file_path) as file_hdl:
            with self.assertRaises(FileError):
                file_hdl.make_copy(f"{self.file_dir}/test.txt")
            with self.assertRaises(TypeError):
                file_hdl.make_copy(1)
            with self.assertRaises(TypeError):
                file_hdl.make_copy(self.file_dir, filename=1)
            with self.assertRaises(TypeError):
                file_hdl.make_copy(self.file_dir, suffix=1)
            with self.assertRaises(ValueError):
                file_hdl.make_copy(self.file_dir, suffix="-2")

            copied_file_hdl1 = file_hdl.make_copy(self.file_dir, suffix="1")
            self.assertIsInstance(copied_file_hdl1, FileHandler)
            self.assertTrue(copied_file_hdl1.file_exists)
            self.assertTrue(copied_file_hdl1.file_basename.endswith("1"))

            copied_file_hdl2 = file_hdl.make_copy(self.file_dir, suffix="1")
            self.assertTrue(copied_file_hdl2.file_basename.endswith("2"))

            copied_file_hdl3 = file_hdl.make_copy(self.file_dir, filename="test2")
            self.assertTrue(copied_file_hdl3.filename == "test2.txt")

            copied_file_hdl4 = file_hdl.make_copy(self.file_dir, filename="test2", suffix="copy")
            self.assertTrue(copied_file_hdl4.filename == "test2_copy.txt")

            copied_file_hdl5 = file_hdl.make_copy(self.file_dir, filename="test2", suffix="copy")
            self.assertTrue(copied_file_hdl5.filename == "test2_copy_1.txt")

            copied_file_hdl1.delete_file()
            copied_file_hdl2.delete_file()
            copied_file_hdl3.delete_file()
            copied_file_hdl4.delete_file()
            copied_file_hdl5.delete_file()


    def test_move_file(self):
        with FileHandler(self.txt_file_path) as file_hdl:
            try:
                with self.assertRaises(FileError):
                    file_hdl.move_file(f"{self.file_dir}/test.txt")
                with self.assertRaises(FileError):
                    file_hdl.move_file(self.file_dir)
                with self.assertRaises(TypeError):
                    file_hdl.move_file(1)

                file_hdl.move_file(self.moved_dir)
                self.assertTrue(file_hdl.file_exists)
                self.assertTrue(os.path.dirname(file_hdl.filepath) == self.moved_dir)
            finally:
                file_hdl.delete_file()


    def test_json_and_update_json(self):
        with FileHandler(f"{self.file_dir}/test.json") as file_hdl:
            json_ = {
                "test": "123",
                "check": "ok",
            }
            file_hdl.write_to_file(json_)
            self.assertEqual(file_hdl.file_content, json_)
            update = {
                "update": "new"
            }
            file_hdl.update_json(update)
            self.assertEqual(file_hdl.file_content, {**json_, **update})


    def test_csv(self):
        with FileHandler(f"{self.file_dir}/test.csv") as file_hdl:
            csv_ = [
                ["test", "check"],
                ["123", "ok"],
            ]
            file_hdl.write_to_file(csv_)
            self.assertEqual(file_hdl.file_content, csv_)


    def test_yaml(self):
        with FileHandler(f"{self.file_dir}/test.yml") as file_hdl:
            yaml_ = {
                "test": "123",
                "check": "ok",
            }
            file_hdl.write_to_file(yaml_)
            self.assertEqual(file_hdl.file_content, yaml_)


    def test_pickle(self):
        with FileHandler(f"{self.file_dir}/test.pickle") as file_hdl:
            pickle_ = {
                "test": 123,
                "check": "ok",
            }
            file_hdl.write_to_file(pickle_)
            self.assertEqual(file_hdl.file_content, pickle_)


    def test_toml(self):
        with FileHandler(f"{self.file_dir}/test.toml") as file_hdl:
            toml_ = {
                "test": "123",
                "check": "ok",
            }
            file_hdl.write_to_file(toml_)
            self.assertEqual(file_hdl.file_content, toml_)


    def test_html(self):
        with FileHandler(f"{self.file_dir}/test.html") as file_hdl:
            html_ = "<html><body><h1>Test</h1></body></html>"
            file_hdl.write_to_file(html_)
            self.assertEqual(file_hdl.file_content, html_)



if __name__ == '__main__':
    unittest.main()

# # RUN WITH 'python -m unittest discover tests "test_*.py"' from project's root directory

