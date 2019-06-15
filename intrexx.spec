%global         intrexxuid      500
%global         ix_user         intrexx
%global         _instdir        /var/www/apps/intrexx
%global         _java_home      /etc/alternatives/java_sdk

%global         __provides_exclude ^%{_instdir}/jre/.*$
%global         __requires_exclude ^%{_instdir}/jre/.*$

# Turn off strip'ng of binaries
%global         __strip         /bin/true
%define         debug_package   %{nil}

%define         __jar_repack 0

%define         internal_ver    90200

Name:           intrexx
Version:        19.03.0
Release:        4%{?dist}
Summary:        Intrexx Server
Group:          System Environment/Daemons
License:        Proprietary
URL:            http://www.unitedplanet.de
Source0:        https://download.unitedplanet.com/%{name}/%{internal_ver}/%{name}-%{version}-linux-x86_64.tar.gz
Source1:        upixsolr.service
Source2:        upixsupervisor.service
Source4:        upixp@.service
Source5:        intrexx-sysconfig
Source10:       configuration.properties

ExclusiveArch:  x86_64 i686
ExclusiveOS:    Linux

AutoReqProv:    no

BuildRequires:  systemd
BuildRequires:  fakeroot
BuildRequires:  user-union
BuildRequires:  esh
BuildRequires:  java >= 11
BuildRequires:  gzip
Requires:       libaio
Requires:       tomcat-native
Requires:       GraphicsMagick
Requires:       java >= 11

Provides:	%{name}-%{version}

%filter_provides_in ^%{_instdir}/jre/.*$ 
%filter_requires_in ^%{_instdir}/jre/.*$ 

%description
Intrexx server packaged from what the installer puts on the system.

%package docs
Requires:       intrexx = %{version}-%{release}
Summary:        Samples and docs for Intrexx
Group:          Development/Libraries
BuildArch:      noarch

%description docs
Samples and documentation for Intrexx %{version} provided by United Planet.

%package client
Requires:       intrexx = %{version}-%{release}
Summary:        Client for Intrexx
Group:          Development/Libraries

%description client
Management Client for Intrexx %{version}.

%package java
Requires:       intrexx = %{version}-%{release}
Summary:        Packaged Java for Intrexx
Group:          Development/Libraries

%description java
Packaged Java for Intrexx

%package selinux
Version:        %{version}
Release:        6%{dist}
Requires:       intrexx = %{version}
Summary:        SELinux policy for Intrexx
Group:          Development/Libraries
Source7:        intrexx.fc
Source8:        intrexx.if
Source9:        intrexx.te

BuildRequires:	selinux-policy selinux-policy-devel
Requires:       policycoreutils, libselinux-utils
Requires(post): selinux-policy-base >= %{selinux_policyver}, selinux-policy-targeted >= %{selinux_policyver}, policycoreutils, policycoreutils-python 
Requires(postun): policycoreutils
BuildArch:      noarch

%description selinux
This package installs and sets up the SELinux policy security module for intrexx.

%prep
%setup -q -n IX_%{version}

mkdir ../selinux
cd ../selinux
cp %{SOURCE8} %{SOURCE9} .
esh %{SOURCE7} instdir=%{_instdir} > $(basename %{SOURCE7})
cd -

esh %{SOURCE10} pwd=$(pwd) ix_home=%{_instdir} ix_user=%{ix_user} > configuration.properties

%clean
rm -rf %{buildroot}

%build
cd ../selinux
make -f /usr/share/selinux/devel/Makefile intrexx.pp || exit
cd -

%install
# Install Intrexx using installer
export DESTDIR=%{buildroot} INTREXX_HOME=%{_instdir}
fakeroot run-redir-union ./setup.sh -t --configFile=configuration.properties < /dev/null

# Gzip the installer logs
find %{buildroot} -iname 'intrexxsetup_*.log' -exec gzip "{}" \;

# Reset permissions
find %{buildroot} -type f -exec chmod a-x "{}" \+
find %{buildroot} -type f -iregex '.*/bin/.*' -exec chmod +x "{}" \;

# Create symlink to Java
ln -snf %{_java_home} %{buildroot}%{_instdir}/java/current

for i in %{SOURCE1} %{SOURCE2} %{SOURCE4} ; do
  esh ${i} ix_home=%{_instdir} ix_user=%{ix_user} java_home=%{_java_home} > $(basename ${i})_tmp
  install -Dpm 0644 $(basename ${i})_tmp %{buildroot}%{_unitdir}/$(basename ${i})
done

install -pm  0644 %{SOURCE1} %{SOURCE2} %{SOURCE4} -t %{buildroot}%{_unitdir}
install -Dpm 0644 %{SOURCE5} %{buildroot}%{_sysconfdir}/sysconfig/intrexx

install -Dpm 0644 ../selinux/intrexx.pp %{buildroot}%{_datadir}/selinux/packages/intrexx.pp
install -Dpm 0644 ../selinux/intrexx.if %{buildroot}%{_datadir}/selinux/devel/include/contrib/intrexx.if
install -d   %{buildroot}/etc/selinux/targeted/contexts/users

