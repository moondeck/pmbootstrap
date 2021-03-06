"""
Copyright 2018 Oliver Smith

This file is part of pmbootstrap.

pmbootstrap is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pmbootstrap is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pmbootstrap.  If not, see <http://www.gnu.org/licenses/>.
"""
import pmb.aportgen.core
import pmb.helpers.git
import pmb.helpers.run


def generate(args, pkgname):
    # Copy original aport
    arch = pkgname.split("-")[1]
    path_original = "main/binutils"
    upstream = (args.work + "/cache_git/aports_upstream/" + path_original)
    pmb.helpers.git.clone(args, "aports_upstream")
    pmb.helpers.run.user(args, ["cp", "-r", upstream, args.work + "/aportgen"])

    # Rewrite APKBUILD
    fields = {
        "pkgname": pkgname,
        "pkgdesc": "Tools necessary to build programs for " + arch + " targets",
        "makedepends_build": "",
        "makedepends_host": "",
        "makedepends": "gettext libtool autoconf automake bison",
        "subpackages": "",
    }

    replace_functions = {
        "build": """
            _target="$(arch_to_hostspec """ + arch + """)"
            cd "$builddir"
            "$builddir"/configure \\
                --build="$CBUILD" \\
                --target=$_target \\
                --with-lib-path=/usr/lib \\
                --prefix=/usr \\
                --with-sysroot=/usr/$_target \\
                --enable-ld=default \\
                --enable-gold=yes \\
                --enable-plugins \\
                --enable-deterministic-archives \\
                --disable-multilib \\
                --disable-werror \\
                --disable-nls
            make
        """,
        "package": """
            cd "$builddir"
            make install DESTDIR="$pkgdir"

            # remove man, info folders
            rm -rf "$pkgdir"/usr/share
        """,
        "libs": None,
        "gold": None,
    }

    pmb.aportgen.core.rewrite(args, pkgname, path_original, fields, "binutils",
                              replace_functions)
