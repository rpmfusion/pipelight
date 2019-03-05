# Conditional for release and snapshot builds. Uncomment for release-builds.
%global rel_build 1

# General needed defines.
%global commit		792e7a4885a6311172f1c876fbe5e9b5b76aace7
%global install_dep_com 1e47c45d70972c111634cc2af7c577bf5eb20b2d
%global shortcommit	%(c=%{commit};echo ${c:0:12})

# Settings used for build from snapshots.
%{!?rel_build:%global commit_date	20140714}
%{!?rel_build:%global gitver		git%{commit_date}-%{shortcommit}}
%{!?rel_build:%global gitrel		.git%{commit_date}.%{shortcommit}}
%{?rel_build:%global  gittar		%{name}-%{version}.tar.gz}
%{!?rel_build:%global gittar		%{name}-%{version}-%{gitver}.tar.gz}

# selinux settings
%{!?_selinux_policy_version: %global _selinux_policy_version %(sed -e 's,.*selinux-policy-\\([^/]*\\)/.*,\\1,' %{_datadir}/selinux/devel/policyhelp 2>/dev/null)}
%global selinux_types	%(%{__awk} '/^#[[:space:]]*SELINUXTYPE=/,/^[^#]/ { if ($3 == "-") printf "%s ", $2 }' %{_sysconfdir}/selinux/config 2>/dev/null)
%global selinux_variants %([ -z "%{selinux_types}" ] && echo mls targeted || echo %{selinux_types})

# lib%%{name}*.so* is a private lib in a private libdir with no headers,
# so we should not provide that.
%global __provides_exclude ^lib%{name}.*\\.so.*$

Name:			pipelight
Version:		0.2.8.2
Release:		13%{?gitrel}%{?dist}
Summary:		NPAPI Wrapper Plugin for using Windows plugins in Linux browsers

