import random
import re
import unittest
import unicodedata

from agent_runtime.knowledge import _terms


def reference(text):
    text = unicodedata.normalize('NFKC', text).casefold()
    result = set(re.findall(r'[a-z0-9]+(?:[-_][a-z0-9]+)*', text))
    for run in re.findall(r'[\u3400-\u9fff]+', text):
        result.update(run[i:i+2] for i in range(len(run)-1))
        if len(run) == 1:
            result.add(run)
    return result


class TermClasses(unittest.TestCase):
    def test_projection(self):
        rng = random.Random(27)
        texts = ['', 'ＡＢＣ量纲', 'ß K ﬀ', '中-文', '甲乙丙', 'a_b a-b a--b', '\uf900', '🙂']
        alphabet = 'abcXYZ19-_ 中文量纲🙂KßﬀＡＢＣ\uf900\u3400\u9fff\ua000'
        texts += [''.join(rng.choice(alphabet) for _ in range(rng.randrange(100))) for _ in range(500)]
        for text in texts:
            expected = reference(text)
            self.assertEqual(_terms(text), expected)
            for ascii_words, cjk in ((True, False), (False, True), (True, True), (False, False)):
                projected = {t for t in expected if (t.isascii() and ascii_words) or (not t.isascii() and cjk)}
                self.assertEqual(_terms(text, ascii_words=ascii_words, cjk=cjk), projected)


if __name__ == '__main__':
    unittest.main()
