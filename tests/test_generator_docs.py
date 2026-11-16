"""Execute the README's finite-generator recipe against the real descriptor."""

import doctest
import unittest
from pathlib import Path


class GeneratorDocumentationTest(unittest.TestCase):
    def test_readme_example(self):
        readme = (Path(__file__).resolve().parents[1] / "README.md").read_text(
            encoding="utf-8"
        )
        heading = "## Generators and iterators\n"
        self.assertIn(heading, readme)
        section = readme.split(heading, 1)[1].split("\n## ", 1)[0]
        parser = doctest.DocTestParser()
        test = parser.get_doctest(
            section,
            {},
            "generator recipe",
            "README.md",
            0,
        )
        self.assertGreaterEqual(len(test.examples), 10)
        runner = doctest.DocTestRunner()
        runner.run(test)
        self.assertEqual(runner.failures, 0)


if __name__ == "__main__":
    unittest.main()
