# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-25 21:45:04
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-29 13:21:12

# custom imports
from tests.configure_test_idp import MockFastAPIKeycloak


def test_singleton():

    instance_1 = MockFastAPIKeycloak()
    instance_2 = MockFastAPIKeycloak()

    assert instance_1 == instance_2

    instance_1.my_var = 0
    assert instance_1.my_var == 0

    instance_2.my_var = 1
    assert instance_2.my_var == 1

    assert instance_1 == instance_2
    assert instance_1.my_var == 1
    assert instance_2.my_var == 1
