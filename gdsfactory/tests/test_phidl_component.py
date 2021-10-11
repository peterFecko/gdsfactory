import phidl.geometry as pg

import gdsfactory as gf


def component_phidl(function_name: str, **kwargs) -> gf.Component:
    if not hasattr(pg, function_name):
        raise ValueError(f"{function_name} not in {dir(pg)}")
    component_function = getattr(pg, function_name)
    device = component_function(**kwargs)
    return gf.read.from_phidl(device)


def test_import_component_phidl():
    component_phidl(function_name="L")


if __name__ == "__main__":
    test_import_component_phidl()
