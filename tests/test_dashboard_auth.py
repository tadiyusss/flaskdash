
import inspect

def test_all_dashboard_routes_require_login(app):
    unprotected_routes = []
    excluded_endpoints = {
        "core.login",
        "core.register",
        "core.forgot_password",
        "core.reset_password",
        "core.logout",
        "core.static"
    }

    with app.test_request_context():
        for rule in app.url_map.iter_rules():
            if rule.endpoint in excluded_endpoints:
                continue
            if not rule.rule.startswith("/dashboard"):
                continue
            view_func = app.view_functions[rule.endpoint]
            source = inspect.getsource(view_func)

            if "@login_required" not in source:
                print(f"Route {rule.rule} does not have @login_required decorator.")
                unprotected_routes.append(rule.rule)

    assert not unprotected_routes, f"Unprotected routes found: {unprotected_routes}"