%pre
# Add intrexx user and group
getent group %{ix_user} >/dev/null || groupadd -f -g %{intrexxuid} -r %{ix_user}
if ! getent passwd %{ix_user} >/dev/null ; then
  if ! getent passwd %{intrexxuid} >/dev/null ; then
    useradd -r -u %{intrexxuid} -g %{ix_user} -d %{_instdir} -s /sbin/nologin -c "Intrexx Server user" intrexx
  else
    useradd -r -g %{ix_user} -d %{_instdir} -s /sbin/nologin -c "Intrexx Server user" intrexx
  fi
fi
exit 0

%post
systemctl daemon-reload
exit 0

%postun
systemctl daemon-reload
exit 0

%files
%defattr(-,intrexx,intrexx,0755)
%{_instdir}/*.version
%{_instdir}/adapter
%{_instdir}/admin
%{_instdir}/bin
%{_instdir}/cfg
%{_instdir}/crawler
%{_instdir}/export
%{_instdir}/fonts
%{_instdir}/groovy
%{_instdir}/installer
%{_instdir}/java/current
%{_instdir}/jfx
%{_instdir}/lib
%{_instdir}/log
%{_instdir}/log4j2_setup.xml
%{_instdir}/org
%{_instdir}/orgtempl
%{_instdir}/res
%{_instdir}/scriptcompressor
%{_instdir}/setup.sh
%{_instdir}/solr
%{_instdir}/tmp
%{_instdir}/uninstall.sh
%{_instdir}/update
%{_instdir}/updlib
/etc/upinstreg.conf
%attr(0644,root,root) 
%{_unitdir}/*.service
%{_sysconfdir}/sysconfig/intrexx

################## SELINUX

%post selinux
semodule -n -i %{_datadir}/selinux/packages/intrexx.pp
if /usr/sbin/selinuxenabled ; then
    /usr/sbin/load_policy
    /usr/sbin/fixfiles -R intrexx restore
fi;
semanage -i - << EOF
port -a -t intrexx_jsw_port_t -p tcp "31000-32999"
port -a -t intrexx_supervisor_port_t -p tcp 7960
port -a -t intrexx_portal_port_t -p tcp 8101
port -a -t intrexx_portal_port_t -p tcp 1234
port -a -t intrexx_portal_port_t -p tcp 8103
port -a -t intrexx_solr_port_t -p tcp 8983
port -a -t intrexx_jolokia_port_t -p tcp "8880-8883"
EOF

exit 0
 
%postun selinux
if [ $1 -eq 0 ]; then
    semodule -n -r intrexx
    if /usr/sbin/selinuxenabled ; then
       /usr/sbin/load_policy
       /usr/sbin/fixfiles -R intrexx restore
    fi;
    semanage -i - << EOF
port -d -t intrexx_jsw_port_t -p tcp "31000-32999"
port -d -t intrexx_supervisor_port_t -p tcp 7960
port -d -t intrexx_portal_port_t -p tcp 8101
port -d -t intrexx_portal_port_t -p tcp 1234
port -d -t intrexx_portal_port_t -p tcp 8103
port -d -t intrexx_solr_port_t -p tcp 8983
port -d -t intrexx_jolokia_port_t -p tcp "8880-8883"
EOF
fi;
exit 0

%files selinux
%defattr(-,root,root,0755)
%attr(0600,root,root) %{_datadir}/selinux/packages/intrexx.pp
%{_datadir}/selinux/devel/include/contrib/intrexx.if


################## JAVA

%files java
%defattr(-,intrexx,intrexx,0755)
%{_instdir}/java/packaged

################## DOCS

%files docs
%defattr(-,intrexx,intrexx,0755)
%{_instdir}/samples
%{_instdir}/log/intrexxsetup_*.log.gz

################## CLIENT

%files client
%defattr(-,intrexx,intrexx,0755)
%{_instdir}/client

%changelog selinux
* Wed May 09 2018 Robert Führicht <robert.fuehricht@jku.at> - 19.03.0-6
- customizations for 19.03 

* Wed May 09 2018 Robert Führicht <robert.fuehricht@jku.at> - 8.0-4
- adds IMAP port access rule

* Wed Mar 30 2018 Robert Führicht <robert.fuehricht@jku.at> - 8.0-3
- Adds IMAP/POP access tunable
- Adds public content access tunable 

* Wed Feb 08 2017 Robert Führicht <robert.fuehricht@jku.at> - 8.0-2
- Port types added for SOLR and Portal
- Fixed TCP Bind permissions for SOLR and Portal
- Allowed Portal to access SOLR service

* Mon Sep 26 2016 Robert Führicht <robert.fuehricht@jku.at> - 8.0-1
- Initial version

%changelog
* Tue May 28 2019 Robert Führicht <robert.fuehricht@jku.at> - 19.03.0-4
- version bump
- Updates for 19.03

* Tue Dec 19 2017 Robert Führicht <robert.fuehricht@jku.at> - 8.0-3
- adds Jolokia monitoring to SELinux policy

* Tue Dec 19 2017 Robert Führicht <robert.fuehricht@jku.at> - 8.0-3
- adds Jolokia monitoring to SELinux policy

* Wed Feb 08 2017 Robert Führicht <robert.fuehricht@jku.at> - 8.0-2
- SELinux fixes

* Mon Sep 26 2016 Robert Führicht <robert.fuehricht@jku.at> - 8.0-1
- Version bump to 8.0
- Split package

* Mon Dec 07 2015 Robert Führicht <robert.fuehricht@jku.at> - 7.0-1
- initial version
