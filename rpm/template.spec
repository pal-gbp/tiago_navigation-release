%bcond_without tests
%bcond_without weak_deps

%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%global __provides_exclude_from ^/opt/ros/humble/.*$
%global __requires_exclude_from ^/opt/ros/humble/.*$

Name:           ros-humble-tiago-2dnav
Version:        4.0.12
Release:        1%{?dist}%{?release_suffix}
Summary:        ROS tiago_2dnav package

License:        Apache License 2.0
URL:            https://github.com/pal-robotics/tiago_simulation
Source0:        %{name}-%{version}.tar.gz

Requires:       ros-humble-launch-pal
Requires:       ros-humble-nav2-bringup
Requires:       ros-humble-pmb2-maps
Requires:       ros-humble-ros2launch
Requires:       ros-humble-rviz2
Requires:       ros-humble-ros-workspace
BuildRequires:  ros-humble-ament-cmake-auto
BuildRequires:  ros-humble-ros-workspace
Provides:       %{name}-devel = %{version}-%{release}
Provides:       %{name}-doc = %{version}-%{release}
Provides:       %{name}-runtime = %{version}-%{release}

%if 0%{?with_tests}
BuildRequires:  ros-humble-ament-lint-auto
BuildRequires:  ros-humble-ament-lint-common
%endif

%description
TIAGo-specific launch files needed to run navigation on a TIAGo robot.

%prep
%autosetup -p1

%build
# In case we're installing to a non-standard location, look for a setup.sh
# in the install tree and source it.  It will set things like
# CMAKE_PREFIX_PATH, PKG_CONFIG_PATH, and PYTHONPATH.
if [ -f "/opt/ros/humble/setup.sh" ]; then . "/opt/ros/humble/setup.sh"; fi
mkdir -p .obj-%{_target_platform} && cd .obj-%{_target_platform}
%cmake3 \
    -UINCLUDE_INSTALL_DIR \
    -ULIB_INSTALL_DIR \
    -USYSCONF_INSTALL_DIR \
    -USHARE_INSTALL_PREFIX \
    -ULIB_SUFFIX \
    -DCMAKE_INSTALL_PREFIX="/opt/ros/humble" \
    -DAMENT_PREFIX_PATH="/opt/ros/humble" \
    -DCMAKE_PREFIX_PATH="/opt/ros/humble" \
    -DSETUPTOOLS_DEB_LAYOUT=OFF \
%if !0%{?with_tests}
    -DBUILD_TESTING=OFF \
%endif
    ..

%make_build

%install
# In case we're installing to a non-standard location, look for a setup.sh
# in the install tree and source it.  It will set things like
# CMAKE_PREFIX_PATH, PKG_CONFIG_PATH, and PYTHONPATH.
if [ -f "/opt/ros/humble/setup.sh" ]; then . "/opt/ros/humble/setup.sh"; fi
%make_install -C .obj-%{_target_platform}

%if 0%{?with_tests}
%check
# Look for a Makefile target with a name indicating that it runs tests
TEST_TARGET=$(%__make -qp -C .obj-%{_target_platform} | sed "s/^\(test\|check\):.*/\\1/;t f;d;:f;q0")
if [ -n "$TEST_TARGET" ]; then
# In case we're installing to a non-standard location, look for a setup.sh
# in the install tree and source it.  It will set things like
# CMAKE_PREFIX_PATH, PKG_CONFIG_PATH, and PYTHONPATH.
if [ -f "/opt/ros/humble/setup.sh" ]; then . "/opt/ros/humble/setup.sh"; fi
CTEST_OUTPUT_ON_FAILURE=1 \
    %make_build -C .obj-%{_target_platform} $TEST_TARGET || echo "RPM TESTS FAILED"
else echo "RPM TESTS SKIPPED"; fi
%endif

%files
/opt/ros/humble

%changelog
* Fri Mar 01 2024 Jordan Palacios <jordan.palacios@pal-robotics.com> - 4.0.12-1
- Autogenerated by Bloom

* Mon Dec 18 2023 Jordan Palacios <jordan.palacios@pal-robotics.com> - 4.0.9-1
- Autogenerated by Bloom

* Fri Jun 30 2023 Jordan Palacios <jordan.palacios@pal-robotics.com> - 4.0.5-1
- Autogenerated by Bloom

* Mon Apr 17 2023 Jordan Palacios <jordan.palacios@pal-robotics.com> - 4.0.4-1
- Autogenerated by Bloom

* Thu Dec 15 2022 Jordan Palacios <jordan.palacios@pal-robotics.com> - 4.0.2-1
- Autogenerated by Bloom

* Tue Nov 29 2022 Jordan Palacios <jordan.palacios@pal-robotics.com> - 4.0.1-1
- Autogenerated by Bloom

* Tue Nov 08 2022 Jordan Palacios <jordan.palacios@pal-robotics.com> - 4.0.0-1
- Autogenerated by Bloom

