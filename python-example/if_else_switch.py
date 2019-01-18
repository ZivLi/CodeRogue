import time


def from_now(ts):
    now = time.time()
    seconds_delta = int(now - ts)

    if seconds_delta < 1:
        return 'less than 1 second ago'
    elif seconds_delta < 60:
        return "{} seconds ago".format(seconds_delta)
    elif seconds_delta < 3600:
        return "{} minutes ago".format(seconds_delta // 60)
    elif seconds_delta < 3600 * 24:
        return "{} hours ago".format(seconds_delta // 3600)
    else:
        return "{} days ago".format(seconds_delta // (3600 * 24))

now = time.time()
print(from_now(now))
print(from_now(now - 24))
print(from_now(now - 600))
print(from_now(now - 7500))
print(from_now(now - 87500))


# Optimize Version
import bisect

# BREAKPOINTS must be ordered.
BREAKPOINTS = (1, 60, 3600, 3600*24)
TMPLS = (
    # unit, template
    (1, "less than 1 second ago"),
    (1, "{units} seconds ago"),
    (60, "{units} minutes ago"),
    (3600, "{units} hours ago"),
    (3600 * 24, "{units} days ago"),
)

def from_now_optimize(ts):
    seconds_delta = int(time.time() - ts)
    unit, tmpl = TMPLS[bisect.bisect(BREAKPOINTS, seconds_delta)]
    return tmpl.format(units=seconds_delta // unit)

print(from_now_optimize(now))
print(from_now_optimize(now - 24))
print(from_now_optimize(now - 600))
print(from_now_optimize(now - 7500))
print(from_now_optimize(now - 87500))
