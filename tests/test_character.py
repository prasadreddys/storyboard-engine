import unittest

from storyboard.character import CharacterError, validate_character

GOOD = {
    "name": "Mara",
    "traits": ["curly red hair", "a brass compass"],
    "palette": ["#0F766E", "#D97706"],
    "style": "flat vector",
    "voice": "calm narrator",
}


class TestCharacter(unittest.TestCase):
    def test_valid_character(self):
        result = validate_character(dict(GOOD))
        self.assertEqual(result["name"], "Mara")
        self.assertEqual(result["traits"], GOOD["traits"])

    def test_optional_fields_default_empty(self):
        result = validate_character({"name": "X", "traits": ["one trait"]})
        self.assertEqual(result["style"], "")
        self.assertEqual(result["voice"], "")
        self.assertEqual(result["palette"], [])

    def test_empty_traits_rejected(self):
        with self.assertRaises(CharacterError):
            validate_character({"name": "X", "traits": []})

    def test_missing_traits_rejected(self):
        with self.assertRaises(CharacterError):
            validate_character({"name": "X"})

    def test_blank_trait_rejected(self):
        with self.assertRaises(CharacterError):
            validate_character({"name": "X", "traits": ["  "]})

    def test_missing_name_rejected(self):
        with self.assertRaises(CharacterError):
            validate_character({"traits": ["one trait"]})

    def test_bad_hex_palette_rejected(self):
        for bad in ["red", "#FFF", "#GGGGGG", "0F766E", "#0F766E0"]:
            with self.assertRaises(CharacterError, msg=bad):
                validate_character(dict(GOOD, palette=[bad]))

    def test_lowercase_hex_accepted(self):
        result = validate_character(dict(GOOD, palette=["#0f766e"]))
        self.assertEqual(result["palette"], ["#0f766e"])

    def test_non_dict_rejected(self):
        with self.assertRaises(CharacterError):
            validate_character(["not", "a", "dict"])


if __name__ == "__main__":
    unittest.main()
