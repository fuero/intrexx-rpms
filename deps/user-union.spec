Name:		user-union
Version:	0.14
Release:	1%{?dist}
Summary:	Union mounts for user

Group:		Development/Tools
License:	MIT
URL:		http://www.dwheeler.com/user-union
Source0: 	%{name}-%{version}.tar.gz

ExclusiveArch:	x86_64

BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool
Requires:	rsync

%description
In a union mount, changes in one directory (the “underlay”), including its contents, appear to happen normally — but any changes to files are actually performed in a separate parallel directory (the “overlay”) instead. Since contents in the overlay take precedence over the contents in the underlay, once a file is “written” in the underlay, reading it back later from the underlay shows the “new” contents.

Union mounts can be used for a variety of tasks. For example, they can be used to make read-only media appear to be read-write; the underlay is the read-only media, and the overlay is some other directory that can be modified. Union mounts can also redirect software installation processes so that files that appear to be written in one place are instead written elsewhere — this lets you automate DESTDIR.

%prep
%setup -q

%build
autoreconf -vfi
%configure
make %{?_smp_mflags}

%install
make DESTDIR="%{buildroot}" install

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{_bindir}/*
%{_libdir}/lib%{name}*
%doc %{_mandir}/man1/*
%doc README COPYING

%changelog
* Sun Apr 15 2018 Robert Führicht <robert.fuehricht@jku.at> 0.14-1
- new package built with tito


