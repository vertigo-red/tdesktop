%ifarch aarch64
    %global _lto_cflags %nil
%endif

%global appname tdesktop

# Vendored tg_owt snapshot (tg_owt is only packaged in RPM Fusion, which we must
# NOT use; so we build it in-tree from a pristine upstream tarball instead).
# NOTE: snapshot repacked WITH submodules from upstream master HEAD 19d51d3
# ("Build with OpenSSL 4", merged 2026-08-03). The version label uses the recipe's
# author-date (%at) of HEAD, which is 2026-07-25; GitHub groups by committer-date.
# The GitHub "Download ZIP" is NOT usable -- it lacks submodule sources.
%global owt_ver git20260725

# Reducing debuginfo verbosity...
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')

Name: telegram-desktop
Version: 7.1.1
Release: 1%{?dist}

# Application and 3rd-party modules licensing:
# * Telegram Desktop - GPL-3.0-or-later with OpenSSL exception -- main tarball;
# * tg_owt - BSD-3-Clause AND BSD-2-Clause AND Apache-2.0 AND MIT AND LicenseRef-Fedora-Public-Domain -- vendored, static;
# * rlottie - LGPL-2.1-or-later AND FTL AND BSD-3-Clause -- static dependency;
# * cld3  - Apache-2.0 -- static dependency;
# * cmark-gfm - BSD-2-Clause AND MIT -- static dependency (not packaged in Fedora);
# * libprisma - MIT -- static dependency (syntax highlighting);
# * MicroTeX - MIT -- static dependency (math rendering);
# * TooManyCooks - BSL-1.0 -- header-only crl threading backend (bundled);
# * qt_functions.cpp - LGPL-3.0-only -- build-time dependency;
# * open-sans-fonts  - Apache-2.0 -- bundled font;
# * vazirmatn-fonts - OFL-1.1 -- bundled font.
# NOTE: libfido2 (BSD-2-Clause) + libcbor (MIT) are UNBUNDLED here -> system libs.
# NOTE: MPL-1.1 is carried over from the original spec; the mapped component is
#       unverified -- review before any submission.
License: GPL-3.0-or-later AND BSD-3-Clause AND BSD-2-Clause AND Apache-2.0 AND MIT AND LicenseRef-Fedora-Public-Domain AND LGPL-2.1-or-later AND FTL AND MPL-1.1 AND LGPL-3.0-only AND OFL-1.1 AND BSL-1.0
URL: https://github.com/telegramdesktop/%{appname}
Summary: Telegram Desktop official messaging app

# Fetch locally before building the SRPM:  spectool -g telegram-desktop.spec
Source0: %{url}/releases/download/v%{version}/%{appname}-%{version}-full.tar.gz
# Pristine upstream tg_owt, packed WITH submodules (recipe from openSUSE OBS):
# n=tg_owt && git clone --depth=1 https://github.com/desktop-app/$n && pushd $n && v=git$(TZ=UTC date -d @`git log -1 --format=%at` +%Y%m%d) && d=$n-$v && git submodule update --init --depth=1 && rm -rf .??* && popd && mv $n $d && tar c --remove-files "$d" | xz -9e > "$d.tar.xz"
Source2: tg_owt-%{owt_ver}.tar.xz

# Telegram Desktop require more than 8 GB of RAM on linking stage.
ExclusiveArch: x86_64 aarch64

