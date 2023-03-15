# _*_ coding: UTF-8 _*_
"""
@file            : curl_generate_util
@Author          : qtclm
@Date            : 2023/2/9 15:47
@Desc            : 
"""
# source_code: curlify库

try:  # py3
    from shlex import quote
except ImportError:  # py2
    from pipes import quote
import requests


def to_curl(request, compressed=False, verify=True):
    if  isinstance(request,requests.models.Response):
        request=request.request
    """
    Returns string with curl command by provided request object

    Parameters
    ----------
    compressed : bool
        If `True` then `--compressed` argument will be added to result
    """
    parts = [
        ('curl', None),
        ('-X', request.method),
    ]

    for k, v in sorted(request.headers.items()):
        parts += [('-H', '{0}: {1}'.format(k, v))]

    if request.body:
        body = request.body
        if isinstance(body, bytes):
            body = body.decode('utf-8')
        parts += [('-d', body)]

    if compressed:
        parts += [('--compressed', None)]

    if not verify:
        parts += [('--insecure', None)]

    parts += [(None, request.url)]

    flat_parts = []
    for k, v in parts:
        if k:
            flat_parts.append(quote(k))
        if v:
            flat_parts.append(quote(v))

    return ' '.join(flat_parts)