"""
Provide a set of Hypothesis Strategies for various Fido related tests.
"""
import hypothesis.strategies as st
from hypothesis import assume
from hypothesis.extra.datetime import datetimes

import datetime
from sunpy.net import attrs as a
from sunpy.time import parse_time, TimeRange


@st.composite
def timedelta(draw):
    """
    Timedelta strategy that limits the maximum timedelta to being positive and
    abs max is about 100 weeks + 100 days + 100 hours + a bit
    """
    keys = st.sampled_from(['days', 'seconds', 'microseconds', 'milliseconds',
                            'minutes', 'hours', 'weeks'])
    values = st.floats(min_value=0, max_value=100)
    return datetime.timedelta(**draw(st.dictionaries(keys, values)))


def offline_instruments():
    """
    Returns a strategy for any instrument that does not need the internet to do
    a query
    """
    offline_instr = ['lyra', 'norh', 'noaa-indices', 'noaa-predict', 'goes']
    offline_instr = st.builds(a.Instrument, st.sampled_from(offline_instr))

    eve = st.just(a.Instrument('eve') & a.Level(0))
    return st.one_of(offline_instr, eve)


def online_instruments():
    """
    Returns a strategy for any instrument that does not need the internet to do
    a query
    """
    online_instr = ['rhessi']
    online_instr = st.builds(a.Instrument, st.sampled_from(online_instr))

    return online_instr


@st.composite
def time_attr(draw, time=datetimes(timezones=[],
                                   max_year=datetime.datetime.utcnow().year,
                                   min_year=1900),
              delta=timedelta()):
    """
    Create an a.Time where it's always positive and doesn't have a massive time
    delta.
    """
    t1 = draw(time)
    t2 = t1 + draw(delta)
    # We can't download data from the future...
    assume(t2 < datetime.datetime.utcnow())

    return a.Time(t1, t2)


@st.composite
def goes_time(draw, time=datetimes(timezones=[],
                                   max_year=datetime.datetime.utcnow().year,
                                   min_year=1981),
              delta=timedelta()):
    """
    Create an a.Time where it's always positive and doesn't have a massive time
    delta.
    """
    t1 = draw(time)
    t2 = t1 + draw(delta)
    # We can't download data from the future...
    assume(t2 < datetime.datetime.utcnow())

    tr = TimeRange(t1, t2)
    assume(parse_time("1983-05-01") not in tr)

    return a.Time(tr)


def rhessi_time():
    time = datetimes(timezones=[], max_year=datetime.datetime.utcnow().year,
                     min_year=2002)
    time = time.filter(lambda x: x > parse_time('2002-02-01'))
    return time_attr(time=time)
