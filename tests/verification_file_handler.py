import sys
import os
import unittest

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.file_handler import FileHandler, ModelError

class TestFileHandler(unittest.TestCase):
    def setUp(self):
        self.handler = FileHandler()
        self.test_file = "test_save.txt"
        self.test_content = "Hello, Save!"

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_save_and_load(self):
        print("Testing save and load...")
        self.handler.save_text_file(self.test_file, self.test_content)
        loaded_content = self.handler.load_text_file(self.test_file)
        self.assertEqual(loaded_content, self.test_content)
        print("Save and load test passed")

    def test_file_too_large(self):
        print("Testing file too large...")
        large_content = "A" * (FileHandler.MAX_FILE_SIZE + 1)
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(large_content)
        
        with self.assertRaises(ModelError) as cm:
            self.handler.load_text_file(self.test_file)
        self.assertIn("File is too large", str(cm.exception))
        print("File too large test passed")

if __name__ == "__main__":
    unittest.main()
