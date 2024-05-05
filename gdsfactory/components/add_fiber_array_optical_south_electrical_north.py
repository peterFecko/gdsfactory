from typing import Any

import gdsfactory as gf
from gdsfactory.components.grating_coupler_elliptical import (
    grating_coupler_elliptical_te,
)
from gdsfactory.components.mzi import mzi_phase_shifter
from gdsfactory.components.pad import pad_small
from gdsfactory.typings import ComponentSpec, CrossSectionSpec


@gf.cell
def add_fiber_array_optical_south_electrical_north(
    component: ComponentSpec = mzi_phase_shifter,
    pad: ComponentSpec = pad_small,
    with_loopback: bool = True,
    pad_spacing: float = 100.0,
    fiber_spacing: float = 127.0,
    pad_gc_spacing: float = 250.0,
    electrical_port_names: list[str] | None = None,
    electrical_port_orientation: float | None = 90,
    npads: int | None = None,
    grating_coupler: ComponentSpec = grating_coupler_elliptical_te,
    xs_metal: CrossSectionSpec = "xs_metal_routing",
    analysis_settings: dict[str, Any] | None = None,
    **kwargs,
) -> gf.Component:
    """Returns a fiber array with Optical gratings on South and Electrical pads on North.

    This a test configuration for DC pads.

    Args:
        component: component spec to add fiber and pads.
        pad: pad spec.
        with_loopback: whether to add a loopback port.
        pad_spacing: spacing between pads.
        fiber_spacing: spacing between grating couplers.
        pad_gc_spacing: spacing between pads and grating couplers.
        electrical_port_names: list of electrical port names. Defaults to all.
        electrical_port_orientation: orientation of electrical ports. Defaults to 90.
        npads: number of pads. Defaults to one per electrical_port_names.
        grating_coupler: grating coupler function.
        xs_metal: metal cross section.
        layer_label: layer for settings label.
        measurement: measurement name.
        measurement_settings: measurement settings.
        analysis: analysis name.
        analysis_settings: analysis settings.
        doe: Design of Experiment.
        anchor: anchor point for the label. Defaults to south-west "sw". \
            Valid options are: "n", "s", "e", "w", "ne", "nw", "se", "sw", "c".

    Keyword Args:
        gc_port_name: grating coupler input port name.
        gc_port_labels: grating coupler list of labels.
        component_name: optional for the label.
        select_ports: function to select ports.
        cross_section: cross_section function.
        get_input_labels_function: function to get input labels. None skips labels.
        layer_label: optional layer for grating coupler label.
        bend: bend spec.
        straight: straight spec.
        taper: taper spec.
        get_input_label_text_loopback_function: function to get input label test.
        get_input_label_text_function: for labels.
        fanout_length: if None, automatic calculation of fanout length.
        max_y0_optical: in um.
        with_loopback: True, adds loopback structures.
        straight_separation: from edge to edge.
        list_port_labels: None, adds TM labels to port indices in this list.
        connected_port_list_ids: names of ports only for type 0 optical routing.
        nb_optical_ports_lines: number of grating coupler lines.
        force_manhattan: False
        excluded_ports: list of port names to exclude when adding gratings.
        grating_indices: list of grating coupler indices.
        routing_straight: function to route.
        routing_method: route_single.
        optical_routing_type: None: auto, 0: no extension, 1: standard, 2: check.
        gc_rotation: fiber coupler rotation in degrees. Defaults to -90.
        input_port_indexes: to connect.

    """
    c = gf.Component()
    component = gf.get_component(component)
    r = c << gf.routing.add_fiber_array(
        component=component,
        grating_coupler=grating_coupler,
        with_loopback=with_loopback,
        fiber_spacing=fiber_spacing,
        **kwargs,
    )
    optical_ports = r.ports.filter(port_type="optical")
    c.add_ports(optical_ports)

    electrical_ports = r.ports.filter(
        port_type="electrical", orientation=electrical_port_orientation
    )
    electrical_port_names = electrical_port_names or [p.name for p in electrical_ports]

    npads = npads or len(electrical_port_names)
    pads = c << gf.components.array(
        component=pad,
        columns=npads,
        spacing=(pad_spacing, 0),
    )
    pads.x = r.x
    pads.d.ymin = r.d.ymin + pad_gc_spacing

    electrical_ports = [r[por_name] for por_name in electrical_port_names]
    nroutes = min(len(electrical_ports), npads)

    ports1 = electrical_ports[:nroutes]
    ports2 = list(pads.ports.filter(orientation=270))[:nroutes]
    gf.routing.route_bundle_electrical(
        c,
        ports1=ports1,
        ports2=ports2,
        cross_section=xs_metal,
        enforce_port_ordering=False,
    )

    c.add_ports(ports2)
    analysis_settings = analysis_settings or {}
    # c.copy_child_info(r)
    return c


if __name__ == "__main__":
    c = add_fiber_array_optical_south_electrical_north()

    # component = mzi_phase_shifter()
    # grating_coupler=grating_coupler_elliptical_te()
    # with_loopback: bool = True
    # pad_spacing: float = 100.0
    # fiber_spacing: float = 127.0
    # pad_gc_spacing: float = 250.0
    # electrical_port_names: list[str] | None = None
    # electrical_port_orientation: float | None = 90
    # npads: int | None = None

    # c = gf.Component()
    # component = gf.get_component(component)
    # r = c << gf.routing.add_fiber_array(
    #     component=component,
    #     grating_coupler=grating_coupler,
    #     with_loopback=with_loopback,
    #     fiber_spacing=fiber_spacing,
    # )
    # optical_ports = gf.port.get_ports_list(r.ports, port_type="optical")
    # c.add_ports(optical_ports)

    # electrical_ports = gf.port.get_ports_list(
    #     r.ports, port_type="electrical", orientation=electrical_port_orientation
    # )
    # electrical_port_names = electrical_port_names or [p.name for p in electrical_ports]

    # d = json.loads(c.labels[0].text)
    # print(d)
    # import gdsfactory as gf
    # from functools import partial

    # component = partial(mzi_phase_shifter, length_y=1)
    # c = add_fiber_array_optical_south_electrical_north(
    #     component=component,
    #     electrical_port_names=["top_l_e2", "top_r_e2"],
    #     npads=5,
    # )
    # component = partial(gf.c.ring_single_heater, length_x=10)
    # c = add_fiber_array_optical_south_electrical_north(
    #     component=component,
    #     electrical_port_names=["l_e2", "r_e2"],
    #     npads=5,
    # )
    c.show()
