#!/usr/bin/python3
# Copyright (C) 2024 iDigitalFlame
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

from os import environ
from django import setup
from sys import exit, stderr
from argparse import ArgumentParser

environ["DJANGO_SETTINGS_MODULE"] = "scorebot.settings"

from scorebot_core.models import token_create_new, AccessToken
from scorebot.utils.constants import CONST_CORE_ACCESS_KEY_LEVELS


def _vet(args):
    if not isinstance(args.days, int):
        print("-d/--days is not valid!", file=stderr)
        return 1
    if args.days <= 0:
        print("-d/--days must be greater than zero!", file=stderr)
        return 1
    if isinstance(args.raw, int) and args.raw < 0:
        print("-r/--raw-perms must be greater than or equal to zero!", file=stderr)
        return 1
    v = list()
    if isinstance(args.perms, str) and len(args.perms) > 0:
        for i in args.perms.split(","):
            x = i.strip()
            try:
                v.append(int(x))
            except ValueError:
                if x not in CONST_CORE_ACCESS_KEY_LEVELS:
                    print(f'permission name "{x}" is invalid!', file=stderr)
                    return 1
                v.append(x)
            del x
    return _main(args, v)


def _main(args, perms):
    try:
        setup()
    except Exception as err:
        print(f"Django setup failed: {err}!", file=stderr)
        return 1
    try:
        t = token_create_new(args.days)
    except Exception as err:
        print(f"Token generation failed: {err}!", file=stderr)
        return 1
    try:
        a = AccessToken(token=t, level=args.raw)
        a.save()
    except Exception as err:
        print(f"AccessToken generation failed: {err}!", file=stderr)
        return 1
    if len(perms) > 0:
        for i in perms:
            a[i] = True
        a.save()
    del a
    if args.json:
        print(f'{{ "token": "{str(t.uuid)}" }}')
    else:
        print(str(t.uuid))
    del t
    return 0


if __name__ == "__main__":
    p = ArgumentParser(description="Scorebot Token Generator")
    p.add_argument(
        "-d",
        "--days",
        type=int,
        dest="days",
        help="days to expire Token in (defaults to 90 days, set to -1 to disable)",
        action="store",
        metavar="days",
        default=90,
        required=False,
    )
    p.add_argument(
        "-p",
        "--perms",
        type=str,
        dest="perms",
        help="comma seperated list of permissions to set (takes str and int)",
        action="store",
        metavar="perms",
        required=False,
    )
    p.add_argument(
        "-r",
        "--raw-perms",
        type=int,
        dest="raw",
        help="permissions to set as a raw number",
        action="store",
        default=None,
        metavar="perm_number",
        required=False,
    )
    p.add_argument(
        "-j",
        "--json",
        dest="json",
        help="output to json",
        action="store_true",
        required=False,
    )
    exit(_vet(p.parse_args()))
