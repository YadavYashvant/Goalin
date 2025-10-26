# Maintainer: YadavYashvant <your-email@example.com>
pkgname=goalin
pkgver=0.1.0
pkgrel=1
pkgdesc="A productivity tracking service for Linux with GTK interface"
arch=('any')
url="https://github.com/YadavYashvant/Goalin"
license=('MIT')
depends=('python>=3.9'
         'python-gobject'
         'gtk4'
         'libadwaita'
         'python-xlib'
         'python-pytz')
makedepends=('python-setuptools')
source=("git+https://github.com/YadavYashvant/Goalin.git#tag=v${pkgver}")
sha256sums=('SKIP')

build() {
    cd "${srcdir}/${pkgname}"
    python setup.py build
}

package() {
    cd "${srcdir}/${pkgname}"
    
    # Install Python package
    python setup.py install --root="${pkgdir}" --optimize=1 --skip-build
    
    # Install systemd user service
    install -Dm644 goalin.service "${pkgdir}/usr/lib/systemd/user/goalin.service"
    
    # Install desktop file
    install -Dm644 goalin.desktop "${pkgdir}/usr/share/applications/goalin.desktop"
    
    # Install license
    install -Dm644 LICENSE "${pkgdir}/usr/share/licenses/${pkgname}/LICENSE"
    
    # Install documentation
    install -Dm644 README.md "${pkgdir}/usr/share/doc/${pkgname}/README.md"
}