#####################################################################
## Telegram Desktop build dependencies (Fedora only; NO RPM Fusion)
#####################################################################
BuildRequires: cmake(Microsoft.GSL)
BuildRequires: cmake(OpenAL)
BuildRequires: cmake(Qt6Concurrent)
BuildRequires: cmake(Qt6Core)
BuildRequires: cmake(Qt6Core5Compat)
BuildRequires: cmake(Qt6DBus)
BuildRequires: cmake(Qt6Gui)
BuildRequires: cmake(Qt6Network)
BuildRequires: cmake(Qt6OpenGL)
BuildRequires: cmake(Qt6OpenGLWidgets)
BuildRequires: cmake(Qt6Svg)
BuildRequires: cmake(Qt6WaylandClient)
BuildRequires: cmake(Qt6WaylandCompositor)
BuildRequires: cmake(Qt6Quick)
BuildRequires: cmake(Qt6QuickWidgets)
BuildRequires: cmake(Qt6Widgets)
BuildRequires: cmake(fmt)
BuildRequires: cmake(range-v3)
BuildRequires: cmake(tl-expected)
BuildRequires: cmake(ada)
BuildRequires: cmake(KF6CoreAddons)
# tde2e-devel provides this (verified: dnf search tde2e -> tde2e-devel present).
# If 'dnf provides cmake(tde2e)' is empty, switch this to: BuildRequires: tde2e-devel
BuildRequires: cmake(tde2e)

# ffmpeg: Fedora's codec-stripped build (NOT the RPM Fusion full ffmpeg)
BuildRequires: ffmpeg-free-devel

BuildRequires: pkgconfig(alsa)
BuildRequires: pkgconfig(gio-2.0)
BuildRequires: pkgconfig(glib-2.0)
BuildRequires: pkgconfig(glibmm-2.68) >= 2.77.0
BuildRequires: pkgconfig(gobject-2.0)
BuildRequires: pkgconfig(gobject-introspection-1.0)
BuildRequires: pkgconfig(hunspell)
BuildRequires: pkgconfig(jemalloc)
BuildRequires: pkgconfig(libavcodec)
BuildRequires: pkgconfig(libavfilter)
BuildRequires: pkgconfig(libavformat)
BuildRequires: pkgconfig(libavutil)
BuildRequires: pkgconfig(libcrypto)
# libfido2: passkey/WebAuthn USB-HID backend (lib_fido2). With this present the
# in-tree lib_fido2.cmake takes the system path and skips the bundled
# libfido2+libcbor (and its libudev requirement). Drop this line to force the
# bundled build -- then also add: BuildRequires: pkgconfig(libudev)
BuildRequires: pkgconfig(libfido2)
BuildRequires: pkgconfig(liblz4)
BuildRequires: pkgconfig(liblzma)
BuildRequires: pkgconfig(libpulse)
BuildRequires: pkgconfig(libswresample)
BuildRequires: pkgconfig(libswscale)
BuildRequires: pkgconfig(libxxhash)
BuildRequires: pkgconfig(opus)
# protobuf: no longer used by cld3 itself since 7.1.1 (pre-generated pb
# headers; system cld3 is not packaged in Fedora so the bundled path builds
# without it). Kept because tde2e's CMake config resolves protobuf targets
# at configure time and we want that satisfied explicitly.
BuildRequires: pkgconfig(protobuf)
BuildRequires: pkgconfig(protobuf-lite)
BuildRequires: pkgconfig(rnnoise)
BuildRequires: pkgconfig(vpx)
BuildRequires: pkgconfig(wayland-client)
BuildRequires: pkgconfig(webkitgtk-6.0)
# xcb headers still needed at compile time; xcb-keysyms/-record/-screensaver
# BuildRequires dropped in 7.0.x: upstream dlopen()s xcb-record/xcb-keysyms at
# runtime with local declarations (see Recommends below), and xcb-screensaver is
# no longer used at all in 7.0.8 (verified against the source).
BuildRequires: pkgconfig(xcb)

BuildRequires: boost-devel
BuildRequires: cmake
BuildRequires: desktop-file-utils
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: libappstream-glib
BuildRequires: libatomic
# Do NOT let libdispatch-devel into the buildroot: crl links the bundled
# TooManyCooks (TMC) threading backend, and a present libdispatch makes the
# build pick it instead and fail. Nothing here pulls it in -- keep it that way.
BuildRequires: libqrcodegencpp-devel
BuildRequires: libstdc++-devel
BuildRequires: minizip-compat-devel
BuildRequires: ninja-build
BuildRequires: python3
BuildRequires: qt6-qtbase-private-devel
BuildRequires: qt6-qtbase-static

