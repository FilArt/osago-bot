import json
import os
import unittest

from conversation import Conversation


class TestConversation(unittest.TestCase):
    def setUp(self) -> None:
        conversation = [
            {
                'text': 'test1',
            },
            {
                'text': 'test2',
            },
            {
                'text': 'test3',
            }
        ]
        fn = 'test_conversation.json'
        self._fn = fn
        with open(fn, 'w') as f:
            f.write(json.dumps(conversation))
        self.conversation = Conversation(fn)

    def tearDown(self) -> None:
        os.remove(self._fn)

    def test_get_question(self):
        text = self.conversation.get_question(0)
        self.assertEqual(text, 'test1')

    def test_add_question(self):
        self.conversation.add_question('test4')
        self.assertEqual(self.conversation.get_question(3), 'test4')
        self.assertEqual(len(self.conversation.questions), 4)
        self.assertEqual(self.conversation.questions[-1]['text'], 'test4')

    def test_change_question(self):
        self.conversation.change_question(1, 'test222')
        self.assertEqual(self.conversation.get_question(1), 'test222')

    def test_remove_question(self):
        self.conversation.remove_question(2)
        self.assertEqual(len(self.conversation.questions), 2)


if __name__ == '__main__':
    unittest.main()
