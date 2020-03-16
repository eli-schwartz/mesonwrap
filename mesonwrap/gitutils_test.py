import unittest

import git

from mesonwrap import gitutils
from mesonwrap import tempfile


class GetRevisionTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = git.Repo.init(self.tmp.name)

    def tearDown(self):
        self.repo.close()
        self.tmp.cleanup()

    def open(self, path, mode='r'):
        return gitutils.GitFile.open(self.repo, path, mode)

    def commit(self, *args, **kwargs):
        return self.repo.index.commit(*args, **kwargs)

    def test_empty(self):
        with self.open('hello.txt', 'w') as f:
            f.write('foo')
        self.commit('first commit')
        self.assertEqual(gitutils.get_revision(self.repo), 0)

    def test_upstream_wrap(self):
        with self.open('hello.txt', 'w') as f:
            f.write('foo')
        self.commit('first')
        self.commit('second')
        with self.open('upstream.wrap', 'w') as f:
            f.write('hello')
        self.commit('project r1')
        self.commit('project r2')
        self.assertEqual(gitutils.get_revision(self.repo), 2)

    def test_merge(self):
        with self.open('upstream.wrap', 'w') as f:
            f.write('hello')
        self.commit('first')
        r = self.commit('second')
        self.commit('third')
        r = self.commit('fourth', [r], head=False)
        self.commit('fifth', [self.repo.head.commit, r])
        self.assertEqual(gitutils.get_revision(self.repo), 5)


if __name__ == '__main__':
    unittest.main()