#####################################################################
## Extra deps for the in-tree tg_owt build (was satisfied by the
## prebuilt tg_owt-devel from RPM Fusion before; now built here).
## H.264 is provided by system openh264 (fedora-cisco-openh264 repo) and
## linked dynamically -- no patented codec code ends up in the binary.
#####################################################################
BuildRequires: pkgconfig(openh264)
BuildRequires: libjpeg-turbo-devel
BuildRequires: pkgconfig(libpipewire-0.3)
BuildRequires: pkgconfig(libdrm)
BuildRequires: pkgconfig(gbm)
BuildRequires: pkgconfig(gl)
BuildRequires: pkgconfig(egl)
BuildRequires: pkgconfig(glesv2)
BuildRequires: pkgconfig(x11)
BuildRequires: pkgconfig(xcomposite)
BuildRequires: pkgconfig(xdamage)
BuildRequires: pkgconfig(xext)
BuildRequires: pkgconfig(xfixes)
BuildRequires: pkgconfig(xrandr)
BuildRequires: pkgconfig(xtst)
BuildRequires: pkgconfig(xrender)
BuildRequires: pkgconfig(xkbcommon)
BuildRequires: pkgconfig(xkbcommon-x11)

Requires: hicolor-icon-theme
Requires: qt6-qtimageformats%{?_isa}
Requires: webkitgtk6.0%{?_isa}
# X11 global shortcuts dlopen() these at runtime (soft dependency):
#   libxcb-record.so.0   -> libxcb
#   libxcb-keysyms.so.1  -> xcb-util-keysyms
Recommends: libxcb%{?_isa}
Recommends: xcb-util-keysyms%{?_isa}

# Short alias for the main package...
Provides: telegram = %{?epoch:%{epoch}:}%{version}-%{release}
Provides: telegram%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

# Virtual provides for bundled libraries (metadata only; no build effect).
# tg_owt is now vendored, so it and its bundled submodules are listed too.
# NOTE: libfido2/libcbor are NOT listed here -- they are unbundled (system libs).
Provides: bundled(tg_owt) = 0~%{owt_ver}
Provides: bundled(abseil-cpp)
Provides: bundled(libyuv)
Provides: bundled(crc32c)
Provides: bundled(libsrtp)
Provides: bundled(usrsctp)
Provides: bundled(cld3) = 3.0.13~gitb48dc46
Provides: bundled(cmark-gfm)
Provides: bundled(libprisma)
Provides: bundled(microtex)
Provides: bundled(kf5-kcoreaddons) = 5.106.0
Provides: bundled(libtgvoip) = 2.4.4~git7c46f4c
Provides: bundled(open-sans-fonts) = 1.10
Provides: bundled(plasma-wayland-protocols) = 1.6.0
Provides: bundled(rlottie) = 0~git8c69fc2
Provides: bundled(vazirmatn-fonts) = 27.2.2
Provides: bundled(cppgir) = 0~git69ef481c
Provides: bundled(minizip) = 1.2.13
Provides: bundled(TooManyCooks) = 1.5.0

%description
Telegram is a messaging app with a focus on speed and security, it's super
fast, simple and free. You can use Telegram on all your devices at the same
time - your messages sync seamlessly across any number of your phones,
tablets or computers.

With Telegram, you can send messages, photos, videos and files of any type
(doc, zip, mp3, etc), as well as create groups for up to 50,000 people or
channels for broadcasting to unlimited audiences.

%prep
# Unpack Telegram (Source0) and the vendored tg_owt (Source2)
%setup -q -n %{appname}-%{version}-full -b2
mv ../tg_owt-%{owt_ver} Telegram/ThirdParty/tg_owt

# No patches since 7.1.1: upstream dropped cld3's find_package(protobuf
# REQUIRED CONFIG) entirely (protoc generation replaced by pre-generated
# headers; system cld3 is optional and Fedora does not package it anyway).

