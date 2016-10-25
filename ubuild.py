import os
import subprocess
import datetime
from uranium import task_requires


SCRIPT_URLS = [
    "https://raw.githubusercontent.com/yunstanford/GraphiteSetup/master/carbon_cache.py",
    "https://raw.githubusercontent.com/yunstanford/GraphiteSetup/feature/MON-128004/run",
    "https://raw.githubusercontent.com/yunstanford/GraphiteSetup/feature/MON-128004/shutdown",
    "https://raw.githubusercontent.com/yunstanford/GraphiteSetup/master/mysql_script.sql",
    "https://raw.githubusercontent.com/yunstanford/GraphiteSetup/feature/MON-128004/setup_carbon_relay_ng.sh"
]
ROOT = os.path.dirname(os.path.realpath("__file__"))


def main(build):
    build.packages.install(".", develop=True)


@task_requires("main")
def build(build):
    _install_dependencies(build)
    build.executables.run([
        "pip", "install", "carbon",
        "--install-option", "--prefix={0}".format(ROOT),
        "--install-option", "--install-lib={0}/lib".format(ROOT)
    ])
    build.executables.run([
        "pip", "install", "graphite-web",
        "--install-option", "--prefix={0}".format(ROOT),
        "--install-option", "--install-lib={0}/webapp".format(ROOT)
    ])
    _config(build)
    _download_scripts(build)
    _setup_carbon_relay_ng(build)


def syncdb(build):
    _print("=== Set up webapp backend ===")
    _print("Creating user and database...")
    cmd = ""
    with open('{0}/bin/mysql_script.sql'.format(ROOT), 'r') as mysql:
        cmd = mysql.read().replace('\n', '')
    build.executables.run([
        "mysql", "-u", "root",
        "-t", "-e", cmd
    ])
    _print("Successfully created user and database!")
    _print("Creating tables...")
    build.executables.run([
        "python", "{0}/webapp/graphite/manage.py".format(ROOT),
        "syncdb"
    ])
    _print("Successfully created tables!")
    _print("=== Done! ===")


def webapp(build):
    build.executables.run([
        "gunicorn", "graphite_wsgi:application",
        "-c", "{0}/conf/gunicorn_prod.py".format(ROOT)
    ])


def dev(build):
    build.executables.run([
        "python", "{0}/bin/run-graphite-devel-server.py".format(ROOT), ROOT
    ])


def distribute(build):
    """ distribute the uranium package """
    build.packages.install("wheel")
    build.executables.run([
        "python", "setup.py",
        "sdist", "bdist_wheel", "--universal", "upload"
    ])


def build_docs(build):
    build.packages.install("sphinx")
    return subprocess.call(
        ["make", "html"], cwd=os.path.join(build.root, "docs")
    )


def _install_dependencies(build):
    build.packages.install("whisper")
    build.packages.install("zope.interface")
    build.packages.install("Django", version="==1.5")
    build.packages.install("django-tagging", version="==0.3.6")
    build.packages.install("python-memcached")
    build.packages.install("txAMQP", version="==0.4")
    build.packages.install("simplejson", version="==2.1.6")
    build.packages.install("pytz")
    build.packages.install("gunicorn")
    build.packages.install("Twisted", version="==16.4.1")
    build.packages.install("pyparsing", version="==1.5.7")
    build.packages.install("MySQL-python")
    build.packages.install("cairocffi")


def _config(build):
    _print("=== Configuring... ===")
    _print("Configuring Carbon...")
    build.executables.run([
        "cp", "-R", "{0}/conf_default/config/".format(ROOT),
        "{0}/conf/".format(ROOT)
    ])
    _print("Successfully done!")
    _print("Configuring Webapp...")
    build.executables.run([
        "cp", "{0}/conf_default/local_settings.py".format(ROOT),
        "{0}/webapp/graphite/".format(ROOT)
    ])
    _print("Successfully done!")
    _print("Configuring general graphite settings...")
    build.executables.run([
        "cp", "{0}/conf_default/graphite.wsgi".format(ROOT),
        "{0}/graphite_wsgi.py".format(ROOT)
    ])
    _print("Successfully done!")
    _print("Configuring gunicorn...")
    build.executables.run([
        "cp", "{0}/conf_default/gunicorn_prod.py".format(ROOT),
        "{0}/conf/".format(ROOT)
    ])
    _print("Successfully done!")
    _print("=== Done! ===")


def _download_scripts(build):
    for url in SCRIPT_URLS:
        _download(build, url, 'bin')


def _download(build, url, destination):
    cache_path = "{0}/{1}".format(ROOT, destination)
    filename = url.split("/")[-1]
    _print("Downloading {0} script from ".format(filename) + url)
    try:
        from urllib2 import urlopen as urlopen
    except:
        from urllib.request import urlopen as urlopen
    _print("loading script...")
    body = urlopen(url).read()
    _print("caching script...")
    _store_cache(body, cache_path, filename)
    _chmod(build, cache_path, filename)
    _print("=== Done! ===")


def _setup_carbon_relay_ng(build):
    _print("=== Compiling Carbon relay ng ===")
    build.executables.run([
        "sh", "{0}/bin/setup_carbon_relay_ng.sh".format(ROOT)
    ])
    _print("=== Done! ===")


def _store_cache(body, cache_path, filename):
    if not os.path.exists(cache_path):
        os.makedirs(cache_path)
    cached_script = os.path.join(cache_path, filename)
    with open(cached_script, "wb+") as fh:
        fh.write(body)


def _chmod(build, path, filename):
    build.executables.run([
        "chmod", "+x", "{0}/{1}".format(path, filename)
    ])
    _print("Change {0}/{1} permision mode to be 755".format(path, filename))


def _now():
    return datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S')


def _print(msg):
    print("[{0}] {1}".format(_now(), msg))
