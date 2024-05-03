"""
File-watching subroutines, built on watchdog.
"""

import sys
import time


def make_handler(ctx, task_, regexes, ignore_regexes, *args, **kwargs):
    args = [ctx] + list(args)
    try:
        from watchdog.events import RegexMatchingEventHandler
    except ImportError:
        sys.exit("If you want to use this, 'pip install watchdog' first.")

    class Handler(RegexMatchingEventHandler):
        def on_any_event(self, event):
            try:
                task_(*args, **kwargs)
            except BaseException:
                pass

    return Handler(regexes=regexes, ignore_regexes=ignore_regexes)


def observe(*handlers):
    try:
        from watchdog.observers import Observer
    except ImportError:
        sys.exit("If you want to use this, 'pip install watchdog' first.")

    observer = Observer()
    # TODO: Find parent directory of tasks.py and use that.
    for handler in handlers:
        observer.schedule(handler, ".", recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def watch(c, task_, regexes, ignore_regexes, *args, **kwargs):
    observe(make_handler(c, task_, regexes, ignore_regexes, *args, **kwargs))


# @task
# def watch_tests(c, module=None, opts=None):
#     """
#     Watch source tree and test tree for changes, rerunning tests as necessary.
#     Honors ``tests.package`` setting re: which source directory to watch for
#     changes.
#     """
#     package = c.config.get("tests", {}).get("package")
#     patterns = [r"\./tests/"]
#     if package:
#         patterns.append(r"\./{}/".format(package))
#     kwargs = {"module": module, "opts": opts}
#     # Kick things off with an initial test (making sure it doesn't exit on its
#     # own if tests currently fail)
#     c.config.run.warn = True
#     test(c, **kwargs)
#     # Then watch
#     watch(c, test, patterns, [r".*/\..*\.swp"], **kwargs)