# Unbundle libraries provided by the system (keep minizip).
# libfido2 + libcbor unbundled: see BuildRequires: pkgconfig(libfido2).
rm -rf Telegram/ThirdParty/{QR,expected,fcitx-qt5,fcitx5-qt,hime,hunspell,jemalloc,kimageformats,libcbor,libfido2,lz4,nimf,range-v3,xxHash}

# Hygiene: drop Windows-only prebuilt binaries shipped in the tarball
rm -rf cmake/win_directx_helper/modules

%build
# 1) Build the vendored tg_owt into a local prefix.
#    PACKAGED_BUILD=ON => links system ffmpeg/openssl/opus/vpx/openh264 etc.,
#    uses tg_owt's own bundled submodules (abseil, libyuv, crc32c, ...).
mkdir -p %{_builddir}/local %{_builddir}/tg_owt-build
cd %{_builddir}/tg_owt-build
cmake -G Ninja %{_builddir}/%{appname}-%{version}-full/Telegram/ThirdParty/tg_owt \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_SHARED_LIBS=OFF \
    -DTG_OWT_PACKAGED_BUILD=ON \
    -DCMAKE_INSTALL_PREFIX=%{_builddir}/local \
    -DCMAKE_C_FLAGS="%{optflags}" \
    -DCMAKE_CXX_FLAGS="%{optflags} -include cstdint"
cmake --build .
cmake --install .

# 2) Build Telegram Desktop against the local tg_owt + system everything else.
cd %{_builddir}/%{appname}-%{version}-full
%cmake -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_AR=%{_bindir}/gcc-ar \
    -DCMAKE_RANLIB=%{_bindir}/gcc-ranlib \
    -DCMAKE_NM=%{_bindir}/gcc-nm \
    -DCMAKE_PREFIX_PATH=%{_builddir}/local \
    -DTDESKTOP_API_ID=611335 \
    -DTDESKTOP_API_HASH=d524b414d21f4d37f08684c1df41ac9c \
    -DDESKTOP_APP_USE_PACKAGED:BOOL=ON \
    -DDESKTOP_APP_USE_PACKAGED_FONTS:BOOL=OFF \
    -DDESKTOP_APP_DISABLE_WAYLAND_INTEGRATION:BOOL=OFF \
    -DDESKTOP_APP_DISABLE_X11_INTEGRATION:BOOL=OFF \
    -DDESKTOP_APP_DISABLE_CRASH_REPORTS:BOOL=ON \
    -DDESKTOP_APP_DISABLE_QT_PLUGINS:BOOL=ON
%cmake_build

%install
%cmake_install

