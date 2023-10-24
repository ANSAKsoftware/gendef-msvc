/*
    gendef - Generate list of exported symbols from a Portable Executable.
    Copyright (C) 2009-2016  mingw-w64 project

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/
#include "fsredir.h"

#ifdef REDIRECTOR
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <wow64apiset.h>
#include <stdlib.h>
#include <stdio.h>

static PVOID revert; /*revert pointer*/

static void undoredirect(void) {
    Wow64RevertWow64FsRedirection(revert);
}

void doredirect(const int redir) {
  if (redir) {
    if (!Wow64DisableWow64FsRedirection(&revert)) {
      fprintf(stderr, "Wow64DisableWow64FsRedirection failed.\n");
      return;
    } else {
      atexit(undoredirect);
    }
  }
}
#endif
