from django.conf import settings
from django.core.checks import Warning, register


@register()
def allowed_hosts_check(app_configs, **kwargs):
    """Warn if ALLOWED_HOSTS is too permissive or doesn't include Render domain.

    On Render we expect at least one non-localhost host or the special
    ".onrender.com" suffix; otherwise the site will raise a DisallowedHost
    error and appear "down".  This helps the user notice misconfiguration
    early in deployment.
    """

    import os

    errors = []
    hosts = [h for h in settings.ALLOWED_HOSTS if h]
    if not hosts:
        errors.append(
            Warning(
                "ALLOWED_HOSTS is empty",
                hint="Set the ALLOWED_HOSTS environment variable (e.g. 'mysite.onrender.com').",
                id="myapp.W001",
            )
        )
    else:
        # check for Render domain in production
        if 'RENDER' in os.environ:
            if not any(h.endswith('.onrender.com') or 'onrender.com' in h for h in hosts):
                errors.append(
                    Warning(
                        "ALLOWED_HOSTS does not include a Render domain",
                        hint="Add your Render URL to ALLOWED_HOSTS or set the env var ALLOWED_HOSTS correctly.",
                        id="myapp.W002",
                    )
                )
    return errors


@register()
def csrf_origins_check(app_configs, **kwargs):
    import os

    errors = []
    origins = [o for o in settings.CSRF_TRUSTED_ORIGINS if o]
    if 'RENDER' in os.environ:
        render_url = os.environ.get('RENDER_EXTERNAL_URL')
        if render_url and render_url not in origins:
            errors.append(
                Warning(
                    "RENDER_EXTERNAL_URL is not in CSRF_TRUSTED_ORIGINS",
                    hint="Add the value of RENDER_EXTERNAL_URL to CSRF_TRUSTED_ORIGINS in settings or via env var.",
                    id="myapp.W003",
                )
            )
    return errors
