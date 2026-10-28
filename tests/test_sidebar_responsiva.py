from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_layout_expoe_controles_acessiveis_da_sidebar():
    sidebar = (ROOT / "app/templates/components/sidebar.html").read_text()
    navbar = (ROOT / "app/templates/components/navbar.html").read_text()
    layout = (ROOT / "app/templates/layout/base.html").read_text()

    assert 'id="appSidebar"' in sidebar
    assert "data-sidebar-close" in sidebar
    assert "data-sidebar-toggle" in navbar
    assert 'aria-controls="appSidebar"' in navbar
    assert "sidebar-overlay" in layout


def test_sidebar_mobile_possui_abertura_e_fechamento_automaticos():
    javascript = (ROOT / "app/static/js/app.js").read_text()
    estilos = (ROOT / "app/static/css/style.css").read_text()

    assert "sidebar-mobile-open" in javascript
    assert 'event.key === "Escape"' in javascript
    assert 'event.target.closest(".sidebar-menu a")' in javascript
    assert "body.sidebar-mobile-open .sidebar" in estilos
    assert "body.sidebar-mobile-open .sidebar-overlay" in estilos


def test_sidebar_recolhida_mantem_icones_no_desktop():
    sidebar = (ROOT / "app/templates/components/sidebar.html").read_text()
    estilos = (ROOT / "app/static/css/style.css").read_text()

    assert "sidebar-item-label" in sidebar
    assert 'title="{{ item.label }}"' in sidebar
    assert "width:76px" in estilos
    assert "body.sidebar-collapsed .sidebar-menu a i" in estilos
