import sys
sys.path.append('../')
from pynyzo.clienthelpers import NyzoClient


def test_client_frozen(verbose=False):
    client = NyzoClient()
    res = client.get_frozen()
    if verbose:
        print("res", res)
    assert "height" in res
    assert "hash" in res
    assert "timestamp" in res


def test_client_send(verbose=False):
    client = NyzoClient()
    # Test vector, do not use IRL
    res = client.send(recipient="id__88idJKWPQ~j4adLXXIVreIHpn1dnHNXL0AvRw.dNI3PZXtxdHx7u",
                      amount=0,
                      data="test",
                      key_="key_87jpjKgC.hXMHGLL50Ym9x4GSnGR918PV6CzpqKwM6WEgqRzfABZ")
    if verbose:
        print("res", res)
    assert "block height" in res
    assert "forwarded" in res
    assert "tx__" in res
    assert res["forwarded"] == "false"
    assert "error" in res
    # Test vector, do not use IRL
    res = client.send(recipient="id__88idJKWPQ~j4adLXXIVreIHpn1dnHNXL0AvRw.dNI3PZXtxdHx7u",
                      amount=1,
                      data="test",
                      key_="key_87jpjKgC.hXMHGLL50Ym9x4GSnGR918PV6CzpqKwM6WEgqRzfABZ")
    if verbose:
        print("res", res)
    assert "block height" in res
    assert "forwarded" in res
    assert "tx__" in res
    assert "error" not in res
    assert res["forwarded"] == "true"


def test_query_tx(verbose=False):
    # valid format but non existing tx
    tx = "tx__Ex80005V9jQZj00000000000y8UQVA7bXcgFUZEDMuFYLGyp4TrI3DW2dZd_SV2Jf7J000000a94zmGmH~BUTQLE0soovtG4Q-Pqsj4.0J.TgZLDSyDId_~yN17hCtVifoSKi8UnJdoTYhCzuvhqq7rjxkr_.ecK~vaJJe.rb2ACj.3icD29_VnH6dz7u~GPS-aNu2m9ztGd_KQvAzRxbTSzXvX8f"
    client = NyzoClient()
    res = client.query_tx(tx)
    if verbose:
        print("res1", res)
    assert "height" not in res

    # real tx, but may be past retention edge
    tx = "tx__Dx40005V9j-ti000000m~Jmn4KhkGGkA.REIoIttwvL70hx4VRdHWeb1ExJBGAqFfA400000000001bkmarm8_tXYTYV77VIyN4p1d-RrL3zNqWb9apUr3WP00KXB4MbiWoAY-bEF~GAC_8rjDDVQ2p_VtiXQVL7yoAaidw5YELtQPEL.7xVE4xjpZX9MaHPdEhLo2SYjoVeJ0eaLH~I"
    res = client.query_tx(tx)
    if verbose:
        print("res2", res)
    assert "height" in res


if __name__ == "__main__":
    test_client_frozen(True)
    test_client_send(True)
    test_query_tx(True)
