import hashlib
import io
import os
import os.path
import unittest
import zipfile

import git

from mesonwrap import gitutils
from mesonwrap import tempfile
from mesonwrap import upstream
from mesonwrap import wrapcreator


class WrapCreatorTest(unittest.TestCase):

    def setUp(self):
        self._workdir = tempfile.TemporaryDirectory()
        self.workdir = self._workdir.name

    def tearDown(self):
        self._workdir.cleanup()

    def mkfile(self, filename, contents=b''):
        with open(os.path.join(self.workdir, filename), 'wb') as f:
            f.write(contents)

    def mkdir(self, dirname):
        os.makedirs(os.path.join(self.workdir, dirname))

    def test_make_zip(self):
        self.mkfile('.gitignore')
        self.mkfile('upstream.wrap', b'hello world')
        self.mkdir('.git')
        self.mkfile('.git/hello')
        self.mkfile('meson.wrap', b'meson project')
        self.mkdir('hello')
        self.mkfile('hello/world', b'some contents')
        with io.BytesIO() as zipf:
            wrapcreator._make_zip(zipf, self.workdir, 'myprefix')
            with zipfile.ZipFile(zipf, 'r') as zip:
                self.assertListEqual(zip.namelist(), [
                    'myprefix/meson.wrap',
                    'myprefix/hello/world',
                ])
                self.assertEqual(zip.read('myprefix/meson.wrap'),
                                 b'meson project')
                self.assertEqual(zip.read('myprefix/hello/world'),
                                 b'some contents')

    def test_check_wrapfile_empty(self):
        with self.assertRaises(RuntimeError):
            wrapcreator._check_wrapfile(upstream.WrapFile())

    def test_check_wrapfile_okay(self):
        up = upstream.WrapFile()
        up.directory = 'hello'
        up.source_url = 'https://example.com/file.tgz'
        up.source_filename = 'file.tgz'
        up.source_hash = 'hash-hash-hash'
        try:
            wrapcreator._check_wrapfile(up)
        except RuntimeError as e:
            self.fail('Unexpected RuntimeError {!r}'.format(e))

    def test_make_wrap(self):
        repo = gitutils.GitProject(git.Repo.init(self.workdir))
        repo.commit('initial commit')
        repo.create_version('1.2.3')
        with repo.open('upstream.wrap', 'w') as f:
            upstream.WrapFile(
                directory='hello',
                source_url='https://example.com/file.tgz',
                source_filename='file.tgz',
                source_hash='hash-hash-hash').write(f)
        with repo.open('meson.wrap', 'w') as f:
            f.write('hello world')
        repo.commit('my commit')
        wrap = wrapcreator.make_wrap('project', repo.git_dir, '1.2.3')
        up = upstream.WrapFile.from_string(wrap.wrapfile_content)
        self.assertEqual(up.directory, 'hello')
        self.assertEqual(up.source_url, 'https://example.com/file.tgz')
        self.assertEqual(up.source_filename, 'file.tgz')
        self.assertEqual(up.source_hash, 'hash-hash-hash')
        self.assertEqual(up.patch_url, 'https://wrapdb.mesonbuild.com/v1/'
                                       'projects/project/1.2.3/1/get_zip')
        self.assertEqual(up.patch_filename, 'project-1.2.3-1-wrap.zip')
        with io.BytesIO(wrap.zip) as zipf:
            with zipfile.ZipFile(zipf, 'r') as zip:
                self.assertListEqual(zip.namelist(), ['hello/meson.wrap'])
                self.assertEqual(zip.read('hello/meson.wrap'), b'hello world')
        self.assertEqual(up.patch_hash, hashlib.sha256(wrap.zip).hexdigest())
        self.assertEqual(wrap.wrapfile_name, 'project-1.2.3-1-wrap.wrap')
        self.assertEqual(wrap.zip_name, 'project-1.2.3-1-wrap.zip')
        self.assertEqual(wrap.commit_sha, repo.head_hexsha)

    def test_make_wrap_bad_wrapfile(self):
        repo = gitutils.GitProject(git.Repo.init(self.workdir))
        repo.commit('initial commit')
        repo.create_version('1.2.3')
        with repo.open('upstream.wrap', 'w') as f:
            f.write('[wrap-file]\n')
            f.write('hello = world\n')
        repo.commit('my commit')
        with self.assertRaisesRegex(RuntimeError, 'Missing .* in upstream.wrap'):
            wrap = wrapcreator.make_wrap('project', repo.git_dir, '1.2.3')


if __name__ == '__main__':
    unittest.main()
