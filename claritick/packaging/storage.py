# -*- coding: utf-8 -*-

from django.core.files.storage import FileSystemStorage
from django.conf import settings
import hashlib


class Sha1FileSystemStorage(FileSystemStorage):
    def _get_sha1_name(self, name):
        return u"%s.sha1" % (name,)

    def _write_sha1_cache(self, name, digest):
        f = self.open(self._get_sha1_name(name), mode="wb+")
        f.write(digest)
        f.close()

    def _read_sha1_cache(self, name):
        if not self.exists(self._get_sha1_name(name)):
            return None
        else:
            f = self.open(self._get_sha1_name(name), mode="rb")
            try:
                return f.read()
            finally:
                f.close()

    def sha1(self, name, use_cache=True):
        if not self.exists(name):
            return

        digest = use_cache and self._read_sha1_cache(name) or None

        # Calculate digest
        if not digest:
            file = self.open(name)
            digest = None
            sha1 = hashlib.sha1()

            # Calculate it
            try:
                for c in file.chunks():
                    sha1.update(c)
            except:
                import traceback
                traceback.print_exc()
                sha1 = None

            if sha1:
                digest = sha1.hexdigest()

            if use_cache and digest:
                self._write_sha1_cache(name, digest)

        return digest

packaging_storage = Sha1FileSystemStorage(settings.PACKAGING_ROOT,
                                          base_url="/packaging/get/")
