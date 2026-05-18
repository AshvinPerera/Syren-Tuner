from io import StringIO
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from syren_tuner import ProtocolError
from syren_tuner.protocol.jsonl import parse_json_line, read_json_lines, write_json_line
from syren_tuner.protocol.messages import message_type


class JsonlProtocolTests(unittest.TestCase):
    def test_parse_json_line_accepts_object(self):
        self.assertEqual(parse_json_line('{"type":"start_study"}')["type"], "start_study")

    def test_parse_json_line_rejects_non_object(self):
        with self.assertRaises(ProtocolError):
            parse_json_line("[1, 2, 3]")

    def test_message_type_requires_type(self):
        with self.assertRaises(ProtocolError):
            message_type({})

    def test_write_and_read_json_line_round_trips(self):
        stream = StringIO()
        write_json_line(stream, {"type": "ready", "study_id": "s"})
        stream.seek(0)
        messages = list(read_json_lines(stream))
        self.assertEqual(messages, [{"type": "ready", "study_id": "s"}])


if __name__ == "__main__":
    unittest.main()