License:		GPLv2+ or LGPLv2+ or MPLv1.1
URL:			https://bitbucket.org/mmueller2012/pipelight/
%{?rel_build:Source0:	%{url}get/v%{version}.tar.gz#/%{?gittar}}
%{!?rel_build:Source0:	%{url}get/%{shortcommit}.tar.gz#/%{?gittar}}
Source1:		https://github.com/besser82/pipelight-selinux/archive/v0.3.1.tar.gz#/pipelight-selinux-0.3.1.tar.gz
Source2:                https://bitbucket.org/mmueller2012/pipelight/raw/%{install_dep_com}/share/install-dependency

# Wine is available on these arches, only.
ExclusiveArch:		%{arm} %{ix86} x86_64

BuildRequires:		gcc-c++
BuildRequires:		%{__gpg}
BuildRequires:		libX11-devel
BuildRequires:		mingw32-gcc-c++
BuildRequires:		mingw64-gcc-c++
%if 0%{?fedora} >= 20 || 0%{?rhel} >= 7
BuildRequires:		mingw32-winpthreads-static
BuildRequires:		mingw64-winpthreads-static
%endif # 0%{?fedora} >= 20 || 0%{?rhel} >= 7

# mozilla-filesystem is arched but not multilibs
# don't enforce %%{_isa} on this package
Requires:		mozilla-filesystem
Requires:		%{name}-common			== %{version}-%{release}
Requires:		%{name}-selinux			== %{version}-%{release}
Requires:		wine%{?_isa}			>= 1.7.22-2
Requires:		cabextract

Requires(post):		%{_bindir}/bash
Requires(post):		grep
Requires(post):		sed
Requires(preun):	%{_bindir}/bash

%description
Pipelight is a NPAPI wrapper plugin for using Windows plugins in Linux
browsers and therefore giving you the possibility to access services
which are otherwise not available for Linux users.  Typical examples of
such services are Netflix and Amazon Instant, which both use the
proprietary browser plugin Silverlight.  These services cannot normally
be used on Linux since this plugin is only available for Windows.

Pipelight helps you access these services by using the original
Silverlight plugin directly in your browser, all while giving you a
better hardware acceleration and performance than a virtual machine.
Besides Silverlight, you can also use a variety of other plugins that
are supported by Pipelight.

Pipelight will take care of installing, configuring and updating all
supported plugins.  From the perspective of the browser these plugins
will behave just like any other normal Linux plugin after you have
enabled them.

For further information about all supported plugins, their installation,
configuration and usage, please visit %{url}.


%package common
Summary:		Common files needed by %{name}
BuildArch:		noarch

Requires:		%{_bindir}/sha256sum
Requires:		%{_bindir}/wget
Requires:		%{_bindir}/zenity
Requires:		%{__gpg}
Requires:		%{name}				== %{version}-%{release}
Requires:		%{name}-selinux			== %{version}-%{release}
Requires:		wine				>= 1.7.22-2

Requires(post):		%{__cp}

%description common
This package contains common files needed by %{name}.


%package selinux
Summary:		SELinux-policy-module for %{name}
License:		GPLv2+
URL:			https://github.com/besser82/%{name}-selinux
BuildArch:		noarch

BuildRequires:		%{_bindir}/checkmodule
BuildRequires:		selinux-policy-doc
BuildRequires:		%{_sbindir}/hardlink
BuildRequires:		selinux-policy-devel

Requires:		%{name}				== %{version}-%{release}
Requires:		%{name}-common			== %{version}-%{release}
%if "%{_selinux_policy_version}" != ""
Requires:		selinux-policy		>= %{_selinux_policy_version}
%else # "%%{_selinux_policy_version}" != ""
Requires:		selinux-policy
%endif # "%%{_selinux_policy_version}" != ""

Requires(post):		%{_sbindir}/fixfiles
Requires(post):		%{_sbindir}/restorecon
Requires(post):		%{_sbindir}/semodule
Requires(post):		%{name}				== %{version}-%{release}
Requires(post):		%{name}-common			== %{version}-%{release}

Requires(postun):	%{_sbindir}/fixfiles
Requires(postun):	%{_sbindir}/restorecon
Requires(postun):	%{_sbindir}/semodule
Requires(postun):	%{name}				== %{version}-%{release}
Requires(postun):	%{name}-common			== %{version}-%{release}

%description selinux
This package contains the SELinux-policy-module for %{name}.


%prep
%setup -qn mmueller2012-%{name}-%{shortcommit} -a 1
cat %{SOURCE2} > share/install-dependency


%build
# the problem is in the new gcc flags
%global optflags %(echo %{optflags} | sed 's/ -mcet//; s/ -fstack-clash-protection//; s/ -fcf-protection//')
#global optflags %(echo %{optflags} | sed 's/ -fasynchronous-unwind-tables//; s/ -Wp,-D_GLIBCXX_ASSERTIONS//')
%global optflags %(echo %{optflags} | sed 's| -specs=/usr/lib/rpm/redhat/redhat-annobin-cc1||')
%global optflags %(echo %{optflags} | sed 's| -mabi=aapcs-linux||')

%configure								\
	--with-win64 --wine-path=%{_bindir}/wine			\
	--so-mode=0755 --gpg-exec=%{__gpg}

%make_build
pushd pipelight-selinux-0.3.1
  for _selinuxvariant in %{selinux_variants}
  do
    %{__make} NAME=${_selinuxvariant} -f %{_datadir}/selinux/devel/Makefile
    %{__mv} %{name}.pp %{name}.pp.${_selinuxvariant}
    %{__make} NAME=${_selinuxvariant} -f %{_datadir}/selinux/devel/Makefile clean
  done
popd


%install
%make_install

# Copy the packaged dependency-installer-script to some non-changing file.
# The original file will be %%ghost inside the build rpm in case of manual
# updates done by the user.  The real file will be installed during %%post.
%{__mv} -f %{buildroot}%{_datadir}/%{name}/install-dependency		\
	%{buildroot}%{_datadir}/%{name}/install-dependency.real
%{_bindir}/touch %{buildroot}%{_datadir}/%{name}/install-dependency	\
	%{buildroot}%{_datadir}/%{name}/install-dependency.sig
%{__chmod} 0755 %{buildroot}%{_datadir}/%{name}/install-dependency

# Install selinux files
pushd pipelight-selinux-0.3.1
  for _selinuxvariant in %{selinux_variants}
  do
    %{__mkdir} -p %{buildroot}%{_datadir}/selinux/${_selinuxvariant}
    %{__install} -pm 644 %{name}.pp.${_selinuxvariant}			\
      %{buildroot}%{_datadir}/selinux/${_selinuxvariant}/%{name}.pp
  done
  %{_sbindir}/hardlink -cv %{buildroot}%{_datadir}/selinux
popd


%post
# This will not enable any plugins.
%{_bindir}/%{name}-plugin --create-mozilla-plugins &>/dev/null
%ifarch x86_64
for _plugin in $(%{_bindir}/%{name}-plugin |				\
			%{__grep} "x64" |				\
			%{__sed} -e 's!^[ \t]*!!g')
do
  %{_bindir}/%{name}-plugin --unlock ${_plugin} &>/dev/null
done
%endif # arch x86_64

%post common
# Restore the dependency-installer-script shipped inside the recent package.
%{__cp} -af %{_datadir}/%{name}/install-dependency.real			\
	%{_datadir}/%{name}/install-dependency

%preun
# This will disable and remove all plugins, if the last instance of this
# package will be removed completely.  This doesn't touch anything on updates.
if [ $1 -eq 0 ]
then
  %{_bindir}/%{name}-plugin --disable-all &>/dev/null
  %{_bindir}/%{name}-plugin --remove-mozilla-plugins &>/dev/null
fi

%post selinux
for _selinuxvariant in %{selinux_variants}
do
  %{_sbindir}/semodule -s ${_selinuxvariant}				\
    -i %{_datadir}/selinux/${_selinuxvariant}/%{name}.pp &> /dev/null || :
done
%{_sbindir}/fixfiles -R %{name},%{name}-common restore || :
%{_sbindir}/restorecon -R /home/*/.wine-pipelight* &> /dev/null || :

%postun selinux
if [ $1 -eq 0 ] ; then
  for _selinuxvariant in %{selinux_variants}
  do
    %{_sbindir}/semodule -s ${_selinuxvariant} -r %{name} &> /dev/null || :
  done
  %{_sbindir}/fixfiles -R %{name},%{name}-common restore || :
  %{_sbindir}/restorecon -R /home/*/.wine-pipelight* &> /dev/null || :
fi


%files
%{_bindir}/%{name}-plugin
%{_libdir}/%{name}

%files common
%license LICENSE licenses debian/copyright
%doc debian/changelog
%dir %{_datadir}/%{name}
%ghost %{_datadir}/%{name}/install-dependency
%ghost %{_datadir}/%{name}/install-dependency.sig
%{_datadir}/%{name}/*/
%{_datadir}/%{name}/install-dependency.real
%{_datadir}/%{name}/pluginloader*
%{_datadir}/%{name}/sig-install-dependency.gpg
%{_datadir}/%{name}/wine*
%{_mandir}/man1/%{name}-plugin.1*

%files selinux
%license pipelight-selinux-0.3.1/LICENSE.txt
%doc pipelight-selinux-0.3.1/ChangeLog.md pipelight-selinux-0.3.1/README.md
%{_datadir}/selinux/*/%{name}.pp


%changelog
* Tue Mar 05 2019 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 0.2.8.2-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Oct 01 2018 Nicolas Chauvet <kwizart@gmail.com> - 0.2.8.2-12
- Fix isa on mozilla-filesystem

* Wed Aug 22 2018 Nicolas Chauvet <kwizart@gmail.com> - 0.2.8.2-11
- Fix broken url

* Sun Aug 19 2018 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 0.2.8.2-10
- Rebuilt for Fedora 29 Mass Rebuild binutils issue

* Fri Jul 27 2018 RPM Fusion Release Engineering <sergio@serjux.com> - 0.2.8.2-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Fri Jul 27 2018 RPM Fusion Release Engineering <sergio@serjux.com> - 0.2.8.2-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Fri Mar 02 2018 RPM Fusion Release Engineering <leigh123linux@googlemail.com> - 0.2.8.2-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild
- Remove some new gcc flags that breaks the build

* Thu Aug 31 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 0.2.8.2-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sun Mar 26 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 0.2.8.2-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Nov  9 2016 Hans de Goede <j.w.r.degoede@gmail.com> - 0.2.8.2-4
- Updated install-dependency script with Flash 23.0.0.205

* Fri Sep 16 2016 Hans de Goede <j.w.r.degoede@gmail.com> - 0.2.8.2-3
- Update install-dependency script to fix plugin installation no
  longer working

* Thu Jan  7 2016 Hans de Goede <j.w.r.degoede@gmail.com> - 0.2.8.2-2
- Add missing Requires: cabextract

* Sat Dec 12 2015 Hans de Goede <j.w.r.degoede@gmail.com> - 0.2.8.2-1
- new upstream release v0.2.8.2
- include selinux policy as part of pipelight-common instead of depending
  on the dead pipelight-selinux package

* Thu Dec 11 2014 Björn Esser <bjoern.esser@gmail.com> - 0.2.8-2
- fix build, link against mingw-winpthreads-static

* Wed Dec 10 2014 Björn Esser <bjoern.esser@gmail.com> - 0.2.8-1
- new upstream release v0.2.8

* Wed Sep 10 2014 Björn Esser <bjoern.esser@gmail.com> - 0.2.7.3-4
- update Flash to 15.0.0.152
- remove extra static-flag from mingw-linker-flags
- fix installing up-to-date install-dependency-script
- remove arched conditionals for minigw-related builds

* Fri Aug 15 2014 Björn Esser <bjoern.esser@gmail.com> - 0.2.7.3-3
- update Flash to 14.0.0.179 and AdobeReader to 11.0.08

* Wed Aug 13 2014 Björn Esser <bjoern.esser@gmail.com> - 0.2.7.3-2
- update Silverlight to 5.1.30514.0 and unity3d checksum

* Sun Jul 20 2014 Björn Esser <bjoern.esser@gmail.com> - 0.2.7.3-1
- new upstream release -- fixes 'pipelight-plugin --update' command

* Sat Jul 19 2014 Björn Esser <bjoern.esser@gmail.com> - 0.2.7.2-1
- new upstream release
- switch back to release-build

* Wed Jul 16 2014 Björn Esser <bjoern.esser@gmail.com> - 0.2.7.1.1-0.16.git20140714.61348bc7adad
- main-pkg should own %%dir %%{_datadir}/%%{name}, too

* Tue Jul 15 2014 Björn Esser <bjoern.esser@gmail.com> - 0.2.7.1.1-0.15.git20140714.61348bc7adad
- fix broken dependencies on grep and sed

* Mon Jul 14 2014 Björn Esser <bjoern.esser@gmail.com> - 0.2.7.1.1-0.14.git20140714.61348bc7adad
- update to new snapshot git20140714.61348bc7adad

* Mon Jul 14 2014 Björn Esser <bjoern.esser@gmail.com> - 0.2.7.1.1-0.13.git20140714.f28c55b42dbe
- update to new snapshot git20140714.f28c55b42dbe

* Mon Jul 14 2014 Björn Esser <bjoern.esser@gmail.com> - 0.2.7.1.1-0.12.git20140714.be8e5d96a755
- update to new snapshot git20140714.be8e5d96a755

* Mon Jul 14 2014 Björn Esser <bjoern.esser@gmail.com> - 0.2.7.1.1-0.11.git20140713.066356f40633
- replaced Requires: wine(compholio) with wine >= 1.7.22-2

* Mon Jul 14 2014 Björn Esser <bjoern.esser@gmail.com> - 0.2.7.1.1-0.10.git20140713.066356f40633
- added Requires for pipelight-selinux
- unlock all 'x64-*'-plugins on x86_64 by default
- added needed Requires and Requires(post)

* Sun Jul 13 2014 Björn Esser <bjoern.esser@gmail.com> - 0.2.7.1.1-0.9.git20140713.066356f40633
- unlock 'x64-flash'-plugin on x86_64 by default

* Sun Jul 13 2014 Björn Esser <bjoern.esser@gmail.com> - 0.2.7.1.1-0.8.git20140713.066356f40633
- update to new snapshot git20140713.066356f40633

* Sun Jul 13 2014 Björn Esser <bjoern.esser@gmail.com> - 0.2.7.1.1-0.7.git20140713.d79c1202f857
- update to new snapshot git20140713.d79c1202f857
- obsoleted pipelight-0.2.7.1.1_improve-buildsys.patch
- use signed updated install-dependency-script
- exclude lib%%{name}*.so* from auto-provides
- added / moved runtime-Requires between build packages,
  Requires: wine(compholio), Requires(post) and Requires(preun)
- fixed typo in %%changelog

* Fri Jul 11 2014 Björn Esser <bjoern.esser@gmail.com> - 0.2.7.1.1-0.6.git20140711.035fa4908b63
- update to new snapshot git20140711.035fa4908b63
- license-change --> upstream dropped file (src/npapi-headers/npruntime.h)
  covered by BSD-license
- upstream now ships proper licese-text-files in src-tarball

* Fri Jul 11 2014 Björn Esser <bjoern.esser@gmail.com> - 0.2.7.1.1-0.5.git20140711.8b41e9505f7a
- split files in %%{pkgdocdir} between main- and common-package

* Fri Jul 11 2014 Björn Esser <bjoern.esser@gmail.com> - 0.2.7.1.1-0.4.git20140711.8b41e9505f7a
- create common-subpackage
- the %%ghost install-dependency must have 0755-perms

* Fri Jul 11 2014 Björn Esser <bjoern.esser@gmail.com> - 0.2.7.1.1-0.3.git20140711.8b41e9505f7a
- package the %%ghost files to be 0-size

* Fri Jul 11 2014 Björn Esser <bjoern.esser@gmail.com> - 0.2.7.1.1-0.2.git20140711.8b41e9505f7a
- use the most recent dependency-installer-script provided in upstream's scm
- copy the original dependency-installer-script to some non-changing file and
  package that one as existing file, the real dependency-installer-script as
  %%ghost; restore the real dependency-installer-script during %%post from
  the packaged one

* Fri Jul 11 2014 Björn Esser <bjoern.esser@gmail.com> - 0.2.7.1.1-0.1.git20140711.8b41e9505f7a
- update to new snapshot git20140711.8b41e9505f7a8710b3817ae93ac46b3be5f96f1f
- reworked spec-file for release or snapshot-builds
- updated Patch0 for changes in upstream-sources
- obsoleted Patch1 and Patch2 -- now in upstream-sources

* Thu Jul 10 2014 Björn Esser <bjoern.esser@gmail.com> - 0.2.7.1-4
- referenced urls to pull-requests for upstreaming patches
- referenced url to pull-request for adding the missing license-textfiles

* Thu Jul 10 2014 Björn Esser <bjoern.esser@gmail.com> - 0.2.7.1-3
- replaced Patch1 with a better solution, thanks to Michael Müller
- refactored pipelight-0.2.7.1_fix-missing-call-to-setgroups.patch
- improved pipelight-0.2.7.1_use-cp-a.patch to use `cp -af`

* Tue Jul 08 2014 Björn Esser <bjoern.esser@gmail.com> - 0.2.7.1-2
- added BSD to License (#1117403)
  see: https://bugzilla.redhat.com/show_bug.cgi?id=1117403#c2

* Mon Jul 07 2014 Björn Esser <bjoern.esser@gmail.com> - 0.2.7.1-1
- initial rpm release (#1117403)
