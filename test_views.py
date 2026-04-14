import os
import django
from django.test import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

def simulate():
    c = Client()
    print("Testing / ...")
    r = c.get("/")
    print("Result /:", r.status_code, r.url if hasattr(r, 'url') else '')

    print("Testing /dashboard/admin/ ...")
    r2 = c.get("/dashboard/admin/")
    print("Result /dashboard/admin/:", r2.status_code)

    print("Testing /login/ ...")
    r3 = c.get("/login/")
    print("Result /login/:", r3.status_code)

    print("Testing /usuarios/registro/ ...")
    r4 = c.get("/usuarios/registro/")
    print("Result /usuarios/registro/:", r4.status_code)

if __name__ == "__main__":
    try:
        simulate()
    except Exception as e:
        import traceback
        traceback.print_exc()
