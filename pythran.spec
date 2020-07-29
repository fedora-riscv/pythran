Name:           pythran
Version:        0.9.5
Release:        3%{?dist}
Summary:        Ahead of Time Python compiler for numeric kernels

# pythran is BSD
# pythran/pythonic/patch/complex is MIT or NCSA
License:        BSD and (MIT or NCSA)

# see pythran/pythonic/patch/README.rst
# The version is probably somewhat around 3
Provides:       bundled(libcxx) = 3

URL:            https://github.com/serge-sans-paille/pythran
Source0:        %{url}/archive/%{version}/%{name}-%{version}.tar.gz

# Fix ipython testing
# Backported from upstream
# https://bugzilla.redhat.com/show_bug.cgi?id=1813075
Patch1:         %{url}/commit/f5ae85881f47bfffe75ff2826e27d56514d69190.patch

# there is no actual arched content
# yet we want to test on all architectures
# and we also might need to skip some
%global debug_package %{nil}

BuildRequires:  boost-devel
BuildRequires:  gcc-c++
BuildRequires:  openblas-devel
BuildRequires:  pandoc
BuildRequires:  python3-beniget
BuildRequires:  python3-devel
BuildRequires:  python3-decorator
BuildRequires:  python3-flake8
BuildRequires:  python3-gast
BuildRequires:  python3-ipython
BuildRequires:  python3-nbsphinx
BuildRequires:  python3-networkx >= 2
BuildRequires:  python3-numpy
BuildRequires:  python3-ply >= 3.4
BuildRequires:  python3-pytest
BuildRequires:  python3-pytest-runner
BuildRequires:  python3-pytest-xdist
BuildRequires:  python3-setuptools
BuildRequires:  python3-scipy
BuildRequires:  python3-six
BuildRequires:  python3-sphinx
BuildRequires:  python3-wheel
BuildRequires:  xsimd-devel

# This is a package that compiles code, it runtime requires devel packages
Requires:       gcc-c++
Requires:       openblas-devel
Requires:       python3-devel
Requires:       boost-devel
Requires:       xsimd-devel

Recommends:     python3-scipy

Provides:       python3-%{name} = %{version}-%{release}
%{?python_provide:%python_provide python3-%{name}}

%description
Pythran is an ahead of time compiler for a subset of the Python language, with
a focus on scientific computing. It takes a Python module annotated with a few
interface description and turns it into a native Python module with the same
interface, but (hopefully) faster. It is meant to efficiently compile
scientific programs, and takes advantage of multi-cores and SIMD
instruction units.

%prep
%autosetup -p1
find -name '*.hpp' -exec chmod -x {} +
sed -i '1{/#!/d}' pythran/run.py

# Remove bundled header libs and use the ones from system
rm -r third_party/boost third_party/xsimd
cat >> setup.cfg << EOF
[build_py]
no_boost=True
no_xsimd=True
EOF

# openblas should be faster and crunchier
sed -i 's|blas=blas|blas=openblas|' pythran/pythran-linux*.cfg
sed -i 's|include_dirs=|include_dirs=/usr/include/openblas|' pythran/pythran-linux*.cfg

# not yet available in Fedora
sed -i '/guzzle_sphinx_theme/d' docs/conf.py

%build
%py3_build
PYTHONPATH=$PWD/build/lib make -C docs html
rm -rf docs/_build/html/.{doctrees,buildinfo}

%install
%py3_install

%check
# tests expect "python" and "ipython" commands
mkdir tmppath
ln -s %{__python3} tmppath/python
ln -s /usr/bin/ipython3 tmppath/ipython
export PATH="$(pwd)/tmppath:$PATH"
export PYTHONPATH=%{buildroot}%{python3_sitelib}

# test_numpy_negative_binomial: https://bugzilla.redhat.com/show_bug.cgi?id=1747029#c12
%{__python3} -m pytest -n auto -k "not test_numpy_negative_binomial"

%files
%license LICENSE
%doc README.rst
%doc docs/_build/html
%{_bindir}/%{name}
%{_bindir}/%{name}-config
%{python3_sitelib}/omp/
%{python3_sitelib}/%{name}/
%{python3_sitelib}/%{name}-*-py%{python3_version}.egg-info/

%changelog
* Wed Jul 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Fri Mar 13 2020 Miro Hrončok <mhroncok@redhat.com> - 0.9.5-2
- Fix tests with ipython 7.12+ (#1813075)

* Fri Jan 31 2020 Miro Hrončok <mhroncok@redhat.com> - 0.9.5-1
- Update to 0.9.5 (#1787813)

* Tue Dec 03 2019 Miro Hrončok <mhroncok@redhat.com> - 0.9.4post1-1
- Update to 0.9.4post1 (#1747029)

* Tue Aug 20 2019 Miro Hrončok <mhroncok@redhat.com> - 0.9.3-1
- Update to 0.9.3 (#1743187)
- Allow 32bit architectures

* Fri Jul 26 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Wed Jun 26 2019 Miro Hrončok <mhroncok@redhat.com> - 0.9.2-1
- Initial package
