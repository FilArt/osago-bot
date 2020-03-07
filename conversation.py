import json
import os


class Base:
    fn = 'file.txt'

    def read(self) -> str:
        if not os.path.exists(self.fn):
            self.write('')
        with open(self.fn) as f:
            data = f.read()
        return data

    def write(self, some: str = ''):
        with open(self.fn, 'w') as f:
            f.write(some)


class Bye(Base):
    fn = 'bye.txt'


class Information(Base):
    fn = 'information.txt'


class Hello(Base):
    fn = 'hello.txt'


class Conversation:
    def __init__(self, file_name: str = 'conversation.json'):
        self._file_name = file_name

        self.questions = self._get_conversation()

    def get_question(self, step: int):
        try:
            question = self.questions[step]
        except IndexError:
            return None

        return question['text']

    def change_question(self, i: int, new_text):
        self.questions[i]['text'] = new_text
        self._write_conversation(self.questions)

    def remove_question(self, idx: int):
        del self.questions[idx]
        self._write_conversation(self.questions)

    def add_question(self, text: str, order=None):
        conversation = self._get_conversation()
        if text in [i['text'] for i in conversation]:
            raise ValueError('Такой вопрос уже есть.')
        question = {'text': text}
        if order is None:
            conversation.append(question)
        elif order and (not str(order).isdigit() or int(order) not in range(len(self.questions))):
            raise Exception('internal')
        else:
            conversation.insert(order, question)
        self._write_conversation(conversation)
        self.questions = conversation

    def _get_conversation(self) -> list:
        with open(self._file_name) as f:
            data = json.loads(f.read())
            if not isinstance(data, list):
                raise Exception('internal')
        return data

    def _write_conversation(self, conversation: list):
        with open(self._file_name, 'w') as f:
            f.write(json.dumps(conversation))
