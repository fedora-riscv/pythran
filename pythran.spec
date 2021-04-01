Name:           pythran
Version:        0.9.9
%global uver    0.9.9
Release:        1%{?dist}
Summary:        Ahead of Time Python compiler for numeric kernels

# pythran is BSD
# pythran/pythonic/patch/complex is MIT or NCSA
License:        BSD and (MIT or NCSA)

# see pythran/pythonic/patch/README.rst
# The version is probably somewhat around 3
Provides:       bundled(libcxx) = 3

%py_provides    python3-%{name}

URL:            https://github.com/serge-sans-paille/pythran
Source0:        %{url}/archive/%{uver}/%{name}-%{uver}.tar.gz

# there is no actual arched content
# yet we want to test on all architectures
# and we also might need to skip some
%global debug_package %{nil}

BuildRequires: make
BuildRequires:  boost-devel
BuildRequires:  flexiblas-devel
BuildRequires:  gcc-c++
BuildRequires:  pandoc
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-devel
BuildRequires:  xsimd-devel

# For tests
BuildRequires:  python3-pytest
BuildRequires:  python3-pytest-xdist
BuildRequires:  /usr/bin/python
BuildRequires:  /usr/bin/ipython
BuildRequires:  python3-scipy

# This is a package that compiles code, it runtime requires devel packages
Requires:       flexiblas-devel
Requires:       gcc-c++
Requires:       python3-devel
Requires:       boost-devel
Requires:       xsimd-devel

%description
Pythran is an ahead of time compiler for a subset of the Python language, with
a focus on scientific computing. It takes a Python module annotated with a few
interface description and turns it into a native Python module with the same
interface, but (hopefully) faster. It is meant to efficiently compile
scientific programs, and takes advantage of multi-cores and SIMD
instruction units.


%prep
%autosetup -p1 -n %{name}-%{uver}
find -name '*.hpp' -exec chmod -x {} +
sed -i '1{/#!/d}' pythran/run.py

# Remove bundled header libs and use the ones from system
rm -r third_party/boost third_party/xsimd
cat >> setup.cfg << EOF
[build_py]
no_boost=True
no_xsimd=True
EOF

# Both OpenBLAS and FlexiBLAS are registered as "openblas" in numpy
sed -i 's|blas=blas|blas=openblas|' pythran/pythran-linux*.cfg
sed -i 's|libs=|libs=flexiblas|' pythran/pythran-linux*.cfg
sed -i 's|include_dirs=|include_dirs=/usr/include/flexiblas|' pythran/pythran-linux*.cfg

# not yet available in Fedora
sed -i '/guzzle_sphinx_theme/d' docs/conf.py docs/requirements.txt


%generate_buildrequires
%pyproject_buildrequires -x doc


%build
%pyproject_wheel

PYTHONPATH=$PWD make -C docs html
rm -rf docs/_build/html/.{doctrees,buildinfo}


%install
%pyproject_install
%pyproject_save_files %{name} omp


%check
# test_numpy_negative_binomial: https://bugzilla.redhat.com/show_bug.cgi?id=1747029#c12
%pytest -n auto -k "not test_numpy_negative_binomial"


%files -f %{pyproject_files}
%license LICENSE
%doc README.rst
%doc docs/_build/html
%{_bindir}/%{name}
%{_bindir}/%{name}-config


%changelog
* Wed Mar 31 2021 sguelton@redhat.com - 0.9.9-1
- Update to 0.9.9

* Wed Jan 27 2021 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.8^post3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Mon Jan 18 2021 Serge Guelton - 0.9.8^post3-2
- Apply compatibility patch with numpy 1.20

* Sun Dec 13 2020 sguelton@redhat.com - 0.9.8^post3-1
- Update to 0.9.8post3
- No longer recommend SciPy

* Wed Sep 23 2020 Miro Hrončok <mhroncok@redhat.com> - 0.9.7-1
- Update to 0.9.7
- Rebuilt for Python 3.9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild
- https://fedoraproject.org/wiki/Changes/FlexiBLAS_as_BLAS/LAPACK_manager
- Fixes: rhbz#1818006
- Fixes: rhbz#1787813

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
