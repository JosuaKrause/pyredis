from test.util import get_test_config

from redipy.redis.conn import RedisConnection


def test_sanity() -> None:
    redis = RedisConnection("test_sanity", cfg=get_test_config())

    def check_expression(
            raw: str,
            out: str,
            *,
            keys: list[str] | None = None,
            args: list[str] | None = None) -> None:
        if keys is None:
            keys = []
        if args is None:
            args = []
        code = f"return tostring({raw})"
        run = redis.get_dynamic_script(code)
        with redis.get_connection() as conn:
            res = run(
                keys=[redis.with_prefix(key) for key in keys],
                args=args,
                client=conn)
        assert res.decode("utf-8") == out

    # get
    check_expression("redis.call('get', KEYS[1])", "false", keys=["foo"])
    check_expression(
        "type(redis.call('get', KEYS[1]))", "boolean", keys=["foo"])
    assert redis.get("foo") is None

    # set
    check_expression(
        "cjson.encode(redis.call('set', KEYS[1], 'a'))",
        r'{"ok":"OK"}',
        keys=["bar"])
    check_expression("redis.call('get', KEYS[1])", "a", keys=["bar"])
    check_expression(
        "type(redis.call('get', KEYS[1]))", "string", keys=["bar"])
    check_expression(
        "cjson.encode(redis.call('set', KEYS[1], 'b'))",
        r'{"ok":"OK"}',
        keys=["bar"])
    check_expression("redis.call('get', KEYS[1])", "b", keys=["bar"])
    check_expression(
        "type(redis.call('get', KEYS[1]))", "string", keys=["bar"])
    assert redis.get("bar") == "b"
    assert redis.set("baz", "c") is True
    assert redis.get("baz") == "c"

    # lpop
    check_expression("redis.call('lpop', KEYS[1])", "false", keys=["foo"])
    check_expression(
        "type(redis.call('lpop', KEYS[1]))", "boolean", keys=["foo"])
    assert redis.lpop("foo") is None

    # rpop
    check_expression("redis.call('rpop', KEYS[1])", "false", keys=["foo"])
    check_expression(
        "type(redis.call('rpop', KEYS[1]))", "boolean", keys=["foo"])
    assert redis.rpop("foo") is None

    # llen
    check_expression("redis.call('llen', KEYS[1])", "0", keys=["foo"])
    check_expression(
        "type(redis.call('llen', KEYS[1]))", "number", keys=["foo"])
    assert redis.llen("foo") == 0

    # zpopmax
    check_expression(
        "cjson.encode(redis.call('zpopmax', KEYS[1]))", r"{}", keys=["foo"])
    assert redis.zpop_max("foo") == []  # pylint: disable=C1803
    check_expression("redis.call('zadd', KEYS[1], 2, 'a')", "1", keys=["zbar"])
    check_expression(
        "cjson.encode(redis.call('zpopmax', KEYS[1]))",
        "[\"a\",\"2\"]",
        keys=["zbar"])
    check_expression("redis.call('zadd', KEYS[1], 2, 'a')", "1", keys=["zbar"])
    check_expression(
        "cjson.encode(redis.call('zpopmax', KEYS[1], 1))",
        "[\"a\",\"2\"]",
        keys=["zbar"])
    check_expression("redis.call('zadd', KEYS[1], 2, 'a')", "1", keys=["zbar"])
    check_expression("redis.call('zadd', KEYS[1], 3, 'b')", "1", keys=["zbar"])
    check_expression(
        "cjson.encode(redis.call('zpopmax', KEYS[1], 2))",
        "[\"b\",\"3\",\"a\",\"2\"]",
        keys=["zbar"])
    check_expression("redis.call('zadd', KEYS[1], 2, 'a')", "1", keys=["zbar"])
    assert redis.zpop_max("zbar", 2) == [("a", 2)]
    check_expression("redis.call('zadd', KEYS[1], 2, 'a')", "1", keys=["zbar"])
    check_expression("redis.call('zadd', KEYS[1], 3, 'b')", "1", keys=["zbar"])
    assert redis.zpop_max("zbar", 2) == [("b", 3), ("a", 2)]

    # zpopmin
    check_expression(
        "cjson.encode(redis.call('zpopmin', KEYS[1]))", r"{}", keys=["foo"])
    assert redis.zpop_min("foo") == []  # pylint: disable=C1803
    check_expression("redis.call('zadd', KEYS[1], 2, 'a')", "1", keys=["zbar"])
    check_expression(
        "cjson.encode(redis.call('zpopmin', KEYS[1]))",
        "[\"a\",\"2\"]",
        keys=["zbar"])
    check_expression("redis.call('zadd', KEYS[1], 2, 'a')", "1", keys=["zbar"])
    check_expression(
        "cjson.encode(redis.call('zpopmin', KEYS[1], 1))",
        "[\"a\",\"2\"]",
        keys=["zbar"])
    check_expression("redis.call('zadd', KEYS[1], 2, 'a')", "1", keys=["zbar"])
    check_expression("redis.call('zadd', KEYS[1], 3, 'b')", "1", keys=["zbar"])
    check_expression(
        "cjson.encode(redis.call('zpopmin', KEYS[1], 2))",
        "[\"a\",\"2\",\"b\",\"3\"]",
        keys=["zbar"])
    check_expression("redis.call('zadd', KEYS[1], 2, 'a')", "1", keys=["zbar"])
    assert redis.zpop_min("zbar", 2) == [("a", 2)]
    check_expression("redis.call('zadd', KEYS[1], 2, 'a')", "1", keys=["zbar"])
    check_expression("redis.call('zadd', KEYS[1], 3, 'b')", "1", keys=["zbar"])
    assert redis.zpop_min("zbar", 2) == [("a", 2), ("b", 3)]
