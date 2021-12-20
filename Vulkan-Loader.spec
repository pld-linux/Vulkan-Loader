#
# Conditional build:
%bcond_with	tests	# run tests (some failing?)
%bcond_without	wayland	# Wayland support in loader
%bcond_without	x11	# XLib support in loader

%define	api_version	1.2.198.0

Summary:	Vulkan API loader
Summary(pl.UTF-8):	Biblioteka wczytująca sterowniki Vulkan
Name:		Vulkan-Loader
# note: prefer "sdk-" tags for better quality level
Version:	1.2.198.1
Release:	1
License:	Apache v2.0, parts MIT-like
Group:		Libraries
#Source0Download: https://github.com/KhronosGroup/Vulkan-Loader/tags
Source0:	https://github.com/KhronosGroup/Vulkan-Loader/archive/sdk-%{version}/%{name}-sdk-%{version}.tar.gz
# Source0-md5:	e2a381bb2457227519a0a75aeee62975
URL:		https://github.com/KhronosGroup/Vulkan-Loader/
BuildRequires:	cmake >= 3.10.2
%if %{with tests} && %(locale -a | grep -q '^C\.utf8$'; echo $?)
BuildRequires:	glibc-localedb-all
%endif
BuildRequires:	Vulkan-Headers = %{api_version}
%{?with_tests:BuildRequires:	gmock-devel}
%{?with_tests:BuildRequires:	gtest-devel}
%{?with_tests:BuildRequires:	libstdc++-devel >= 6:4.7}
%{?with_x11:BuildRequires:	libxcb-devel}
BuildRequires:	pkgconfig
BuildRequires:	python3 >= 1:3
BuildRequires:	python3-lxml
BuildRequires:	python3-modules >= 1:3
BuildRequires:	rpmbuild(macros) >= 1.605
%{?with_wayland:BuildRequires:	wayland-devel}
%{?with_x11:BuildRequires:	xorg-lib-libX11-devel}
Provides:	vulkan(loader) = %{version}
Obsoletes:	vulkan-loader < 1.1
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Common loader for Vulkan API drivers.

%description -l pl.UTF-8
Wspólna biblioteka wczytująca sterowniki Vulkan.

%package devel
Summary:	Development files files for the Vulkan loader
Summary(pl.UTF-8):	Pliki nagłówkowe loadera Vulkan
Group:		Development/Libraries
Requires:	Vulkan-Headers = %{api_version}
Requires:	Vulkan-Loader = %{version}-%{release}
Obsoletes:	vulkan-devel < 1.1.106

%description devel
Development files for the Vulkan loader.

%description devel -l pl.UTF-8
Pliki nagłówkowe loadera Vulkan.

%prep
%setup -qn %{name}-sdk-%{version}

%build
install -d build
cd build

# .pc file creation expect CMAKE_INSTALL_LIBDIR to be relative (to CMAKE_INSTALL_PREFIX)
%cmake .. \
	-DCMAKE_INSTALL_LIBDIR:PATH=%{_lib} \
	-DBUILD_TESTS=%{?with_tests:ON}%{!?with_tests:OFF} \
	-DBUILD_WSI_WAYLAND_SUPPORT=%{?with_wayland:ON}%{!?with_wayland:OFF} \
	-DBUILD_WSI_XLIB_SUPPORT=%{?with_x11:ON}%{!?with_x11:OFF} \
	-DBUILD_WSI_XCB_SUPPORT=%{?with_x11:ON}%{!?with_x11:OFF}

%{__make}

%if %{with tests}
cd tests
LC_ALL=C.UTF-8 \
LD_LIBRARY_PATH=../loader:layers \
VK_LAYER_PATH=layers \
./run_loader_tests.sh
cd ..
%endif

cd ..

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},%{_datadir}}/vulkan/{icd.d,explicit_layer.d,implicit_layer.d}

%{__make} -C build install \
	DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc README.md GOVERNANCE.md CONTRIBUTING.md
%dir %{_sysconfdir}/vulkan
%dir %{_sysconfdir}/vulkan/icd.d
%dir %{_sysconfdir}/vulkan/explicit_layer.d
%dir %{_sysconfdir}/vulkan/implicit_layer.d
%dir %{_datadir}/vulkan
%dir %{_datadir}/vulkan/icd.d
%dir %{_datadir}/vulkan/explicit_layer.d
%dir %{_datadir}/vulkan/implicit_layer.d
%attr(755,root,root) %{_libdir}/libvulkan.so.1.*.*
%attr(755,root,root) %ghost %{_libdir}/libvulkan.so.1

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libvulkan.so
%{_pkgconfigdir}/vulkan.pc