%check
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/*.metainfo.xml
desktop-file-validate %{buildroot}%{_datadir}/applications/*.desktop

%files
%doc README.md changelog.txt
%license LICENSE LEGAL
%{_bindir}/Telegram
%{_datadir}/applications/*.desktop
%{_datadir}/icons/hicolor/*/apps/*.png
%{_datadir}/icons/hicolor/*/apps/*.svg
%{_datadir}/dbus-1/services/org.telegram.desktop.service
%{_metainfodir}/*.metainfo.xml

%changelog
* Tue Aug 25 2026 Vertigo.Red <vertigo.red@example.com> - 7.1.1-1
- Update to 7.1.1.
- DROP findprotobuf_fix.patch: upstream rewrote cmake/external/cld3 -- the
  build-time protoc generation (and the offending find_package(protobuf
  REQUIRED CONFIG)) is gone, replaced by pre-generated .pb.h headers shipped
  in-tree; system cld3 detection is optional and falls back to the bundled
  build when not found (Fedora does not package cld3). Nothing applies the
  patch anymore; no replacement needed.
- pkgconfig(protobuf)/pkgconfig(protobuf-lite) kept: tde2e's CMake config
  resolves protobuf targets at configure time (comment updated).
- tg_owt snapshot git20260725 kept unchanged (same HEAD 19d51d3 as 7.0.9);
  in-tree repack with submodules and -include cstdint CXXFLAGS stay.
- Telegram/ThirdParty set identical to 7.0.9: %%prep unbundle rm-list still
  valid verbatim; no new system dependencies, BuildRequires otherwise
  unchanged.
- New in 7.1.x built from existing deps: video editor/encoder
  (media_video_encode*, ffmpeg), web proxy (lib_webview/webkitgtk6.0),
  iv rich-text editor, statistics xlsx export; all static/in-tree or
  already-required libraries.

* Fri Aug 07 2026 Vertigo.Red <vertigo.red@example.com> - 7.0.9-1
- Update to 7.0.9.
- No build-system changes vs 7.0.8: the only cmake diffs are internal
  include-dir tweaks (SYSTEM -> normal for header dependency tracking in
  kcoreaddons, microtex and cmake/generate_target.cmake). No new external
  dependencies; BuildRequires unchanged.
- findprotobuf_fix.patch kept: cld3/CMakeLists.txt is unchanged upstream; the
  CONFIG-first/MODULE-fallback still applies cleanly (-p1) and remains the path
  that satisfies the Fedora build.
- tg_owt snapshot git20260725 kept unchanged (same HEAD as 7.0.8). We keep the
  in-tree repack and force-include <cstdint> via CXXFLAGS; not swapped for
  openSUSE's tarball, which instead carries tg_owt-gcc16.patch.
- %%prep unbundle rm-list unchanged and still valid against the 7.0.9 tree.
- Upstream adds iv/iv_rich_message_html_export.{cpp,h} + export_rich.qrc
  (Instant View rich-HTML export) to Telegram/CMakeLists.txt; built from existing
  Qt deps, no packaging impact.

* Wed Aug 05 2026 Vertigo.Red <vertigo.red@example.com> - 7.0.8-2
- Add Recommends: xcb-util-keysyms (provides libxcb-keysyms.so.1) alongside
  Recommends: libxcb (provides libxcb-record.so.0). lib_base dlopen()s both at
  runtime for X11 global shortcuts; without them the feature silently no-ops.
- Document the libdispatch-devel footgun in %%build deps: if present in the
  buildroot, crl links it instead of the bundled TooManyCooks and the build
  fails (nothing here pulls it in; comment is preventive).
- Clarify the xcb BuildRequires comment: xcb-screensaver is unused in 7.0.8.

* Wed Aug 05 2026 Vertigo.Red <vertigo.red@example.com> - 7.0.8-1
- Update to 7.0.8.
- Unbundle libfido2 + libcbor: 7.0.x adds lib_fido2 (passkey/WebAuthn USB-HID
  backend). Add BuildRequires: pkgconfig(libfido2); the in-tree lib_fido2.cmake
  now takes the system path and skips bundled libfido2/libcbor (and libudev).
  Remove Telegram/ThirdParty/{libfido2,libcbor} in %%prep.
- Bump glibmm BuildRequires to >= 2.77.0 (upstream now needs glibmm/giomm 2.77).
- Drop the openssl/engine.h sed in %%prep: upstream already removed that include
  from core/utils.cpp.
- Add Provides: bundled(libprisma), bundled(microtex) (new static deps).
- No new required system deps otherwise: libavif/libheif/libjxl stay confined to
  the static Qt image plugins, which are off (DESKTOP_APP_DISABLE_QT_PLUGINS=ON);
  formats come from system qt6-qtimageformats.
- findprotobuf_fix.patch kept: cld3 cmake code unchanged; the CONFIG-first/
  MODULE-fallback still applies cleanly and remains the path that satisfies the
  Fedora build (system protobuf CONFIG needs abseil+protoc plumbing we don't add).
- tde2e resolved via cmake(tde2e) (tde2e-devel present in Fedora repos).
- tg_owt snapshot bumped to git20260725 (repacked WITH submodules from master
  HEAD 19d51d3 "Build with OpenSSL 4"; label is HEAD author-date, merged Aug 3).

* Tue Jul 28 2026 Vertigo.Red <vertigo.red@example.com> - 7.0.6-1
- Update to 7.0.6.
- No build-system changes vs 7.0.1: cmake/external/* and Telegram/ThirdParty/*
  sets are identical, no new external dependencies.
- findprotobuf_fix.patch still applies cleanly (cld3 cmake code unchanged).
- Upstream reworked cmake/external/cmark_gfm/CMakeLists.txt for CMake >= 4.4
  (CMP0218 / cmake_diagnostic) and now also accepts prebuilt
  libcmark-gfm*_static targets; cmark-gfm is still built statically in-tree.
- tg_owt snapshot git20260409 kept unchanged.

* Thu Jul 16 2026 Vertigo.Red <vertigo.red@example.com> - 7.0.1-1
- Update to 7.0.1 (Rich Text Editor, Communities, invisible bot messages).
- Keep findprotobuf_fix.patch: cld3 cmake code unchanged upstream, patch is a
  safe CONFIG-first/MODULE-fallback and still applies cleanly.
- Drop pkgconfig(xcb-keysyms), pkgconfig(xcb-record), pkgconfig(xcb-screensaver)
  BuildRequires: upstream lib_base now dlopen()s these libraries at runtime
  with local declarations; add Recommends: libxcb for X11 global shortcuts.
- Add Provides: bundled(cmark-gfm): upstream changed its detection logic and
  Fedora does not package cmark-gfm, so it is always built in statically.
- Remove Windows-only prebuilt d3dcompiler_47.dll from the build tree in %%prep.
- tg_owt snapshot git20260409 verified identical to current upstream master;
  no rebase needed.

* Tue Jun 23 2026 Vertigo.Red <vertigo.red@example.com> - 6.9.3-3
- Fix tg_owt build on Fedora 44 (GCC 15): force-include <cstdint> for the
  in-tree tg_owt build ('uint32_t has not been declared' in stats_counter).
- openh264 build dependency is satisfied by Fedora's noopenh264 stub
  (no cisco/RPM Fusion repo needed at build time).

* Tue Jun 23 2026 Vertigo.Red <vertigo.red@example.com> - 6.9.3-1
- Drop RPM Fusion entirely to comply with Copr's legal policy (no binaries
  linked against unlicensed patented codecs):
  * ffmpeg-devel (RPM Fusion, full) -> ffmpeg-free-devel (Fedora). Media
    playback of patented formats is limited out of the box; users may
    'dnf swap ffmpeg-free ffmpeg' from RPM Fusion on their own systems.
  * tg_owt: dropped cmake(tg_owt) (RPM Fusion); now vendored as Source2 and
    built in-tree with TG_OWT_PACKAGED_BUILD. H.264 is provided by system
    openh264 (fedora-cisco-openh264, Cisco-licensed) linked dynamically, so
    no patented codec code is shipped in the binary.
- Add Provides: bundled(tg_owt) and its bundled submodules.
- Update to 6.9.3; Qt6 Wayland-compositor BuildRequires keep the Instant View
  single-window fix; crl uses bundled TooManyCooks (TMC), not libdispatch.
- TODO before any RPM Fusion submission: real maintainer e-mail; verify MPL-1.1.

* Wed Jun 17 2026 Vertigo.Red <vertigo.red@example.com> - 6.8.2-3
- Add Qt6WaylandCompositor, Qt6Quick and Qt6QuickWidgets BuildRequires
  to enable the embedded lib_webview Wayland compositor
- Fixes Instant View / Mini Apps opening as a second empty window on Wayland

* Wed May 20 2026 Leigh Scott <leigh123linux@gmail.com> - 6.8.2-2
- Rebuild for qt6

* Tue May 12 2026 Leigh Scott <leigh123linux@gmail.com> - 6.8.2-1
- Update to 6.8.2

* Fri Apr 17 2026 Nicolas Chauvet <kwizart@gmail.com> - 6.7.6-1
- Update to 6.7.6