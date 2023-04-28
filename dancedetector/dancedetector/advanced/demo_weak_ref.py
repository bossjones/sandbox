"""
Weak references are a way to help the Python interpreter remove unused data
more easily. This module shows how it can be used to keep a server registry
up-to-date as it explicitly sets up and implicitly tears down servers as
the program enters and leaves a function scope.
"""
import weakref
from uuid import uuid4
import logging
from loguru import logger
from dancedetector.dbx_logger import (
    get_logger,
    intercept_all_loggers,
    global_log_config
)

global_log_config(
    log_level=logging.getLevelName("DEBUG"),
    json=False,
)

# Module-level constants
_CLOUD_PROVIDER = "aws"
_CLOUD_APPS = ["yelp", "pinterest", "uber", "twitter"]
_CLOUD_APP_COMPONENTS = ("db", "web", "cache")


class Server:
    """General server."""

    @classmethod
    def create(cls, role, provider=_CLOUD_PROVIDER):
        """Create server with autogenerated SSID."""
        return cls(uuid4().hex, role, provider)

    def __init__(self, ssid, role, provider):
        self.ssid = ssid
        self.role = role
        self.provider = provider


class ServerRegistry:
    """Server registry with weak references."""

    def __init__(self):
        self._servers = weakref.WeakSet()

    @property
    def servers(self):
        """Get set of added servers."""
        return {s for s in self._servers}

    @property
    def server_count(self):
        """Get count of added servers."""
        return len(self.servers)

    def add(self, server):
        """Add server to registry."""
        self._servers.add(server)


def setup_and_teardown_servers(registry):
    """Explicitly setup and implicitly teardown servers."""
    app_servers = {}

    # Let's create all of the servers and store them properly
    for app in _CLOUD_APPS:
        app_servers[app] = set()
        for component in _CLOUD_APP_COMPONENTS:
            server = Server.create(f"{app}_{component}")
            registry.add(server)
            app_servers[app].add(server)

    # All of these counts are equivalent. This is no surprise since our
    # for loop unconditionally creates a server for every permutation of
    # apps and components. The loop also adds each server to the registry
    # and dictionary unconditionally
    assert (
        registry.server_count
        == len(_CLOUD_APPS) * len(_CLOUD_APP_COMPONENTS)
        == len(
            [
                (app, server)
                for app, servers in app_servers.items()
                for server in servers
            ]
        )
    )

    # What's really interesting is that servers go away when we leave the
    # scope of this function. In this function, each server is created and
    # strongly referenced by the `app_servers` variable. When we leave this
    # function, the `app_servers` variable no longer exists which brings
    # the reference count for each server from 1 to 0. A reference count of
    # 0 for each server triggers the garbage collector to run the cleanup
    # process for all of the servers in this function scope


def main():
    # Initialize a server registry
    registry = ServerRegistry()

    # Setup and teardown servers with the registry
    setup_and_teardown_servers(registry)

    # Notice that our registry does not remember the servers because
    # it uses weak references. Because there are no strong references
    # to the created servers in `setup_and_teardown_servers`, the
    # garbage collector cleans up the servers. This behavior is usually
    # desired if we want to keep our software memory-efficient
    assert registry.servers == set()
    assert registry.server_count == 0


if __name__ == "__main__":
    main()
