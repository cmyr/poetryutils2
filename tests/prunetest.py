# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

from poetryutils2 import prune_dict
test_dict = {"contributors": None, "truncated": False, "text": "@swirlylapin its like a control panel thing, look at this ;P http://t.co/a70Q8fWevd", "in_reply_to_status_id": 561219746591703040, "id": 561222286385377281, "favorite_count": 0, "source": "<a href=\"http://twitter.com\" rel=\"nofollow\">Twitter Web Client</a>", "retweeted": False, "properties": {"fake": "definitely", "cool": "always"}}

def test_prune():
    dict_template = {
    "contributors": True,
    "text": True,
    "properties": {"fake": True}
    }

    result = prune_dict(test_dict, dict_template)
    print(result)




def main():
    test_prune()


if __name__ == "__main__":
    main()