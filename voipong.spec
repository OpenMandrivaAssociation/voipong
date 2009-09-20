Summary:	VoIPong Voice Over IP Sniffer
Name:		voipong
Version:	2.0
Release:	%mkrel 6
License:	GPL
Group:		System/Servers
URL:		http://www.enderunix.org/voipong/
Source0:	http://www.enderunix.org/voipong/%{name}-%{version}.tar.bz2
Source1:	voipong.init.bz2
Source2:	voipong.sysconfig.bz2
Patch0:		voipong-2.0-mdv_conf.diff
Requires(post): rpm-helper
Requires(preun): rpm-helper
BuildRequires:	libpcap-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
VoIPong is a utility which detects all Voice Over IP calls on a
pipeline, and for those which are G711 encoded, dumps actual
conversation to separate wave files. It supports SIP, H323,
Cisco's Skinny Client Protocol, RTP and RTCP. 

%prep

%setup -q -n %{name}-%{version}
%patch0 -p1

# lib64 fix
perl -pi -e "s|/usr/lib|%{_libdir}|g" etc/*

# fix attribs 
chmod 644 ALGORITHMS AUTHORS COPYING ChangeLog INSTALL KNOWN_BUGS LICENSE NEWS README THANKS TODO
chmod 644 docs/users-manual/*.html docs/users-manual/*.css

bzcat %{SOURCE1} > voipong.init
bzcat %{SOURCE2} > voipong.sysconfig

%build

%make \
    CFLAGS="%{optflags} -Wall -Iinclude" \
    SHLIBS="-L%{_libdir} -lpcap -ldl" -f Makefile.linux

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

# don't fiddle with the initscript!
export DONT_GPRINTIFY=1

install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{_sysconfdir}/logrotate.d
install -d %{buildroot}%{_sysconfdir}/%{name}
install -d %{buildroot}%{_sysconfdir}/sysconfig
install -d %{buildroot}%{_sbindir}
install -d %{buildroot}%{_libdir}/%{name}
install -d %{buildroot}%{_localstatedir}/lib/%{name}
install -d %{buildroot}/var/run/%{name}
install -d %{buildroot}/var/log/%{name}

install -m0755 voipong %{buildroot}%{_sbindir}/
install -m0755 voipctl %{buildroot}%{_sbindir}/
install -m0755 modvocoder_pcmu.so %{buildroot}%{_libdir}/%{name}/
install -m0755 modvocoder_pcma.so %{buildroot}%{_libdir}/%{name}/
install -m0644 etc/voipong.conf %{buildroot}%{_sysconfdir}/%{name}/
install -m0644 etc/voipongnets %{buildroot}%{_sysconfdir}/%{name}/

install -m0755 voipong.init %{buildroot}%{_initrddir}/%{name}
install -m0644 voipong.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/%{name}

# install log rotation stuff
cat > %{buildroot}%{_sysconfdir}/logrotate.d/%{name} << EOF
/var/log/%{name}/voipong.log /var/log/%{name}/voipcdr.log {
    rotate 5
    monthly
    missingok
    notifempty
    nocompress
    prerotate
	%{_initrddir}/%{name} restart > /dev/null 2>&1
    endscript
    postrotate
        %{_initrddir}/%{name} restart > /dev/null 2>&1
    endscript
}
EOF

%post
%_post_service %{name}

%preun
%_preun_service %{name}

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc ALGORITHMS AUTHORS COPYING ChangeLog INSTALL KNOWN_BUGS LICENSE NEWS README THANKS TODO
%doc docs/users-manual/*.html docs/users-manual/*.css
%attr(0755,root,root) %{_initrddir}/%{name}
%dir %{_sysconfdir}/%{name}
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}/voipong.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}/voipongnets
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%attr(0755,root,root) %{_sbindir}/voipong
%attr(0755,root,root) %{_sbindir}/voipctl
%attr(0755,root,root) %dir %{_libdir}/%{name}
%attr(0755,root,root) %{_libdir}/%{name}/*.so
%attr(0755,root,root) %dir %{_localstatedir}/lib/%{name}
%attr(0755,root,root) %dir /var/run/%{name}
%attr(0755,root,root) %dir /var/log/%{name}


